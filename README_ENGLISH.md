# TradeWind · Global B2B Lead Generation Skill for OpenClaw / Cursor / Claude Code / Codex

An **Agent Skill** and **Python CLI toolkit** for the [TradeWind](https://www.trade-wind.co) HTTP API (utilizing the standard `urllib` library with no external `pip` dependencies required). Designed for environments like OpenClaw and Cursor, enabling AI agents to accurately invoke endpoints for company/contact search, customs data, agentic lead generation, and email verification according to the documentation.

---

## About the Author & Product

Maintained by the **TradeWind AI Lead Generation Agent**, this Skill is designed to work seamlessly with the TradeWind product ecosystem:

| Resource | Link |
|----------|------|
| Official Website (Brand & Products) | [https://www.trade-wind.co](https://www.trade-wind.co) |
| API Homepage | [https://api.trade-wind.co](https://api.trade-wind.co) |
| API Documentation | [https://docs.trade-wind.co](https://docs.trade-wind.co) |
| API Console (Login, API Key Generation) | [https://app.trade-wind.co/console/auth/login](https://app.trade-wind.co/console/auth/login) |

After creating a **`tw_*` API Key** or obtaining a **JWT** from the console, provide it to the scripts and the Agent via the `TRADEWIND_API_KEY` environment variable (do not commit your keys to Git).

API Base URL: `https://app.trade-wind.co`

---

## What's Included in This Repository

- **`SKILL.md`**: The primary guide for the Agent (intent routing, waterfall request bodies, `first_match` / `aggregate`, differences between agentic and ISO country codes, etc.).
- **`scripts/`**: CLI tools aligned with online routes (e.g., `people_api.py`, `company_api.py`, `customs_api.py`, `agentic_api.py`).
- **`references/`**: Supplementary documentation including request body cheatsheets, country/language codes, and natural language intent routing.

For a detailed list of scripts and important notes, please refer to [SKILL.md](SKILL.md).

---

## Prerequisites

- **Python 3** (required to run the scripts in the `scripts/` directory).
- Optional: Agent runtimes that support Skill mounting, such as **OpenClaw / Cursor**.

---

## Installation

### Method A: Use as an OpenClaw / Agent Skill

1. Clone this repository (or download and extract the ZIP) to your local machine.
2. Add the **repository root directory containing `SKILL.md`** to your Agent's **skills search path** (the specific directory name depends on your OpenClaw / Cursor configuration; a common practice is to place this repository in your skills collection directory or create a symlink to it).
3. Configure **`TRADEWIND_API_KEY`** (and `TRADEWIND_API_BASE_URL` if necessary) in the environment where the Agent runs, as detailed in the "Environment Variables" section below.
4. Instruct the Agent to read the **`SKILL.md`** in the root directory and the documents linked under **`references/`** before initiating any API calls.

### Method B: Use as a Standalone CLI Tool

1. `git clone` this repository.
2. `cd scripts`.
3. Set the required environment variables and execute subcommands like `python3 people_api.py --help` (see examples in [SKILL.md](SKILL.md)).

---

## Quick Start (CLI)

In the `scripts/` directory (Linux / macOS example):

```bash
export TRADEWIND_API_KEY="tw_live_xxx"   # Or tw_test_* / Console JWT
export TRADEWIND_API_BASE_URL="https://app.trade-wind.co"   # Default value, modify based on deployment

python3 health.py liveness
python3 people_api.py search --body '{"page":1,"per_page":5,"company":{"domains":["stripe.com"]},"job":{"departments":["sales"]}}'

---

## Frequent Issues for debugging purpose

 - base url is not correct.
 - required parameters of the request are missing / invalid.
 - invalid enum parameter value. For example, 'Limit' must be one of [10, 20, 50, 100].
