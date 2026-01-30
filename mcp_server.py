#!/usr/bin/env python3
"""
MCP Server for Cortex Core
Exposes all tools from tool_catalog.json as MCP tools.
"""

import json
import sys
import subprocess
import importlib.util
from pathlib import Path
from typing import Any, Dict, List

BASE_DIR = Path(__file__).parent
TOOL_CATALOG = BASE_DIR / "config" / "tool_catalog.json"

def load_tool_catalog() -> List[Dict[str, Any]]:
    """Load the tool catalog."""
    with open(TOOL_CATALOG, 'r') as f:
        return json.load(f)

def get_tool_implementation(tool: Dict[str, Any]) -> Path:
    """Get the path to a tool's implementation."""
    impl_path = tool.get("implementationPath", "")
    if impl_path.startswith("../"):
        impl_path = impl_path.replace("../", "")
    return BASE_DIR / impl_path / "index.py"

def call_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Call a tool implementation with given arguments."""
    catalog = load_tool_catalog()
    
    # Find the tool
    tool = None
    for t in catalog:
        if t.get("name") == tool_name:
            tool = t
            break
    
    if not tool:
        return {"error": f"Tool '{tool_name}' not found"}
    
    # Get implementation path
    impl_path = get_tool_implementation(tool)
    if not impl_path.exists():
        return {"error": f"Implementation not found at {impl_path}"}
    
    # Call the tool
    try:
        # Import and call the tool's main function
        spec = importlib.util.spec_from_file_location("tool_module", impl_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Call main() with arguments unpacked
        if hasattr(module, 'main'):
            result = module.main(**arguments)
            return result if isinstance(result, dict) else {"result": result}
        else:
            return {"error": "Tool implementation missing main() function"}
    except Exception as e:
        return {"error": str(e)}

def list_tools() -> List[Dict[str, Any]]:
    """List all available tools in MCP format."""
    catalog = load_tool_catalog()
    mcp_tools = []
    
    for tool in catalog:
        mcp_tool = {
            "name": tool["name"],
            "description": tool["description"],
            "inputSchema": tool["schema"]
        }
        mcp_tools.append(mcp_tool)
    
    return mcp_tools

# JSON-RPC 2.0 constants
JSONRPC_VERSION = "2.0"

def make_result_response(req_id: Any, result: Dict[str, Any]) -> Dict[str, Any]:
    """Build a JSON-RPC 2.0 success response."""
    return {"jsonrpc": JSONRPC_VERSION, "id": req_id, "result": result}


def make_error_response(req_id: Any, code: int, message: str) -> Dict[str, Any]:
    """Build a JSON-RPC 2.0 error response (error must be an object)."""
    return {"jsonrpc": JSONRPC_VERSION, "id": req_id, "error": {"code": code, "message": message}}


def handle_mcp_request(method: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle an MCP method; returns the result payload (no envelope)."""
    if method == "initialize":
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "cortex-core", "version": "1.0.0"},
        }
    if method == "tools/list":
        return {"tools": list_tools()}
    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments") or {}
        result = call_tool(tool_name, arguments)
        return {"content": [{"type": "text", "text": json.dumps(result)}]}
    raise ValueError(f"Unknown method: {method}")


if __name__ == "__main__":
    # Stdio JSON-RPC 2.0 server: only write single JSON lines to stdout
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        req_id = None
        try:
            msg = json.loads(line)
            req_id = msg.get("id")
            method = msg.get("method")
            params = msg.get("params") or {}

            # Notifications have no id; do not send a response
            if method and "id" not in msg:
                continue

            if not method:
                out = make_error_response(req_id, -32600, "Missing method")
            else:
                result = handle_mcp_request(method, params)
                out = make_result_response(req_id, result)
        except json.JSONDecodeError:
            out = make_error_response(req_id, -32700, "Parse error")
        except Exception as e:
            out = make_error_response(req_id, -32603, str(e))

        # Only one JSON object per response, no extra prints
        print(json.dumps(out), flush=True)
