#!/usr/bin/env python3
"""
MCP tool implementation for listing models from cortex-core catalogs.
Supports CORTEX_CATALOG_PATH so other projects can point to a symlinked catalog.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List

BASE_DIR = Path(__file__).parent.parent.parent.parent
DEFAULT_MODEL_CATALOG = BASE_DIR / "config" / "model_catalog.json"


def _catalog_path() -> Path:
    path = os.environ.get("CORTEX_CATALOG_PATH")
    if path:
        p = Path(path)
        if p.is_file():
            return p
        p = p / "model_catalog.json"
        if p.is_file():
            return p
    return DEFAULT_MODEL_CATALOG


def _load_model_catalog() -> Dict[str, Any]:
    with open(_catalog_path(), "r") as f:
        return json.load(f)


def _split_csv(value: str) -> List[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def _matches_modalities(value: str, required: str) -> bool:
    if not required:
        return True
    required_list = _split_csv(required)
    value_list = _split_csv(value or "")
    return all(req in value_list for req in required_list)


def _is_deprecated(model: Dict[str, Any]) -> bool:
    return bool(model.get("_deprecated") or model.get("deprecated"))


def _role_for(model: Dict[str, Any]) -> str:
    """Derive role from capabilities for pipeline selection (small-text, large-text, vision)."""
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


def main(
    provider: str = None,
    capability: str = None,
    modality_in: str = None,
    modality_out: str = None,
    include_deprecated: bool = False,
    format: str = "summary",
):
    """
    List models from the catalog with optional filtering.

    Args:
        provider: Filter by provider (e.g., "openai", "google")
        capability: Filter by capability (e.g., "vision")
        modality_in: Required input modalities (comma-separated)
        modality_out: Required output modalities (comma-separated)
        include_deprecated: Include deprecated models
        format: "summary", "full", or "codes"

    Returns:
        dict with count and models list
    """
    catalog = _load_model_catalog()
    results: List[Dict[str, Any]] = []

    for model_id, model in catalog.items():
        if not include_deprecated and _is_deprecated(model):
            continue
        if provider and model.get("provider") != provider:
            continue
        if capability and capability not in (model.get("capabilities") or []):
            continue
        if modality_in and not _matches_modalities(model.get("modality_in", ""), modality_in):
            continue
        if modality_out and not _matches_modalities(model.get("modality_out", ""), modality_out):
            continue

        if format == "codes":
            results.append({"code": model_id})
        elif format == "full":
            results.append(model)
        else:
            results.append(
                {
                    "code": model_id,
                    "provider": model.get("provider"),
                    "model": model.get("model"),
                    "modality_in": model.get("modality_in"),
                    "modality_out": model.get("modality_out"),
                    "context_tokens": model.get("context_tokens"),
                    "capabilities": model.get("capabilities"),
                    "role": _role_for(model),
                }
            )

    return {"count": len(results), "models": results}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="List models from cortex-core catalog")
    parser.add_argument("--provider", default=None)
    parser.add_argument("--capability", default=None)
    parser.add_argument("--modality-in", dest="modality_in", default=None)
    parser.add_argument("--modality-out", dest="modality_out", default=None)
    parser.add_argument("--include-deprecated", action="store_true")
    parser.add_argument("--format", choices=["summary", "full", "codes"], default="summary")
    args = parser.parse_args()

    output = main(
        provider=args.provider,
        capability=args.capability,
        modality_in=args.modality_in,
        modality_out=args.modality_out,
        include_deprecated=args.include_deprecated,
        format=args.format,
    )
    print(json.dumps(output, indent=2))
