#!/usr/bin/env python3
"""
Export cortex-core model catalog to a single JSON file for pipelines.
Consumable by any repo: read this file at startup to resolve "what is available."
Set CORTEX_CATALOG_PATH to a directory or path to model_catalog.json to use a symlinked catalog.
"""

import json
import os
import sys
from pathlib import Path

# Reuse catalog path and loading from listModels
sys.path.insert(0, str(Path(__file__).parent))
from tools.cortex.listModels.index import (
    _catalog_path,
    _load_model_catalog,
    _is_deprecated,
    _matches_modalities,
)


def _filtered_models(provider=None, capability=None, modality_in=None, modality_out=None, include_deprecated=False):
    catalog = _load_model_catalog()
    out = []
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
        out.append({
            "code": model_id,
            "provider": model.get("provider"),
            "model": model.get("model"),
            "modality_in": model.get("modality_in"),
            "modality_out": model.get("modality_out"),
            "context_tokens": model.get("context_tokens"),
            "capabilities": model.get("capabilities"),
            "baseUrl": model.get("baseUrl"),
            "role": _role_for(model),
        })
    return out


def _role_for(model: dict) -> str:
    """Derive a simple role from capabilities for pipeline selection (e.g. small-text, large-text)."""
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


def export(
    output_path: str = None,
    provider: str = None,
    capability: str = None,
    modality_in: str = None,
    modality_out: str = None,
    include_deprecated: bool = False,
) -> dict:
    """
    Export runtime-consumable catalog. Returns the payload written.
    """
    models = _filtered_models(
        provider=provider,
        capability=capability,
        modality_in=modality_in,
        modality_out=modality_out,
        include_deprecated=include_deprecated,
    )
    source = os.environ.get("CORTEX_CATALOG_PATH") or _catalog_path().name
    payload = {"catalog_version": "1.0", "source": str(source), "count": len(models), "models": models}
    out = json.dumps(payload, indent=2)
    if output_path:
        Path(output_path).write_text(out)
    else:
        print(out)
    return payload


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Export cortex-core model catalog for pipelines")
    p.add_argument("--output", "-o", default=None, help="Write to file; default stdout")
    p.add_argument("--provider", default=None)
    p.add_argument("--capability", default=None)
    p.add_argument("--modality-in", dest="modality_in", default=None)
    p.add_argument("--modality-out", dest="modality_out", default=None)
    p.add_argument("--include-deprecated", action="store_true")
    args = p.parse_args()
    export(
        output_path=args.output,
        provider=args.provider,
        capability=args.capability,
        modality_in=args.modality_in,
        modality_out=args.modality_out,
        include_deprecated=args.include_deprecated,
    )
