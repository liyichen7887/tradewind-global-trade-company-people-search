# 自然语言意图 → TradeWind 脚本（OpenClaw）

同一需求可用多种说法；Agent 应先归类 **意图**，再选 **脚本** 与 **请求体形状**。**瀑布流**（people/company search）与 **智能体**（agentic）使用的 **国家编码体系不同**，见 [country-and-locale.md](country-and-locale.md)。

## 找人 / 联系人 / 招聘 / 销售

| 用户说法（示例） | 脚本 | 关键 body 思路 |
|------------------|------|----------------|
| 「Stripe 的销售」「某司 account executive」「这家公司 VP」 | `people_api.py search` | `company.domains` 或 `company.names`；`job.departments`（枚举如 `sales`）、`job.job_titles` |
| 「美国公司里的采购」 | `people_api.py search` | `company_locations.country_code: ["US"]`（ISO2）；部门/职级用 `job.*` |
| 「查这个人邮箱电话详情」 | `people_api.py enrich` | `identity`：`first_name`、`last_name`、`domain` 等（与 search 的 `company`/`job` 块不同） |

## 找公司 / 拓客（B2B 列表）

| 用户说法（示例） | 脚本 | 关键 body 思路 |
|------------------|------|----------------|
| 「加州的软件公司」「英国 fintech」 | `company_api.py search` | `location.country_code` / `states` / `cities`；`industry`、`technologies` 等见官方文档 |
| 「和 Shopify 类似的公司」 | `company_api.py search` | 文档中的 `similar_to` 等（以 Swagger 为准） |

## 海关 / 进出口 / HS

| 用户说法（示例） | 脚本 | 关键 body 思路 |
|------------------|------|----------------|
| 「HS 编码 xxx 的进口商」「海关数据」 | `customs_api.py search` 或 `post` | 先 `customs_api.py countries` 核对国家/地区字段；再按官方 customs 请求体组 JSON |
| 「这家公司海关画像」 | `customs_api.py post --path companies/detail --body '...'` | `--path` 为 `customs/` 后的相对路径 |

## 智能体 / 异步获客 / 任务跑一阵

| 用户说法（示例） | 脚本 | 关键 body 思路 |
|------------------|------|----------------|
| 「帮我跑一批潜客任务」「多渠道画像获客」「一两小时后要结果」 | `validate_agentic_plan.py` → `agentic_api.py search` → `list` / `task` | **先** 下载国家语言参考，按 [agentic-search-planning.md](agentic-search-planning.md) 建产品×角色×意图覆盖计划并提交 pilot；勿直接用一个宽 keyword 代表整个国家范围 |
| 「任务进度」「任务列表」 | `agentic_api.py list` / `task` | `--body` 以官方文档为准 |

## 邮箱验证

| 用户说法（示例） | 脚本 |
|------------------|------|
| 「验证这个邮箱是否有效」 | `email_api.py verify` → `result` |

## 控制台 / 用量

| 用户说法（示例） | 脚本 |
|------------------|------|
| 「API Key」「账单」「调用日志」 | `user_api.py` 各子命令 |

## 模式选择速记

- **实时、条件明确**（公司名/域名/职位/地域）：`people` 或 `company` **search**，并显式设置 `waterfall.mode`（要快用 `first_match`，要更全用 `aggregate`）。
- **批量、异步、画像式**：**agentic**；国家语言必须对齐 **cr-lang 参考 JSON**，国家级或多产品/角色任务必须先验证 Agentic Search Plan。
