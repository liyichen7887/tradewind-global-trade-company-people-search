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
from pathlib import Path
from typing import Any

from auth import load_api_key
from common import TradewindClient, load_settings
from _util import die, dump_json
from validate_agentic_plan import load_plan, resolve_submittable_task


def resolve_search_body(args: argparse.Namespace) -> dict[str, Any]:
    if args.direct:
        if args.plan_file or args.task_key:
            die("--direct 不能与 --plan-file/--task-key 同时使用")
        if not args.direct_reason or not args.direct_reason.strip():
            die("--direct 需要 --direct-reason 记录用户明确授权的单一边界")
        if not args.body:
            die("--direct 需要 --body")
        body = json.loads(args.body)
        if not isinstance(body, dict):
            die("Agentic search body 必须是 JSON object")
        return body

    if not args.plan_file or not args.task_key:
        die("Agentic search 默认需要 --plan-file 与 --task-key；一次性明确请求才可使用 --direct")
    if args.body:
        die("计划内提交直接使用计划 requestBody，不接受额外 --body")
    plan = load_plan(Path(args.plan_file))
    task = resolve_submittable_task(plan, args.task_key)
    return dict(task["requestBody"])


def main() -> None:
    p = argparse.ArgumentParser(description="TradeWind agentic APIs")
    sub = p.add_subparsers(dest="cmd", required=True)
    search = sub.add_parser("search", help="POST /api/agentic/search")
    search.add_argument("--plan-file", help="已通过校验的 Agentic Search Plan")
    search.add_argument("--task-key", help="计划内已批准的 taskKey")
    search.add_argument("--body", help="仅与 --direct 一起使用的 JSON 字符串")
    search.add_argument("--direct", action="store_true", help="用户明确授权的一次性单边界任务")
    search.add_argument("--direct-reason", help="一次性 direct 任务的授权与边界说明")
    for name, desc in (
        ("list", "POST /api/agentic/list"),
        ("task", "POST /api/agentic/task"),
    ):
        sp = sub.add_parser(name, help=desc)
        sp.add_argument("--body", required=True, help="JSON 字符串")
    args = p.parse_args()
    body = resolve_search_body(args) if args.cmd == "search" else json.loads(args.body)
    load_api_key()
    client = TradewindClient(load_settings())
    dump_json(client.post_api(f"agentic/{args.cmd}", body))


if __name__ == "__main__":
    main()
