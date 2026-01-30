#!/usr/bin/env python3
"""
MCP tool implementation for adding models/tools to cortex-core catalogs.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path to import add_to_catalog
BASE_DIR = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from add_to_catalog import add_model, add_tool

def main(type: str, data: dict, model_id: str = None):
    """
    Add a model or tool to the catalog.
    
    Args:
        type: "model" or "tool"
        data: Dictionary with model/tool definition
        model_id: Optional model ID (for models)
    
    Returns:
        dict with success status and message
    """
    try:
        if type == "model":
            model_id = model_id or data.get("code")
            if not model_id:
                return {
                    "success": False,
                    "error": "Model ID required (provide model_id or include 'code' in data)"
                }
            success = add_model(model_id, data)
            return {
                "success": success,
                "message": f"Model '{model_id}' added successfully" if success else "Failed to add model"
            }
        else:  # tool
            success = add_tool(data)
            tool_name = data.get("name", "unknown")
            return {
                "success": success,
                "message": f"Tool '{tool_name}' added successfully" if success else "Failed to add tool"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    # CLI usage
    if len(sys.argv) < 3:
        print("Usage: python3 index.py <type> <json_data> [model_id]")
        sys.exit(1)
    
    type_arg = sys.argv[1]
    data_str = sys.argv[2]
    model_id_arg = sys.argv[3] if len(sys.argv) > 3 else None
    
    data = json.loads(data_str)
    result = main(type_arg, data, model_id_arg)
    
    print(json.dumps(result, indent=2))
