#!/usr/bin/env python3
"""ROM-free regression checks; synthetic data is not runtime evidence."""
import csv
import json
from plan_g2_probe008_font import (
    ROOT, EXPECTED_SIZE, MAPPING_AUDIT_START,
    blank_unreferenced_slots, cell_bit_locations, make_plan, validate_font,
)

def main():
    cp={r['unicode']:r for r in csv.DictReader((ROOT/'translation/codepage/vi_codepage_v4_fe4_native.csv').open())}
    font=json.loads((ROOT/'translation/codepage/g2_probe008_custom_round_glyphs.json').read_text())
    validate_font(font,cp)
    rom=bytearray(EXPECTED_SIZE)
    protected={0x0000,0x0001}
    # A blank slot can still be referenced: it must be excluded.
    rom[MAPPING_AUDIT_START+5:MAPPING_AUDIT_START+7]=(0x0102).to_bytes(2,'little')
    # One lit pixel is sufficient to reject the entire glyph cell.
    _,_,off,mask=next(cell_bit_locations(0x0103));rom[off]|=mask
    original=bytes(rom)
    slots=blank_unreferenced_slots(rom,protected)
    assert not set(slots).intersection({0,1,0x0102,0x0103})
    assert 0x0104 in slots and bytes(rom)==original
    try: make_plan(rom,font,cp)
    except ValueError as exc: assert 'Exact Probe 003' in str(exc)
    else: raise AssertionError('Synthetic ROM accepted')
    broken={k:dict(v) for k,v in font.items()}
    broken['a']['code_hex']=broken['b']['code_hex']
    try: validate_font(broken,cp)
    except ValueError: pass
    else: raise AssertionError('Mapping corruption accepted')
    print('PASS: font schema, protected/referenced/occupied slot exclusion, read-only scan, strict ROM identity, corrupt mapping rejection')

if __name__=='__main__':main()
