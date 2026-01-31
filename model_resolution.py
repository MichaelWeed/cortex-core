"""
Lightweight model resolution for pipelines: load catalog (file or env), validate config
model names, pick by role. Copy this file into your repo or set CORTEX_CATALOG_PATH.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Default: same repo layout; override with CORTEX_CATALOG_PATH (file or dir to config/)
def _catalog_path(catalog_path: Optional[str] = None) -> Path:
    path = catalog_path or os.environ.get("CORTEX_CATALOG_PATH")
    if path:
        p = Path(path)
        if p.is_file():
            return p
        p = p / "model_catalog.json"
        if p.is_file():
            return p
    # Fallback: assume we're inside cortex-core or a sibling
    base = Path(__file__).resolve().parent
    default = base / "config" / "model_catalog.json"
    if default.is_file():
        return default
    return base / "model_catalog.json"


def load_catalog(catalog_path: Optional[str] = None) -> Dict[str, Any]:
    """Load the model catalog (SSoT). Pass path or set CORTEX_CATALOG_PATH."""
    with open(_catalog_path(catalog_path), "r") as f:
        return json.load(f)


def _is_deprecated(model: Dict[str, Any]) -> bool:
    return bool(model.get("_deprecated") or model.get("deprecated"))


def _role_for(model: Dict[str, Any]) -> str:
    caps = model.get("capabilities") or []
    if "reasoning" in caps or "long-context" in caps:
        return "large-text"
    if "vision" in caps or "image-generation" in caps:
        return "vision"
    if "fast" in caps and "local" in caps:
        return "small-text"
    if "fast" in caps:
        return "fast"
    if "local" in caps:
        return "local"
    return "default"


def available_models(
    catalog_path: Optional[str] = None,
    include_deprecated: bool = False,
) -> List[Dict[str, Any]]:
    """List models from catalog with optional role; exclude deprecated unless requested."""
    raw = load_catalog(catalog_path)
    out = []
    for code, m in raw.items():
        if not include_deprecated and _is_deprecated(m):
            continue
        out.append({
            "code": code,
            "provider": m.get("provider"),
            "model": m.get("model"),
            "capabilities": m.get("capabilities"),
            "modality_in": m.get("modality_in"),
            "modality_out": m.get("modality_out"),
            "context_tokens": m.get("context_tokens"),
            "baseUrl": m.get("baseUrl"),
            "role": _role_for(m),
        })
    return out


def validate_or_map(
    requested_models: List[str],
    catalog_path: Optional[str] = None,
) -> Tuple[List[str], List[str], Dict[str, str]]:
    """
    Validate requested model names (catalog codes) against catalog.
    Returns (valid, missing, code_to_model). Use code_to_model to resolve code -> provider model id.
    """
    catalog = load_catalog(catalog_path)
    code_to_model = {
        code: m.get("model", code)
        for code, m in catalog.items()
        if not _is_deprecated(m)
    }
    valid = [n for n in requested_models if n in catalog and not _is_deprecated(catalog.get(n, {}))]
    missing = [n for n in requested_models if n not in valid]
    return valid, missing, code_to_model


def get_by_capability(
    capability: str,
    catalog_path: Optional[str] = None,
    include_deprecated: bool = False,
) -> List[Dict[str, Any]]:
    """Return all models that have this capability (e.g. 'vision', 'fast', 'local')."""
    models = available_models(catalog_path=catalog_path, include_deprecated=include_deprecated)
    return [m for m in models if capability in (m.get("capabilities") or [])]


def get_by_role(
    role: str,
    catalog_path: Optional[str] = None,
    prefer_provider: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Return first model matching role (e.g. 'small-text', 'large-text', 'vision')."""
    models = available_models(catalog_path=catalog_path)
    candidates = [m for m in models if m.get("role") == role]
    if prefer_provider:
        by_provider = [m for m in candidates if m.get("provider") == prefer_provider]
        if by_provider:
            return by_provider[0]
    return candidates[0] if candidates else None


def resolve_preferred(
    preferred_code: str,
    role_fallback: Optional[str] = None,
    catalog_path: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Resolve preferred model by code; if not in catalog or deprecated, fall back to role.
    Returns full model entry (code, provider, model, ...) or None.
    """
    catalog = load_catalog(catalog_path)
    if preferred_code in catalog and not _is_deprecated(catalog[preferred_code]):
        m = catalog[preferred_code].copy()
        m["code"] = preferred_code
        m["role"] = _role_for(m)
        return m
    if role_fallback:
        return get_by_role(role_fallback, catalog_path=catalog_path)
    return None
