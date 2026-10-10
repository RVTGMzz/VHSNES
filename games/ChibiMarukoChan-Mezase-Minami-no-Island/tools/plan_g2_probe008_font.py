#!/usr/bin/env python3
"""Read-only font slot preflight. Does not generate or modify a ROM."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
from build_g2_probe_005_clean_dialogue_font import (
    EXPECTED_BASE_SHA1, EXPECTED_SIZE, cell_bit_locations,
    MAPPING_AUDIT_START, MAPPING_AUDIT_END, MAP_BASE,
)

ROOT = Path(__file__).resolve().parent.parent
EXPECTED_SHA256 = '5208bec10147f478cc17955c4f262a5cde08e5b85708caa2717370f6835fbacd'

def validate_font(font, codepage):
    seen = set()
    for ch, row in font.items():
        if len(ch) != 1:
            raise ValueError('font key must be one Unicode character')
        code = bytes.fromhex(row['code_hex'])
        if len(code) != 2 or code[0] != 0x84 or not 0x40 <= code[1] <= 0xFC or code in seen:
            raise ValueError(f'invalid/duplicate code: {ch!r}')
        seen.add(code)
        bitmap = bytes.fromhex(row['bitmap_hex'])
        if len(bitmap) != 18:
            raise ValueError(f'bad bitmap size: {ch!r}')
        if ch != ' ' and not any(bitmap):
            raise ValueError(f'empty printable glyph: {ch!r}')
        if ch in codepage and row['code_hex'].upper() != codepage[ch]['code_hex'].upper():
            raise ValueError(f'existing code changed: {ch!r}')
    if set(codepage) - set(font):
        raise ValueError('font omits existing codepage entries')

def blank_unreferenced_slots(rom, protected):
    # Scan every byte alignment conservatively: false positives reduce capacity
    # but do not turn a referenced glyph into a candidate.
    audit = rom[MAPPING_AUDIT_START:MAPPING_AUDIT_END]
    out = []
    for page in range(10):
        for idx in range(100):
            gid = page * 256 + idx
            if gid in protected or gid.to_bytes(2, 'little') in audit:
                continue
            if any(rom[off] & mask for _,_,off,mask in cell_bit_locations(gid)):
                continue
            out.append(gid)
    return out

def make_plan(rom, font, codepage):
    if (len(rom) != EXPECTED_SIZE or hashlib.sha1(rom).hexdigest() != EXPECTED_BASE_SHA1
            or hashlib.sha256(rom).hexdigest() != EXPECTED_SHA256):
        raise ValueError('Exact Probe 003 ROM required; no relaxed identity mode')
    validate_font(font, codepage)
    protected = {int(r['glyph_id_hex'],16) for r in codepage.values()}
    # Existing native AND custom cells are excluded, even when blank. This
    # first preflight chooses only fresh slots and cannot overwrite Japanese.
    free = blank_unreferenced_slots(rom, protected)
    bitmaps = list(dict.fromkeys(row['bitmap_hex'] for row in font.values()))
    extras = sorted(set(font) - set(codepage))
    allocation = dict(zip(bitmaps, free)) if len(free) >= len(bitmaps) else {}
    return {
        'mode': 'READ_ONLY_PREFLIGHT', 'rom_modified': False,
        'runtime_status': 'UNTESTED', 'build_ready': False,
        'base_sha256': hashlib.sha256(rom).hexdigest(),
        'entry_count': len(font), 'unique_bitmap_count': len(bitmaps),
        'blank_unreferenced_candidate_count': len(free),
        'capacity_pass': len(free) >= len(bitmaps),
        'unproven_code_extensions': extras,
        'blockers': ['Mapping-table capacity for added codes is not proven',
                     'Candidates require confirmation against non-mapping glyph references',
                     'No independent patched-ROM verifier or runtime confirmation yet']
                    + ([] if allocation else ['Insufficient verified fresh slot candidates']),
        'candidate_entries': {
            ch: {'code_hex': row['code_hex'],
                 'map_offset': f'0x{MAP_BASE+(int(row["code_hex"],16)-0x8440)*2:06X}',
                 'candidate_glyph_id': f'0x{allocation[row["bitmap_hex"]]:04X}' if allocation else None}
            for ch,row in font.items()
        },
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('probe003_rom',type=Path)
    ap.add_argument('report',type=Path)
    ap.add_argument('--font',type=Path,default=ROOT/'translation/codepage/g2_probe008_custom_round_glyphs.json')
    args=ap.parse_args()
    if args.report.resolve() in {args.probe003_rom.resolve(), args.font.resolve()}:
        raise SystemExit('Report must not overwrite an input')
    cp={r['unicode']:r for r in csv.DictReader((ROOT/'translation/codepage/vi_codepage_v4_fe4_native.csv').open())}
    report=make_plan(args.probe003_rom.read_bytes(),json.loads(args.font.read_text()),cp)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(f"capacity_pass={report['capacity_pass']}; build_ready=False; ROM unchanged")

if __name__=='__main__': main()
