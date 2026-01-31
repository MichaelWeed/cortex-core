# Pipeline Integration: Cortex-Core as SSoT

Use cortex-core as the **single source of truth** for "what models exist" from a Python/CLI pipeline or another repo. No MCP required in the pipeline—consume via **file** or **resolution module**.

## Quick choices

| Goal | Use this |
|------|----------|
| **One CLI** | `cortex export` / `list-models` / `check` |
| Get a JSON file to read at startup | `cortex export -o catalog.json` |
| Resolve models in Python (validate, role, capability) | `model_resolution.py` (`get_by_role`, `get_by_capability`) |
| Health check (CI/startup) | `cortex check` — exit 0/1 |
| Let agents list/read catalog via MCP | `cortex_list_models` (MCP tool) |
| Live "what’s on this machine" list | Run ai-model-scanner; parse to [runtime schema](RUNTIME_CATALOG_SCHEMA.md#2-scanner-output-contract) |

## 1. Catalog file (no Python dependency on cortex-core)

1. **Export once** (or in CI / cron):
   ```bash
   python3 /path/to/cortex-core/cortex.py export -o catalog.json
   # or: python3 /path/to/cortex-core/export_catalog.py -o catalog.json
   ```
   Copy `catalog.json` into your repo, or point your app to it via `catalog_path`.

2. **At startup in your app**: Read `catalog.json`; validate your config model names against `payload["models"][i]["code"]`; optionally choose by `payload["models"][i]["role"]` (e.g. `small-text`, `large-text`).

3. **Optional filters**: `export_catalog.py --provider ollama --capability vision -o catalog.json`

## 2. Resolution module (Python)

Copy **one file** into your repo: [model_resolution.py](../model_resolution.py). Or add cortex-core to the path and import it.

Set `CORTEX_CATALOG_PATH` to the cortex-core `config/` directory (or to a path to `model_catalog.json`).

```python
from model_resolution import load_catalog, available_models, validate_or_map, get_by_role, get_by_capability, resolve_preferred

# Load catalog (from env or path)
catalog = load_catalog()  # or load_catalog("/path/to/config")

# List available models (with derived role)
models = available_models()

# Validate config model names
valid, missing, code_to_model = validate_or_map(["gemini-2.5-flash", "unknown-model"])
if missing:
    print("Not in catalog:", missing)

# Pick by role (e.g. for discovery vs generation)
small = get_by_role("small-text")
large = get_by_role("large-text", prefer_provider="google")

# All models with a capability (e.g. vision)
vision_models = get_by_capability("vision")

# Preferred model with fallback by role
entry = resolve_preferred("gemini-2.5-flash", role_fallback="small-text")
if entry:
    print(entry["provider"], entry["model"])
```

## 3. MCP (agents only)

If your **agent** uses MCP, point it at cortex-core. Then it can call:

- **cortex_list_models** – list/filter models (same shape as export).
- **cortex_add_to_catalog** – add models/tools (writes catalog).

The pipeline (Python/CLI) does **not** need to call MCP; use file or `model_resolution.py` for "what is available" at runtime.

## 4. Scanner + catalog together

1. **Catalog** = SSoT (cortex-core). Defines codes, providers, capabilities, roles.
2. **Scanner** (e.g. ai-model-scanner) = "what’s actually available on this machine."
3. **Contract**: Scanner output should match the [runtime catalog schema](RUNTIME_CATALOG_SCHEMA.md#2-scanner-output-contract) (array of `{ code?, provider, model }`).
4. **Resolution**: Load catalog; optionally run scanner and parse output; validate config model names against catalog (and optionally against scanner); fall back by role with `get_by_role()`.

See [RUNTIME_CATALOG_SCHEMA.md](RUNTIME_CATALOG_SCHEMA.md) for the exact JSON shape and config conventions.

## 5. Unified CLI and health check

From any directory:

```bash
python3 /path/to/cortex-core/cortex.py export -o catalog.json
python3 /path/to/cortex-core/cortex.py list-models --format codes
python3 /path/to/cortex-core/cortex.py check          # exit 0 if catalogs load
python3 /path/to/cortex-core/cortex.py check -q       # quiet (CI)
python3 /path/to/cortex-core/cortex.py check --catalog-path /path/to/config
```

Exported JSON includes `catalog_version: "1.0"` so consumers can branch on schema.

## 6. Env summary

| Env | Meaning |
|-----|--------|
| `CORTEX_CATALOG_PATH` | Path to `model_catalog.json` or directory containing it (used by export_catalog, list_models, model_resolution). |

No API keys in cortex-core for catalog read/export; keys live in your app or validation env.
