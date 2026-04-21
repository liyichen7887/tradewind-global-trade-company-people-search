"""
智能获客任务（对应 src/agentic/agentic.controller.ts）。
- POST /api/agentic/search
- POST /api/agentic/list
- POST /api/agentic/task

内部结算 POST /api/internal/agentic/settlement/row 面向平台回调，一般不在 skill 中调用。
"""
from __future__ import annotations

import argparse
import json

from auth import load_api_key
from common import TradewindClient, load_settings
from _util import dump_json


def main() -> None:
    p = argparse.ArgumentParser(description="TradeWind agentic APIs")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, desc in (
        ("search", "POST /api/agentic/search"),
        ("list", "POST /api/agentic/list"),
        ("task", "POST /api/agentic/task"),
    ):
        sp = sub.add_parser(name, help=desc)
        sp.add_argument("--body", required=True, help="JSON 字符串")
    args = p.parse_args()
    load_api_key()
    client = TradewindClient(load_settings())
    body = json.loads(args.body)
    dump_json(client.post_api(f"agentic/{args.cmd}", body))


if __name__ == "__main__":
    main()
