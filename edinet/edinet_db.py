#!/usr/bin/env python3
"""EDINET DBの提出書類を必要なときだけ取得する読み取り専用CLI。"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


BASE_URL = os.environ.get("EDINET_DB_BASE_URL", "https://edinetdb.jp/v1").rstrip("/")
TIMEOUT_SECONDS = 45
MAX_COMPANIES = 20
MAX_PAGES = 20


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="EDINET DBから指定企業・期間の提出書類を読み取り専用で取得します。",
    )
    parser.add_argument(
        "--company",
        action="append",
        required=True,
        metavar="EDINET_CODE",
        help="対象のEDINETコード。複数指定できます（最大20社）。",
    )
    parser.add_argument(
        "--published-after",
        required=True,
        metavar="YYYY-MM-DD",
        help="提出日時の起点日。広範囲な取得を避けるため必須です。",
    )
    parser.add_argument("--limit", type=int, default=100, help="1ページあたりの最大件数（1〜500、既定100）。")
    parser.add_argument("--pages", type=int, default=1, help="取得する最大ページ数（1〜20、既定1）。")
    parser.add_argument(
        "--with-pdf-url",
        action="store_true",
        help="各文書の一時PDF URLを追加取得します。PDF本体は保存しません。",
    )
    parser.add_argument(
        "--max-pdf-urls",
        type=int,
        default=20,
        help="一時PDF URLを取得する文書数の上限（0〜100、既定20）。",
    )
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> list[str]:
    try:
        datetime.strptime(args.published_after, "%Y-%m-%d")
    except ValueError as error:
        raise ValueError("--published-after は YYYY-MM-DD 形式で指定してください。") from error
    companies = sorted({code.strip().upper() for code in args.company if code.strip()})
    if not companies or any(len(code) != 6 or not code.startswith("E") or not code[1:].isdigit() for code in companies):
        raise ValueError("--company は E00026 のようなEDINETコードで指定してください。")
    if len(companies) > MAX_COMPANIES:
        raise ValueError(f"--company は最大{MAX_COMPANIES}社です。")
    if not 1 <= args.limit <= 500:
        raise ValueError("--limit は1〜500で指定してください。")
    if not 1 <= args.pages <= MAX_PAGES:
        raise ValueError(f"--pages は1〜{MAX_PAGES}で指定してください。")
    if not 0 <= args.max_pdf_urls <= 100:
        raise ValueError("--max-pdf-urls は0〜100で指定してください。")
    return companies


def fetch_json(url: str, api_key: str) -> Any:
    request = Request(url, headers={"X-API-Key": api_key, "Accept": "application/json"})
    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            return json.load(response)
    except HTTPError as error:
        detail = error.read(500).decode("utf-8", errors="replace").replace("\n", " ")
        raise RuntimeError(f"EDINET DBの応答が不正です（HTTP {error.code}）。{detail}") from error
    except URLError as error:
        raise RuntimeError("EDINET DBへ接続できませんでした。ネットワークまたは接続先を確認してください。") from error


def extract_items(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []
    for key in ("data", "documents", "items", "results"):
        candidate = payload.get(key)
        if isinstance(candidate, list):
            return [item for item in candidate if isinstance(item, dict)]
        if isinstance(candidate, dict):
            for nested_key in ("documents", "items", "results"):
                nested = candidate.get(nested_key)
                if isinstance(nested, list):
                    return [item for item in nested if isinstance(item, dict)]
    return []


def next_cursor(payload: Any) -> str | None:
    if not isinstance(payload, dict):
        return None
    meta = payload.get("meta")
    if isinstance(meta, dict) and isinstance(meta.get("next_cursor"), str):
        return meta["next_cursor"].strip() or None
    value = payload.get("next_cursor")
    return value.strip() if isinstance(value, str) and value.strip() else None


def string_value(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def document_id(item: dict[str, Any]) -> str | None:
    for key in ("doc_id", "id", "document_id"):
        value = string_value(item.get(key))
        if value:
            return value
    return None


def company_value(item: dict[str, Any], key: str) -> str | None:
    value = string_value(item.get(key))
    if value:
        return value
    company = item.get("company")
    return string_value(company.get(key)) if isinstance(company, dict) else None


def compact_document(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "document_id": document_id(item),
        "company_name": string_value(item.get("company_name")) or string_value(item.get("filer_name")),
        "edinet_code": company_value(item, "edinet_code") or company_value(item, "company_code"),
        "securities_code": string_value(item.get("sec_code")) or string_value(item.get("securities_code")),
        "title": string_value(item.get("title")),
        "document_type": string_value(item.get("doc_type")) or string_value(item.get("type")),
        "published_at": string_value(item.get("published_at")) or string_value(item.get("discovered_at")) or string_value(item.get("created_at")),
        "source_url": string_value(item.get("source_url")) or string_value(item.get("url")),
        "raw": item,
    }


def fetch_pdf_url(document: dict[str, Any], api_key: str) -> str | None:
    identifier = document.get("document_id")
    if not isinstance(identifier, str) or not identifier:
        return None
    payload = fetch_json(f"{BASE_URL}/ir/documents/{identifier}/pdf-url", api_key)
    if not isinstance(payload, dict):
        return None
    for key in ("url", "signed_url", "pdf_url"):
        value = string_value(payload.get(key))
        if value:
            return value
    data = payload.get("data")
    if isinstance(data, dict):
        for key in ("url", "signed_url", "pdf_url"):
            value = string_value(data.get(key))
            if value:
                return value
    return None


def main() -> int:
    args = parse_args()
    try:
        companies = validate_args(args)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2
    api_key = os.environ.get("EDINET_DB_API_KEY", "").strip()
    if not api_key:
        print("EDINET_DB_API_KEY が設定されていないため、通信せず終了しました。", file=sys.stderr)
        return 2

    cursor: str | None = None
    documents: list[dict[str, Any]] = []
    try:
        for _ in range(args.pages):
            query: list[tuple[str, str]] = [
                ("published_after", args.published_after),
                ("is_latest_only", "false"),
                ("limit", str(args.limit)),
            ]
            query.extend(("company", company) for company in companies)
            if cursor:
                query.append(("cursor", cursor))
            payload = fetch_json(f"{BASE_URL}/ir/documents?{urlencode(query)}", api_key)
            items = extract_items(payload)
            documents.extend(compact_document(item) for item in items)
            next_value = next_cursor(payload)
            if not next_value or next_value == cursor or not items:
                break
            cursor = next_value
        if args.with_pdf_url:
            for document in documents[: args.max_pdf_urls]:
                document["pdf_url"] = fetch_pdf_url(document, api_key)
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        return 1

    result = {
        "source": "EDINET DB",
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "query": {
            "company": companies,
            "published_after": args.published_after,
            "limit": args.limit,
            "pages": args.pages,
            "with_pdf_url": args.with_pdf_url,
        },
        "document_count": len(documents),
        "documents": documents,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
