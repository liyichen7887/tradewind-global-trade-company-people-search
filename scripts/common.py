"""
HTTP 客户端、环境配置、可选请求/响应日志与简单节流。
与主项目 Nest 全局前缀一致：业务路径为 {base_url}/api/...
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Mapping

from auth import bearer_headers


UPSTREAM_FAILURE_MARKERS = (
    "thinkphp", "think\\", "vendor/topthink", "stack trace", "fatal error",
    "uncaught exception", "call stack", "traceback",
)
UPSTREAM_TECHNICAL_MARKERS = (".php", "php:", "vendor/", "framework/")
TOTAL_KEYS = {"total", "totalresults", "totalcount"}
HAS_MORE_KEYS = {"hasmore", "hasnext", "more"}
ITEM_KEYS = {"results", "items", "records", "companies", "people", "shipments"}


def _env(name: str, default: str | None = None) -> str | None:
    v = os.environ.get(name)
    if v is None or v == "":
        return default
    return v


@dataclass(frozen=True)
class Settings:
    base_url: str
    api_key: str
    min_interval_sec: float
    log_http: bool


def load_settings() -> Settings:
    base = (_env("TRADEWIND_API_BASE_URL", "https://app.trade-wind.co") or "").rstrip("/")
    key = _env("TRADEWIND_API_KEY", "") or ""
    interval = float(_env("TRADEWIND_MIN_INTERVAL_SEC", "0") or "0")
    log_http = (_env("TRADEWIND_HTTP_LOG", "") or "").strip() in ("1", "true", "yes")
    return Settings(
        base_url=base,
        api_key=key,
        min_interval_sec=max(0.0, interval),
        log_http=log_http,
    )


class RateLimiter:
    def __init__(self, min_interval_sec: float) -> None:
        self._min = min_interval_sec
        self._last = 0.0

    def wait(self) -> None:
        if self._min <= 0:
            return
        now = time.monotonic()
        elapsed = now - self._last
        if elapsed < self._min:
            time.sleep(self._min - elapsed)
        self._last = time.monotonic()


def _log(prefix: str, obj: Any) -> None:
    text = json.dumps(obj, ensure_ascii=False, indent=2) if not isinstance(obj, str) else obj
    print(f"[tradewind] {prefix}\n{text}", file=sys.stderr)


def _normalized_key(value: str) -> str:
    return "".join(character for character in value.casefold() if character.isalnum())


def _all_strings(value: Any) -> list[str]:
    output: list[str] = []
    if isinstance(value, str):
        output.append(value)
    elif isinstance(value, dict):
        for key, child in value.items():
            output.append(str(key))
            output.extend(_all_strings(child))
    elif isinstance(value, list):
        for child in value:
            output.extend(_all_strings(child))
    return output


def invalid_upstream_payload(value: Any) -> bool:
    text = "\n".join(_all_strings(value)).casefold()
    return (
        any(marker in text for marker in UPSTREAM_FAILURE_MARKERS)
        and any(marker in text for marker in UPSTREAM_TECHNICAL_MARKERS)
    )


def _pagination_conflicts(value: Any, path: str = "$") -> list[str]:
    conflicts: list[str] = []
    if isinstance(value, dict):
        normalized = {_normalized_key(str(key)): child for key, child in value.items()}
        metadata = [normalized]
        metadata.extend(
            {_normalized_key(str(key)): child for key, child in node.items()}
            for name in ("meta", "metadata", "pagination", "pageinfo")
            if isinstance((node := normalized.get(name)), dict)
        )
        total = next(
            (node[key] for node in metadata for key in TOTAL_KEYS if key in node),
            None,
        )
        has_more = next(
            (node[key] for node in metadata for key in HAS_MORE_KEYS if key in node),
            None,
        )
        items = next(
            (normalized[key] for key in ITEM_KEYS if key in normalized and isinstance(normalized[key], list)),
            None,
        )
        if isinstance(total, (int, float)) and has_more is False and isinstance(items, list) and total > len(items):
            conflicts.append(
                f"{path}: total={total} exceeds returned={len(items)} while has_more=false"
            )
        for key, child in value.items():
            conflicts.extend(_pagination_conflicts(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            conflicts.extend(_pagination_conflicts(child, f"{path}[{index}]"))
    return conflicts


def assess_provider_payload(value: Any) -> Any:
    if invalid_upstream_payload(value):
        return {
            "provider": "tradewind",
            "providerStatus": "upstream_unavailable",
            "data": None,
            "warnings": [{
                "code": "invalid_upstream_payload",
                "message": "Upstream returned an application stack/error payload; no records were accepted.",
            }],
        }
    conflicts = _pagination_conflicts(value)
    if conflicts and isinstance(value, dict):
        result = dict(value)
        warnings = list(result.get("providerWarnings", []))
        warnings.append({
            "code": "pagination_metadata_inconsistent",
            "message": "Pagination metadata does not prove exhaustive coverage.",
            "details": conflicts,
        })
        result["providerWarnings"] = warnings
        result["coverageStatus"] = "not_exhaustive"
        return result
    return value


class TradewindClient:
    """调用 TradeWind HTTP API。未配置 TRADEWIND_API_KEY 时不发送 Authorization（用于 @Public 路由）。"""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or load_settings()
        self.limiter = RateLimiter(self.settings.min_interval_sec)

    def _headers(
        self,
        *,
        content_type_json: bool,
        accept: str = "application/json",
        extra: Mapping[str, str] | None = None,
    ) -> dict[str, str]:
        h: dict[str, str] = {"Accept": accept}
        if self.settings.api_key:
            h.update(bearer_headers(self.settings.api_key))
        if content_type_json:
            h["Content-Type"] = "application/json"
        if extra:
            h.update(dict(extra))
        return h

    def _url(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return f"{self.settings.base_url}{path}"

    def request_json(
        self,
        method: str,
        path: str,
        body: Mapping[str, Any] | None = None,
        *,
        timeout_sec: float = 120.0,
        extra_headers: Mapping[str, str] | None = None,
    ) -> Any:
        url = self._url(path)
        data: bytes | None
        m = method.upper()
        want_ct = body is not None or m in ("POST", "PUT", "PATCH")
        headers = self._headers(content_type_json=want_ct, extra=extra_headers)
        if body is not None:
            data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        else:
            data = None
            if want_ct and m in ("POST", "PUT", "PATCH"):
                headers.setdefault("Content-Type", "application/json")

        self.limiter.wait()
        if self.settings.log_http:
            _log(f"{m} {url}", dict(body or {}))

        req = urllib.request.Request(url, data=data, headers=dict(headers), method=m)
        try:
            with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                raw = resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", errors="replace")
            if self.settings.log_http:
                _log(f"response HTTP {e.code}", raw)
            raise RuntimeError(f"HTTP {e.code}: {raw}") from e

        if self.settings.log_http:
            _log("response", raw[:8000] + ("…" if len(raw) > 8000 else ""))

        return assess_provider_payload(json.loads(raw)) if raw else None

    def get_api(
        self,
        subpath: str,
        query: Mapping[str, Any] | None = None,
        *,
        timeout_sec: float = 120.0,
        extra_headers: Mapping[str, str] | None = None,
    ) -> Any:
        p = subpath if subpath.startswith("/api/") else f"/api/{subpath.lstrip('/')}"
        if query:
            pairs: list[tuple[str, str]] = []
            for k, v in query.items():
                if v is None or v == "":
                    continue
                if isinstance(v, (list, tuple)):
                    for item in v:
                        if item is not None and str(item) != "":
                            pairs.append((k, str(item)))
                else:
                    pairs.append((k, str(v)))
            if pairs:
                p = f"{p}?{urllib.parse.urlencode(pairs)}"
        return self.request_json("GET", p, None, timeout_sec=timeout_sec, extra_headers=extra_headers)

    def get_text(
        self,
        subpath: str,
        query: Mapping[str, Any] | None = None,
        *,
        timeout_sec: float = 120.0,
        accept: str = "*/*",
    ) -> str:
        p = subpath if subpath.startswith("/api/") else f"/api/{subpath.lstrip('/')}"
        if query:
            pairs: list[tuple[str, str]] = []
            for k, v in query.items():
                if v is None or v == "":
                    continue
                pairs.append((k, str(v)))
            if pairs:
                p = f"{p}?{urllib.parse.urlencode(pairs)}"
        url = self._url(p)
        headers = self._headers(content_type_json=False, accept=accept)
        self.limiter.wait()
        if self.settings.log_http:
            _log(f"GET {url}", "(no body)")
        req = urllib.request.Request(url, headers=dict(headers), method="GET")
        try:
            with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {e.code}: {raw}") from e

    def get_bytes(self, subpath: str, *, timeout_sec: float = 120.0) -> bytes:
        p = subpath if subpath.startswith("/api/") else f"/api/{subpath.lstrip('/')}"
        url = self._url(p)
        headers = self._headers(content_type_json=False, accept="*/*")
        self.limiter.wait()
        req = urllib.request.Request(url, headers=dict(headers), method="GET")
        try:
            with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {e.code}: {raw}") from e

    def post_api(self, subpath: str, body: Mapping[str, Any] | None = None, **kwargs: Any) -> Any:
        p = subpath if subpath.startswith("/api/") else f"/api/{subpath.lstrip('/')}"
        return self.request_json("POST", p, body, **kwargs)

    def put_api(self, subpath: str, body: Mapping[str, Any] | None = None, **kwargs: Any) -> Any:
        p = subpath if subpath.startswith("/api/") else f"/api/{subpath.lstrip('/')}"
        return self.request_json("PUT", p, body, **kwargs)

    def patch_api(self, subpath: str, body: Mapping[str, Any] | None = None, **kwargs: Any) -> Any:
        p = subpath if subpath.startswith("/api/") else f"/api/{subpath.lstrip('/')}"
        return self.request_json("PATCH", p, body, **kwargs)

    def delete_api(self, subpath: str, **kwargs: Any) -> Any:
        p = subpath if subpath.startswith("/api/") else f"/api/{subpath.lstrip('/')}"
        return self.request_json("DELETE", p, None, **kwargs)
