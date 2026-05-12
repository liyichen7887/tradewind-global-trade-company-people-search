"""
海关与贸易数据（对应 src/customs、src/customs/customs-extended.controller.ts）。
- POST /api/customs/search
- POST /api/customs/enrich
- GET  /api/customs/reference/countries（`customs_api.py countries` 可不设 Key，401 时再设）
- POST /api/customs/<path>  — extended 下各子路径，如 companies/detail、analytics/market-trend 等
"""
from __future__ import annotations

import argparse
import json

from auth import load_api_key
from common import TradewindClient, load_settings
from _util import dump_json


def main() -> None:
    p = argparse.ArgumentParser(description="TradeWind customs APIs")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser(
        "countries",
        help=(
            "GET /api/customs/reference/countries（海关国家参考；可不设 TRADEWIND_API_KEY；"
            "若返回 401 请设置 Key 后重试）"
        ),
    )
    s = sub.add_parser("search", help="POST /api/customs/search")
    s.add_argument("--body", required=True, help="JSON 字符串")
    e = sub.add_parser("enrich", help="POST /api/customs/enrich")
    e.add_argument("--body", required=True, help="JSON 字符串")
    x = sub.add_parser(
        "post",
        help="POST /api/customs/<path>（extended：如 companies/detail、companies/match-contacts）",
    )
    x.add_argument(
        "--path",
        required=True,
        help="customs 下的相对路径，不含 customs/ 前缀，例如 companies/detail",
    )
    x.add_argument("--body", required=True, help="JSON 字符串")
    args = p.parse_args()
    if args.cmd == "countries":
        client = TradewindClient(load_settings())
        dump_json(client.get_api("customs/reference/countries"))
        return
    load_api_key()
    client = TradewindClient(load_settings())
    if args.cmd == "search":
        dump_json(client.post_api("customs/search", json.loads(args.body)))
    elif args.cmd == "enrich":
        dump_json(client.post_api("customs/enrich", json.loads(args.body)))
    else:
        rel = args.path.strip().lstrip("/")
        dump_json(client.post_api(f"customs/{rel}", json.loads(args.body)))


if __name__ == "__main__":
    main()
