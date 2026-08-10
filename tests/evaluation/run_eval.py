"""Evaluate the real /query endpoint against a golden question/keyword dataset.

Usage:
    python tests/evaluation/run_eval.py [--api-url http://127.0.0.1:8000]
"""

import argparse
import json
import sys
from pathlib import Path

import httpx

DATASET_PATH = Path(__file__).parent / "golden_dataset.json"
KEYWORD_PASS_RATIO = 0.5


def load_dataset() -> list[dict]:
    return json.loads(DATASET_PATH.read_text(encoding="utf-8"))


def evaluate_case(api_url: str, case: dict) -> dict:
    response = httpx.post(
        f"{api_url}/query",
        json={"question": case["question"]},
        timeout=60,
    )
    response.raise_for_status()
    body = response.json()

    answer_lower = body.get("answer", "").lower()
    sources = body.get("sources", [])

    matched_keywords = [
        keyword
        for keyword in case["expected_keywords"]
        if keyword.lower() in answer_lower
    ]
    keyword_ratio = (
        len(matched_keywords) / len(case["expected_keywords"])
        if case["expected_keywords"]
        else 0.0
    )
    retrieval_ok = len(sources) > 0

    return {
        "question": case["question"],
        "expected_keywords": case["expected_keywords"],
        "matched_keywords": matched_keywords,
        "keyword_ratio": keyword_ratio,
        "retrieval_ok": retrieval_ok,
        "passed": retrieval_ok and keyword_ratio >= KEYWORD_PASS_RATIO,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Golden dataset üzerinden /query kalite değerlendirmesi."
    )
    parser.add_argument(
        "--api-url",
        default="http://127.0.0.1:8000",
        help="Çalışan backend'in adresi (varsayılan: http://127.0.0.1:8000)",
    )
    args = parser.parse_args()

    dataset = load_dataset()
    results = []

    for index, case in enumerate(dataset, start=1):
        try:
            result = evaluate_case(args.api_url, case)
        except Exception as exc:
            print(f"[{index}/{len(dataset)}] HATA — {case['question']}\n    {exc}")
            results.append(
                {
                    "question": case["question"],
                    "expected_keywords": case["expected_keywords"],
                    "matched_keywords": [],
                    "keyword_ratio": 0.0,
                    "retrieval_ok": False,
                    "passed": False,
                }
            )
            continue

        status = "OK" if result["passed"] else "FAIL"
        print(
            f"[{index}/{len(dataset)}] {status} — {case['question']}\n"
            f"    retrieval: {'var' if result['retrieval_ok'] else 'yok'}, "
            f"keyword eşleşmesi: {len(result['matched_keywords'])}/"
            f"{len(result['expected_keywords'])} ({result['keyword_ratio']:.0%})"
        )
        results.append(result)

    passed_count = sum(1 for r in results if r["passed"])
    retrieval_ok_count = sum(1 for r in results if r["retrieval_ok"])
    avg_keyword_ratio = sum(r["keyword_ratio"] for r in results) / len(results)

    print("\n" + "=" * 50)
    print(f"Sonuç: {passed_count}/{len(results)} doğru")
    print(f"Retrieval başarı oranı: {retrieval_ok_count}/{len(results)}")
    print(f"Ortalama keyword eşleşme oranı: {avg_keyword_ratio:.0%}")

    if passed_count < len(results):
        sys.exit(1)


if __name__ == "__main__":
    main()
