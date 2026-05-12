# 国家与地区：瀑布流（ISO2）vs 智能体（country / cr / lang）

两套体系 **不要混用**：把 `"美国"` 或 `"US"` 直接塞进 agentic 的 `country` 而不查表，容易导致 **400 / 校验失败** 或任务不符合预期。

## 一、瀑布流：`people` / `company` search

使用 **ISO 3166-1 alpha-2** 双字母码（大写常见，以实际 API 校验为准）。

| API / 路径片段 | 字段示例 |
|----------------|----------|
| `POST /api/people/search` | `company_locations.country_code: ["US"]`；`person_locations.country_code` |
| `POST /api/company/search` | `location.country_code: ["GB"]` |

请求体其它键与误写对照见 [request-body-cheatsheet.md](request-body-cheatsheet.md)。

### 附录：中文常用称呼 → ISO2（瀑布流，精简表）

无 Key、无网时可作粗映射；**最终以官方接口与文档为准**。

| 中文（常见） | ISO2 |
|--------------|------|
| 美国 / 美 | US |
| 中国 / 大陆 | CN |
| 英国 / 英 | GB |
| 德国 | DE |
| 法国 | FR |
| 日本 | JP |
| 韩国 | KR |
| 印度 | IN |
| 加拿大 | CA |
| 澳大利亚 | AU |
| 新加坡 | SG |
| 香港 | HK |
| 台湾 | TW |
| 荷兰 | NL |
| 瑞士 | CH |
| 意大利 | IT |
| 西班牙 | ES |
| 巴西 | BR |
| 墨西哥 | MX |

## 二、智能体：`POST /api/agentic/search`

文档要求 **`country`**、**`cr`**、**`lang`** 等与「国家与语言编码参考」一致（示例形如 `country: "USA"`、`cr: "countryUS"`、`lang: "English"`）。**不要手写猜码。**

### 推荐步骤（无需 API Key）

在 `scripts/` 目录：

```bash
python reference_api.py agentic-country-cr-lang -o agentic-country-cr-lang.json
```

从 JSON 中按用户目标国家/语言 **查找并复制** 对应的 `country`、`cr`、`lang`（及文档中的 `zone` 等若需要），再组装：

```bash
python agentic_api.py search --body '{"keyword":"...","country":"USA","cr":"countryUS","lang":"English"}'
```

创建任务后用 `agentic_api.py list` / `agentic_api.py task` 轮询（`--body` 以官方文档为准）。

## 三、海关：`GET /api/customs/reference/countries`

使用 `python customs_api.py countries` 拉取国家参考列表（**可不设 `TRADEWIND_API_KEY`**；若返回 **401**，再设置 Key 重试）。用于组 `customs/search` 等 body 前的核对。
