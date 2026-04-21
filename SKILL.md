---
name: tradewind-api
description: >-
  Guides agents to develop, run, and operate the TradeWind API backend
  (NestJS, Fastify, Prisma, PostgreSQL, Redis/BullMQ) and includes Python CLI
  scripts under scripts/ aligned with production HTTP routes (company, people,
  customs, agentic, email, user, auth). Use when working in the
  tradewind-api repository, calling https://app.trade-wind.co APIs from
  scripts, fixing API or database issues, or when the user mentions TradeWind,
  Prisma, NestJS, or deployment of this API.
version: 0.3.1
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

标准库 `urllib`，无 pip 依赖；脚本名与主项目 **控制器域** 对齐（非旧版 human/company 文件名）。多数子命令需 `TRADEWIND_API_KEY`；`health` / `reference` / `auth_session register|login` 可无 Key。

| 脚本 | 主项目对应 | 用法提示 |
|------|------------|----------|
| `_util.py` | — | 内部：`dump_json`、`query_from_kv` |
| `auth.py` | — | `load_api_key()` / `bearer_headers` |
| `common.py` | — | `TradewindClient`：`get_api` / `post_api` / `patch_api` / `delete_api` / `get_text` / `get_bytes` |
| `health.py` | `health`, `metrics` | `python health.py liveness` · `python health.py metrics` |
| `reference_api.py` | `reference` | `technologies-csv` / `agentic-country-lang`，`-o` 保存文件 |
| `company_api.py` | `company-search`, `company-enrich` | `search` / `enrich`（`--body` 或 enrich 的 `--batch-file`） |
| `people_api.py` | `people-search`, `people-enrich` | 同上 |
| `customs_api.py` | `customs`, `customs-extended` | `countries` / `search` / `enrich` / `post --path companies/detail --body '{...}'` |
| `agentic_api.py` | `agentic` | `search` / `list` / `task`，各需 `--body` |
| `email_api.py` | `email-verify` | `verify` / `result --task-id` |
| `user_api.py` | `user-api/*` | `api-keys-list`、`billing-checkout-session --body`、`access-logs -F skip=0` 等；`-F key=value` 可重复 |
| `auth_session.py` | `auth` | `register` / `login` / `me`（me 需 Bearer） |

管理员紧急运维使用的 `POST/GET /api/admin/*`（`x-admin-token`）**不放在本 skill**；请在运维环境用 curl、Postman 或自建脚本调用。

未单独封装：`POST /api/internal/agentic/settlement/row`（内部回调）；可用 `common.post_api` 自行调用。

环境变量：

- `TRADEWIND_API_BASE_URL`：默认 **`https://app.trade-wind.co`**
- `TRADEWIND_API_KEY`：Bearer（`tw_*` 或控制台 JWT；在 [信风](https://app.trade-wind.co) 获取）
- `TRADEWIND_MIN_INTERVAL_SEC`、`TRADEWIND_HTTP_LOG=1`：同上

示例（在 `scripts/` 目录下）：

```bash
set TRADEWIND_API_KEY=tw_test_xxx
python health.py liveness
python reference_api.py agentic-country-lang -o cr_lang.json
python company_api.py search --body "{\"page\":1,\"per_page\":2,\"company\":{\"names\":[\"Stripe\"]}}"
python user_api.py access-logs -F take=10
```

## Agent 注意事项

- 修改业务逻辑时遵守仓库既有风格与模块边界；不确定时先阅读相关模块与 Prisma schema。
- 涉及计费、外部数据源密钥时，仅通过环境变量与已有配置读取，不要在 Skill 或回复中硬编码密钥。
- Windows 下 PowerShell 链式命令使用分号 `;` 分隔（若用户环境为 PowerShell）。

## 延伸阅读

- 更细的部署与运维说明：[references/repo-layout.md](references/repo-layout.md)
