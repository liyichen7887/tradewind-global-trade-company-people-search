"""脚本内部小工具（非 OpenClaw 入口）。"""
from __future__ import annotations

import json
import sys
from typing import Any, Mapping


def dump_json(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def die(msg: str, code: int = 1) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def parse_body_json(s: str) -> Mapping[str, Any]:
    return json.loads(s)


def query_from_kv(pairs: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for p in pairs:
        if "=" not in p:
            die(f"查询参数需为 key=value 形式: {p!r}")
        k, v = p.split("=", 1)
        out[k.strip()] = v
    return out
