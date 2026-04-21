"""
公开参考资源（对应 src/reference/reference.controller.ts），无需 API Key。
- GET /api/reference/supported-technologies.csv
- GET /api/reference/agentic-country-cr-lang.json
"""
from __future__ import annotations

import argparse
import json
import sys

from common import TradewindClient, load_settings


def main() -> None:
    p = argparse.ArgumentParser(description="TradeWind reference downloads")
    sub = p.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("technologies-csv", help="企业技术栈 CSV")
    t.add_argument("-o", "--out", help="保存路径；省略则打印到 stdout")
    j = sub.add_parser("agentic-country-lang", help="Agentic cr/lang 对照 JSON")
    j.add_argument("-o", "--out", help="保存路径；省略则尝试 stdout JSON 美化")
    args = p.parse_args()
    client = TradewindClient(load_settings())
    if args.cmd == "technologies-csv":
        raw = client.get_bytes("reference/supported-technologies.csv")
        if args.out:
            with open(args.out, "wb") as fp:
                fp.write(raw)
            print(args.out, file=sys.stderr)
        else:
            sys.stdout.buffer.write(raw)
    else:
        raw = client.get_bytes("reference/agentic-country-cr-lang.json")
        if args.out:
            with open(args.out, "wb") as fp:
                fp.write(raw)
            print(args.out, file=sys.stderr)
        else:
            try:
                print(json.dumps(json.loads(raw.decode("utf-8")), ensure_ascii=False, indent=2))
            except json.JSONDecodeError:
                sys.stdout.buffer.write(raw)


if __name__ == "__main__":
    main()
