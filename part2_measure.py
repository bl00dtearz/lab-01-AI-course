from __future__ import annotations

import argparse
import json
import os
import time

from dotenv import load_dotenv
from google import genai

from prices import MODELS, DEFAULT_MODEL
from texts import CORPUS, LANGUAGES


load_dotenv()

MAX_TOKENS = 2048


def count_tokens(client, model_id: str, text: str) -> int:
    response = client.models.count_tokens(
        model=model_id,
        contents=text,
    )
    return response.total_tokens


def count_request_tokens(
    client,
    model_id: str,
    system_prompt: str,
    complaint: str,
) -> int:
    # Gemini Developer API does not allow system_instruction
    # inside count_tokens(), so we count the two parts separately.
    system_tokens = count_tokens(client, model_id, system_prompt)
    complaint_tokens = count_tokens(client, model_id, complaint)

    return system_tokens + complaint_tokens


def make_request(
    client,
    model_id: str,
    system_prompt: str,
    complaint: str,
) -> dict:

    max_retries = 5

    for attempt in range(max_retries):

        try:
            response = client.models.generate_content(
                model=model_id,
                contents=complaint,
                config={
                    "system_instruction": system_prompt,
                    "max_output_tokens": MAX_TOKENS,
                },
            )

            usage = response.usage_metadata

            print("\nMODEL ANSWER")
            print("=" * 70)
            print(response.text)
            print("=" * 70)

            input_tokens = usage.prompt_token_count
            output_tokens = usage.candidates_token_count

            print(f"Input tokens:   {input_tokens}")
            print(f"Output tokens: {output_tokens}")

            return {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            }

        except Exception as e:

            if "503" not in str(e) or attempt == max_retries - 1:
                raise

            wait_time = 5 * (2 ** attempt)

            print(
                f"Gemini is temporarily busy. "
                f"Retry {attempt + 1}/{max_retries} "
                f"in {wait_time} seconds..."
            )

            time.sleep(wait_time)

    raise RuntimeError("Gemini request failed after retries.")


def main() -> None:

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        choices=MODELS.keys(),
    )

    parser.add_argument(
        "--call",
        action="store_true",
    )

    args = parser.parse_args()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Put it in .env"
        )

    client = genai.Client(api_key=api_key)

    model_id = MODELS[args.model].model_id

    print(f"Using Gemini model: {model_id}")
    print("Counting tokens...\n")

    # ---------------------------------------------------------
    # PART 1: individual texts
    # ---------------------------------------------------------

    counts = {}

    for item_name, texts in CORPUS.items():

        counts[item_name] = {}

        for language in LANGUAGES:

            tokens = count_tokens(
                client,
                model_id,
                texts[language],
            )

            counts[item_name][language] = tokens

            print(
                f"{item_name:15} "
                f"{language.upper():2} "
                f"{tokens:5} tokens"
            )

    # ---------------------------------------------------------
    # REQUEST TOKENS
    # ---------------------------------------------------------

    request_tokens = {}

    print("\nREQUEST TOKENS")
    print("=" * 70)

    for language in LANGUAGES:

        tokens = count_request_tokens(
            client,
            model_id,
            CORPUS["system_prompt"][language],
            CORPUS["complaint"][language],
        )

        request_tokens[language] = tokens

        print(
            f"{language.upper():2}: "
            f"{tokens} tokens"
        )

    # ---------------------------------------------------------
    # REAL API REQUESTS
    # ---------------------------------------------------------

    real_requests = {}

    if args.call:

        print("\nMAKING REAL REQUESTS")
        print("=" * 70)

        for language in LANGUAGES:

            print(
                f"\n### LANGUAGE: "
                f"{language.upper()} ###"
            )

            result = make_request(
                client,
                model_id,
                CORPUS["system_prompt"][language],
                CORPUS["complaint"][language],
            )

            real_requests[language] = result

    # ---------------------------------------------------------
    # SAVE RESULTS
    # ---------------------------------------------------------

    payload = {
        "provider": "gemini",
        "model": args.model,
        "model_id": model_id,
        "token_counts": counts,
        "request_tokens": request_tokens,
        "one_request_billed": real_requests,
    }

    with open(
        "measurements.json",
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            payload,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print("\nSaved measurements.json")


if __name__ == "__main__":
    main()