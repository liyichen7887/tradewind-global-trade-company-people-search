"""
从环境读取 API Key，生成 Authorization Bearer 头。勿在代码中硬编码密钥。
"""
from __future__ import annotations

import os
import sys


def load_api_key() -> str:
    key = (os.environ.get("TRADEWIND_API_KEY") or "").strip()
    if not key:
        print(
            "缺少环境变量 TRADEWIND_API_KEY（Bearer tw_test_* / tw_live_*）。",
            file=sys.stderr,
        )
        sys.exit(2)
    return key


def bearer_headers(api_key: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }
