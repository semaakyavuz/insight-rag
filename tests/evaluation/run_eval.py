"""Evaluate the real /query endpoint against a golden question/keyword dataset.

Usage:
    python tests/evaluation/run_eval.py [--api-url http://127.0.0.1:8000]
"""

import argparse
import json
import sys
import time
from pathlib import Path

import httpx

DATASET_PATH = Path(__file__).parent / "golden_dataset.json"
KEYWORD_PASS_RATIO = 0.5
RETRYABLE_STATUS_CODES = {502, 503}
RETRY_DELAY_SECONDS = 2


def load_dataset() -> list[dict]:
    return json.loads(DATASET_PATH.read_text(encoding="utf-8"))


def _keyword_label(keyword_or_group) -> str:
    if isinstance(keyword_or_group, list):
        return " / ".join(keyword_or_group)
    return keyword_or_group


def _keyword_matches(keyword_or_group, answer_lower: str) -> bool:
    alternatives = (
        keyword_or_group if isinstance(keyword_or_group, list) else [keyword_or_group]
    )
    return any(alt.lower() in answer_lower for alt in alternatives)


def _post_query(api_url: str, question: str) -> httpx.Response:
    last_exc = None
    for attempt in range(2):
        try:
            response = httpx.post(
                f"{api_url}/query", json={"question": question}, timeout=60
            )
            if response.status_code in RETRYABLE_STATUS_CODES and attempt == 0:
                time.sleep(RETRY_DELAY_SECONDS)
                continue
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as exc:
            last_exc = exc
            if exc.response.status_code in RETRYABLE_STATUS_CODES and attempt == 0:
                time.sleep(RETRY_DELAY_SECONDS)
                continue
            raise
    raise last_exc


def evaluate_case(api_url: str, case: dict) -> dict:
    response = _post_query(api_url, case["question"])
    body = response.json()

    answer = body.get("answer", "")
    answer_lower = answer.lower()
    sources = body.get("sources", [])

    matched_keywords = [
        _keyword_label(keyword)
        for keyword in case["expected_keywords"]
        if _keyword_matches(keyword, answer_lower)
    ]
    missing_keywords = [
        _keyword_label(keyword)
        for keyword in case["expected_keywords"]
        if not _keyword_matches(keyword, answer_lower)
    ]
    keyword_ratio = (
        len(matched_keywords) / len(case["expected_keywords"])
        if case["expected_keywords"]
        else 0.0
    )
    retrieval_ok = len(sources) > 0

    return {
        "question": case["question"],
        "expected_keywords": [
            _keyword_label(keyword) for keyword in case["expected_keywords"]
        ],
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
        "keyword_ratio": keyword_ratio,
        "retrieval_ok": retrieval_ok,
        "answer": answer,
        "sources": sources,
        "passed": retrieval_ok and keyword_ratio >= KEYWORD_PASS_RATIO,
    }


def format_verbose_case(index: int, total: int, result: dict) -> str:
    sources_desc = ", ".join(
        f"{s.get('document_filename')} ({s.get('similarity_score'):.3f})"
        for s in result.get("sources", [])
    ) or "yok"
    return (
        f"[{index}/{total}] FAIL — {result['question']}\n"
        f"    beklenen keywords : {result['expected_keywords']}\n"
        f"    eşleşen keywords  : {result['matched_keywords']}\n"
        f"    eksik keywords    : {result['missing_keywords']}\n"
        f"    retrieval kaynakları: {sources_desc}\n"
        f"    TAM CEVAP:\n"
        f"    {result.get('answer', '')}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Golden dataset üzerinden /query kalite değerlendirmesi."
    )
    parser.add_argument(
        "--api-url",
        default="http://127.0.0.1:8000",
        help="Çalışan backend'in adresi (varsayılan: http://127.0.0.1:8000)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Başarısız sorular için tam cevabı ve eksik keyword'leri yazdır",
    )
    parser.add_argument(
        "--save-failed",
        metavar="PATH",
        help="Başarısız soruların ayrıntılı raporunu bu dosyaya kaydet",
    )
    args = parser.parse_args()

    dataset = load_dataset()
    results = []
    verbose_failed_blocks = []
    infra_error_count = 0

    for index, case in enumerate(dataset, start=1):
        try:
            result = evaluate_case(args.api_url, case)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code in RETRYABLE_STATUS_CODES:
                infra_error_count += 1
                print(
                    f"[{index}/{len(dataset)}] ALTYAPI HATASI (skora dahil "
                    f"edilmedi) — {case['question']}\n    {exc}"
                )
                continue
            print(f"[{index}/{len(dataset)}] HATA — {case['question']}\n    {exc}")
            results.append(
                {
                    "question": case["question"],
                    "expected_keywords": case["expected_keywords"],
                    "matched_keywords": [],
                    "missing_keywords": case["expected_keywords"],
                    "keyword_ratio": 0.0,
                    "retrieval_ok": False,
                    "answer": "",
                    "sources": [],
                    "passed": False,
                }
            )
            continue
        except Exception as exc:
            print(f"[{index}/{len(dataset)}] HATA — {case['question']}\n    {exc}")
            results.append(
                {
                    "question": case["question"],
                    "expected_keywords": case["expected_keywords"],
                    "matched_keywords": [],
                    "missing_keywords": case["expected_keywords"],
                    "keyword_ratio": 0.0,
                    "retrieval_ok": False,
                    "answer": "",
                    "sources": [],
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
        if not result["passed"]:
            block = format_verbose_case(index, len(dataset), result)
            verbose_failed_blocks.append(block)
            if args.verbose:
                print(block)
        results.append(result)

    passed_count = sum(1 for r in results if r["passed"])
    retrieval_ok_count = sum(1 for r in results if r["retrieval_ok"])
    avg_keyword_ratio = (
        sum(r["keyword_ratio"] for r in results) / len(results) if results else 0.0
    )

    print("\n" + "=" * 50)
    print(f"Sonuç: {passed_count}/{len(results)} doğru")
    print(f"Retrieval başarı oranı: {retrieval_ok_count}/{len(results)}")
    print(f"Ortalama keyword eşleşme oranı: {avg_keyword_ratio:.0%}")
    if infra_error_count:
        print(
            f"Altyapı hatası nedeniyle atlanan sorular (skora dahil değil): "
            f"{infra_error_count}"
        )

    if args.save_failed and verbose_failed_blocks:
        save_path = Path(args.save_failed)
        save_path.write_text("\n".join(verbose_failed_blocks), encoding="utf-8")
        print(f"\nBaşarısız sorular kaydedildi: {save_path}")

    if passed_count < len(results):
        sys.exit(1)


if __name__ == "__main__":
    main()
