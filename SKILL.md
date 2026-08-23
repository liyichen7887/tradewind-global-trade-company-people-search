---
name: tradewind-api
description: >-
  TradeWind 信风 API: Python CLI for https://app.trade-wind.co — company search,
  people search, customs/HS, agentic async lead gen, email verify, user/billing,
  reference (technologies CSV, agentic country/lang JSON). 找公司、找人、招聘、
  销售职位、海关数据、进出口、智能体获客、国家地区筛选、ISO country code、
  瀑布流 first_match/aggregate、OpenClaw. Also NestJS/Prisma tradewind-api repo work.
metadata:
  openclaw:
    emoji: "\u2693"
    homepage: https://app.trade-wind.co
    requires:
      anyBins:
        - npm
        - pnpm
        - node
        - python
        - python3
    primaryEnv: TRADEWIND_API_KEY
---

# TradeWind API（本仓库）

## 快速定位

- **栈**：NestJS（Fastify）+ Prisma + PostgreSQL + Redis/BullMQ。
- **根目录文档**：`README.md`（本地开发步骤）、`DEPLOYMENT.md`（部署与 Docker）。
- **环境变量模板**：`.env.example`（勿把真实密钥写入 Skill；在运行环境配置）。

## 推荐工作流

1. **本地依赖**：首次或异常依赖时，在仓库根执行 `npm run deps:reset`（见根 `README.md`）。
2. **数据库与 Redis**：`docker compose up -d postgres redis`，再 `npx prisma migrate deploy` 与 `npm run seed`。
3. **启动 API**：按根 `README.md` 中的启动命令（如 `npm run start:dev`）。
4. **鉴权**：种子会打印 `tw_test_*` / `tw_live_*`；请求头 `Authorization: Bearer <KEY>`。

## Python 脚本（`scripts/`）

标准库 `urllib`，无 pip 依赖；脚本名与主项目 **控制器域** 对齐（非旧版 human/company 文件名）。多数子命令需 `TRADEWIND_API_KEY`；`health` / `reference` / `customs_api.py countries`（可不设 Key，若接口返回 401 再设 Key）/ `auth_session register|login` 可无 Key。

| 脚本 | 主项目对应 | 用法提示 |
|------|------------|----------|
| `_util.py` | — | 内部：`dump_json`、`query_from_kv` |
| `_body_hints.py` | — | `TRADEWIND_BODY_HINTS=1` 时由 `people_api` / `company_api` 的 `search` 在 stderr 提示常见误写字段 |
| `auth.py` | — | `load_api_key()` / `bearer_headers` |
| `common.py` | — | `TradewindClient`：`get_api` / `post_api` / `patch_api` / `delete_api` / `get_text` / `get_bytes` |
| `health.py` | `health`, `metrics` | `python health.py liveness` · `python health.py metrics` |
| `reference_api.py` | `reference` | `technologies-csv` / `agentic-country-cr-lang`（与 `agentic-country-lang` 等价），`-o` 保存文件 |
| `company_api.py` | `company-search`, `company-enrich` | `search` / `enrich`（`--body` 或 enrich 的 `--batch-file`） |
| `people_api.py` | `people-search`, `people-enrich` | 同上 |
| `customs_api.py` | `customs`, `customs-extended` | `countries`（国家参考，可不设 Key）/ `search` / `enrich` / `post --path companies/detail --body '{...}'` |
| `validate_agentic_plan.py` | — | 国家级、多产品或多角色 Agentic Search Plan 的本地提交前校验 |
| `agentic_api.py` | `agentic` | `search` 默认从已验证计划按 taskKey 取 body；`list` / `task` 使用 `--body`；用户明确的一次性单边界请求才用 `--direct` |
| `email_api.py` | `email-verify` | `verify` / `result --task-id` |
| `user_api.py` | `user-api/*` | `api-keys-list`、`billing-checkout-session --body`、`access-logs -F skip=0` 等；`-F key=value` 可重复 |
| `auth_session.py` | `auth` | `register` / `login` / `me`（me 需 Bearer） |

管理员紧急运维使用的 `POST/GET /api/admin/*`（`x-admin-token`）**不放在本 skill**；请在运维环境用 curl、Postman 或自建脚本调用。

未单独封装：`POST /api/internal/agentic/settlement/row`（内部回调）；可用 `common.post_api` 自行调用。

环境变量：

- `TRADEWIND_API_BASE_URL`：默认 **`https://app.trade-wind.co`**
- `TRADEWIND_API_KEY`：Bearer（`tw_*` 或控制台 JWT；在 [信风](https://app.trade-wind.co) 获取）
- `TRADEWIND_MIN_INTERVAL_SEC`、`TRADEWIND_HTTP_LOG=1`：同上；**调试请求体**时建议打开 `TRADEWIND_HTTP_LOG=1`，在 stderr 核对实际 POST 的 JSON。
- `TRADEWIND_BODY_HINTS=1`：`people_api.py search` / `company_api.py search` 在发现常见误写字段时于 stderr 提示正确嵌套路径（默认关闭，避免干扰管道）。

## 用户意图 → 接口与模式（路由）

不同问法先归类意图，再选脚本；**国家/地区编码**见 [references/country-and-locale.md](references/country-and-locale.md)，**问法示例**见 [references/intent-routing.md](references/intent-routing.md)。

| 用户意图（示例） | 优先脚本 | 要点 |
|------------------|----------|------|
| 某公司某职位的人、销售/VP、按部门找人 | `people_api.py` `search` / `enrich` | 有域名用 `company.domains`；`job.departments` 用文档枚举；地域用 `company_locations.country_code` 或 `person_locations`（ISO2，见 country-and-locale） |
| 按行业/规模/地域找公司 | `company_api.py` `search` | `location.country_code` 等为 ISO2 |
| 进出口、HS、海关企业 | `customs_api.py` | 不确定国家码可先 `countries`；再 `search` / `enrich` / `post` |
| 大量潜客、画像式、任务式、可稍后取结果（异步，常 1–2 小时级） | `validate_agentic_plan.py`，再 `agentic_api.py` `search` / `list` / `task` | **先**取得 `country` / `cr` / `lang`；国家级、多产品或多角色研究按产品×角色×意图建立覆盖矩阵，每个意图先跑 pilot |
| 验证邮箱 | `email_api.py` | `verify` → `result` |
| API Key、账单、用量日志 | `user_api.py` | 见脚本 `--help` |

**瀑布流 `waterfall.mode`（`people`/`company` 的 search）**

- **`first_match`**：优先速度、接受「先命中的数据源先返回」、试探性单次查询。
- **`aggregate`**：需要多源拼全、同一条件要更完整的列表时。

**瀑布流 vs 智能体**：实时、明确公司/职位/地域筛选 → 瀑布流；要跨渠道画像、批量任务、异步拉取 → 智能体。国家级或多产品/角色研究不能用一个宽泛 keyword 代替完整范围，必须先读取 [Agentic Search 提交规划合同](references/agentic-search-planning.md)，验证覆盖矩阵并按 pilot → scale 提交。智能体必填字段与参考 JSON 流程见 [references/country-and-locale.md](references/country-and-locale.md)。

## 瀑布流 POST 请求体约定（API 2.0）

`POST /api/people/search` 与 `POST /api/company/search` 等瀑布流接口的筛选条件写在 **文档规定的嵌套对象** 内（如 `company`、`job`、`waterfall`）。**禁止** 自行发明顶层字段名（例如 `company_names`、`titles`、顶层 `emails`）：这些通常会被忽略，表现为 `meta.total_results` 极大、返回人物与公司无关。

- **`POST /api/people/search`**：公司用 `company.names` / `company.domains`（二者同时有时 **域名优先**）；职位用 `job.job_titles`、`job.departments`（`departments` 为 **枚举**，如销售条线用 `"sales"`，不是任意中文部门名）、`job.seniorities`。需要多源拼全时可设 `waterfall.mode` 为 `"aggregate"`（默认多为 `first_match`）。
- **`POST /api/people/enrich`**：人员维度在 **`identity`** 下（文档示例含 `first_name`、`last_name`、`domain`），另有 `waterfall`；**不要** 把 search 用的 `company`/`job` 大块不经查抄进 enrich。

更全的合法键与「误写 → 正写」对照见 [references/request-body-cheatsheet.md](references/request-body-cheatsheet.md)。

精确公司、人员、海关或邮箱结果交给 GETO 前，按 [Provider Observation 采纳合同](references/observation-acceptance.md) 记录主体锚点、国家字段、覆盖状态和证据范围。法律后缀不构成主体锚点；请求国家没有体现在返回记录时，不能声称该记录通过国家过滤。邮箱验证只支持邮箱可投递性。

Agentic 异步任务按 plan、pilot、submit、status、result、coverage review 六阶段处理。计划先记录全部 productFamily、roleLane、sourceGoal、排除项、任务依赖和停止条件；lead 与 competitor 分开，购买链明显不同的产品面分开。pilot 未验收国家/角色/产品命中、漂移、重复和分页前，不批量提交 scale。计划内 `search` 只允许 `approved_for_pilot|approved_for_submit` 的 taskKey，并直接使用计划 requestBody，防止临时改词漂移。submit 成功消息和非空 taskId 只记录为 `submission_acknowledged_unconfirmed`；状态明确 completed 后才分页读取结果。已有 taskId 和相同 queryBoundary 时恢复原任务，不重复 submit；状态接口错误、HTTP 500、认证失败、限流和余额不足分别保留原状态，不写成 no_result。分页参数、返回条数、去重键、总量和覆盖状态随 ExternalObservation 保存。

精确域名或法定名称锚定、完整姓名和 Provider 联系方式可以支持联系人 Observation；公司官网或公开职业页用于确认当前任职、职位和职责。姓名掩码、雇主锚点不足或同名冲突不进入正式联系人。Provider 记录可以支持 reachability，不支持 buyingRole、签字权、buyer、payer 或项目授权。精确人员查询 0 结果时，可使用官网、公开职业页或更宽公司名称边界补查，并分别保留查询边界。

示例（在 `scripts/` 目录下）：

```bash
set TRADEWIND_API_KEY=tw_test_xxx
python health.py liveness
python reference_api.py agentic-country-cr-lang -o cr_lang.json
python validate_agentic_plan.py ../agentic-search-plan.json
python agentic_api.py search --plan-file ../agentic-search-plan.json --task-key us-formwork-main-contractors-pilot
python company_api.py search --body "{\"page\":1,\"per_page\":2,\"company\":{\"names\":[\"Stripe\"]}}"
python people_api.py search --body "{\"page\":1,\"per_page\":10,\"company\":{\"domains\":[\"stripe.com\"]},\"job\":{\"departments\":[\"sales\"],\"job_titles\":[\"account executive\"]}}"
python user_api.py access-logs -F take=10
```

### 排错（结果像「没筛选」）

若返回里人物与目标公司明显无关，且 `meta.total_results` 异常大：先检查 `--body` 是否含 **文档未列出的顶层键**；再设 `TRADEWIND_HTTP_LOG=1` 重跑，确认发出的 JSON 与 cheatsheet / 官方文档一致。需要更稳的部门筛选时，使用文档枚举值（如 `sales`），并视情况改用 `waterfall.mode: "aggregate"`。

## Agent 注意事项

- 修改业务逻辑时遵守仓库既有风格与模块边界；不确定时先阅读相关模块与 Prisma schema。
- 涉及计费、外部数据源密钥时，仅通过环境变量与已有配置读取，不要在 Skill 或回复中硬编码密钥。
- Windows 下 PowerShell 链式命令使用分号 `;` 分隔（若用户环境为 PowerShell）。

## 延伸阅读

- 自然语言问法 → 脚本与字段：[references/intent-routing.md](references/intent-routing.md)
- 国家码：瀑布流 ISO2 vs 智能体 country/cr/lang：[references/country-and-locale.md](references/country-and-locale.md)
- 请求体合法键与常见误写：[references/request-body-cheatsheet.md](references/request-body-cheatsheet.md)
- Agentic 产品×角色×意图覆盖、pilot 与提交门禁：[references/agentic-search-planning.md](references/agentic-search-planning.md)
- Provider 结果采纳、覆盖和邮箱证据：[references/observation-acceptance.md](references/observation-acceptance.md)
- 更细的部署与运维说明：[references/repo-layout.md](references/repo-layout.md)
