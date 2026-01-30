#!/bin/bash
# Monthly Catalog Validation Runner
# Run this monthly to validate all models and tools

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

# Load .env if it exists
if [ -f .env ]; then
    echo "📝 Loading API keys from .env..."
    set -a  # automatically export all variables
    source .env
    set +a
else
    echo "⚠️  No .env file found."
    echo "   Create one from .env.template: cp .env.template .env"
    echo "   Then add your API keys to .env"
    echo ""
    echo "   Continuing with system environment variables only..."
fi

# Run validation
echo "🚀 Running monthly catalog validation..."
echo "📅 $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

cd tests
python3 validate_catalog.py

# Show summary
echo ""
echo "✅ Validation complete!"
echo ""
echo "📊 Check these files for results:"
echo "   - validation_report.json (full results)"
echo "   - backlog/validation_backlog.json (issues to fix)"
echo "   - config/model_catalog.json (updated with deprecations)"
echo ""

