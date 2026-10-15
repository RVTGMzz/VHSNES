"""Repair live G1 sprite tile geometry and install a readable compact VI face.

The actual Snes9x OAM headings use noncontiguous 16x16 sprite tiles, not the
linear canvases assumed by historical 035/036. Preserve native cursor tiles.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

from PIL import Image,ImageDraw,ImageFont
from build_content_first_040_fortune import make_ips,apply_ips
from build_g0_first_boot_title_votri_experimental import encode_chibi,tile_to_4bpp
from decompress_chibi_resource import decompress_resource

CLEAN_SHA='e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956'
BASE_SHA='9c88d9ef2d84f3794e3a8da6ef2f9bddb77c68998a6570408011536fb3274fa8'
ROOT=Path(__file__).resolve().parent.parent


def raster(text,font,size,width,height,baseline=None):
    # At 9px Tahoma's u/ư hook tone rasterizes identically to the acute.
    # Draw an explicit three-row hook so Vietnamese tones stay distinct.
    hook_fix=baseline is not None and text in ('ủ','ử')
    if hook_fix:text='u' if text=='ủ' else 'ư'
    face=ImageFont.truetype(str(font),size)
    im=Image.new('L',(width,height),0);draw=ImageDraw.Draw(im)
    if baseline is None:
        l,t,r,b=draw.textbbox((0,0),text,font=face)
        if b-t>height:raise ValueError(f'Label is taller than native sprite: {text!r}')
        mask=Image.new('L',(r-l,b-t),0)
        ImageDraw.Draw(mask).text((-l,-t),text,font=face,fill=255)
        if r-l>width:mask=mask.resize((width,b-t),Image.Resampling.LANCZOS)
        im.paste(mask,((width-mask.width)//2,(height-mask.height)//2))
    else:
        l,t,r,b=draw.textbbox((0,0),text,font=face,anchor='ls')
        if baseline+t<0 or baseline+b>12:
            raise ValueError(f'Font glyph does not fit 8px pitch / 12px cell: {text!r}')
        mask=Image.new('L',(max(1,r-l),height),0)
        ImageDraw.Draw(mask).text((-l,baseline),text,font=face,anchor='ls',fill=255)
        if r-l>8:mask=mask.resize((8,height),Image.Resampling.LANCZOS)
        im.paste(mask,(1,0))
    im=im.point(lambda p:255 if p>=100 else 0)
    if hook_fix:
        for x,y in ((3,1),(4,1),(4,2),(3,3)):im.putpixel((x,y),255)
    return im


def sprite_block(raw,tile,canvas,color=2):
    for yy in range(canvas.height//8):
        for xx in range(canvas.width//8):
            at=(tile+yy*16+xx)*32
            bits=bytes(color if canvas.getpixel((xx*8+x,yy*8+y)) else 0
                       for y in range(8) for x in range(8))
            raw[at:at+32]=tile_to_4bpp(bits)


def glyph_locations(gid):
    page,cell=divmod(gid,256)
    if page not in (8,9,10) or cell>=100:
        raise AssertionError('V2 font mapping escapes reserved copied/custom cells')
    start=0x125000 if page==10 else 0x128000+page*0x800
    x0=(cell%10)*12;y0=(cell//10)*12
    for y in range(12):
        for x in range(12):yield start+(y0+y)*16+(x0+x)//8,128>>((x0+x)%8),x,y


def build(clean,baseline,root,font):
    if hashlib.sha256(clean).hexdigest()!=CLEAN_SHA or hashlib.sha256(baseline).hexdigest()!=BASE_SHA:
        raise ValueError('Requires exact clean ROM and integrated 089 baseline')
    output=bytearray(baseline);allowed=set(range(0x7fdc,0x7fe0));font_masks={}
    rows=list(csv.DictReader((root/'translation/codepage/vi_codepage_v4_fe4_native.csv').open(encoding='utf-8-sig')))
    if len(rows)!=160:raise AssertionError('V2 codepage inventory changed')
    coverage_face=ImageFont.truetype(str(font),9)
    unknown=coverage_face.getmask('\uffff',mode='1')
    unknown_signature=(unknown.size,bytes(unknown))
    missing=set()
    for row in rows:
        mask=coverage_face.getmask(row['visual_key'],mode='1')
        if row['visual_key']!=' ' and (mask.size,bytes(mask))==unknown_signature:
            missing.add(ord(row['visual_key']))
    if missing:raise ValueError('Font lacks Vietnamese glyphs: '+','.join(hex(v) for v in sorted(missing)))
    mapped={};font_report=[];ink_names={}
    for row in rows:
        code=int(row['code_hex'],16);at=0x29a74+((code&255)-0x40)*2
        gid=int.from_bytes(baseline[at:at+2],'little')
        canvas=raster(row['visual_key'],font,9,12,12,baseline=10)
        dots=bytes(1 if canvas.getpixel((x,y)) else 0 for y in range(12) for x in range(12))
        if gid in mapped and mapped[gid]!=dots:
            raise AssertionError('Aliases sharing a glyph disagree')
        mapped[gid]=dots
        ink_names.setdefault(dots,set()).add(row['unicode'])
        for off,mask,x,y in glyph_locations(gid):
            if canvas.getpixel((x,y)):output[off]|=mask
            else:output[off]&=255^mask
            font_masks[off]=font_masks.get(off,0)|mask;allowed.add(off)
        font_report.append({'unicode':row['unicode'],'gid':hex(gid)})
    collisions=[chars for chars in ink_names.values() if len(chars)>1 and not chars<=set('"“”')]
    if collisions:raise AssertionError('Distinct Vietnamese glyphs share identical pixels')
    # Main-menu heading live OAM: 122/E2/E4/E6/E8/EA; extra EC accent.
    # Relative sprite positions retain the original gently staggered shape.
    menu_off=0xC706F;menu_span=3485
    raw,h,_=decompress_resource(clean,menu_off)
    if len(raw)!=8192 or h.span!=menu_span or h.postprocess:
        raise AssertionError('Original menu resource shape changed')
    menu=bytearray(raw)
    for tile in (0x22,0xE2,0xE4,0xE6,0xE8,0xEA):
        sprite_block(menu,tile,Image.new('L',(16,16),0))
    menu[0xEC*32:0xED*32]=bytes(32) # native Japanese dakuten decoration
    # Story Start: actual 56x16 sprite blocks 80/82/84/86+96; Password:
    # 48x16 blocks 87/89/8B. 8D+9D cursor graphic must stay original.
    story_off=0xBF95E;story_span=436
    raw_story,sh,_=decompress_resource(clean,story_off)
    if len(raw_story)!=992 or sh.span!=story_span or sh.postprocess:
        raise AssertionError('Original Story option resource shape changed')
    story=bytearray(raw_story)
    start=raster('Bắt đầu',font,11,56,16)
    password=raster('Mật khẩu',font,11,48,16)
    for tile,x,w in ((0,0,16),(2,16,16),(4,32,16),(6,48,8)):
        sprite_block(story,tile,start.crop((x,0,x+w,16)))
    for tile,x in ((7,0),(9,16),(11,32)):
        sprite_block(story,tile,password.crop((x,0,x+16,16)))
    for tile in (13,14,15,29,30):
        if story[tile*32:(tile+1)*32]!=raw_story[tile*32:(tile+1)*32]:
            raise AssertionError('Native Story cursor/spacing tile changed')
    resources=[]
    # Thirteen packages share the source. Restore it and redirect only the
    # main-menu owner to a private copy in the FF gap freed by title088.
    menu_dst=0x596fe;menu_pointer=0x12235;old_pointer=bytes.fromhex('6FF098')
    owners=[i for i in range(len(clean)) if clean.startswith(old_pointer,i)]
    if len(owners)!=13 or menu_pointer not in owners or baseline[menu_pointer:menu_pointer+3]!=old_pointer:
        raise AssertionError('Shared menu/result asset owners changed')
    output[menu_off:menu_off+menu_span]=clean[menu_off:menu_off+menu_span]
    allowed.update(range(menu_off,menu_off+menu_span))
    for off,span,data in ((menu_dst,3420,menu),(story_off,story_span,story)):
        packed=encode_chibi(bytes(data));newspan=len(packed)+2
        if newspan>span:raise AssertionError(f'G1 resource overflow {newspan}/{span}')
        if off==menu_dst and (clean[off:off+span]!=b'\xff'*span or baseline[off:off+span]!=b'\xff'*span):
            raise AssertionError('Isolated menu asset relocation collision')
        output[off:off+span]=newspan.to_bytes(2,'little')+packed+bytes([255])*(span-newspan)
        allowed.update(range(off,off+span))
        decoded,rh,_=decompress_resource(output,off)
        if decoded!=data or rh.postprocess:raise AssertionError('G1 round-trip failed')
        resources.append({'resource':hex(off),'packed_bytes':newspan,'roundtrip':True})
    output[menu_pointer:menu_pointer+3]=bytes.fromhex('FE968B');allowed.update(range(menu_pointer,menu_pointer+3))
    if output[menu_off:menu_off+menu_span]!=clean[menu_off:menu_off+menu_span] or any(output[p:p+3]!=baseline[p:p+3] for p in owners if p!=menu_pointer):
        raise AssertionError('Other shared result/menu package modified')
    # Replace the awkward M.Q label with a clear Vietnamese compact label.
    old_label=b''.join(bytes.fromhex(row['code_hex']) for ch in 'M.Q ' for row in rows if row['unicode']==ch)
    new_label=b''.join(bytes.fromhex(row['code_hex']) for ch in 'Đố  ' for row in rows if row['unicode']==ch)
    if baseline[0x28852:0x2885a]!=old_label:raise AssertionError('Menu Quiz label baseline changed')
    output[0x28852:0x2885a]=new_label;allowed.update(range(0x28852,0x2885a))
    # A complete native text line avoids the uneven Japanese per-character
    # sprite layout. Keep the original animation initializer, with its tiles
    # transparent, and draw the heading using the normal text-job renderer.
    cp={row['unicode']:bytes.fromhex(row['code_hex']) for row in rows}
    heading=bytes.fromhex('0E030F02')+b''.join(cp[ch] for ch in 'Chọn gì đây?')+bytes.fromhex('816F00')
    stub=bytes.fromhex('A00CBE227DC480A9010022268085A000FF224B80852260818590FA6B')
    for at,blob in ((0x2FE80,stub),(0x2FF00,heading)):
        if baseline[at:at+len(blob)]!=b'\xff'*len(blob):raise AssertionError('Menu text staging area occupied')
        output[at:at+len(blob)]=blob;allowed.update(range(at,at+len(blob)))
    at=0x2004E
    if baseline[at:at+7]!=bytes.fromhex('A00CBE227DC480'):
        raise AssertionError('Native heading initializer call changed')
    output[at:at+7]=bytes.fromhex('2280FE85EAEAEA');allowed.update(range(at,at+7))
    for off,mask in font_masks.items():
        if (baseline[off]^output[off])&(~mask&255):raise AssertionError('Font modifies neighboring cell ink')
    output[0x7fdc:0x7fe0]=bytes(4);checksum=(sum(output)+0x1fe)&0xffff
    output[0x7fdc:0x7fde]=(checksum^0xffff).to_bytes(2,'little')
    output[0x7fde:0x7fe0]=checksum.to_bytes(2,'little')
    if any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(baseline,output))):
        raise AssertionError('Font/menu changes escaped approved spans')
    ips,count=make_ips(clean,output)
    if apply_ips(clean,ips)!=bytes(output):raise AssertionError('090 IPS replay failed')
    return ips,{'status':'090_FONT_AND_LIVE_G1_GEOMETRY_BINARY_PASS',
      'IPS_SHA256':hashlib.sha256(ips).hexdigest(),'IPS_bytes':len(ips),'IPS_records':count,
      'ROM_SHA256':hashlib.sha256(output).hexdigest(),'checksum':hex(checksum),
      'font':'Tahoma Bold, 9px; wide Latin glyphs condensed to 8px','local_font_SHA256':hashlib.sha256(Path(font).read_bytes()).hexdigest(),
      'glyph_codes':len(rows),'distinct_reserved_glyphs':len(mapped),
      'neighboring_font_cell_bits_preserved':True,'G1_resources':resources,
      'Vietnamese_tone_bitmap_collisions':0,'shared_original_gfx_restored':True,'other_shared_gfx_owners_preserved':12,
      'native_Story_cursor_tiles_preserved':True,'whole_game_complete':False}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('original',type=Path);ap.add_argument('baseline_089_ips',type=Path)
    ap.add_argument('--font',type=Path,required=True);ap.add_argument('--ips',type=Path,required=True)
    ap.add_argument('--report',type=Path,required=True)
    a=ap.parse_args()
    if len({p.resolve() for p in (a.original,a.baseline_089_ips,a.ips,a.report)})!=4:
        ap.error('Do not overwrite inputs')
    clean=a.original.read_bytes();base=apply_ips(clean,a.baseline_089_ips.read_bytes())
    ips,qa=build(clean,base,ROOT,a.font)
    a.ips.parent.mkdir(parents=True,exist_ok=True);a.report.parent.mkdir(parents=True,exist_ok=True)
    a.ips.write_bytes(ips);a.report.write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(qa,ensure_ascii=True,indent=2))


if __name__=='__main__':main()
