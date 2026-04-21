"""
控制台身份（对应 src/auth/auth.controller.ts）。
- POST /api/auth/register  — 公开，无需 tw_* Key
- POST /api/auth/login    — 公开
- GET  /api/auth/me       — Bearer：JWT 或 tw_* 均可（与后端一致）
"""
from __future__ import annotations

import argparse
import json

from common import TradewindClient, load_settings
from _util import dump_json


def main() -> None:
    p = argparse.ArgumentParser(description="TradeWind auth APIs")
    sub = p.add_subparsers(dest="cmd", required=True)
    reg = sub.add_parser("register", help="POST /api/auth/register")
    reg.add_argument("--body", required=True, help="JSON 字符串")
    log = sub.add_parser("login", help="POST /api/auth/login")
    log.add_argument("--body", required=True, help="JSON 字符串")
    sub.add_parser("me", help="GET /api/auth/me（需 TRADEWIND_API_KEY 或控制台 JWT）")
    args = p.parse_args()
    client = TradewindClient(load_settings())
    if args.cmd == "register":
        dump_json(client.post_api("auth/register", json.loads(args.body)))
    elif args.cmd == "login":
        dump_json(client.post_api("auth/login", json.loads(args.body)))
    else:
        if not client.settings.api_key:
            raise SystemExit("me 需设置环境变量 TRADEWIND_API_KEY（tw_* 或 JWT）")
        dump_json(client.get_api("auth/me"))


if __name__ == "__main__":
    main()
