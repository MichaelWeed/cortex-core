# Catalog Validation

This script validates all models and tools in the Cortex Core catalogs.

## Usage

```bash
python3 validate_catalog.py
```

## What It Does

1. **Model Validation**:
   - Checks for API keys per provider
   - Makes minimal test API calls to verify models work
   - Marks models as deprecated if they fail (404, etc.)
   - Skips entire providers if no API key is found

2. **Tool Validation**:
   - Validates tool schema structure
   - Checks for implementation files
   - Marks tools for review if issues found

3. **Backlog Creation**:
   - Creates backlog items for failed models/tools
   - Tracks issues in `backlog/validation_backlog.json`

4. **Reporting**:
   - Generates `validation_report.json` with full results
   - Updates model catalog with deprecation flags

## API Keys Required

Set these environment variables for full validation:

- `OPENAI_API_KEY` - OpenAI models
- `ANTHROPIC_API_KEY` - Anthropic/Claude models
- `GOOGLE_API_KEY` or `GEMINI_API_KEY` - Google models
- `XAI_API_KEY` or `GROK_API_KEY` - xAI/Grok models
- `DEEPSEEK_API_KEY` - DeepSeek models
- `PERPLEXITY_API_KEY` - Perplexity models
- `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` - Amazon Bedrock

Ollama is detected automatically if running locally.

## Output

- **validation_report.json**: Full validation results
- **backlog/validation_backlog.json**: Issues to address
- **config/model_catalog.json**: Updated with deprecation flags

