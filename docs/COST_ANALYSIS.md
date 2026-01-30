# Monthly Validation Summary

## Cost Breakdown

**Per Validation Run:**
- Models tested: ~20-30
- Tokens per test: 3-5 (input + output)
- Total tokens: ~100-150
- **Cost: < $0.01 per month**

**Annual Cost:**
- 12 runs × $0.01 = **< $0.12/year**

## Validation Strategy

The validator uses **ultra-minimal** test calls:
- Shortest possible prompts ("OK")
- Maximum 3 tokens in response
- Single confirmation test per model
- Just enough to verify the model exists and responds

## Monthly Workflow

1. **Run validation:**
   ```bash
   ./validate_monthly.sh
   ```

2. **Review results:**
   - Check `validation_report.json` for summary
   - Review `backlog/validation_backlog.json` for issues
   - Check `config/model_catalog.json` for new deprecations

3. **Take action:**
   - Remove deprecated models from projects
   - Fix tools marked for review
   - Update catalog as needed

## Automation

Set up monthly automation (see `MONTHLY_VALIDATION.md`):
- **macOS**: launchd (runs 1st of month at 2 AM)
- **Linux**: cron job
- **Manual**: Calendar reminder

## Benefits

✅ **Automatic deprecation tracking** - Models marked when they fail
✅ **Tool health monitoring** - Implementation status tracked
✅ **Minimal cost** - < $0.01 per month
✅ **Early detection** - Catch issues before they affect projects
✅ **Historical tracking** - Reports saved with timestamps

