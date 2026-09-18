#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_replacement(
    fragment_path: Path,
    patch: dict,
) -> Path:
    raw = Path(str(patch["replacement_file"]))
    if raw.is_absolute():
        return raw
    return fragment_path.parent / raw


def main() -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Assemble proven graphics patch fragments into "
            "one ready Build 036 manifest"
        )
    )
    ap.add_argument("template", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument(
        "fragments",
        nargs="+",
        type=Path,
    )
    args = ap.parse_args()

    manifest = load_json(args.template)
    if manifest.get("schema") != "chibi.graphics.patch.v1":
        raise SystemExit("template schema mismatch")

    output_dir = args.output.parent.resolve()
    args.output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    patches: list[dict] = []
    ids: set[str] = set()
    spans: list[tuple[int, int, str]] = []
    fragment_ids: list[str] = []

    for fragment_path in args.fragments:
        fragment = load_json(fragment_path)
        if (
            fragment.get("schema")
            != "chibi.graphics.patch.fragment.v1"
        ):
            raise SystemExit(
                f"{fragment_path}: fragment schema mismatch"
            )

        fragment_id = str(fragment.get("id", ""))
        if not fragment_id:
            raise SystemExit(
                f"{fragment_path}: missing fragment id"
            )
        fragment_ids.append(fragment_id)

        evidence = str(fragment.get("evidence", "")).strip()
        if not evidence:
            raise SystemExit(
                f"{fragment_path}: missing evidence"
            )

        entries = fragment.get("patches")
        if not isinstance(entries, list) or not entries:
            raise SystemExit(
                f"{fragment_path}: no patch entries"
            )

        for entry in entries:
            patch = dict(entry)
            patch_id = str(patch.get("id", ""))
            if not patch_id:
                raise SystemExit(
                    f"{fragment_path}: patch missing id"
                )
            if patch_id in ids:
                raise SystemExit(
                    f"duplicate patch id: {patch_id}"
                )
            ids.add(patch_id)

            start = int(str(patch["offset"]), 0)
            length = int(str(patch["length"]), 0)
            end = start + length
            if length <= 0:
                raise SystemExit(
                    f"{patch_id}: invalid length"
                )

            for a, b, other in spans:
                if max(start, a) < min(end, b):
                    raise SystemExit(
                        f"{patch_id}: overlaps {other}"
                    )
            spans.append(
                (start, end, patch_id)
            )

            if "replacement_file" not in patch:
                raise SystemExit(
                    f"{patch_id}: fragment must use replacement_file"
                )

            source = resolve_replacement(
                fragment_path,
                patch,
            )
            if not source.is_file():
                raise SystemExit(
                    f"{patch_id}: missing replacement file {source}"
                )

            actual_sha256 = hashlib.sha256(
                source.read_bytes()
            ).hexdigest()
            declared_sha256 = str(
                patch.get(
                    "replacement_sha256",
                    actual_sha256,
                )
            ).lower()
            if actual_sha256 != declared_sha256:
                raise SystemExit(
                    f"{patch_id}: replacement SHA256 mismatch"
                )

            relative = os.path.relpath(
                source.resolve(),
                output_dir,
            )
            patch["replacement_file"] = relative
            patch["replacement_sha256"] = actual_sha256
            patch["fragment_id"] = fragment_id
            patch["fragment_evidence"] = evidence
            patches.append(patch)

    patches.sort(
        key=lambda patch: (
            int(str(patch["offset"]), 0),
            str(patch["id"]),
        )
    )

    manifest["ready"] = True
    manifest["patches"] = patches
    manifest["assembled_from"] = [
        str(path)
        for path in args.fragments
    ]
    manifest["fragment_ids"] = fragment_ids
    manifest["runtime_status"] = "UNTESTED"
    manifest["runtime_claim"] = False

    args.output.write_text(
        json.dumps(
            manifest,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print("template_schema=PASS")
    print(f"fragment_count={len(args.fragments)}")
    print(f"patch_count={len(patches)}")
    print("patch_ids_unique=PASS")
    print("patch_spans_overlap=0 PASS")
    print("replacement_files=PASS")
    print("replacement_sha256=PASS")
    print("manifest_ready=true")
    print(f"output={args.output}")
    print("runtime_status=UNTESTED")
    print("runtime_claim=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
