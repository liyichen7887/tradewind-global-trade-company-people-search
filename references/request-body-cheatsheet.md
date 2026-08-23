# TradeWind API 2.0：请求体速查（OpenClaw / CLI）

与官方《信风 TradeWind AI API 2.0》一致：**未知顶层字段会被服务端忽略**，导致瀑布流在无有效筛选时返回看似「全库」的结果。以下只列 **常用合法顶层键** 与 **常见误写**。

## `POST /api/people/search`

**合法顶层键（节选）**：`page`、`per_page`、`waterfall`、`company`、`job`、`company_locations`、`person_locations`、`person`、`education`、`contact_requirements`。

| 误写（顶层或错误块名） | 应改为 |
|------------------------|--------|
| `company_names` | `company.names`（数组） |
| `company_domains` | `company.domains`（数组） |
| `titles`、`job_titles`（顶层） | `job.job_titles`（数组） |
| `department`（单数）、`departments`（顶层） | `job.departments`（数组；值为文档枚举，如 `sales`） |
| `linkedin_url`、`emails`（顶层，用于搜索） | 文档中 search 体以 `company` / `job` / `person` 等为主；领英/邮箱筛选以官方 Swagger 为准，勿臆造字段 |
| `seniority`（顶层） | `job.seniorities`（数组） |

**`job.departments` 枚举（文档）**：`executive`、`it`、`product_engineering`、`finance`、`hr`、`legal`、`marketing`、`health`、`operations`、`sales`、`education`、`management`、`support`、`design`、`communication`。

**`waterfall.mode`**：`first_match`（默认，先命中先返回）或 `aggregate`（多源聚合，需更全结果时可试）。

## `POST /api/people/enrich`

**合法顶层键**：`identity`、`waterfall`（节选）。

**`identity`（文档示例字段）**：`first_name`、`last_name`、`domain`（所属公司域名）。与 **people/search** 的 `company` / `job` 结构不同，勿把 search 的 JSON 直接用于 enrich。

## `POST /api/company/search`

**合法顶层键（节选）**：`page`、`per_page`、`waterfall`、`company`、`industry`、`technologies`、`location`、`size`、`funding`、`similar_to`、`ecommerce`、`local_search`、`response`。

| 误写 | 应改为 |
|------|--------|
| `company_names` | `company.names` |
| `domain`（单字符串顶层） | `company.domains`（数组） |

## 其它脚本（透传 body）

| 端点 | 说明 |
|------|------|
| `POST /api/customs/search`、`/enrich`、`/customs/*` | 以官方请求体为准；`customs_api.py post` 的 `--path` 为 `customs/` 后的相对路径 |
| `POST /api/agentic/search` 等 | 国家级/多产品研究从已验证计划按 taskKey 读取 requestBody；用户明确的一次性单边界任务才用 `--direct --body` |
| `POST /api/email/verify` | 仅透传 `--body` |
| `POST /api/user/*` | 各子命令见 `user_api.py` |

调试时建议设置 `TRADEWIND_HTTP_LOG=1`，在 stderr 查看实际发出的 JSON。

## 与智能体 `country` / `cr` / `lang` 的区别（勿混用）

- **本页上文**（people/company search）中的 **`country_code`** 为 **ISO 3166-1 alpha-2**（如 `US`），用于瀑布流地理位置筛选。
- **`POST /api/agentic/search`** 使用文档规定的 **`country`、`cr`、`lang`**（取值来自国家与语言编码参考，如 `USA` / `countryUS` / `English`），与 ISO2 **不是同一套枚举**。
- 智能体组 body 前请先拉取参考 JSON：`python reference_api.py agentic-country-cr-lang -o ...`（无需 API Key）。国家级、多产品或多角色任务还要读取 [agentic-search-planning.md](agentic-search-planning.md) 并验证覆盖计划。详见 [country-and-locale.md](country-and-locale.md)。
