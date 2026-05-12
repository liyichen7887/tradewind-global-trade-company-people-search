# TradeWind 信风 · OpenClaw / Cursor Skill

面向 [TradeWind 信风](https://www.trade-wind.co) HTTP API 的 **Agent Skill** 与 **Python 命令行脚本**（标准库 `urllib`，无额外 pip 依赖）。适合在 OpenClaw、Cursor 等环境中让 AI 按文档正确调用企业/联系人搜索、海关数据、智能体获客、邮箱验证等接口。

---

## 关于作者与产品

本 Skill 由 **信风 AI 外贸获客智能体** 维护，与信风产品体系配套使用：

| 资源 | 链接 |
|------|------|
| 信风官网（品牌与产品） | [https://www.trade-wind.co](https://www.trade-wind.co) |
| API 主页 | [https://api.trade-wind.co](https://api.trade-wind.co) |
| API 文档 | [https://docs.trade-wind.co](https://docs.trade-wind.co) |
| API 控制台（登录、创建 API Key） | [https://app.trade-wind.co/console/auth/login](https://app.trade-wind.co/console/auth/login) |

在控制台创建 **`tw_*` API Key** 或取得 **JWT** 后，通过环境变量 `TRADEWIND_API_KEY` 供脚本与 Agent 使用（勿将密钥提交到 Git）。

---

## 本仓库包含什么

- **`SKILL.md`**：Agent 主指引（意图路由、瀑布流请求体、`first_match` / `aggregate`、智能体与 ISO 国家码区别等）。
- **`scripts/`**：与线上路由对齐的 CLI（`people_api.py`、`company_api.py`、`customs_api.py`、`agentic_api.py` 等）。
- **`references/`**：请求体速查、国家/语言编码、自然语言问法路由等补充文档。

详细脚本列表与注意事项见 [SKILL.md](SKILL.md)。

---

## 环境要求

- **Python 3**（用于运行 `scripts/` 下脚本）。
- 可选：**OpenClaw / Cursor** 等支持挂载 Skill 的 Agent 运行时。

---

## 安装方式

### 方式 A：作为 OpenClaw / Agent Skill 使用

1. 克隆本仓库（或下载 ZIP 解压）到本机。
2. 将 **包含 `SKILL.md` 的仓库根目录** 加入 Agent 的 **skills 搜索路径**（具体目录名取决于你的 OpenClaw / Cursor 配置；常见做法是把本仓库放在 skills 集合目录下，或建立符号链接指向该目录）。
3. 在运行 Agent 的环境中配置 **`TRADEWIND_API_KEY`**（以及按需的 `TRADEWIND_API_BASE_URL` 等），见下文「环境变量」。
4. 让 Agent 阅读根目录 **`SKILL.md`** 与 **`references/`** 下的链接文档后再发起 API 调用。

### 方式 B：仅作为命令行工具使用

1. `git clone` 本仓库。
2. `cd scripts`。
3. 设置环境变量后执行 `python3 people_api.py --help` 等子命令（见 [SKILL.md](SKILL.md) 中的示例）。

---

## 快速上手（CLI）

在 `scripts/` 目录下（Linux / macOS 示例）：

```bash
export TRADEWIND_API_KEY="tw_live_xxx"   # 或 tw_test_* / 控制台 JWT
export TRADEWIND_API_BASE_URL="https://app.trade-wind.co"   # 默认值，可按部署修改

python3 health.py liveness
python3 people_api.py search --body '{"page":1,"per_page":5,"company":{"domains":["stripe.com"]},"job":{"departments":["sales"]}}'
```

**Windows PowerShell** 示例（多句命令请用分号 `;` 分隔）：

```powershell
$env:TRADEWIND_API_KEY = "tw_live_xxx"
cd scripts; python people_api.py search --body "{\"page\":1,\"per_page\":5,\"company\":{\"domains\":[\"stripe.com\"]}}"
```

更多环境变量与排错说明见 [SKILL.md](SKILL.md)（如 `TRADEWIND_HTTP_LOG=1`、`TRADEWIND_BODY_HINTS=1`）。

---

## 环境变量一览

| 变量 | 说明 |
|------|------|
| `TRADEWIND_API_KEY` | 必填（多数业务脚本）：`Authorization: Bearer <KEY>` |
| `TRADEWIND_API_BASE_URL` | 可选，默认 `https://app.trade-wind.co` |
| `TRADEWIND_MIN_INTERVAL_SEC` | 可选，请求最小间隔（秒） |
| `TRADEWIND_HTTP_LOG` | 可选，设为 `1` / `true` 时在 stderr 打印请求与响应摘要 |
| `TRADEWIND_BODY_HINTS` | 可选，设为 `1` 时在 people/company `search` 前对常见误写字段给出 stderr 提示 |

---

## 文档索引

| 文档 | 内容 |
|------|------|
| [SKILL.md](SKILL.md) | Agent 入口：路由、瀑布流 body、示例命令 |
| [references/request-body-cheatsheet.md](references/request-body-cheatsheet.md) | 合法字段与常见误写 |
| [references/intent-routing.md](references/intent-routing.md) | 自然语言问法 → 脚本 |
| [references/country-and-locale.md](references/country-and-locale.md) | 瀑布流 ISO2 vs 智能体 country/cr/lang |
| [references/repo-layout.md](references/repo-layout.md) | 若在 `tradewind-api` 单体仓库内导航时的布局说明 |

完整 HTTP 语义与字段以 **[官方 API 文档](https://docs.trade-wind.co)** 为准。

---

## 安全提示

- 永远不要把真实的 `TRADEWIND_API_KEY` 或 JWT 写进 Skill、README 或提交到 Git。
- 本 Skill **不包含** `POST/GET /api/admin/*` 等运维向接口封装；管理员操作请在受控环境自行使用专用工具。

---

## 反馈与支持

功能与计费问题请以 [信风官网](https://www.trade-wind.co) 与控制台内说明为准；本仓库 Issues 可用于 Skill 与脚本的改进反馈。
