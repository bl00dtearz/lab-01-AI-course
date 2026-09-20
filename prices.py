from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


PRICE_SOURCE = "https://ai.google.dev/gemini-api/docs/pricing"
PRICE_CHECKED = "2026-09-20"


@dataclass(frozen=True)
class Model:
    model_id: str
    input_per_mtok: float
    output_per_mtok: float
    context_tokens: int


MODELS: Dict[str, Model] = {
    "gemini-3.8-flash": Model(
        "gemini-3.8-flash",
        0.75,   # USD per 1M input tokens
        3.75,   # USD per 1M output tokens
        1_048_576,
    ),
}


DEFAULT_MODEL = "gemini-3.8-flash"


def cost_usd(
    model_key: str,
    input_tokens: int,
    output_tokens: int,
) -> float:

    model = MODELS[model_key]

    return (
        input_tokens * model.input_per_mtok
        + output_tokens * model.output_per_mtok
    ) / 1_000_000