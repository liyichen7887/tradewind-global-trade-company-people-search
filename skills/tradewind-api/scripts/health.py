"""
存活与健康检查（对应 src/health、src/observability/metrics）。
- GET /api/health  — 无需 API Key
- GET /api/metrics — Prometheus 文本，无需 API Key
"""
from __future__ import annotations

import argparse

from common import TradewindClient, load_settings
from _util import dump_json


def main() -> None:
    p = argparse.ArgumentParser(description="TradeWind health / metrics")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("liveness", help="GET /api/health")
    sub.add_parser("metrics", help="GET /api/metrics (text/plain)")
    args = p.parse_args()
    client = TradewindClient(load_settings())
    if args.cmd == "liveness":
        dump_json(client.get_api("health"))
    else:
        text = client.get_text("metrics", accept="text/plain")
        print(text)


if __name__ == "__main__":
    main()
