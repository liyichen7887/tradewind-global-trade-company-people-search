"""
人员检索与画像（对应 src/people-search、src/people-enrich）。
- POST /api/people/search
- POST /api/people/enrich
"""
from __future__ import annotations

import argparse
import json

from auth import load_api_key
from common import TradewindClient, load_settings
from _util import dump_json


def main() -> None:
    p = argparse.ArgumentParser(description="TradeWind people APIs")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="POST /api/people/search")
    s.add_argument("--body", required=True, help="JSON 字符串")
    e = sub.add_parser("enrich", help="POST /api/people/enrich")
    e.add_argument("--body", help="单条 JSON")
    e.add_argument("--batch-file", help="NDJSON，每行一个请求体")
    args = p.parse_args()
    load_api_key()
    client = TradewindClient(load_settings())
    if args.cmd == "search":
        dump_json(client.post_api("people/search", json.loads(args.body)))
        return
    if args.body:
        dump_json(client.post_api("people/enrich", json.loads(args.body)))
        return
    if not args.batch_file:
        raise SystemExit("enrich 需指定 --body 或 --batch-file")
    batch: list[object] = []
    with open(args.batch_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            batch.append(client.post_api("people/enrich", json.loads(line)))
    dump_json(batch)


if __name__ == "__main__":
    main()
