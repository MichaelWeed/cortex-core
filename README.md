# Cortex Core

![Cortex Core](assets/flag.jpg)

**Your Central Intelligence & Action Registry**

This repository serves as the single source of truth for all AI models ("Brains") and executable tools ("Hands") used across your local projects, operating as an "intelligence core" and an "actions core". By centralizing these definitions, you ensure that every project has access to the latest capabilities without manual updates.

## 📂 Structure

- **`config/`**: Core catalog files
  - `model_catalog.json`: The registry of available LLMs (xAI, OpenAI, Google, etc.), including their pricing, context windows, and capabilities.
  - `tool_catalog.json`: The registry of executable tools (Search, Scrape, etc.) and their schemas.
- **`cortex.py`**: Unified CLI — `export`, `list-models`, `check` (use from any directory).
- **`export_catalog.py`**: Export model catalog to JSON for pipelines.
- **`model_resolution.py`**: Copy into other repos for `load_catalog()`, `validate_or_map()`, `get_by_role()`, `get_by_capability()`.
- **`tools/cortex/listModels/`**: List-models implementation (MCP tool `cortex_list_models`).
- **`tests/`**: Test infrastructure and validation scripts
  - `validate_catalog.py`: Full validation with API calls (monthly runs)
  - `validate_schema.py`: Schema validation only (static checks)
  - `runner.py`: Tool implementation test runner
- **`docs/`**: Project documentation (see [docs/README.md](docs/README.md))
- **`bugs/`**: Bug tracking system (YAML format)
- **`assets/`**: Static assets (images, etc.)

## 🚀 How to Use

**Quick start (from another repo):** `python3 /path/to/cortex-core/cortex.py export -o catalog.json` then read the file at startup; or run `cortex check` in CI. See [Pipeline integration](#-pipeline--other-repo-integration) below.

### Option 1: Symlink (Recommended for Local Dev)

Download the project to a central location that your various projects can access. Link these config files directly into your project's configuration directory. If done correctly, you can always maintain one centralized cortex for all of your intelligence platforms.

**Mac/Linux:**

```bash
# In your project root (e.g., ~/Projects/your-project)
ln -s ~/cortex-core/config/model_catalog.json ./config/model_catalog.json
ln -s ~/cortex-core/config/tool_catalog.json ./config/tool_catalog.json
```

**Windows (PowerShell):**

```powershell
New-Item -ItemType SymbolicLink -Path ".\config\model_catalog.json" -Target "$env:USERPROFILE\cortex-core\config\model_catalog.json"
New-Item -ItemType SymbolicLink -Path ".\config\tool_catalog.json" -Target "$env:USERPROFILE\cortex-core\config\tool_catalog.json"
```

### Option 2: Copy

If you need a static snapshot for deployment, simply copy the `config/` folder into your project. You won't get updates, and you should be aware that models get deprecated over time by their providers/owners but thats a general maintenance concern and not related to the cortex core.

## 🔌 Pipeline & other-repo integration

Cortex-core is the **SSoT** for "what models exist." Other repos can consume that truth **without MCP**:

- **One CLI:** `python3 cortex.py export | list-models | check` — export catalog, list models, health check (exit 0/1 for CI).
- **Export catalog (file):** `cortex export -o catalog.json` — pipelines read this at startup; output includes `catalog_version: "1.0"`.
- **Resolution (Python):** Copy [model_resolution.py](model_resolution.py); use `load_catalog()`, `validate_or_map()`, `get_by_role()`, `get_by_capability()`.
- **MCP (agents):** `cortex_list_models` and `cortex_add_to_catalog` — list/read and add models from agents.

See [docs/PIPELINE_INTEGRATION.md](docs/PIPELINE_INTEGRATION.md) and [docs/RUNTIME_CATALOG_SCHEMA.md](docs/RUNTIME_CATALOG_SCHEMA.md).

## 🛠 Maintenance

- **Adding a Model:** Edit `config/model_catalog.json`. All linked projects update instantly.
- **Adding a Tool:** Edit `config/tool_catalog.json`. Ensure your project has the corresponding implementation code.
- **Validation:** Run `./validate_monthly.sh` monthly to check catalog health (see [docs/VALIDATION_GUIDE.md](docs/VALIDATION_GUIDE.md))
