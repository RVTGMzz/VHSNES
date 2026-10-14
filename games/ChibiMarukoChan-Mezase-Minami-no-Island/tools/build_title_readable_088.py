"""Rebuild the complete G0 title group with contrast and clear credit.

Run after the exact integrated runtime 087 candidate. All other game assets,
Quiz geometry and content remain intact. Fonts are supplied locally by path.
"""
import argparse
import hashlib
import json
from pathlib import Path

from build_g0_first_boot_title_votri_experimental import build as build_g0, TITLE
from build_content_first_040_fortune import apply_ips, make_ips
from decompress_chibi_resource import decompress_resource, cpu_to_file

BASE_SHA='9b4ad402d679ca9cf0b75e65b0b834467603ae91d88f41ed93a8fd2fbb71562b'
NEW_RESOURCE=0x5A45A


def title_art(bold, regular):
    from PIL import Image, ImageDraw, ImageFont
    plane=Image.new('P',(256,88),0)
    draw=ImageDraw.Draw(plane)
    def ink(position,label,face,color,stroke=0):
        mask=Image.new('L',plane.size,0)
        ImageDraw.Draw(mask).text(position,label,font=face,fill=255,
                                 stroke_width=stroke,stroke_fill=255)
        mask=mask.point(lambda value:255 if value>=128 else 0)
        plane.paste(color,(0,0),mask)  # Never blend palette indices.
    # Colors measured from actual G0 palette in Snes9x: 3 black, 5 white,
    # 13 red. Indexed drawing keeps exact native 4bpp resource semantics.
    for label,px,top,fill in ((TITLE[0],20,8,13),
                              (TITLE[1],15,36,5)):
        face=ImageFont.truetype(bold,px)
        l,t,r,b=draw.textbbox((0,0),label,font=face)
        if r-l>232:raise ValueError('Title line exceeds its margin')
        x=(256-(r-l))//2-l;y=top-t
        ink((x,y),label,face,3,1)
        ink((x,y),label,face,fill)
    face=ImageFont.truetype(bold,12)
    l,t,r,b=draw.textbbox((0,0),TITLE[2],font=face)
    x=(256-(r-l))//2-l;y=65-t
    draw.rounded_rectangle((x+l-5,61,x+r+5,81),radius=3,fill=5,outline=3,width=1)
    ink((x,y),TITLE[2],face,3)
    tiles=[bytes(64)];lookup={tiles[0]:0};index_map=bytearray(2048)
    for row in range(11):
        for col in range(32):
            tile=bytes(plane.getpixel((col*8+x,row*8+y)) for y in range(8) for x in range(8))
            if tile not in lookup:lookup[tile]=len(tiles);tiles.append(tile)
            at=(row*32+col)*2
            index_map[at:at+2]=lookup[tile].to_bytes(2,'little')
    return plane,tiles,index_map


def build(clean,baseline,bold,regular):
    if hashlib.sha256(clean).hexdigest()!='e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956':
        raise ValueError('Requires exact original ROM')
    if hashlib.sha256(baseline).hexdigest()!=BASE_SHA:
        raise ValueError('Requires exact 087 cumulative runtime baseline')
    graphics,plane,qa=build_g0(clean,bold,regular,art_factory=title_art,relocation_file=NEW_RESOURCE)
    output=bytearray(baseline);allowed=set(range(0x7fdc,0x7fe0))
    for item in qa['asset_report']:
        if item.get('unchanged'):continue
        old=int(item['source'],16);dest=int(item['output_source'],16)
        size=item['old_span'] if dest==old else item['new_span']
        if dest!=old and baseline[dest:dest+size]!=b'\xff'*size:
            raise AssertionError('Readable-title resource destination occupied')
        output[dest:dest+size]=graphics[dest:dest+size]
        allowed.update(range(dest,dest+size))
        original_decoded,h,_=decompress_resource(graphics,dest)
        rebuilt,rh,_=decompress_resource(output,dest)
        if original_decoded!=rebuilt or h.postprocess!=rh.postprocess:
            raise AssertionError('Merged title asset decoding differs')
    output[0x12095:0x12098]=graphics[0x12095:0x12098]
    allowed.update(range(0x12095,0x12098))
    # Remove the superseded exact G0 stream; never touch bank06 Quiz data.
    output[0x596FE:0x5A45A]=clean[0x596FE:0x5A45A]
    allowed.update(range(0x596FE,0x5A45A))
    actual=cpu_to_file(int.from_bytes(output[0x12095:0x12098],'little'))
    expected=cpu_to_file(int.from_bytes(graphics[0x12095:0x12098],'little'))
    if actual!=expected:raise AssertionError('G0 loader pointer mismatch')
    if output[0x30000:0x38000]!=baseline[0x30000:0x38000]:
        raise AssertionError('Title repair changed Quiz bank06')
    output[0x7fdc:0x7fe0]=bytes(4)
    checksum=(sum(output)+0x1fe)&0xffff
    output[0x7fdc:0x7fde]=(checksum^0xffff).to_bytes(2,'little')
    output[0x7fde:0x7fe0]=checksum.to_bytes(2,'little')
    if any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(baseline,output))):
        raise AssertionError('Title repair escaped whitelisted assets')
    ips,count=make_ips(clean,output)
    if apply_ips(clean,ips)!=bytes(output):raise AssertionError('088 cumulative IPS replay failed')
    return ips,{
        'status':'088_READABLE_G0_BINARY_PASS_RUNTIME_QA_SEPARATE',
        'IPS_SHA256':hashlib.sha256(ips).hexdigest(),'IPS_bytes':len(ips),'IPS_records':count,
        'candidate_ROM_SHA256':hashlib.sha256(output).hexdigest(),'checksum':hex(checksum),
        'title_texts':list(TITLE),'artwork_preserves_non_title_shared_tiles':True,
        'quiz_bank06_byte_identical_to_087':True,'asset_report':qa['asset_report'],
        'title_unique_tiles':qa['unique_title_tiles'],
        'bold_font_SHA256':hashlib.sha256(Path(bold).read_bytes()).hexdigest(),
        'source_font_files_distributed':False,'whole_game_complete':False,
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('original',type=Path)
    ap.add_argument('baseline_087_ips',type=Path,help='Exact 087 IPS OR original historical 039–043 ZIP (rebuilds entire chain in memory)')
    ap.add_argument('--font-bold',type=Path,required=True)
    ap.add_argument('--font-regular',type=Path,required=True)
    ap.add_argument('--ips',type=Path,required=True);ap.add_argument('--report',type=Path,required=True)
    ap.add_argument('--translate-quiz-counter',action='store_true',help='Append 089 Vietnamese Câu counter to the cumulative output')
    a=ap.parse_args()
    if len({p.resolve() for p in (a.original,a.baseline_087_ips,a.ips,a.report)})!=4:
        ap.error('Input and output paths must differ')
    if a.ips.suffix.lower()!='.ips' or a.report.suffix.lower()!='.json':ap.error('Expected IPS/JSON outputs')
    clean=a.original.read_bytes()
    baseline_qa=None
    if a.baseline_087_ips.suffix.lower()=='.zip':
        from recover_merge_061_81_one_ips_076 import rebuild_one_patch
        recovered,baseline_qa=rebuild_one_patch(clean,a.baseline_087_ips,Path(__file__).resolve().parent.parent)
        base=apply_ips(clean,recovered)
    else:
        base=apply_ips(clean,a.baseline_087_ips.read_bytes())
    ips,qa=build(clean,base,str(a.font_bold),str(a.font_regular))
    if a.translate_quiz_counter:
        from build_quiz_counter_089 import build as build_counter
        ips,counter_qa=build_counter(clean,apply_ips(clean,ips),Path(__file__).resolve().parent.parent)
        qa={**counter_qa,'readable_title_088_report':qa}
    if baseline_qa is not None:qa['recovered_087_baseline_report']=baseline_qa
    a.ips.parent.mkdir(parents=True,exist_ok=True);a.report.parent.mkdir(parents=True,exist_ok=True)
    a.ips.write_bytes(ips);a.report.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in qa.items() if k!='recovered_087_baseline_report'},ensure_ascii=True,indent=2))


if __name__=='__main__':main()
