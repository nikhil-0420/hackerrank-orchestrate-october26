"""
Unit tests for Ghost Audit LLM bounded subsystem (Phase 5).
Verifies:
- Schemas reject unknown fields and enforce types
- Cache operations (get/set/hash)
- Usage ledger cost calculation and reconciliation
- Prompts integrity and presence of adversarial examples
- Keyless client behavior (deterministic fallback, no key leaks)
"""

import os
from pathlib import Path
import unittest
from pydantic import ValidationError

from ghost_audit.llm.schemas import (
    ExtractedRecord,
    IntentType,
    L1IntentOutput,
    L2DocumentOutput,
    L4LinkageOutput,
    LinkageDecision,
)
from ghost_audit.llm.cache import LLMCache
from ghost_audit.llm.usage import UsageLedger, load_pricing_table
from ghost_audit.llm.client import LLMClient


class TestLLMSchemas(unittest.TestCase):
    def test_l1_intent_valid(self):
        data = {
            "intent": "DELETE",
            "authorizes_deletion": True,
            "quote": "delete all my data",
            "confidence": 0.99,
        }
        res = L1IntentOutput.model_validate(data)
        self.assertEqual(res.intent, IntentType.DELETE)
        self.assertTrue(res.authorizes_deletion)
        self.assertEqual(res.confidence, 0.99)

    def test_l1_intent_rejects_extra_fields(self):
        data = {
            "intent": "DELETE",
            "authorizes_deletion": True,
            "quote": "delete",
            "confidence": 0.95,
            "unknown_extra_field": "injected",
        }
        with self.assertRaises(ValidationError):
            L1IntentOutput.model_validate(data)

    def test_l2_document_valid_and_rejects_extra(self):
        valid = {
            "records": [
                {
                    "resource_id": "audit_record_003",
                    "category": "AUDIT_RECORD",
                    "identifiers": {"user_id": "usr_123"},
                    "state": "ACTIVE",
                    "fields_visible": ["user_id", "state"],
                }
            ]
        }
        res = L2DocumentOutput.model_validate(valid)
        self.assertEqual(len(res.records), 1)
        self.assertEqual(res.records[0].resource_id, "audit_record_003")

        # Unknown field inside record
        invalid_record = {
            "records": [
                {
                    "resource_id": "audit_record_003",
                    "category": "AUDIT_RECORD",
                    "identifiers": {},
                    "state": "ACTIVE",
                    "fields_visible": [],
                    "fabricated_field": True,
                }
            ]
        }
        with self.assertRaises(ValidationError):
            L2DocumentOutput.model_validate(invalid_record)

    def test_l4_linkage_valid_and_rejects_extra(self):
        data = {
            "decision": "LINK",
            "confidence": 0.95,
            "reasoning": "Hard signal S1 matched",
            "hard_signal_ids": ["S1"],
        }
        res = L4LinkageOutput.model_validate(data)
        self.assertEqual(res.decision, LinkageDecision.LINK)

        data_extra = dict(data, hallucinated_extra=123)
        with self.assertRaises(ValidationError):
            L4LinkageOutput.model_validate(data_extra)


class TestLLMCache(unittest.TestCase):
    def test_cache_set_and_get(self):
        cache_dir = Path(__file__).resolve().parent / ".test_cache"
        cache = LLMCache(cache_dir=cache_dir)
        try:
            model = "test-model"
            prompt = "system prompt"
            user_input = "test user input"
            resp = {"status": "ok", "value": 42}

            key = cache.set(model, prompt, user_input, resp)
            self.assertIsInstance(key, str)
            self.assertEqual(len(key), 64)  # sha256 hex length

            retrieved = cache.get(model, prompt, user_input)
            self.assertEqual(retrieved, resp)

            # Different input yields None
            self.assertIsNone(cache.get(model, prompt, "other input"))
        finally:
            cache.clear()
            if cache_dir.exists():
                try:
                    cache_dir.rmdir()
                except Exception:
                    pass


class TestLLMUsageLedger(unittest.TestCase):
    def test_ledger_recording_and_reconciliation(self):
        ledger = UsageLedger()
        # Add call 1
        ledger.record_call(
            provider="google",
            model="gemini-2.5-flash",
            target_id="case_1",
            input_tokens=1000,
            output_tokens=100,
            cache_hit=False,
            task="L1",
        )
        # Add call 2 (cache hit)
        ledger.record_call(
            provider="google",
            model="gemini-2.5-flash",
            target_id="case_2",
            input_tokens=1000,
            output_tokens=100,
            cache_hit=True,
            task="L1",
        )
        summ = ledger.summary()
        self.assertEqual(summ["total_calls"], 2)
        self.assertEqual(summ["cache_hits"], 1)
        self.assertEqual(summ["api_calls"], 1)
        self.assertAlmostEqual(summ["cache_hit_rate"], 0.5)

        # Cost: 1000 * 0.000000075 + 100 * 0.000000300 = 0.000075 + 0.000030 = 0.000105
        expected_cost = (1000 * 0.000000075) + (100 * 0.000000300)
        self.assertAlmostEqual(summ["total_cost_usd"], expected_cost, places=8)

        reconciled, msg = ledger.reconcile()
        self.assertTrue(reconciled, msg)


class TestLLMClientNoKey(unittest.TestCase):
    def test_fallback_when_no_key(self):
        # Force GEMINI_API_KEY to empty
        old_key = os.environ.get("GEMINI_API_KEY")
        if "GEMINI_API_KEY" in os.environ:
            del os.environ["GEMINI_API_KEY"]
        try:
            client = LLMClient(provider="google", model="gemini-2.5-flash")
            self.assertFalse(client.has_key)

            def fallback():
                return L1IntentOutput(
                    intent=IntentType.DELETE,
                    authorizes_deletion=True,
                    quote="fallback",
                    confidence=1.0,
                )

            res, is_model, status = client.call_structured(
                task_name="L1",
                system_prompt="sys",
                task_prompt="task",
                user_input="input text",
                schema_cls=L1IntentOutput,
                fallback_fn=fallback,
                target_id="case_test",
            )
            self.assertFalse(is_model)
            self.assertEqual(status, "DETERMINISTIC_FALLBACK_NO_KEY")
            self.assertEqual(res.intent, IntentType.DELETE)
        finally:
            if old_key is not None:
                os.environ["GEMINI_API_KEY"] = old_key


class TestLLMPromptsIntegrity(unittest.TestCase):
    def test_prompts_exist_and_contain_adversarial_examples(self):
        prompts_dir = Path(__file__).resolve().parent.parent / "code" / "ghost_audit" / "llm" / "prompts"
        for name in ["system_prompt.md", "l1_intent.md", "l2_document.md", "l4_linkage.md"]:
            p = prompts_dir / name
            self.assertTrue(p.exists(), f"Prompt file {name} missing")
            content = p.read_text(encoding="utf-8")
            self.assertGreater(len(content), 100)
            if name != "system_prompt.md":
                self.assertIn("Adversarial Example", content)


if __name__ == "__main__":
    unittest.main()
