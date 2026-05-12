"""可选：在 POST 前根据常见误写字段打印 stderr 提示（TRADEWIND_BODY_HINTS=1）。"""
from __future__ import annotations

import os
import sys
from typing import Any, Mapping


def enabled() -> bool:
    v = (os.environ.get("TRADEWIND_BODY_HINTS") or "").strip().lower()
    return v in ("1", "true", "yes")


def _warn(msg: str) -> None:
    print(f"[tradewind-body-hint] {msg}", file=sys.stderr)


def warn_people_search_body(body: Mapping[str, Any] | None) -> None:
    if not enabled() or body is None:
        return
    hints: list[tuple[str, str]] = [
        ("company_names", "请使用 company.names（字符串数组），不要使用顶层 company_names"),
        ("company_domains", "请使用 company.domains（字符串数组）"),
        ("titles", "请使用 job.job_titles（数组），不要使用顶层 titles"),
        ("linkedin_url", "people/search 请求体以官方文档为准；勿使用未文档化的顶层 linkedin_url"),
        ("emails", "people/search 请求体以官方文档为准；勿使用未文档化的顶层 emails"),
        ("department", "请使用 job.departments（数组；值为文档枚举，例如 sales）"),
    ]
    for key, msg in hints:
        if key in body:
            _warn(msg)
    if "departments" in body and "job" not in body:
        _warn("departments 应放在 job.departments 内，不要作为顶层字段")
    if "job_titles" in body and "job" not in body:
        _warn("job_titles 应放在 job.job_titles 内，不要作为顶层字段")
    job = body.get("job")
    if isinstance(job, Mapping) and "titles" in job and "job_titles" not in job:
        _warn("job 内应使用 job_titles，不要使用 job.titles")


def warn_company_search_body(body: Mapping[str, Any] | None) -> None:
    if not enabled() or body is None:
        return
    company = body.get("company")
    if "company_names" in body:
        _warn("请使用 company.names（数组），不要使用顶层 company_names")
    if "names" in body and not isinstance(company, Mapping):
        _warn("公司名应放在 company.names，不要单独使用顶层 names")
    if "domains" in body and not isinstance(company, Mapping):
        _warn("域名应放在 company.domains，不要单独使用顶层 domains")
    if "domain" in body and "company" not in body:
        _warn("单公司域名请使用 company.domains（字符串数组），不要使用顶层 domain")
