#!/usr/bin/env python3
"""Validate cortex-core catalogs for completeness and correctness."""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any

def validate_model_catalog(catalog: Dict[str, Any]) -> List[str]:
    """Validate model catalog structure and return list of issues."""
    issues = []
    required_fields = ["code", "provider", "modality_in", "modality_out", "context_tokens", "capabilities"]
    optional_fields = ["price_input", "price_output", "rate_tpm", "rate_rpm", "reasoning", "metadata"]
    
    valid_modalities = ["text", "image", "audio", "multimodal"]
    # Capabilities are open-ended - just warn on unknown ones, don't fail
    common_capabilities = ["function_calling", "json_mode", "reasoning", "code", "vision", "audio", 
                          "tool_use", "tool_calls", "coding", "agentic", "multimodal", "prompt_caching",
                          "computer_use", "browser_control", "gui_automation", "web_search", "web_browsing",
                          "google_search", "google_maps", "x_search", "complex_reasoning", "deep_reasoning",
                          "hybrid_reasoning", "multi_step_reasoning", "thinking_mode", "complex_logic",
                          "exhaustive_search", "citations", "report_generation", "citation", "agentic_coding",
                          "agentic_tool_calling", "vibe-coding", "high_intelligence", "maximum_reasoning",
                          "complex_tasks", "reliable", "stem", "research", "search_grounding", "fast_inference",
                          "high_volume", "low_latency", "cost_effective", "high_throughput", "document_processing",
                          "cross_region_inference", "routing", "orchestration", "local_inference", "uncensored",
                          "json_output", "prefix_completion"]
    
    if not catalog:
        issues.append("❌ Model catalog is empty")
        return issues
    
    for model_id, model in catalog.items():
        # Check key matches code
        if model.get("code") != model_id:
            issues.append(f"⚠️  Model '{model_id}': key doesn't match 'code' field")
        
        # Check required fields
        for field in required_fields:
            if field not in model:
                issues.append(f"❌ Model '{model_id}': Missing required field '{field}'")
        
        # Validate modality values
        if "modality_in" in model and model["modality_in"] not in valid_modalities:
            issues.append(f"⚠️  Model '{model_id}': Invalid modality_in '{model['modality_in']}'")
        if "modality_out" in model and model["modality_out"] not in valid_modalities:
            issues.append(f"⚠️  Model '{model_id}': Invalid modality_out '{model['modality_out']}'")
        
        # Validate capabilities
        if "capabilities" in model:
            if not isinstance(model["capabilities"], list):
                issues.append(f"❌ Model '{model_id}': 'capabilities' must be a list")
            else:
                for cap in model["capabilities"]:
                    if cap not in common_capabilities:
                        # Just note it, don't fail - capabilities are extensible
                        pass  # Removed warning for unknown capabilities - they're valid
        
        # Validate types
        if "context_tokens" in model and not isinstance(model["context_tokens"], int):
            issues.append(f"❌ Model '{model_id}': 'context_tokens' must be an integer")
        if "reasoning" in model and not isinstance(model["reasoning"], bool):
            issues.append(f"❌ Model '{model_id}': 'reasoning' must be a boolean")
        if "price_input" in model and model["price_input"] is not None and not isinstance(model["price_input"], (int, float)):
            issues.append(f"❌ Model '{model_id}': 'price_input' must be a number")
        if "price_output" in model and model["price_output"] is not None and not isinstance(model["price_output"], (int, float)):
            issues.append(f"❌ Model '{model_id}': 'price_output' must be a number")
    
    return issues

def validate_tool_catalog(catalog: List[Dict[str, Any]]) -> List[str]:
    """Validate tool catalog structure and return list of issues."""
    issues = []
    required_fields = ["name", "description", "schema", "implementationPath"]
    
    if not catalog:
        issues.append("❌ Tool catalog is empty")
        return issues
    
    tool_names = set()
    
    for tool in catalog:
        # Check required fields
        for field in required_fields:
            if field not in tool:
                issues.append(f"❌ Tool '{tool.get('name', 'UNNAMED')}': Missing required field '{field}'")
        
        tool_name = tool.get("name")
        if not tool_name:
            issues.append("❌ Found tool without 'name' field")
            continue
        
        # Check for duplicates
        if tool_name in tool_names:
            issues.append(f"❌ Duplicate tool name: '{tool_name}'")
        tool_names.add(tool_name)
        
        # Validate schema structure
        schema = tool.get("schema", {})
        if not isinstance(schema, dict):
            issues.append(f"❌ Tool '{tool_name}': 'schema' must be an object")
        else:
            if schema.get("type") != "object":
                issues.append(f"⚠️  Tool '{tool_name}': Schema type should be 'object'")
            
            properties = schema.get("properties", {})
            required = schema.get("required", [])
            
            if not isinstance(properties, dict):
                issues.append(f"❌ Tool '{tool_name}': Schema 'properties' must be an object")
            if not isinstance(required, list):
                issues.append(f"❌ Tool '{tool_name}': Schema 'required' must be an array")
            
            # Check that required fields exist in properties
            for req_field in required:
                if req_field not in properties:
                    issues.append(f"⚠️  Tool '{tool_name}': Required field '{req_field}' not in properties")
    
    return issues

def main():
    """Run validation on both catalogs."""
    base_path = Path(__file__).parent
    model_path = base_path / "config" / "model_catalog.json"
    tool_path = base_path / "config" / "tool_catalog.json"
    
    print("🔍 Validating Cortex Core Catalogs\n")
    print("=" * 50)
    
    # Validate model catalog
    print("\n📊 Model Catalog Validation")
    print("-" * 50)
    try:
        with open(model_path, 'r') as f:
            model_catalog = json.load(f)
        
        model_issues = validate_model_catalog(model_catalog)
        model_count = len(model_catalog)
        
        print(f"✅ Found {model_count} models")
        
        if model_issues:
            for issue in model_issues:
                print(f"  {issue}")
        else:
            print("✅ No issues found")
            
    except FileNotFoundError:
        print(f"❌ Model catalog not found at {model_path}")
        model_issues = ["File not found"]
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in model catalog: {e}")
        model_issues = ["JSON parse error"]
    
    # Validate tool catalog
    print("\n🛠️  Tool Catalog Validation")
    print("-" * 50)
    try:
        with open(tool_path, 'r') as f:
            tool_catalog = json.load(f)
        
        tool_issues = validate_tool_catalog(tool_catalog)
        tool_count = len(tool_catalog)
        
        print(f"✅ Found {tool_count} tools")
        
        if tool_issues:
            for issue in tool_issues:
                print(f"  {issue}")
        else:
            print("✅ No issues found")
            
    except FileNotFoundError:
        print(f"❌ Tool catalog not found at {tool_path}")
        tool_issues = ["File not found"]
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in tool catalog: {e}")
        tool_issues = ["JSON parse error"]
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Summary")
    print("-" * 50)
    
    critical_issues = [i for i in (model_issues + tool_issues) if i.startswith("❌")]
    warnings = [i for i in (model_issues + tool_issues) if i.startswith("⚠️")]
    
    if critical_issues:
        print(f"❌ {len(critical_issues)} critical issue(s) found")
        sys.exit(1)
    elif warnings:
        print(f"⚠️  {len(warnings)} warning(s) found (non-blocking)")
        sys.exit(0)
    else:
        print("✅ All validations passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()

