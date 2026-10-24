"""
Persistent disk cache for LLM requests.
Cache key is sha256 of (model, prompt, input_str).
Stored under code/.cache/llm/<hash>.json (gitignored).
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class LLMCache:
    def __init__(self, cache_dir: Optional[Path] = None):
        if cache_dir is None:
            # Default to code/.cache/llm relative to this file
            self.cache_dir = Path(__file__).resolve().parent.parent.parent / ".cache" / "llm"
        else:
            self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _compute_key(self, model: str, prompt: str, user_input: str) -> str:
        h = hashlib.sha256()
        h.update(model.strip().encode("utf-8"))
        h.update(b"::")
        h.update(prompt.strip().encode("utf-8"))
        h.update(b"::")
        h.update(user_input.strip().encode("utf-8"))
        return h.hexdigest()

    def get(self, model: str, prompt: str, user_input: str) -> Optional[Dict[str, Any]]:
        key = self._compute_key(model, prompt, user_input)
        entry_file = self.cache_dir / f"{key}.json"
        if not entry_file.exists():
            return None
        try:
            with open(entry_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("response")
        except Exception:
            return None

    def set(self, model: str, prompt: str, user_input: str, response: Dict[str, Any]) -> str:
        key = self._compute_key(model, prompt, user_input)
        entry_file = self.cache_dir / f"{key}.json"
        payload = {
            "key": key,
            "model": model,
            "response": response,
        }
        try:
            with open(entry_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
        return key

    def clear(self) -> int:
        count = 0
        for p in self.cache_dir.glob("*.json"):
            try:
                p.unlink()
                count += 1
            except Exception:
                pass
        return count
