from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from prices import (
    DEFAULT_MODEL,
    PRICE_CHECKED,
    PRICE_SOURCE,
    cost_usd,
)
from texts import LANGUAGES


DEFAULT_MEASUREMENTS = Path(__file__).with_name(
    "measurements.json"
)


def load_measurements(path: Path):
    try:
        return json.loads(
            path.read_text(encoding="utf-8")
        )
    except FileNotFoundError:
        sys.exit(
            "measurements.json not found. "
            "Run part2_measure.py --call first."
        )


def main() -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--measurements",
        type=Path,
        default=DEFAULT_MEASUREMENTS,
    )

    parser.add_argument(
        "--requests-per-day",
        type=int,
        default=2000,
    )

    args = parser.parse_args()

    data = load_measurements(
        args.measurements
    )

    model = data["model"]
    model_id = data["model_id"]

    inputs = data["request_tokens"]
    measured = data["one_request_billed"]

    print(
        f"prices from {PRICE_SOURCE}"
    )

    print(
        f"checked {PRICE_CHECKED}; "
        f"tokens counted on {model_id}"
    )

    print(
        "\nONE SUPPORT REQUEST"
    )

    print("-" * 70)

    print(
        f"{'':15}"
        f"{'EN':>12}"
        f"{'RU':>12}"
        f"{'KK':>12}"
    )

    print(
        f"{'input tokens':15}"
        f"{inputs['en']:>12}"
        f"{inputs['ru']:>12}"
        f"{inputs['kk']:>12}"
    )

    print(
        f"{'output tokens':15}"
        f"{measured['en']['output_tokens']:>12}"
        f"{measured['ru']['output_tokens']:>12}"
        f"{measured['kk']['output_tokens']:>12}"
    )

    print(
        f"{'cost, USD':15}"
        f"{cost_usd(model, inputs['en'], measured['en']['output_tokens']):>12.4f}"
        f"{cost_usd(model, inputs['ru'], measured['ru']['output_tokens']):>12.4f}"
        f"{cost_usd(model, inputs['kk'], measured['kk']['output_tokens']):>12.4f}"
    )

    requests_per_year = args.requests_per_day * 365

    print(
        f"\nAT {args.requests_per_day:,} REQUESTS/DAY"
    )

    print("-" * 70)

    print(
        f"{'':15}"
        f"{'EN':>12}"
        f"{'RU':>12}"
        f"{'KK':>12}"
    )

    for language in LANGUAGES:
        pass

    yearly = {}

    for language in LANGUAGES:
        one_request = cost_usd(
            model,
            inputs[language],
            measured[language]["output_tokens"],
        )

        yearly[language] = (
            one_request * requests_per_year
        )

    print(
        f"{model:15}"
        f"{yearly['en']:>12.2f}"
        f"{yearly['ru']:>12.2f}"
        f"{yearly['kk']:>12.2f}"
    )

    print(
        "\nTOKEN RATIOS"
    )

    print("-" * 70)

    print(
        f"RU / EN input: "
        f"{inputs['ru'] / inputs['en']:.2f}x"
    )

    print(
        f"KK / EN input: "
        f"{inputs['kk'] / inputs['en']:.2f}x"
    )

    print(
        f"RU / EN output: "
        f"{measured['ru']['output_tokens'] / measured['en']['output_tokens']:.2f}x"
    )

    print(
        f"KK / EN output: "
        f"{measured['kk']['output_tokens'] / measured['en']['output_tokens']:.2f}x"
    )

    print("\nNote: The measurements were made using the Gemini Free Tier.")
    print("The annual figures above are hypothetical costs using the published paid API price.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
    