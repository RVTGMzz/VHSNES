"""Finish four Fortune captions with guarded native pointers and column layout.

Original bank82 label caller reads $F5A6,Y. The actual bank85 value caller
$85:EFB2 reads seven tables, including $F113,Y and $F185,Y. Keep all outcomes.
"""
import argparse
import hashlib
import json
from pathlib import Path

from build_content_first_040_fortune import apply_ips,make_ips
from build_quiz_relocated_81_jobwait_075 import read_codepage
from build_quiz_layout_087 import spacing_stub,destination_stub,wrap_stub
from audit_fortune_expansion_083 import audit

BASE_SHA='d4185b5231506368646bb08f88b18402c854f686b7081a3805a09fe76358e127'
ROOT=Path(__file__).resolve().parent.parent


def compact_selector(a,story=False):
    a.emit(0xAF,0x86,0x1F,0x00,0x29,0x7F,0x00)
    if story:
        a.cmp16(3);a.branch(0xF0,'quiz')
    a.cmp16(6);a.branch(0xF0,'quiz')
    a.cmp16(5);a.branch(0xF0,'fortune')
    a.cmp16(0x7e);a.branch(0xD0,'native')
    a.emit(0xAF,0x94,0x1F,0x00)
    a.cmp16(0x8000);a.branch(0x90,'native')
    a.cmp16(0x8090);a.branch(0x90,'quiz')
    a.branch(0x80,'native')
    a.label('fortune')
    a.emit(0xAF,0x94,0x1F,0x00)
    a.cmp16(0xbd24);a.branch(0x90,'relocated')
    a.cmp16(0xcb9b);a.branch(0x90,'quiz')
    a.label('relocated')
    a.cmp16(0xff20);a.branch(0x90,'native')
    a.cmp16(0xffa0);a.branch(0x90,'quiz')


def build(clean,baseline,root):
    if hashlib.sha256(clean).hexdigest()!='e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956':
        raise ValueError('Requires exact original ROM')
    if hashlib.sha256(baseline).hexdigest()!=BASE_SHA:raise ValueError('Requires exact 090 font/menu baseline')
    audit(root)
    # Actual callers: bank82 labels; bank85 Heaven-message and color tables.
    anchors=((0x1757f,'AD00140AA8B9A6F5A8224B8085'),
             (0x2EFD5,'AD16140AA8B913F1A8224B8085'),
             (0x2F06B,'AD20140AA8B985F1A8224B8085'))
    for at,hx in anchors:
        b=bytes.fromhex(hx)
        if clean[at:at+len(b)]!=b or baseline[at:at+len(b)]!=b:
            raise AssertionError(f'Fortune native caller changed: {at:#x}')
    output=bytearray(baseline);allowed=set(range(0x7fdc,0x7fe0))
    def replace(at,old,new):
        if baseline[at:at+len(old)]!=old or len(old)!=len(new):raise AssertionError(f'Fortune anchor changed {at:#x}')
        output[at:at+len(new)]=new;allowed.update(range(at,at+len(new)))
    cp=read_codepage(root)
    plans=((0x2BD5A,'天の声','Lời trời mách',0x175AE,0x2FF20),
           (0x2C867,'また来週','Hẹn tuần sau',0x2F151,0x2FF48),
           (0x2CA79,'きいろ','Vàng',0x2F189,0x2FF70),
           (0x2CAD9,'しろいろ','Trắng',0x2F195,0x2FF80))
    fields=[]
    for old,jp,vi,pointer,dst in plans:
        original=clean[old:old+4]+jp.encode('cp932')+bytes.fromhex('816F00')
        if baseline[old:old+len(original)]!=original:
            raise AssertionError('Four outstanding Fortune originals are not intact')
        if original[0]!=14 or original[2]!=15:raise AssertionError('Unexpected Fortune native header')
        header=bytearray(original[:4]);header[1]=1 if old==0x2bd5a else 15
        rec=bytes(header)+b''.join(bytes.fromhex(cp[ch]) for ch in vi)+bytes.fromhex('816F00')
        replace(dst,b'\xff'*len(rec),rec)
        replace(pointer,(old&0xffff).to_bytes(2,'little'),(dst&0xffff).to_bytes(2,'little'))
        fields.append({'original_record':hex(old),'pointer_at':hex(pointer),'new_record':hex(dst),'full_Vietnamese':vi,'bytes':len(rec)})
    # All dynamic value records fit <=12 glyphs. Start at column 15, after the
    # 13-cell Heaven label at column 1. Every row fits the 28-column 8px grid.
    value_headers=[]
    for at in range(0x2BD24,0x2CB9B):
        if at in {plan[0] for plan in plans}:continue
        if (clean[at]==14 and clean[at+2]==15 and clean[at+1] in (6,7)
                and clean[at+3] in (13,15,17,19,21,23,25)):
            if baseline[at:at+4]!=clean[at:at+4]:raise AssertionError('Fortune header already changed')
            end=baseline.find(bytes.fromhex('816F'),at+4,at+80)
            if end<0 or (end-at-4)//2>12:raise AssertionError('Fortune value exceeds reviewed 12-cell budget')
            replace(at+1,bytes([clean[at+1]]),bytes([15]));value_headers.append(hex(at))
    for old,jp,vi,pointer,dst in plans:
        length=4+len(jp.encode('cp932'))+3
        if output[old:old+length]!=clean[old:old+length]:
            raise AssertionError('Original relocated Fortune record changed')
    # Reassemble all three position consumers AND wrap logic with the extended
    # source context. Native menu, Story and other bank85 text stay unchanged.
    for at,old,new in ((0x2FB80,spacing_stub(True),spacing_stub(True,compact_selector)),
                       (0x2FC00,spacing_stub(False),spacing_stub(False,compact_selector)),
                       (0x2FC80,wrap_stub(),wrap_stub(compact_selector)),
                       (0x2FE00,destination_stub(),destination_stub(compact_selector))):
        if len(new)>128:raise AssertionError('Extended source selector exceeds reserved code cell')
        if baseline[at:at+len(old)]!=old:raise AssertionError('Known renderer hook code changed')
        replace(at,old+b'\xff'*(len(new)-len(old)),new)
    output[0x7fdc:0x7fe0]=bytes(4);checksum=(sum(output)+0x1fe)&0xffff
    output[0x7fdc:0x7fde]=(checksum^0xffff).to_bytes(2,'little')
    output[0x7fde:0x7fe0]=checksum.to_bytes(2,'little')
    if any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(baseline,output))):raise AssertionError('Fortune mutation escaped bounds')
    ips,n=make_ips(clean,output)
    if apply_ips(clean,ips)!=bytes(output):raise AssertionError('Fortune final IPS replay failed')
    return ips,{'status':'091_ALL_FOUR_FORTUNE_EXPANSIONS_BINARY_PASS',
      'IPS_SHA256':hashlib.sha256(ips).hexdigest(),'IPS_bytes':len(ips),'IPS_records':n,
      'ROM_SHA256':hashlib.sha256(output).hexdigest(),'checksum':hex(checksum),
      'four_full_Vietnamese_fields':fields,'dynamic_value_headers_shifted':len(value_headers),
      'original_four_Japanese_records_preserved':True,'emulator_acceptance':False,'whole_game_complete':False}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('original',type=Path);ap.add_argument('baseline_090_ips',type=Path)
    ap.add_argument('--ips',type=Path,required=True);ap.add_argument('--report',type=Path,required=True)
    a=ap.parse_args()
    if len({p.resolve() for p in (a.original,a.baseline_090_ips,a.ips,a.report)})!=4:ap.error('Input/output paths must differ')
    c=a.original.read_bytes();b=apply_ips(c,a.baseline_090_ips.read_bytes());ips,qa=build(c,b,ROOT)
    a.ips.parent.mkdir(parents=True,exist_ok=True);a.report.parent.mkdir(parents=True,exist_ok=True)
    a.ips.write_bytes(ips);a.report.write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(qa,ensure_ascii=True,indent=2))


if __name__=='__main__':main()
