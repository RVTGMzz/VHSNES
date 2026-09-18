#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from scan_g1_shape_fingerprints import (
    GlyphShape,
    Hit,
    cluster_hits,
    extract_glyph,
    require_clean,
    scan_packed_1bpp,
    scan_snes_blocks,
)

BATCHES = {
    "g2": {
        "start_banner": "今からやるよ",
        "rules_heading": "ルールをせつめいするよ",
        "first_to_two": "２本先取だよ",
        "until_win": "ゲームの時間は勝つまでだよ",
    },
    "g3": {
        "win": "勝ち",
        "lose": "敗けた",
        "continue": "コンティニュー",
        "quit": "やめる",
        "final_win": "最終勝利",
        "ending": "エンディング",
    },
}


def unique_chars(targets: dict[str, str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for text in targets.values():
        for ch in text:
            if ch not in seen:
                seen.add(ch)
                out.append(ch)
    return out


def coverage(chars: set[str], targets: dict[str, str]) -> str:
    parts = []
    for name, text in targets.items():
        unique = set(text)
        got = len(unique & chars)
        parts.append(f"{name}:{got}/{len(unique)}")
    return ",".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="READ-ONLY bitmap-shape scanner for Chibi G2/G3 graphics labels"
    )
    ap.add_argument("rom", type=Path)
    ap.add_argument("--batch", choices=sorted(BATCHES), required=True)
    ap.add_argument("--max-diff", type=int, default=14)
    ap.add_argument("--cluster-span", type=lambda s: int(s, 0), default=0x800)
    ap.add_argument("--top", type=int, default=320)
    args = ap.parse_args()

    if not 0 <= args.max_diff <= 72:
        raise SystemExit("--max-diff must be in 0..72")

    data = require_clean(args.rom)
    targets = BATCHES[args.batch]
    chars = unique_chars(targets)

    shapes: list[GlyphShape] = []
    skipped: list[tuple[str, str]] = []
    for ch in chars:
        try:
            shapes.append(extract_glyph(data, ch))
        except Exception as exc:
            skipped.append((ch, str(exc)))

    if not shapes:
        raise SystemExit("no usable glyph shapes could be extracted")

    print(f"CHIBI MARUKO {args.batch.upper()} SHAPE FINGERPRINT SCAN")
    print("mode=READ_ONLY")
    print("clean_rom_contract=PASS")
    print("runtime_claim=NO")
    print(
        "targets="
        + " | ".join(f"{name}:{text}" for name, text in targets.items())
    )
    print(
        f"usable_glyphs={len(shapes)} skipped_glyphs={len(skipped)} "
        f"max_diff={args.max_diff} min_similarity={1-args.max_diff/144:.4f}"
    )
    for shape in shapes:
        print(
            f"glyph={shape.ch} gid=0x{shape.gid:04X} "
            f"ink={shape.ink}"
        )
    for ch, reason in skipped:
        print(f"skipped_glyph={ch} reason={reason}")

    hits: list[Hit] = []
    hits.extend(scan_packed_1bpp(data, shapes, args.max_diff))
    hits.extend(scan_snes_blocks(data, shapes, 2, args.max_diff))
    hits.extend(scan_snes_blocks(data, shapes, 4, args.max_diff))

    print(f"raw_hits={len(hits)}")
    for hit in sorted(
        hits,
        key=lambda h: (-h.score, h.off, h.mode, h.ch),
    )[: args.top]:
        print(
            f"hit mode={hit.mode:20s} off=0x{hit.off:06X} "
            f"ch={hit.ch} score={hit.score:.4f}"
        )

    clusters = cluster_hits(hits, args.cluster_span)
    ranked = sorted(
        clusters,
        key=lambda members: (
            -len({h.ch for h in members}),
            -max(h.score for h in members),
            members[0].off,
        ),
    )
    print(
        f"clusters={len(clusters)} "
        f"cluster_span=0x{args.cluster_span:X}"
    )

    shape_order = [shape.ch for shape in shapes]
    for members in ranked[:120]:
        chars_here = {hit.ch for hit in members}
        chars_s = "".join(ch for ch in shape_order if ch in chars_here)
        modes = sorted({hit.mode for hit in members})
        best = max(hit.score for hit in members)
        print(
            f"cluster 0x{members[0].off:06X}..0x{members[-1].off:06X} "
            f"unique_chars={len(chars_here)} chars={chars_s} "
            f"hits={len(members)} best={best:.4f} "
            f"coverage={coverage(chars_here, targets)} "
            f"modes={','.join(modes)}"
        )

    print(
        "interpretation=multi-glyph clusters are reverse candidates only, "
        "not patch offsets"
    )
    print(
        "proof_gate=correlate cluster with descriptor/screen path, "
        "pointer/DMA evidence, and decoded visible asset"
    )
    print("do_not_patch=0x286B4..0x287FC descriptor/debug prose")
    print("runtime_claim=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
