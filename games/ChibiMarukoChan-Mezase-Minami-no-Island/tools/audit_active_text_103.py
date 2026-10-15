"""Audit actual Quiz pointer tables and all157 Fortune source fields.

This checks active text encoding, not graphics, semantic accuracy or a full
playthrough. Original Japanese copies retained by relocation are excluded.
"""
import argparse,csv,hashlib,json
from pathlib import Path
from build_content_first_040_fortune import apply_ips
ROOT=Path(__file__).resolve().parent.parent

def audit(rom,root=ROOT):
 rows=list(csv.DictReader((root/'translation/codepage/vi_codepage_v4_fe4_native.csv').open(encoding='utf-8-sig')))
 cp={bytes.fromhex(r['code_hex']):r['unicode'] for r in rows}
 if len(cp)!=160:raise AssertionError('Reviewed V2 codepage changed')
 def record(at,limit=512):
  start=at;text='';native=[];controls=[]
  while at<start+limit:
   b=rom[at]
   if b in (14,15):at+=2;continue
   if b==0:break
   if b==0x10:
    controls.append({'offset':hex(at),'bytes':rom[at:at+2].hex()});at+=2;continue
   if b==0x20:text+=' ';at+=1;continue
   if rom[at:at+2]==b'\x81\x6f':text+=' / ';at+=2;continue
   pair=bytes(rom[at:at+2])
   if pair in cp:text+=cp[pair];at+=2;continue
   if b<0x80:raise AssertionError(f'Unrecognized native control {b:02X} at {at:X}')
   try:ch=pair.decode('cp932')
   except UnicodeDecodeError:ch='?'
   text+=ch;native.append({'offset':hex(at),'bytes':pair.hex(),'character':ch});at+=2
  else:raise AssertionError(f'Unterminated native record {start:X}')
  return {'ROM_offset':hex(start),'text':text.strip(' /'),'native_non_V2_glyphs':native,'preserved_controls':controls}
 groups={};unexpected=[];intentional=[]
 for name,tables in [('Quiz_questions',(0x31147,)),('Quiz_choices',(0x31217,0x3127f,0x312e7)),('Quiz_explanation_pages',(0x3134f,0x313b7,0x3141f))]:
  fields=[]
  for table in tables:
   for slot in range(50):
    ptr=int.from_bytes(rom[table+slot*2:table+slot*2+2],'little')
    if ptr<0x8000:raise AssertionError('Native bank06 pointer escaped ROM')
    row={'table':hex(table),'slot':slot,**record(0x30000+ptr-0x8000)};fields.append(row)
    if row['native_non_V2_glyphs']:
     known=name=='Quiz_choices' and slot==39 and table in (0x31217,0x312e7) and ''.join(v['character'] for v in row['native_non_V2_glyphs']) in ('一雄','和雄')
     (intentional if known else unexpected).append({'group':name,**row})
  groups[name]=fields
 relocated={0x2bd5e:0x175ae,0x2c86b:0x2f151,0x2ca7d:0x2f189,0x2cadd:0x2f195};fortune=[]
 for path in sorted((root/'translation/source').glob('fortune_batch01_part*_vi.csv')):
  for source in csv.DictReader(path.open(encoding='utf-8-sig')):
   original=int(source['file_offset'],16)
   at=original-4 if original not in relocated else 0x28000+int.from_bytes(rom[relocated[original]:relocated[original]+2],'little')-0x8000
   row={'original_source':hex(original),**record(at,200)};fortune.append(row)
   if row['native_non_V2_glyphs']:unexpected.append({'group':'Fortune',**row})
 if len(fortune)!=157 or len({r['original_source'] for r in fortune})!=157:raise AssertionError('Fortune source inventory changed')
 groups['Fortune']=fortune
 return {'status':'PASS_ACTIVE_TEXT_ENCODING' if not unexpected else 'FAIL_UNEXPECTED_NATIVE_TEXT','ROM_SHA256':hashlib.sha256(rom).hexdigest(),'scope_counts':{k:len(v) for k,v in groups.items()},'unexpected_native_text':unexpected,'intentional_Kazuo_Kanji_choices':intentional,'age_nine_question':groups['Quiz_questions'][18],'mother_explanation':groups['Quiz_explanation_pages'][20],'records':groups,'graphics_audited':False,'semantic_accuracy_certified':False,'whole_game_complete':False}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('original',type=Path);p.add_argument('ips',type=Path);p.add_argument('--report',type=Path,required=True);a=p.parse_args();clean=a.original.read_bytes()
 if hashlib.sha256(clean).hexdigest()!='e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956':p.error('Exact original ROM required')
 r=audit(apply_ips(clean,a.ips.read_bytes()));r['IPS_SHA256']=hashlib.sha256(a.ips.read_bytes()).hexdigest();a.report.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:r[k] for k in ('status','scope_counts','unexpected_native_text','intentional_Kazuo_Kanji_choices')},ensure_ascii=True))
 if r['unexpected_native_text']:raise SystemExit(2)
if __name__=='__main__':main()
