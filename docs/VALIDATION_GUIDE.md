# Monthly Catalog Validation

This script validates all models and tools in the Cortex Core catalogs with minimal API usage.

## Cost Estimate

**Per validation run (monthly):**
- ~20-30 models tested
- ~5 tokens per test (minimal prompt)
- **Total: ~100-150 tokens per month**
- **Cost: < $0.01 per month** (even with expensive models)

The validator uses the absolute minimum:
- Shortest possible prompts ("Say 'OK'")
- Maximum 5 tokens in response
- Single test per model

## Setup (One-Time)

1. **Create `.env` file:**
   ```bash
   cp .env.template .env
   ```

2. **Add your API keys to `.env`:**
   ```bash
   nano .env  # Add your actual keys
   ```

3. **Verify `.env` is ignored by git:**
   ```bash
   git check-ignore .env  # Should output: .env
   ```

## Monthly Validation

### Option 1: Manual Run
```bash
./validate_monthly.sh
```

### Option 2: Automated (Cron)
Add to your crontab for monthly runs:
```bash
crontab -e
```

Add this line (runs on 1st of each month at 2 AM):
```
0 2 1 * * cd /path/to/cortex-core && ./validate_monthly.sh >> logs/validation.log 2>&1
```

### Option 3: Calendar Reminder
Set a monthly reminder in your calendar to run:
```bash
./validate_monthly.sh
```

## What Gets Tracked

- **Deprecated Models**: Automatically marked in catalog
- **Failed Tests**: Added to backlog
- **Missing Implementations**: Tools marked for review
- **Validation History**: Reports saved with timestamps

## Output Files

- `validation_report.json` - Full validation results
- `backlog/validation_backlog.json` - Issues to address
- `config/model_catalog.json` - Updated with deprecation flags

## Example Output

```
🚀 Cortex Core Catalog Validator
📅 2025-12-06 20:04:27

🧠 VALIDATING MODELS
  ✅ huihui_ai/orchestrator-abliterated:latest: PASS
  ✅ gpt-4.1: PASS
  ⚠️  old-model-v1: DEPRECATED (Model not found)
  
🛠️  VALIDATING TOOLS
  ✅ file_read: PASS
  ⚠️  old_tool: NEEDS REVIEW (Implementation not found)

📊 VALIDATION SUMMARY
Models: 25 passed, 1 failed, 3 skipped, 1 deprecated
Tools: 15 passed, 0 failed, 2 need review
```

## Troubleshooting

**"No API key" errors:**
- Check your `.env` file has the correct variable names
- Verify keys are valid (not expired)
- Some providers may need different key names (see `.env.template`)

**Models failing:**
- May indicate model is deprecated by provider
- Check provider documentation for model status
- Failed models are automatically marked deprecated

**High costs:**
- The validator uses minimal tokens (5 max per test)
- If costs are high, check for API key leaks
- Review `validation_report.json` for unexpected calls

