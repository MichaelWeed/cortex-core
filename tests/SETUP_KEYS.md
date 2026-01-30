# Setting Up API Keys for Validation

## Quick Setup

1. **Create a `.env` file** (copy from template):
   ```bash
   cp .env.template .env
   ```

2. **Edit `.env`** and add your actual API keys:
   ```bash
   nano .env  # or use your preferred editor
   ```

3. **Run validation** with environment loaded:
   ```bash
   ./validate_monthly.sh
   ```

## Alternative: Set Environment Variables Directly

You can also set environment variables in your current shell session:

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="..."
# etc.

cd tests
python3 validate_catalog.py
```

## Or Use a One-Liner

```bash
export OPENAI_API_KEY="sk-..." && export ANTHROPIC_API_KEY="sk-ant-..." && cd tests && python3 validate_catalog.py
```

## Security Notes

- ✅ `.env` is in `.gitignore` - your keys won't be committed
- ✅ Never commit API keys to git
- ✅ The validator only makes minimal test calls (5 tokens max)
- ✅ Keys are only used for validation, not stored

## What Gets Tested

Once keys are set, the validator will:
- Test all models from providers with API keys
- Skip providers without keys (graceful)
- Mark deprecated models automatically
- Create backlog items for issues

