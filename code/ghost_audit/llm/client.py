"""
Provider-agnostic LLM client adapter with deterministic fallback.
Strictly adheres to:
- Temperature = 0
- Retries once on schema failure, then returns deterministic fallback and logs a silent-failure signal
- Reads API key ONLY from environment variable (or uncommitted .env)
- NEVER prints, logs, or commits an API key
- Keyless runs transparently use deterministic fallback
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Type
from pydantic import BaseModel, ValidationError

from ghost_audit.llm.cache import LLMCache
from ghost_audit.llm.usage import UsageLedger


def _load_env_silently() -> None:
    """
    Load environment variables from an uncommitted .env file if present.
    NEVER logs, prints, or exposes variable values.
    """
    # Look for .env in project root
    root = Path(__file__).resolve().parent.parent.parent.parent
    env_file = root / ".env"
    if not env_file.exists():
        return
    try:
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                if k and k not in os.environ:
                    os.environ[k] = v
    except Exception:
        pass


class SilentFailureSignal:
    def __init__(self, task: str, target_id: str, reason: str, timestamp: float):
        self.task = task
        self.target_id = target_id
        self.reason = reason
        self.timestamp = timestamp

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task": self.task,
            "target_id": self.target_id,
            "reason": self.reason,
            "timestamp": self.timestamp,
        }


class LLMClient:
    def __init__(
        self,
        provider: str = "google",
        model: str = "gemini-2.5-flash",
        cache: Optional[LLMCache] = None,
        ledger: Optional[UsageLedger] = None,
        no_cache: bool = False,
    ):
        _load_env_silently()
        self.provider = provider
        self.model = model
        self.cache = cache or LLMCache()
        self.ledger = ledger or UsageLedger()
        self.no_cache = no_cache
        self.silent_failures: List[SilentFailureSignal] = []
        self.schema_validation_failures = 0
        self.total_structured_attempts = 0
        self.fallback_count = 0
        self.cache_reads = 0
        self.cache_hits = 0
        self.cache_misses = 0

        # Detect API key presence without ever revealing or logging it
        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        self.has_key = bool(api_key)
        self._genai_client = None

        if self.has_key and self.provider == "google":
            try:
                from google import genai
                # Pass api_key directly without logging or echoing
                self._genai_client = genai.Client(api_key=api_key)
            except Exception as e:
                self.silent_failures.append(
                    SilentFailureSignal("INIT", "client", f"Init failure: {type(e).__name__}", time.time())
                )
                self._genai_client = None

    @property
    def cache_hit_rate(self) -> float:
        if self.cache_reads == 0:
            return 0.0
        return self.cache_hits / self.cache_reads

    def log_silent_failure(self, task: str, target_id: str, reason: str) -> None:
        self.silent_failures.append(SilentFailureSignal(task, target_id, reason, time.time()))

    def call_structured(
        self,
        task_name: str,
        system_prompt: str,
        task_prompt: str,
        user_input: str,
        schema_cls: Type[BaseModel],
        fallback_fn: Callable[[], BaseModel],
        target_id: str = "unknown",
    ) -> Tuple[BaseModel, bool, str]:
        """
        Execute structured LLM call with strict caching, schema validation, and fallback.
        Returns:
            (validated_pydantic_object, is_model_call, status_message)
        """
        full_prompt = f"{task_prompt}\n\nUser Input Data:\n{user_input}"

        # 1. Check disk cache first (unless no_cache is active)
        if not self.no_cache:
            self.cache_reads += 1
            cached_data = self.cache.get(self.model, full_prompt, user_input)
            if cached_data is not None:
                try:
                    obj = schema_cls.model_validate(cached_data)
                    self.cache_hits += 1
                    self.ledger.record_call(
                        provider=self.provider,
                        model=self.model,
                        target_id=target_id,
                        input_tokens=0,
                        output_tokens=0,
                        cache_hit=True,
                        task=task_name,
                        is_fallback=False,
                        status="CACHE_HIT",
                        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    )
                    return obj, True, "CACHE_HIT"
                except ValidationError:
                    pass  # Stale or invalid cache format, re-fetch
            self.cache_misses += 1

        # 2. Check if API client is active
        if not self.has_key or self._genai_client is None:
            self.fallback_count += 1
            self.ledger.record_call(
                provider=self.provider,
                model=self.model,
                target_id=target_id,
                input_tokens=0,
                output_tokens=0,
                cache_hit=False,
                task=task_name,
                is_fallback=True,
                status="DETERMINISTIC_FALLBACK_NO_KEY",
                timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            )
            fallback_val = fallback_fn()
            return fallback_val, False, "DETERMINISTIC_FALLBACK_NO_KEY"

        # 3. Attempt API call with at most 1 retry on schema failure
        from google.genai import types

        max_attempts = 2  # initial + 1 retry
        last_error = ""

        for attempt in range(1, max_attempts + 1):
            self.total_structured_attempts += 1
            try:
                config = types.GenerateContentConfig(
                    temperature=0.0,
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    response_schema=schema_cls,
                )

                response = self._genai_client.models.generate_content(
                    model=self.model,
                    contents=full_prompt,
                    config=config,
                )

                raw_text = response.text or "{}"
                parsed_json = json.loads(raw_text)
                validated_obj = schema_cls.model_validate(parsed_json)

                # Token usage
                in_tok = 0
                out_tok = 0
                if hasattr(response, "usage_metadata") and response.usage_metadata is not None:
                    in_tok = getattr(response.usage_metadata, "prompt_token_count", 0) or 0
                    out_tok = getattr(response.usage_metadata, "candidates_token_count", 0) or 0
                else:
                    # Fallback token estimate
                    in_tok = len(full_prompt) // 4
                    out_tok = len(raw_text) // 4

                # Record cache & ledger
                if not self.no_cache:
                    self.cache.set(self.model, full_prompt, user_input, validated_obj.model_dump())
                self.ledger.record_call(
                    provider=self.provider,
                    model=self.model,
                    target_id=target_id,
                    input_tokens=in_tok,
                    output_tokens=out_tok,
                    cache_hit=False,
                    task=task_name,
                    is_fallback=False,
                    status="SUCCESS",
                    timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                )
                return validated_obj, True, "SUCCESS"

            except (ValidationError, json.JSONDecodeError) as val_err:
                self.schema_validation_failures += 1
                last_error = f"Schema failure on attempt {attempt}: {val_err}"
                if attempt == max_attempts:
                    self.log_silent_failure(task_name, target_id, last_error)
            except Exception as api_err:
                last_error = f"API error on attempt {attempt}: {type(api_err).__name__}"
                self.log_silent_failure(task_name, target_id, last_error)
                break

        # Fallback to deterministic code
        self.fallback_count += 1
        self.ledger.record_call(
            provider=self.provider,
            model=self.model,
            target_id=target_id,
            input_tokens=0,
            output_tokens=0,
            cache_hit=False,
            task=task_name,
            is_fallback=True,
            status=f"FALLBACK_AFTER_FAILURE: {last_error}",
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )
        fallback_val = fallback_fn()
        return fallback_val, False, f"FALLBACK_AFTER_FAILURE: {last_error}"

    def schema_failure_rate(self) -> float:
        if self.total_structured_attempts == 0:
            return 0.0
        return self.schema_validation_failures / self.total_structured_attempts
