# TradeWind 信风 · Skill for OpenClaw / Cursor / Claude Code / WorkBuddy / Accio / Coze

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

Base URL: https://app.trade-wind.co

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


---
## TradeWind Skill 新手教程：省积分、写准 Prompt

1. 先弄清三种「模式」
<img width="399" height="243" alt="截屏2026-06-01 下午3 22 57" src="https://github.com/user-attachments/assets/a740cb11-cf88-4276-a026-38ce2407b87e" />

原则：能一句话说清公司 + 职位 + 国家的，用 瀑布流 + first_match；只有当你明确要「尽量搜全、多源合并」时才写 aggregate；只有当你要「跑任务、批量画像」时才用 agentic。

2. 最容易浪费积分的 5 类情况

  （1）误用 aggregate 或 Prompt 里写「尽量全面 / 多源 / 全部渠道」
  Agent 容易把 waterfall.mode 设成 aggregate，或反复换数据源重试。
  省钱写法：在 Prompt 里显式约束：
  使用 TradeWind 瀑布流 people search，waterfall.mode 用 first_match，不要 aggregate。先只查第 1 页，per_page 不超过 10。
  
  （2）请求体字段写错 → 筛选失效 → 白打一次（甚至像「全库」）
  例如用 company_names、titles、顶层 emails，服务端会忽略未知字段，仍计费但结果不对，Agent 可能再试 aggregate / 换接口。
  省钱 + 准确写法：
  公司用 company.domains: ["stripe.com"]（有域名优先域名）。销售用 job.departments: ["sales"]，不要用中文「销售部」当 department。不要用 company_names 这种顶层字段。
  可让环境开 TRADEWIND_BODY_HINTS=1，在误写时 stderr 有提示（见 SKILL.md）。
  
  （3）该用瀑布流却上了智能体
  「帮我找 Stripe 的销售」→ 若 Agent 创建 agentic 任务，成本高、且慢。
  省钱写法：
  这是实时、单公司、明确职位查询，用 people_api.py search，不要创建 agentic 任务。
  
  （4）per_page 过大、无分页地「多要几条」
  省钱写法：
  page: 1，per_page: 5（或 10）。满意再要下一页，不要一次 100。
  
  （5）search 后又 enrich、又 verify，链式调用过多
  search 已有基础列表时，不要对每一个人立刻 enrich + 邮箱验证。
  省钱写法：
  先 search 返回列表；我只对你列出的前 3 个候选人做 enrich。邮箱验证仅在我提供的地址上执行。

3. 怎么写 Prompt：模板与反例
模板 A：某公司某职位（最常用，最便宜路径）
用 TradeWind skill：
- 接口：people search（瀑布流）
- waterfall.mode：first_match（禁止 aggregate）
- 公司：stripe.com → company.domains
- 职位：销售 → job.departments: ["sales"]，可加 job.job_titles: ["account executive"]
- 分页：page 1，per_page 5
- 若结果 meta.total_results 异常大或人与公司无关，先检查 JSON 字段是否嵌套正确，不要先开 aggregate
模板 B：按国家找公司
用 company search，first_match，location.country_code: ["US"]（ISO2），per_page 10。
不要 agentic。不要 aggregate，除非我明确说「要多源拼全」。
模板 C：只有在你真的要跑任务时用智能体
用 agentic：先 reference_api agentic-country-cr-lang 查美国对应的 country/cr/lang，
再 agentic search。keyword: coffee importer。这是异步任务，不要同时再跑 people search 重复搜。
反例 Prompt（容易烧钱）
暂时无法在飞书文档外展示此内容

4.让 Agent「更准」的 Prompt 技巧
  1. 给结构化事实：公司域名 > 公司中文名；职位用英文关键词或文档枚举 sales，不要只写「销售岗」。
  2. 区分 search / enrich：「先列表」用 search；「要某人邮箱电话详情」再 enrich，且 enrich 用 identity（姓名 + domain），不要把 search 整段 JSON 抄过去。
  3. 国家两套体系：瀑布流用 ISO2（US）；智能体用参考 JSON 的 USA / countryUS / English（见 skill 里 country-and-locale.md）。Prompt 里可写：「瀑布流用 ISO2，agentic 必须先下 cr-lang 参考」。
  4. 一次说清约束：把「不要 aggregate / 不要 agentic / per_page 上限」写进同一条 Prompt，减少 Agent 自作主张。
  5. 调试阶段：TRADEWIND_HTTP_LOG=1 看 stderr 实际 body，避免「猜字段 → 失败 → 再试 aggregate」的连环调用。

5. 推荐工作流（低成本）
  1. 明确意图 → 找人/找公司/海关/异步任务（对照 intent-routing）
  2. 默认：瀑布流 + first_match + 小 per_page
  3. 有域名 → company.domains；有部门 → job.departments 枚举
  4. 看返回 meta.total_results 与 people/companies 是否匹配
  5. 不够再：加大 page / 略放宽 job_titles（仍 first_match）
  6. 仍不够且你接受多源成本 → 再明确说「本次改用 aggregate」
  7. 要批量潜客画像 → 单独一次 agentic，不要和 2–6 混跑
响应里的 meta.billing（若 API 返回）可用来核对单次扣费；长期可在控制台 https://app.trade-wind.co/console/auth/login 看用量，或用 user_api.py access-logs（需 Key）。

6. 给 OpenClaw / Cursor 的「系统级」一句约束（可选）
挂载 skill 后，可在自定义说明里加：
调用 TradeWind 时：默认 waterfall.mode=first_match；禁止在未明确要求时使用 aggregate 或 agentic；per_page≤10；公司优先 company.domains；遵守 SKILL.md 与 references/request-body-cheatsheet.md；失败时先查字段嵌套，不要通过 aggregate 补救。

7. 自检清单（每次让 Agent 调 API 前）
  -  用的是 people/company/customs/agentic 里哪一种？
  -  是否写了 first_match（除非你要 aggregate）？
  -  aggregate/first_match模式是否选择错误，造成积分大量消耗？
  -  公司是否是 company.domains / company.names，不是 company_names？
  -  部门是否是 job.departments 枚举（如 sales）？
  -  per_page 是否克制？
  -  是否避免「全面 / 所有渠道 / 智能体 + 实时搜索」混用？

最容易出现的错误如下，在返回报错时请自检：
  -  base url填写错误（正确url为https://app.trade-wind.co）‘
  -  未申请Api key
  -  接口的必填参数未正确填写，漏填，或使用AI生成的错误近义词填写
  -  有枚举值的接口参数未正确填写，如Limit必须填[10,20,50,100]值中的一个，或国家/语言编码未正确传参

说明：具体扣费规则以 信风 API 文档 与控制台为准；本教程按 skill 与 API 2.0 行为归纳，帮助你在 Prompt 层减少误用模式与无效请求。
