"""Translate native credits roles and correct one canonical Karaoke lyric."""
import argparse,csv,hashlib,json
from pathlib import Path
from build_content_first_040_fortune import apply_ips,make_ips
from build_quiz_layout_087 import Assembly,spacing_stub,destination_stub,wrap_stub
from layout_contexts_109 import rules_selector
ROOT=Path(__file__).resolve().parent.parent
BASE_SHA='30aa68f493d01844ed2d421394b85879e99b9fa98a4bb4923fed591be2dbdfb0'

def credit_bank_helper():
 a=Assembly();a.emit(0xaf,0x86,0x1f,0,0x29,0x7f,0);a.cmp16(3);a.branch(0xd0,'ret')
 a.emit(0xaf,0x94,0x1f,0);a.cmp16(0xded4);a.branch(0x90,'story');a.cmp16(0xe2fb);a.branch(0xb0,'story')
 a.emit(0xa9,0,0,0x6b);a.label('story');a.emit(0xa9,3,0);a.label('ret');a.emit(0x6b)
 return a.assemble()

def credit_selector(a):
 # Replace only the source-bank load in the established selector. The helper
 # maps credits to bank0 (native13px); all other contexts receive their bank.
 start=len(a.code);rules_selector(a,stage=True)
 if a.code[start:start+7]!=bytes.fromhex('af861f00297f00'):raise AssertionError('Selector entry changed')
 a.code[start:start+7]=bytes.fromhex('2296f081eaeaea')

def build(clean,base,root=ROOT):
 if hashlib.sha256(base).hexdigest()!=BASE_SHA or hashlib.sha256(clean).hexdigest()!='e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956':raise ValueError('Exact112/original required')
 cp={r['unicode']:bytes.fromhex(r['code_hex']) for r in csv.DictReader((root/'translation/codepage/vi_codepage_v4_fe4_native.csv').open(encoding='utf-8-sig'))};out=bytearray(base);allowed=set(range(0x7fdc,0x7fe0));report=[]
 def put(at,data):out[at:at+len(data)]=data;allowed.update(range(at,at+len(data)))
 def enc(t):
  data=b''
  for ch in t:
   glyph=cp.get(ch)
   if glyph is None:
    glyph=ch.encode('cp932')
    if len(glyph)!=2 or glyph in cp.values():raise AssertionError('Native staff glyph collision '+ch)
   data+=glyph
  return data
 plans=json.loads((root/'translation/runtime/credits_roles_113.json').read_text(encoding='utf-8'))
 if len(plans)!=19 or base[0x1ded4:0x1e2fb]!=clean[0x1ded4:0x1e2fb] or base[0x1dea6:0x1ded4]!=clean[0x1dea6:0x1ded4]:raise AssertionError('Native credits ownership changed')
 cursor=0x1ded4;put(cursor,bytes(0x1e2fb-cursor))
 for i,lines in enumerate(plans):
  old=int.from_bytes(clean[0x1dea6+2*i:0x1dea8+2*i],'little');data=b''
  if not 1<=len(lines)<=2:raise AssertionError('Credit page line count')
  for j,line in enumerate(lines):
   if len(line)>19:raise AssertionError('Native credits row width')
   data+=bytes([14,(19-len(line))//2,15,23+j*2])+enc(line)+bytes.fromhex('816f')
  data+=b'\x00'
  if cursor+len(data)>0x1e2fb:raise AssertionError('Native credits pool exhausted')
  put(cursor,data);put(0x1dea6+2*i,(cursor&65535).to_bytes(2,'little'));report.append({'native_record':hex(old),'new_record':hex(cursor),'lines':lines,'bytes':len(data)});cursor+=len(data)
 # 104 explicitly retired/padded this resource tail. 111's helper endsF096.
 helper=credit_bank_helper()
 if base[0xf096:0xf096+len(helper)]!=b'\xff'*len(helper):raise AssertionError('Owned104 padding collision')
 put(0xf096,helper)
 for at,fn in [(0x2fb80,lambda s:spacing_stub(True,s)),(0x2fc00,lambda s:spacing_stub(False,s)),(0x2fc80,wrap_stub),(0x2fe00,destination_stub)]:
  old=fn(lambda a:rules_selector(a,stage=True));new=fn(credit_selector)
  if len(new)!=len(old) or len(new)>128 or base[at:at+len(old)]!=old:raise AssertionError('Credits selector hook changed')
  put(at,new)
 # Page9 alone: preserve original native style controls and second canonical
 # paragraph; replace conditional desire with the source's obligation.
 lyric=json.loads((root/'translation/runtime/karaoke_semantic_113.json').read_text(encoding='utf-8'))
 oldpage=0x2f4f2
 if int.from_bytes(base[0x2b370:0x2b372],'little')!=oldpage&65535:raise AssertionError('Karaoke9 pointer changed')
 data=b'\x10\x01'
 for text,row in [(lyric['Vietnamese'],19),('Phải rèn thể lực cho thật khỏe',23)]:
  data+=bytes([14,1,15,row]);col=1
  for word in text.split(' '):
   space=col>1
   if col+len(word)+int(space)>28:
    row+=2;data+=bytes.fromhex('816f')+bytes([14,1,15,row]);col=1;space=False
   if space:data+=cp[' '];col+=1
   data+=enc(word);col+=len(word)
  data+=bytes.fromhex('816f')
 data+=b'\x00'
 if len(data)>151:raise AssertionError('Owned Karaoke page overflow')
 put(oldpage,data+bytes(151-len(data)))
 out[0x7fdc:0x7fe0]=bytes(4);checksum=(sum(out)+510)&65535;out[0x7fdc:0x7fe0]=(checksum^65535).to_bytes(2,'little')+checksum.to_bytes(2,'little')
 if any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(base,out))):raise AssertionError('Write escaped owned spans')
 ips,_=make_ips(clean,out)
 if apply_ips(clean,ips)!=bytes(out):raise AssertionError('IPS replay')
 return ips,{'status':'113_CREDITS_ROLES_AND_LYRIC_BINARY_PASS','credits':report,'credits_bytes':cursor-0x1ded4,'original_staff_names_preserved':True,'credits_native_pitch':13,'other_context_spacing_unchanged':True,'Karaoke':lyric,'Karaoke_page_bytes':len(data),'IPS_SHA256':hashlib.sha256(ips).hexdigest(),'ROM_SHA256':hashlib.sha256(out).hexdigest(),'whole_game_complete':False}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('original',type=Path);p.add_argument('baseline_ips',type=Path);p.add_argument('--ips',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args();ips,r=build(a.original.read_bytes(),apply_ips(a.original.read_bytes(),a.baseline_ips.read_bytes()));a.ips.write_bytes(ips);a.report.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in r.items() if k!='credits'},ensure_ascii=True))
if __name__=='__main__':main()
