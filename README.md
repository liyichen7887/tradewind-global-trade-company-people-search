# TradeWind · OpenClaw Skills

本目录为 **OpenClaw / ClawHub** 兼容的 Skill 集合，可单独开源；安装时由 OpenClaw CLI 拉取各子目录中的 Skill 包。

规范来源：[ClawHub · Skill format](https://github.com/openclaw/clawhub/blob/main/docs/skill-format.md)（`SKILL.md`  frontmatter、`metadata.openclaw`、允许的文件类型与体积限制等）。

## 目录结构

```
_openClawSkill/
├── README.md                 # 本说明
├── LICENSE                   # MIT-0，与 ClawHub 发布许可一致
├── .gitignore
├── .clawhubignore            # 发布/同步时忽略项
└── skills/
    └── <skill-slug>/         # 每个 Skill 一个文件夹，slug: ^[a-z0-9][a-z0-9-]*$
        ├── SKILL.md          # 必填：说明 + YAML frontmatter
        ├── references/       # 可选：按需加载的参考文档
        ├── scripts/          # 可选：可执行脚本（须为发布允许的文本类型）
        └── assets/           # 可选：模板等（文本类为主）
```

## 新增 Skill

1. 在 `skills/` 下新建文件夹，名称使用小写与连字符（与 `name` 字段一致）。
2. 编写 `SKILL.md`：至少包含 `name`、`description`、`version`；若读写环境变量或调用 CLI，在 `metadata.openclaw` 中声明 `requires.env`、`requires.bins` 等。
3. 仅使用 ClawHub 允许的文本类扩展名，控制总包体积（当前规范约 50MB 上限）。

## 与主仓库的关系

- **Skill 相关文件仅存在于 `_openClawSkill`**，不修改主项目业务代码。
- 主仓库根目录的 `README.md`、`DEPLOYMENT.md`、`.env.example` 等仍由主项目维护；Skill 内通过文字说明引导 Agent 去阅读那些路径（克隆主仓库后路径为仓库根相对路径）。

## 发布与安装（概要）

- 发布：按 ClawHub / OpenClaw 文档使用官方 CLI 或平台，从 `skills/<slug>` 目录作为单个 Skill 根目录上传。
- 安装：由 OpenClaw 侧 `skill install`（或等价命令）指定来源；具体命令以 OpenClaw 当前文档为准。
