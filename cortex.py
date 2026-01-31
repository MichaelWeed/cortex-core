#!/usr/bin/env python3
"""
Unified CLI for cortex-core. Use from any project: python3 /path/to/cortex-core/cortex.py <cmd> [args]
"""
import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def cmd_export(args):
    from export_catalog import export
    export(
        output_path=args.output,
        provider=args.provider,
        capability=args.capability,
        modality_in=args.modality_in,
        modality_out=args.modality_out,
        include_deprecated=args.include_deprecated,
    )


def cmd_list_models(args):
    from tools.cortex.listModels.index import main as list_models
    out = list_models(
        provider=args.provider,
        capability=args.capability,
        modality_in=args.modality_in,
        modality_out=args.modality_out,
        include_deprecated=args.include_deprecated,
        format=args.format,
    )
    print(json.dumps(out, indent=2))


def cmd_check(args):
    """Validate catalogs load; exit 0 if OK, 1 on error. Use in CI or startup."""
    errors = []
    model_path = ROOT / "config" / "model_catalog.json"
    tool_path = ROOT / "config" / "tool_catalog.json"
    if args.catalog_path:
        p = Path(args.catalog_path)
        model_path = p / "model_catalog.json" if p.is_dir() else p
        tool_path = p.parent / "tool_catalog.json" if p.name == "model_catalog.json" else p.parent / "tool_catalog.json"
    for label, path in [("model_catalog", model_path), ("tool_catalog", tool_path)]:
        if not path.exists():
            errors.append(f"{label}: missing {path}")
            continue
        try:
            with open(path) as f:
                json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"{label}: invalid JSON - {e}")
    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        sys.exit(1)
    if not args.quiet:
        print("OK: catalogs load")
    sys.exit(0)


def main():
    ap = argparse.ArgumentParser(prog="cortex", description="Cortex-core CLI: export, list-models, check")
    sub = ap.add_subparsers(dest="cmd", required=True)

    # export
    p_export = sub.add_parser("export", help="Export model catalog to JSON for pipelines")
    p_export.add_argument("-o", "--output", default=None, help="Output file (default: stdout)")
    p_export.add_argument("--provider", default=None)
    p_export.add_argument("--capability", default=None)
    p_export.add_argument("--modality-in", dest="modality_in", default=None)
    p_export.add_argument("--modality-out", dest="modality_out", default=None)
    p_export.add_argument("--include-deprecated", action="store_true")
    p_export.set_defaults(func=cmd_export)

    # list-models
    p_list = sub.add_parser("list-models", help="List models from catalog (filtered)")
    p_list.add_argument("--provider", default=None)
    p_list.add_argument("--capability", default=None)
    p_list.add_argument("--modality-in", dest="modality_in", default=None)
    p_list.add_argument("--modality-out", dest="modality_out", default=None)
    p_list.add_argument("--include-deprecated", action="store_true")
    p_list.add_argument("--format", choices=["summary", "full", "codes"], default="summary")
    p_list.set_defaults(func=cmd_list_models)

    # check
    p_check = sub.add_parser("check", help="Validate catalogs load (exit 0/1 for CI)")
    p_check.add_argument("--catalog-path", default=None, help="Path to config dir or model_catalog.json")
    p_check.add_argument("-q", "--quiet", action="store_true")
    p_check.set_defaults(func=cmd_check)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
