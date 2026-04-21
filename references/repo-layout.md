# TradeWind API 仓库布局（给 Agent 的速查）

以下内容便于在已克隆 `tradewind-api` 仓库内导航；路径均相对于**仓库根目录**。

| 区域 | 说明 |
|------|------|
| `_openClawSkill/skills/tradewind-api/scripts/` | 与主项目路由对齐的 CLI：`health`、`company_api`、`people_api`、`customs_api`、`agentic_api`、`email_api`、`user_api`、`auth_session` 等（不含 `admin` 运维接口） |
| `prisma/` | `schema.prisma`、迁移与 `seed.ts` |
| `src/` | NestJS 应用源码（模块、控制器、服务） |
| `docker-compose.yml` | 本地 Postgres / Redis 等 |
| `DEPLOYMENT.md` | 服务器部署、外网库、Redis 等 |
| `.env.example` | 环境变量清单与注释 |

集成外部能力（Apollo、海关、Agentic 等）时，以 `.env.example` 中的变量名为准，并在代码中查找对应模块，避免臆测端点或鉴权方式。
