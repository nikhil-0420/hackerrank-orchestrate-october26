"""
Usage and Cost Ledger for LLM calls.
Tracks per-call token counts, cache hits, provider, model, target ID, and calculated cost.
Enforces reconciliation between row totals and aggregated summary.
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
import re
from typing import Dict, List, Optional, Tuple


@dataclass
class UsageEntry:
    provider: str
    model: str
    target_id: str  # e.g. case_id or file:evidence_XX
    input_tokens: int
    output_tokens: int
    cache_hit: bool
    cost_usd: float
    task: str  # L1, L2, L4
    timestamp: str = ""


# Default rates ($ / token)
DEFAULT_PRICING: Dict[str, Tuple[float, float]] = {
    "gemini-2.5-flash": (0.000000075, 0.000000300),
    "gemini-2.0-flash": (0.000000100, 0.000000400),
    "gemini-1.5-flash": (0.000000075, 0.000000300),
    "gemini-1.5-pro": (0.000001250, 0.000005000),
    "mock-model": (0.0, 0.0),
    "deterministic": (0.0, 0.0),
}


def load_pricing_table(pricing_path: Optional[Path] = None) -> Dict[str, Tuple[float, float]]:
    pricing = dict(DEFAULT_PRICING)
    if pricing_path is None:
        pricing_path = Path(__file__).resolve().parent.parent.parent.parent / "docs" / "pricing.md"

    if pricing_path.exists():
        try:
            with open(pricing_path, "r", encoding="utf-8") as f:
                content = f.read()
            # Match markdown table rows: | provider | model | input_rate | output_rate | input_token | output_token |
            for line in content.splitlines():
                if not line.strip().startswith("|") or "Model" in line or "---" in line:
                    continue
                cols = [c.strip() for c in line.split("|")[1:-1]]
                if len(cols) >= 6:
                    model = cols[1]
                    try:
                        inp_token = float(cols[4].replace("$", ""))
                        out_token = float(cols[5].replace("$", ""))
                        pricing[model] = (inp_token, out_token)
                    except ValueError:
                        pass
        except Exception:
            pass
    return pricing


class UsageLedger:
    def __init__(self, pricing_path: Optional[Path] = None):
        self.pricing = load_pricing_table(pricing_path)
        self.entries: List[UsageEntry] = []

    def record_call(
        self,
        provider: str,
        model: str,
        target_id: str,
        input_tokens: int,
        output_tokens: int,
        cache_hit: bool,
        task: str,
        timestamp: str = "",
    ) -> UsageEntry:
        if cache_hit:
            cost = 0.0
        else:
            in_rate, out_rate = self.pricing.get(model, (0.000000075, 0.000000300))
            cost = (input_tokens * in_rate) + (output_tokens * out_rate)

        entry = UsageEntry(
            provider=provider,
            model=model,
            target_id=target_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cache_hit=cache_hit,
            cost_usd=cost,
            task=task,
            timestamp=timestamp,
        )
        self.entries.append(entry)
        return entry

    def summary(self) -> Dict[str, Any]:
        total_calls = len(self.entries)
        cache_hits = sum(1 for e in self.entries if e.cache_hit)
        api_calls = total_calls - cache_hits
        total_in_tokens = sum(e.input_tokens for e in self.entries)
        total_out_tokens = sum(e.output_tokens for e in self.entries)
        total_cost = sum(e.cost_usd for e in self.entries)

        by_task: Dict[str, Dict[str, Any]] = {}
        for e in self.entries:
            t = by_task.setdefault(e.task, {"calls": 0, "cache_hits": 0, "in_tokens": 0, "out_tokens": 0, "cost": 0.0})
            t["calls"] += 1
            if e.cache_hit:
                t["cache_hits"] += 1
            t["in_tokens"] += e.input_tokens
            t["out_tokens"] += e.output_tokens
            t["cost"] += e.cost_usd

        return {
            "total_calls": total_calls,
            "cache_hits": cache_hits,
            "api_calls": api_calls,
            "cache_hit_rate": (cache_hits / total_calls) if total_calls > 0 else 0.0,
            "total_input_tokens": total_in_tokens,
            "total_output_tokens": total_out_tokens,
            "total_cost_usd": total_cost,
            "by_task": by_task,
        }

    def reconcile(self) -> Tuple[bool, str]:
        """
        Reconcile row items against summary totals.
        """
        summ = self.summary()
        sum_in = sum(e.input_tokens for e in self.entries)
        sum_out = sum(e.output_tokens for e in self.entries)
        sum_cost = sum(e.cost_usd for e in self.entries)

        if summ["total_input_tokens"] != sum_in:
            return False, f"Input tokens mismatch: summary {summ['total_input_tokens']} != rows {sum_in}"
        if summ["total_output_tokens"] != sum_out:
            return False, f"Output tokens mismatch: summary {summ['total_output_tokens']} != rows {sum_out}"
        if abs(summ["total_cost_usd"] - sum_cost) > 1e-9:
            return False, f"Cost mismatch: summary {summ['total_cost_usd']} != rows {sum_cost}"

        return True, "Usage ledger reconciled successfully."

    def save_csv(self, dest_path: Path) -> None:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = [
            "timestamp",
            "provider",
            "model",
            "task",
            "target_id",
            "input_tokens",
            "output_tokens",
            "cache_hit",
            "cost_usd",
        ]
        with open(dest_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for e in self.entries:
                writer.writerow(asdict(e))
