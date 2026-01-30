#!/usr/bin/env python3
"""
Cortex Core Catalog Validator
Validates all models and tools in the catalogs, marks deprecated items,
and creates backlog items for issues.
"""

import json
import os
import sys
import urllib.request
import urllib.error
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Configuration
BASE_DIR = Path(__file__).parent.parent
MODEL_CATALOG = BASE_DIR / "config" / "model_catalog.json"
TOOL_CATALOG = BASE_DIR / "config" / "tool_catalog.json"
BACKLOG_DIR = BASE_DIR / "backlog"
BACKLOG_FILE = BACKLOG_DIR / "validation_backlog.json"
VALIDATION_REPORT = BASE_DIR / "validation_report.json"

# Provider API Key mappings
PROVIDER_KEYS = {
    "OpenAI": ["OPENAI_API_KEY"],
    "Anthropic": ["ANTHROPIC_API_KEY"],
    "Google": ["GOOGLE_API_KEY", "GEMINI_API_KEY"],
    "xAI": ["XAI_API_KEY", "GROK_API_KEY"],
    "DeepSeek": ["DEEPSEEK_API_KEY"],
    "Perplexity": ["PERPLEXITY_API_KEY"],
    "Amazon": ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"],
    "Ollama": []  # No API key needed for local
}

# Model test prompts (minimal, cheap - designed for monthly validation)
# Using absolute minimum tokens to keep costs < $0.01 per month
MODEL_TEST_PROMPTS = {
    "default": "OK",  # Shortest possible - just confirmation
    "reasoning": "2",  # Single token response
    "coding": "ok"     # Minimal confirmation
}

class CatalogValidator:
    def __init__(self):
        self.models = self.load_json(MODEL_CATALOG)
        self.tools = self.load_json(TOOL_CATALOG)
        self.backlog = self.load_backlog()
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "models": {"tested": 0, "passed": 0, "failed": 0, "skipped": 0, "deprecated": []},
            "tools": {"tested": 0, "passed": 0, "failed": 0, "skipped": 0, "needs_review": []},
            "providers_skipped": []
        }
        
    def load_json(self, path: Path) -> dict:
        """Load JSON file."""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Error: Could not find {path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ Error: Invalid JSON in {path}: {e}")
            return {}
    
    def load_backlog(self) -> List[Dict]:
        """Load or create backlog."""
        BACKLOG_DIR.mkdir(exist_ok=True)
        if BACKLOG_FILE.exists():
            try:
                with open(BACKLOG_FILE, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_backlog(self):
        """Save backlog to file."""
        with open(BACKLOG_FILE, 'w') as f:
            json.dump(self.backlog, f, indent=2)
    
    def has_api_key(self, provider: str) -> bool:
        """Check if API key exists for provider."""
        if provider == "Ollama":
            # Check if Ollama is running locally
            try:
                req = urllib.request.Request("http://localhost:11434/api/tags")
                with urllib.request.urlopen(req, timeout=2) as response:
                    return response.status == 200
            except:
                return False
        
        keys = PROVIDER_KEYS.get(provider, [])
        if not keys:
            return True  # No key needed
        
        return any(os.getenv(key) for key in keys)
    
    def test_model(self, model_id: str, model_def: Dict) -> Tuple[str, Optional[str]]:
        """
        Test a model with minimal API call.
        Returns: (status, error_message)
        Status: "PASS", "FAIL", "SKIP", "DEPRECATED"
        """
        provider = model_def.get("provider", "Unknown")
        
        # Check API key
        if not self.has_api_key(provider):
            return "SKIP", f"No API key for {provider}"
        
        # Skip if already marked deprecated
        if model_def.get("deprecated", False):
            return "SKIP", "Already marked as deprecated"
        
        # Test based on provider
        try:
            if provider == "Ollama":
                return self.test_ollama_model(model_id, model_def)
            elif provider == "OpenAI":
                return self.test_openai_model(model_id, model_def)
            elif provider == "Anthropic":
                return self.test_anthropic_model(model_id, model_def)
            elif provider == "Google":
                return self.test_google_model(model_id, model_def)
            elif provider == "xAI":
                return self.test_xai_model(model_id, model_def)
            elif provider == "DeepSeek":
                return self.test_deepseek_model(model_id, model_def)
            elif provider == "Perplexity":
                return self.test_perplexity_model(model_id, model_def)
            elif provider == "Amazon":
                return self.test_amazon_model(model_id, model_def)
            else:
                return "SKIP", f"Unknown provider: {provider}"
        except Exception as e:
            return "FAIL", str(e)
    
    def test_ollama_model(self, model_id: str, model_def: Dict) -> Tuple[str, Optional[str]]:
        """Test Ollama model."""
        try:
            prompt = MODEL_TEST_PROMPTS.get("default", "Say OK")
            payload = {
                "model": model_id,
                "prompt": prompt,
                "stream": False
            }
            req = urllib.request.Request(
                "http://localhost:11434/api/generate",
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    return "PASS", None
                else:
                    return "FAIL", f"HTTP {response.status}"
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return "DEPRECATED", "Model not found in Ollama"
            return "FAIL", f"HTTP {e.code}: {e.reason}"
        except Exception as e:
            return "FAIL", str(e)
    
    def test_openai_model(self, model_id: str, model_def: Dict) -> Tuple[str, Optional[str]]:
        """Test OpenAI model with minimal call."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "SKIP", "No API key"
        
        try:
            payload = {
                "model": model_id,
                "messages": [{"role": "user", "content": MODEL_TEST_PROMPTS["default"]}],
                "max_tokens": 3  # Absolute minimum - just need confirmation
            }
            req = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions",
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {api_key}'
                }
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    return "PASS", None
                elif response.status == 404:
                    return "DEPRECATED", "Model not found"
                else:
                    data = json.load(response)
                    return "FAIL", data.get("error", {}).get("message", f"HTTP {response.status}")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return "DEPRECATED", "Model not found"
            error_data = json.loads(e.read().decode())
            return "FAIL", error_data.get("error", {}).get("message", str(e))
        except Exception as e:
            return "FAIL", str(e)
    
    def test_anthropic_model(self, model_id: str, model_def: Dict) -> Tuple[str, Optional[str]]:
        """Test Anthropic model."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return "SKIP", "No API key"
        
        try:
            payload = {
                "model": model_id,
                "max_tokens": 3,  # Absolute minimum - just need confirmation
                "messages": [{"role": "user", "content": MODEL_TEST_PROMPTS["default"]}]
            }
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'x-api-key': api_key,
                    'anthropic-version': '2023-06-01'
                }
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    return "PASS", None
                elif response.status == 404:
                    return "DEPRECATED", "Model not found"
                else:
                    return "FAIL", f"HTTP {response.status}"
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return "DEPRECATED", "Model not found"
            return "FAIL", f"HTTP {e.code}"
        except Exception as e:
            return "FAIL", str(e)
    
    def test_google_model(self, model_id: str, model_def: Dict) -> Tuple[str, Optional[str]]:
        """Test Google/Gemini model."""
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "SKIP", "No API key"
        
        try:
            # Use Gemini API
            model_name = model_id.replace("gemini-", "").replace("-", "-")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            payload = {
                "contents": [{"parts": [{"text": MODEL_TEST_PROMPTS["default"]}]}]
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    return "PASS", None
                elif response.status == 404:
                    return "DEPRECATED", "Model not found"
                else:
                    return "FAIL", f"HTTP {response.status}"
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return "DEPRECATED", "Model not found"
            return "FAIL", f"HTTP {e.code}"
        except Exception as e:
            return "FAIL", str(e)
    
    def test_xai_model(self, model_id: str, model_def: Dict) -> Tuple[str, Optional[str]]:
        """Test xAI/Grok model."""
        api_key = os.getenv("XAI_API_KEY") or os.getenv("GROK_API_KEY")
        if not api_key:
            return "SKIP", "No API key"
        
        try:
            payload = {
                "model": model_id,
                "messages": [{"role": "user", "content": MODEL_TEST_PROMPTS["default"]}],
                "max_tokens": 3  # Absolute minimum - just need confirmation
            }
            req = urllib.request.Request(
                "https://api.x.ai/v1/chat/completions",
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {api_key}'
                }
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    return "PASS", None
                elif response.status == 404:
                    return "DEPRECATED", "Model not found"
                else:
                    return "FAIL", f"HTTP {response.status}"
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return "DEPRECATED", "Model not found"
            return "FAIL", f"HTTP {e.code}"
        except Exception as e:
            return "FAIL", str(e)
    
    def test_deepseek_model(self, model_id: str, model_def: Dict) -> Tuple[str, Optional[str]]:
        """Test DeepSeek model."""
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            return "SKIP", "No API key"
        
        try:
            payload = {
                "model": model_id,
                "messages": [{"role": "user", "content": MODEL_TEST_PROMPTS["default"]}],
                "max_tokens": 3  # Absolute minimum - just need confirmation
            }
            req = urllib.request.Request(
                "https://api.deepseek.com/v1/chat/completions",
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {api_key}'
                }
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    return "PASS", None
                elif response.status == 404:
                    return "DEPRECATED", "Model not found"
                else:
                    return "FAIL", f"HTTP {response.status}"
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return "DEPRECATED", "Model not found"
            return "FAIL", f"HTTP {e.code}"
        except Exception as e:
            return "FAIL", str(e)
    
    def test_perplexity_model(self, model_id: str, model_def: Dict) -> Tuple[str, Optional[str]]:
        """Test Perplexity model."""
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            return "SKIP", "No API key"
        
        try:
            payload = {
                "model": model_id,
                "messages": [{"role": "user", "content": MODEL_TEST_PROMPTS["default"]}],
                "max_tokens": 3  # Absolute minimum - just need confirmation
            }
            req = urllib.request.Request(
                "https://api.perplexity.ai/chat/completions",
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {api_key}'
                }
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    return "PASS", None
                elif response.status == 404:
                    return "DEPRECATED", "Model not found"
                else:
                    return "FAIL", f"HTTP {response.status}"
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return "DEPRECATED", "Model not found"
            return "FAIL", f"HTTP {e.code}"
        except Exception as e:
            return "FAIL", str(e)
    
    def test_amazon_model(self, model_id: str, model_def: Dict) -> Tuple[str, Optional[str]]:
        """Test Amazon Bedrock model."""
        # AWS requires boto3, skip for now or use CLI
        return "SKIP", "AWS Bedrock requires boto3 SDK"
    
    def validate_tool(self, tool_def: Dict) -> Tuple[str, Optional[str]]:
        """
        Validate a tool definition.
        Returns: (status, error_message)
        Status: "PASS", "FAIL", "NEEDS_REVIEW"
        """
        # Check required fields
        if "name" not in tool_def:
            return "FAIL", "Missing 'name' field"
        if "schema" not in tool_def:
            return "NEEDS_REVIEW", "Missing 'schema' field"
        
        # Validate schema structure
        schema = tool_def.get("schema", {})
        if not isinstance(schema, dict):
            return "FAIL", "Schema must be an object"
        
        # Check implementation path
        impl_path = tool_def.get("implementationPath", "")
        if impl_path:
            # Resolve relative to config/
            impl_name = Path(impl_path).name
            real_path = BASE_DIR / "tools" / impl_name
            if not real_path.exists() and not real_path.with_suffix('.py').exists():
                return "NEEDS_REVIEW", f"Implementation not found: {impl_path}"
        
        return "PASS", None
    
    def mark_deprecated(self, model_id: str, reason: str):
        """Mark model as deprecated in catalog."""
        if model_id in self.models:
            self.models[model_id]["deprecated"] = True
            self.models[model_id]["deprecated_reason"] = reason
            self.models[model_id]["deprecated_date"] = datetime.now().isoformat()
            print(f"  ⚠️  Marked {model_id} as deprecated: {reason}")
    
    def add_backlog_item(self, item_type: str, identifier: str, issue: str, priority: str = "medium"):
        """Add item to backlog."""
        item = {
            "id": len(self.backlog) + 1,
            "type": item_type,  # "model" or "tool"
            "identifier": identifier,
            "issue": issue,
            "priority": priority,
            "created": datetime.now().isoformat(),
            "status": "open"
        }
        self.backlog.append(item)
    
    def validate_all_models(self):
        """Validate all models in catalog."""
        print("\n" + "="*60)
        print("🧠 VALIDATING MODELS")
        print("="*60)
        
        providers_checked = set()
        
        for model_id, model_def in self.models.items():
            provider = model_def.get("provider", "Unknown")
            
            # Skip entire provider if no API key (first time only)
            if provider not in providers_checked:
                providers_checked.add(provider)
                if not self.has_api_key(provider):
                    print(f"\n⏭️  Skipping {provider} (no API key)")
                    self.report["providers_skipped"].append(provider)
                    continue
            
            self.report["models"]["tested"] += 1
            print(f"\n🔍 Testing: {model_id} ({provider})")
            
            status, error = self.test_model(model_id, model_def)
            
            if status == "PASS":
                self.report["models"]["passed"] += 1
                print(f"  ✅ PASS")
            elif status == "SKIP":
                self.report["models"]["skipped"] += 1
                print(f"  ⏭️  SKIP: {error}")
            elif status == "DEPRECATED":
                self.report["models"]["deprecated"].append(model_id)
                self.mark_deprecated(model_id, error or "Model test failed")
                self.add_backlog_item("model", model_id, f"Deprecated: {error}", "high")
                print(f"  ⚠️  DEPRECATED: {error}")
            else:  # FAIL
                self.report["models"]["failed"] += 1
                self.add_backlog_item("model", model_id, f"Test failed: {error}", "high")
                print(f"  ❌ FAIL: {error}")
    
    def validate_all_tools(self):
        """Validate all tools in catalog."""
        print("\n" + "="*60)
        print("🛠️  VALIDATING TOOLS")
        print("="*60)
        
        for tool_def in self.tools:
            tool_name = tool_def.get("name", "unknown")
            self.report["tools"]["tested"] += 1
            print(f"\n🔍 Testing: {tool_name}")
            
            status, error = self.validate_tool(tool_def)
            
            if status == "PASS":
                self.report["tools"]["passed"] += 1
                print(f"  ✅ PASS")
            elif status == "NEEDS_REVIEW":
                self.report["tools"]["needs_review"].append(tool_name)
                self.add_backlog_item("tool", tool_name, error or "Needs review", "medium")
                print(f"  ⚠️  NEEDS REVIEW: {error}")
            else:  # FAIL
                self.report["tools"]["failed"] += 1
                self.add_backlog_item("tool", tool_name, error or "Validation failed", "high")
                print(f"  ❌ FAIL: {error}")
    
    def save_catalogs(self):
        """Save updated catalogs with deprecation flags."""
        with open(MODEL_CATALOG, 'w') as f:
            json.dump(self.models, f, indent=2)
        print(f"\n💾 Saved updated model catalog")
    
    def save_report(self):
        """Save validation report."""
        with open(VALIDATION_REPORT, 'w') as f:
            json.dump(self.report, f, indent=2)
        print(f"💾 Saved validation report to {VALIDATION_REPORT}")
    
    def run(self):
        """Run full validation."""
        print("🚀 Cortex Core Catalog Validator")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        self.validate_all_models()
        self.validate_all_tools()
        
        # Save results
        self.save_catalogs()
        self.save_backlog()
        self.save_report()
        
        # Print summary
        print("\n" + "="*60)
        print("📊 VALIDATION SUMMARY")
        print("="*60)
        print(f"\nModels: {self.report['models']['passed']} passed, "
              f"{self.report['models']['failed']} failed, "
              f"{self.report['models']['skipped']} skipped, "
              f"{len(self.report['models']['deprecated'])} deprecated")
        print(f"Tools: {self.report['tools']['passed']} passed, "
              f"{self.report['tools']['failed']} failed, "
              f"{len(self.report['tools']['needs_review'])} need review")
        print(f"\nProviders skipped: {', '.join(self.report['providers_skipped']) or 'None'}")
        print(f"\nBacklog items created: {len(self.backlog)}")
        print(f"\n📄 Full report: {VALIDATION_REPORT}")
        print(f"📋 Backlog: {BACKLOG_FILE}")

if __name__ == "__main__":
    validator = CatalogValidator()
    validator.run()

