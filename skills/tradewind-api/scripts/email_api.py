"""
邮箱验证（对应 src/email-verify/email-verify.controller.ts）。
- POST /api/email/verify
- GET  /api/email/verify/result/:taskId
"""
from __future__ import annotations

import argparse
import json

from auth import load_api_key
from common import TradewindClient, load_settings
from _util import dump_json


def main() -> None:
    p = argparse.ArgumentParser(description="TradeWind email verify APIs")
    sub = p.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("verify", help="POST /api/email/verify")
    v.add_argument("--body", required=True, help="JSON 字符串")
    r = sub.add_parser("result", help="GET /api/email/verify/result/:taskId")
    r.add_argument("--task-id", required=True, dest="task_id")
    args = p.parse_args()
    load_api_key()
    client = TradewindClient(load_settings())
    if args.cmd == "verify":
        dump_json(client.post_api("email/verify", json.loads(args.body)))
    else:
        tid = args.task_id.strip()
        dump_json(client.get_api(f"email/verify/result/{tid}"))


if __name__ == "__main__":
    main()
