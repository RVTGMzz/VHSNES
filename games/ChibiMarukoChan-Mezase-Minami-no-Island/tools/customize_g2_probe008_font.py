#!/usr/bin/env python3
"""Hand-drawn rounded 7-pixel face; preview only, never writes a ROM."""
import json
import unicodedata as ud
from PIL import Image, ImageDraw, ImageFont
import generate_g2_probe008_font as old

# Explicit pixel outlines, not dilation or rasterized vector type.
LOWER = dict(zip('abcdefghijklmnopqrstuvwxyz', [
 '0111100/0000010/0111110/1000010/0111110',
 '1000000/1000000/1011100/1100010/1000010/1000010/1111100',
 '0111110/1000000/1000000/1000000/0111110',
 '0000010/0000010/0111010/1000110/1000010/1000010/0111110',
 '0111100/1000010/1111110/1000000/0111110',
 '0001100/0010000/0111100/0010000/0010000/0010000/0010000',
 '0111110/1000010/1000010/0111110/0000010/1000010/0111100',
 '1000000/1000000/1011100/1100010/1000010/1000010/1000010',
 '0010000/0010000/0010000/0010000/0010000',
 '0001000/0001000/0001000/0001000/0001000/1001000/0110000',
 '1000000/1000000/1000100/1001000/1110000/1001000/1000100',
 '0010000/0010000/0010000/0010000/0010000/0010000/0001000',
 '1101100/1010010/1010010/1010010/1010010',
 '1011100/1100010/1000010/1000010/1000010',
 '0111100/1000010/1000010/1000010/0111100',
 '1111100/1000010/1000010/1111100/1000000/1000000/1000000',
 '0111110/1000010/1000010/0111110/0000010/0000010/0000010',
 '1011100/1100010/1000000/1000000/1000000',
 '0111110/1000000/0111100/0000010/1111100',
 '0010000/0010000/1111100/0010000/0010000/0010010/0001100',
 '1000010/1000010/1000010/1000110/0111010',
 '1000001/1000001/0100010/0100010/0011100',
 '1000001/1000001/1001001/1010101/0100010',
 '1000001/0100010/0011100/0100010/1000001',
 '1000010/1000010/1000010/0111110/0000010/1000010/0111100',
 '1111110/0000100/0011000/0100000/1111110',
]))
UPPER = dict(zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ', [
 '0011100/0100010/1000001/1000001/1111111/1000001/1000001',
 '1111100/1000010/1000010/1111100/1000010/1000010/1111100',
 '0111110/1000001/1000000/1000000/1000000/1000001/0111110',
 '1111100/1000010/1000001/1000001/1000001/1000010/1111100',
 '1111110/1000000/1000000/1111100/1000000/1000000/1111110',
 '1111110/1000000/1000000/1111100/1000000/1000000/1000000',
 '0111110/1000001/1000000/1001111/1000001/1000001/0111110',
 '1000001/1000001/1000001/1111111/1000001/1000001/1000001',
 '0111110/0001000/0001000/0001000/0001000/0001000/0111110',
 '0011111/0000010/0000010/0000010/1000010/1000010/0111100',
 '1000001/1000010/1000100/1111000/1000100/1000010/1000001',
 '1000000/1000000/1000000/1000000/1000000/1000000/1111110',
 '1000001/1100011/1010101/1001001/1000001/1000001/1000001',
 '1000001/1100001/1010001/1001001/1000101/1000011/1000001',
 '0111110/1000001/1000001/1000001/1000001/1000001/0111110',
 '1111110/1000001/1000001/1111110/1000000/1000000/1000000',
 '0111110/1000001/1000001/1000001/1001001/1000101/0111110',
 '1111110/1000001/1000001/1111110/1000100/1000010/1000001',
 '0111110/1000001/1000000/0111110/0000001/1000001/0111110',
 '1111111/0001000/0001000/0001000/0001000/0001000/0001000',
 '1000001/1000001/1000001/1000001/1000001/1000001/0111110',
 '1000001/1000001/1000001/0100010/0100010/0010100/0001000',
 '1000001/1000001/1000001/1001001/1001001/1010101/0100010',
 '1000001/0100010/0010100/0001000/0010100/0100010/1000001',
 '1000001/0100010/0010100/0001000/0001000/0001000/0001000',
 '1111111/0000001/0000010/0001000/0100000/1000000/1111111',
]))

def glyph(ch):
    seq = ud.normalize('NFD', ch); base = seq[0]; marks = set(seq[1:])
    if ch in 'đĐ': base = 'd' if ch == 'đ' else 'D'
    if base not in LOWER | UPPER: return old.glyph(ch)
    rows = (LOWER | UPPER)[base].split('/')
    y = 2 if base.isupper() or base in 'bdfhklt' else 4
    if base.isupper() and marks:
        rows = [rows[i] for i in (0,1,3,5,6)]; y = 4
    if base == 'y' and '\u0323' in marks:
        # Keep the dot under the centre, separate from the right descender.
        rows = ['1000010','1000010','1000010','0111110','0000010','0000010','0000110']
    pts = old.points('/'.join(rows), 2, y)
    if base in 'ij' and not marks.intersection(old.TONES):
        pts.add((4 if base == 'i' else 5, 2))
    if ch in 'đĐ': pts |= old.points('1111', 5 if ch == 'đ' else 1, 3 if ch == 'đ' else 5)
    stacked = bool(marks.intersection({'\u0302','\u0306'}))
    if '\u0302' in marks: pts |= old.points('00100/01010', 2, 1)
    if '\u0306' in marks: pts |= old.points('10001/01110', 2, 1)
    if '\u031b' in marks: pts |= {(9,2),(9,3),(8,4),(7,4)}
    for mark, pattern in old.TONES.items():
        if mark in marks:
            # Side-stacked tones retain a blank column after the base modifier.
            x = 7 if stacked else (2 if mark == '\u0303' else 3)
            pts |= old.points(pattern, x, 0)
    if '\u0323' in marks: pts.add((4,10))
    assert all(0 <= x < 12 and 0 <= y < 11 for x,y in pts), ch
    return int(''.join('1' if (x,y) in pts else '0' for y in range(12) for x in range(12)),2).to_bytes(18,'big').hex()

def tile(hexstr, scale=3):
    im = Image.new('RGB',(12,12))
    im.putdata([(40,48,57) if b == '1' else (255,249,233) for b in f'{int(hexstr,16):0144b}'])
    return im.resize((12*scale,12*scale),Image.Resampling.NEAREST)

def main():
    before = old.generate()
    after = {ch: dict(row, bitmap_hex=glyph(row['visual_key'])) for ch,row in before.items()}
    out = old.ROOT / 'docs/previews/probe008-custom'; out.mkdir(parents=True,exist_ok=True)
    dest = old.ROOT / 'translation/codepage/g2_probe008_custom_round_glyphs.json'
    dest.write_text(json.dumps(after,ensure_ascii=False,indent=2)+'\n')
    label = ImageFont.truetype('DejaVuSans.ttf',20)
    small = ImageFont.truetype('DejaVuSans.ttf',15)
    im = Image.new('RGB',(1500,850),'#e9eef0'); d=ImageDraw.Draw(im)
    d.text((24,18),'CHIBI MARUKO | CUSTOM PIXEL FONT',font=label,fill='#26343e')
    d.text((24,50),'Trái: mẫu trước  •  Phải: thân chữ rộng, bo góc nhẹ',font=label,fill='#26343e')
    for i,s in enumerate(old.SAMPLES):
        yy=100+i*125
        d.text((24,yy),s,font=small,fill='#26343e')
        for xx,data in [(24,before),(770,after)]:
            for j,ch in enumerate(s):
                im.paste(tile(data[ch]['bitmap_hex'],3),(xx+j*36,yy+30))
                im.paste(tile(data[ch]['bitmap_hex'],1),(xx+j*12,yy+76))
    d.text((24,746),'12×12 px • 1-bit • Cùng bước chữ 12 px để so sánh công bằng.',font=small,fill='#26343e')
    d.text((24,775),'Ảnh dựng từ bitmap; chưa xác nhận khoảng cách và hiển thị trong game.',font=small,fill='#26343e')
    im.save(out/'font-comparison.png')
    chars=list(after)
    atlas=Image.new('RGB',(1040,70+((len(chars)+11)//12)*90),'#e9eef0');d=ImageDraw.Draw(atlas)
    d.text((20,15),'CUSTOM ROUND — full current codepage, offline preview',font=label,fill='#26343e')
    for i,ch in enumerate(chars):
        x=20+(i%12)*85; y=60+(i//12)*90
        d.text((x,y),ch,font=small,fill='#26343e');atlas.paste(tile(after[ch]['bitmap_hex'],4),(x,y+24))
    atlas.save(out/'full-codepage.png')
    family=Image.new('RGB',(1040,70+len(old.FAMILIES)*90),'#e9eef0');d=ImageDraw.Draw(family)
    d.text((20,15),'CUSTOM ROUND — Vietnamese families, offline preview',font=label,fill='#26343e')
    for i,row in enumerate(old.FAMILIES):
        for j,ch in enumerate(row):
            x=20+j*85;y=60+i*90
            d.text((x,y),ch,font=small,fill='#26343e');family.paste(tile(after[ch]['bitmap_hex'],4),(x,y+24))
    family.save(out/'vietnamese-families.png')
    assert len(after)==163 and len({r['code_hex'] for r in after.values()})==163
    for ch,row in after.items():
        assert len(bytes.fromhex(row['bitmap_hex']))==18
        assert row['code_hex']==before[ch]['code_hex']
    for row in old.FAMILIES:
        assert len({after[ch]['bitmap_hex'] for ch in row})==len(row), row
    print(f'{len(after)} entries; mapping preserved; family silhouettes distinct; ROM untouched')
    print(out)

if __name__=='__main__':main()
