"""
用户侧：API Key、Stripe 账单、调用/消耗日志、Webhook、BYOK（src/user-api/*）。
鉴权：Bearer tw_* 或控制台 JWT。
"""
from __future__ import annotations

import argparse
import json

from auth import load_api_key
from common import TradewindClient, load_settings
from _util import dump_json, query_from_kv


def _add_filters(ap: argparse.ArgumentParser) -> None:
    ap.add_argument(
        "-F",
        "--filter",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="查询参数，可重复，如 -F skip=0 -F take=20",
    )


def main() -> None:
    p = argparse.ArgumentParser(description="TradeWind user self-service APIs")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("api-keys-list", help="GET /api/user/api-keys")

    ck = sub.add_parser("api-keys-create", help="POST /api/user/api-keys")
    ck.add_argument("--body", required=True)

    pk = sub.add_parser("api-keys-patch", help="PATCH /api/user/api-keys/:id")
    pk.add_argument("--id", required=True)
    pk.add_argument("--body", required=True)

    dk = sub.add_parser("api-keys-delete", help="DELETE /api/user/api-keys/:id")
    dk.add_argument("--id", required=True)

    b1 = sub.add_parser("billing-checkout-session", help="POST /api/user/billing/checkout-session")
    b1.add_argument("--body", required=True)
    b2 = sub.add_parser("billing-portal-session", help="POST /api/user/billing/portal-session")
    b2.add_argument("--body", required=True)
    b3 = sub.add_parser("billing-confirm-checkout", help="POST /api/user/billing/confirm-checkout")
    b3.add_argument("--body", required=True)

    al = sub.add_parser("access-logs", help="GET /api/user/access-logs")
    _add_filters(al)
    ul = sub.add_parser("usage-logs", help="GET /api/user/usage-logs")
    _add_filters(ul)
    ud = sub.add_parser("usage-log-detail", help="GET /api/user/usage-logs/:id")
    ud.add_argument("--id", required=True)

    mo = sub.add_parser("metrics-overview", help="GET /api/user/metrics/overview")
    _add_filters(mo)

    sub.add_parser("webhooks-list", help="GET /api/user/webhooks")
    wh = sub.add_parser("webhooks-create", help="POST /api/user/webhooks")
    wh.add_argument("--body", required=True)
    wd = sub.add_parser("webhooks-delete", help="DELETE /api/user/webhooks/:id")
    wd.add_argument("--id", required=True)

    sub.add_parser("byok-list", help="GET /api/user/byok/keys")
    bc = sub.add_parser("byok-create", help="POST /api/user/byok/keys")
    bc.add_argument("--body", required=True)
    bp = sub.add_parser("byok-patch", help="PATCH /api/user/byok/keys/:id")
    bp.add_argument("--id", required=True)
    bp.add_argument("--body", required=True)
    bd = sub.add_parser("byok-delete", help="DELETE /api/user/byok/keys/:id")
    bd.add_argument("--id", required=True)

    args = p.parse_args()
    load_api_key()
    client = TradewindClient(load_settings())
    cmd = args.cmd

    if cmd == "api-keys-list":
        dump_json(client.get_api("user/api-keys"))
    elif cmd == "api-keys-create":
        dump_json(client.post_api("user/api-keys", json.loads(args.body)))
    elif cmd == "api-keys-patch":
        dump_json(client.patch_api(f"user/api-keys/{args.id}", json.loads(args.body)))
    elif cmd == "api-keys-delete":
        dump_json(client.delete_api(f"user/api-keys/{args.id}"))
    elif cmd == "billing-checkout-session":
        dump_json(client.post_api("user/billing/checkout-session", json.loads(args.body)))
    elif cmd == "billing-portal-session":
        dump_json(client.post_api("user/billing/portal-session", json.loads(args.body)))
    elif cmd == "billing-confirm-checkout":
        dump_json(client.post_api("user/billing/confirm-checkout", json.loads(args.body)))
    elif cmd == "access-logs":
        dump_json(client.get_api("user/access-logs", query_from_kv(args.filter)))
    elif cmd == "usage-logs":
        dump_json(client.get_api("user/usage-logs", query_from_kv(args.filter)))
    elif cmd == "usage-log-detail":
        dump_json(client.get_api(f"user/usage-logs/{args.id}"))
    elif cmd == "metrics-overview":
        dump_json(client.get_api("user/metrics/overview", query_from_kv(args.filter)))
    elif cmd == "webhooks-list":
        dump_json(client.get_api("user/webhooks"))
    elif cmd == "webhooks-create":
        dump_json(client.post_api("user/webhooks", json.loads(args.body)))
    elif cmd == "webhooks-delete":
        dump_json(client.delete_api(f"user/webhooks/{args.id}"))
    elif cmd == "byok-list":
        dump_json(client.get_api("user/byok/keys"))
    elif cmd == "byok-create":
        dump_json(client.post_api("user/byok/keys", json.loads(args.body)))
    elif cmd == "byok-patch":
        dump_json(client.patch_api(f"user/byok/keys/{args.id}", json.loads(args.body)))
    elif cmd == "byok-delete":
        dump_json(client.delete_api(f"user/byok/keys/{args.id}"))
    else:
        raise SystemExit(f"未知子命令: {cmd}")


if __name__ == "__main__":
    main()
