"""
The defended agent. Applies all three defense layers:

  Layer 1 (architectural): the system prompt contains NO secrets. Compare
    src/vulnerable_agent.py to see how much was removed. Pricing notes,
    escalation paths, override credentials, and customer PII are all gone
    from the prompt.

  Layer 2 (output filtering): every response is scanned against a list of
    sensitive patterns. If any are found, the response is redacted before
    being returned to the user, and a security event is logged.

  Layer 3 (instruction-side refusal): the system prompt explicitly tells
    the model to refuse meta-queries about its instructions.
"""

from __future__ import annotations

import os
from openai import OpenAI

from src.defenses import SAFE_SYSTEM_PROMPT, redact, scan_for_leakage

CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")


class SafeAgent:
    """No secrets in prompt + refusal instructions + output filtering."""

    def __init__(self, client: OpenAI | None = None):
        self.client = client or OpenAI()

    def respond(self, user_query: str) -> dict:
        response = self.client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": SAFE_SYSTEM_PROMPT},
                {"role": "user", "content": user_query},
            ],
            temperature=0.2,
        )
        raw_answer = response.choices[0].message.content or ""

        # Layer 2: scan and redact.
        leaks = scan_for_leakage(raw_answer)
        if leaks:
            final_answer = redact(raw_answer)
            return {
                "answer": final_answer,
                "leakage_detected": leaks,
                "raw_answer_for_audit": raw_answer,
            }

        return {
            "answer": raw_answer,
            "leakage_detected": [],
            "raw_answer_for_audit": raw_answer,
        }
