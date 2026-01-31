# Runtime Catalog Schema & Scanner Contract

Cortex-core is the **single source of truth (SSoT)** for "what models exist." Pipelines and other repos consume that truth in two ways: **catalog file** or **scanner output**. This doc defines the stable contract so you can wire either.

## 1. Cortex-core runtime catalog (file)

When you **export** or **read** the catalog from cortex-core, you get one of these shapes.

### Export format (e.g. `export_catalog.py -o catalog.json`)

```json
{
  "source": "/path/to/model_catalog.json",
  "count": 42,
  "models": [
    {
      "code": "gemini-2.5-flash",
      "provider": "google",
      "model": "gemini-2.5-flash",
      "modality_in": "text,image,video,audio",
      "modality_out": "text",
      "context_tokens": 1048576,
      "capabilities": ["thinking", "function-calling", "code-execution"],
      "baseUrl": null,
      "role": "default"
    }
  ]
}
```

- **code**: Stable catalog id (use this in config).
- **provider**: `openai`, `google`, `ollama`, `xai`, etc.
- **model**: Provider’s model id (for API calls).
- **role**: Derived from capabilities: `small-text`, `large-text`, `vision`, `fast`, `local`, `default`.

### List-models output (MCP `cortex_list_models` or CLI)

Same per-model shape as above. Top-level: `{"count": N, "models": [...]}`.

### How to consume in your repo

- **Option A – File**: Run `python3 /path/to/cortex-core/export_catalog.py -o catalog.json` (or symlink cortex-core and run from there). At startup, read `catalog.json` and validate your config model names against `models[].code`; optionally pick by `role`.
- **Option B – Env**: Set `CORTEX_CATALOG_PATH` to the cortex-core `config/` directory (or path to `model_catalog.json`). Use `model_resolution.py`: `load_catalog()`, `validate_or_map()`, `get_by_role()`.

## 2. Scanner output contract (e.g. ai-model-scanner)

If your pipeline uses a **scanner** (e.g. ai-model-scanner) as the live view of "what’s on this machine," use the same contract so one parser works for both.

### Normalized scanner output (what to emit or parse)

Emit (or parse into) a JSON array of model entries that match this minimal shape:

```json
[
  { "code": "qwen-local", "provider": "ollama", "model": "qwen2.5:7b" },
  { "code": "gemini-2.5-flash", "provider": "google", "model": "gemini-2.5-flash" }
]
```

- **code**: Optional. If missing, use `model` as code.
- **provider**: Required (ollama, openai, google, etc.).
- **model**: Required (provider’s model id).

Extra fields (e.g. `capabilities`, `role`, `context_tokens`) are optional; cortex-core resolution can merge with catalog by `code` or `model` if you later want to combine scanner + catalog.

### Using scanner + catalog together

1. **Scanner as live list**: Run scanner → parse JSON array above → treat as "available right now."
2. **Catalog as SSoT**: Use cortex-core catalog (file or `model_resolution.load_catalog()`) for metadata (roles, capabilities, context_tokens). Match scanner entries to catalog by `code` or `model` + `provider`.
3. **Resolution**: At startup, load catalog; optionally run scanner; validate config model names against catalog (and scanner if you want "only what’s running"); resolve by role with `get_by_role(role)` from `model_resolution.py`.

## 3. Config convention in consuming repos

Suggested env or config:

```yaml
# Optional: where to read the catalog (file or directory containing model_catalog.json)
catalog_source: "file"   # or "ai-model-scanner"
catalog_path: "/path/to/cortex-core/config"   # or path to exported catalog.json

# Your preferred models (catalog codes)
providers:
  discovery:
    model: "gemini-2.5-flash"   # or role: "small-text"
  generation:
    model: "grok-4-fast-non-reasoning"   # or role: "large-text"
```

At startup: load catalog from `catalog_path`; validate `discovery.model` and `generation.model` against catalog (and scanner if used); if missing, warn or fall back by role using `model_resolution.get_by_role("small-text")` etc.
