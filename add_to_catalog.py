#!/usr/bin/env python3
"""
Quick script to add models or tools to cortex-core catalogs.
Usage:
  python3 add_to_catalog.py model <model_id> <json_data>
  python3 add_to_catalog.py tool <json_data>
  
Or pipe JSON:
  echo '{"code":"test-model",...}' | python3 add_to_catalog.py model test-model
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, Any

BASE_DIR = Path(__file__).parent
MODEL_CATALOG = BASE_DIR / "config" / "model_catalog.json"
TOOL_CATALOG = BASE_DIR / "config" / "tool_catalog.json"

def load_json_file(path: Path) -> Any:
    """Load JSON file, return empty dict/list if not exists."""
    if not path.exists():
        return {} if "model" in str(path) else []
    with open(path, 'r') as f:
        return json.load(f)

def save_json_file(path: Path, data: Any, indent: int = 2):
    """Save JSON file with proper formatting."""
    with open(path, 'w') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
        f.write('\n')

def add_model(model_id: str, model_data: Dict[str, Any]) -> bool:
    """Add or update a model in the catalog."""
    catalog = load_json_file(MODEL_CATALOG)
    
    # Ensure code matches model_id
    model_data["code"] = model_id
    
    # Check required fields
    required = ["provider", "modality_in", "modality_out", "context_tokens", "capabilities"]
    missing = [f for f in required if f not in model_data]
    if missing:
        print(f"❌ Missing required fields: {', '.join(missing)}")
        return False
    
    # Add/update model
    catalog[model_id] = model_data
    save_json_file(MODEL_CATALOG, catalog)
    
    print(f"✅ Added model '{model_id}' to catalog")
    return True

def add_tool(tool_data: Dict[str, Any]) -> bool:
    """Add a tool to the catalog."""
    catalog = load_json_file(TOOL_CATALOG)
    
    # Check required fields
    required = ["name", "description", "schema", "implementationPath"]
    missing = [f for f in required if f not in tool_data]
    if missing:
        print(f"❌ Missing required fields: {', '.join(missing)}")
        return False
    
    tool_name = tool_data["name"]
    
    # Check for duplicates
    existing_names = [t.get("name") for t in catalog if isinstance(t, dict)]
    if tool_name in existing_names:
        print(f"⚠️  Tool '{tool_name}' already exists. Updating...")
        # Remove old entry
        catalog = [t for t in catalog if t.get("name") != tool_name]
    
    # Add new tool
    catalog.append(tool_data)
    save_json_file(TOOL_CATALOG, catalog)
    
    print(f"✅ Added tool '{tool_name}' to catalog")
    return True

def main():
    parser = argparse.ArgumentParser(description="Add models or tools to cortex-core catalogs")
    parser.add_argument("type", choices=["model", "tool"], help="Type: model or tool")
    parser.add_argument("data", help="JSON data (or '-' to read from stdin)")
    parser.add_argument("--model-id", help="Model ID (required for models, inferred from code if not provided)")
    
    args = parser.parse_args()
    
    # Read JSON data
    if args.data == "-":
        json_str = sys.stdin.read()
    else:
        json_str = args.data
    
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return 1
    
    # Handle model or tool
    if args.type == "model":
        model_id = args.model_id or data.get("code")
        if not model_id:
            print("❌ Model ID required (use --model-id or include 'code' in JSON)")
            return 1
        success = add_model(model_id, data)
    else:  # tool
        success = add_tool(data)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
