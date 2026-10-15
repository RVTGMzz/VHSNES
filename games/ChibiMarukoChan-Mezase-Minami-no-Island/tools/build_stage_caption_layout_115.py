"""Keep all15 complete stage titles inside the native footer paper."""
import argparse,csv,hashlib,json,textwrap
from pathlib import Path
from build_content_first_040_fortune import apply_ips,make_ips
from build_native_setup_headings_101 import decoded
from build_g0_first_boot_title_votri_experimental import encode_chibi
ROOT=Path(__file__).resolve().parent.parent
BASE_SHA='2cec214b1adb3618ad211427f8ba2269fd602bd668d6e8fba8ebf36d88bc4891'

def build(clean,base,root=ROOT):
 if hashlib.sha256(base).hexdigest()!=BASE_SHA or hashlib.sha256(clean).hexdigest()!='e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956':raise ValueError('Exact114/original required')
 out=bytearray(base);allowed=set(range(0x7fdc,0x7fe0));cp={r['unicode']:bytes.fromhex(r['code_hex']) for r in csv.DictReader((root/'translation/codepage/vi_codepage_v4_fe4_native.csv').open(encoding='utf-8-sig'))};rows=list(csv.DictReader((root/'translation/source/stage_names_batch01_vi.csv').open(encoding='utf-8-sig')))
 def put(at,data):out[at:at+len(data)]=data;allowed.update(range(at,at+len(data)))
 def enc(text):return b''.join(cp[c] for c in text)
 records=[];report=[]
 for i,row in enumerate(rows):
  game,stage=divmod(i,5);title=row['vi_full'];caption=f'{stage+1}. {title}';lines=textwrap.wrap(caption,width=17,break_long_words=False,break_on_hyphens=False)
  if not 1<=len(lines)<=2 or any(len(t)>17 for t in lines) or ' '.join(lines)!=caption:raise AssertionError('Stage wrapping changed content')
  data=bytes.fromhex('1001')
  for j,line in enumerate(lines):
   # Native BG3 scrolls6px left. Keep actual screen ink inside62..198,
   # clear of the flowers on both sides of the paper.
   column=(31-len(line))//2;rownum=24 if len(lines)==1 else 23+2*j
   data+=bytes([14,column,15,rownum])+enc(line)+bytes.fromhex('816f')
  data+=b'\x00';records.append(data);report.append({'game':game,'stage':stage,'title':title,'lines':lines,'bytes':len(data),'table_pointer':hex(0x21b9d+game*16+stage*2)})
 if len(rows)!=15:raise AssertionError('Stage inventory')
 # These pools are owned by110, after all original stage/lyric references moved.
 pools=[[0x2cba3,0x2cd74],[0x2f67e,0x2f800]]
 for lo,hi in pools:put(lo,bytes(hi-lo))
 for i in sorted(range(15),key=lambda i:len(records[i]),reverse=True):
  choices=[p for p in pools if p[1]-p[0]>=len(records[i])]
  if not choices:raise AssertionError('Stage-owned pools exhausted')
  slot=min(choices,key=lambda p:p[1]-p[0]);at=slot[0];slot[0]+=len(records[i]);put(at,records[i]);put(int(report[i]['table_pointer'],16),(at&65535).to_bytes(2,'little'));report[i]['record']=hex(at)
 # Extend just the paper's bottom edge by8px. Short titles stay centered on
 # row24; long titles occupy rows23/25 within the enlarged footer.
 tm=bytearray(decoded(base,0xd67d8));original=bytes(tm)
 for x in range(6,26):
  tm[(27*32+x)*2:(27*32+x+1)*2]=original[(26*32+x)*2:(26*32+x+1)*2]
  tm[(26*32+x)*2:(26*32+x+1)*2]=original[(25*32+x)*2:(25*32+x+1)*2]
 packed=encode_chibi(bytes(tm));blob=(len(packed)+2).to_bytes(2,'little')+packed
 if len(blob)>0xd6d45-0xd67d8 or base[0xd6b56:0xd6d45]!=clean[0xd6b56:0xd6d45]:raise AssertionError('114-owned map tail collision')
 put(0xd67d8,blob+b'\xff'*(0xd6d45-0xd67d8-len(blob)))
 if decoded(out,0xd67d8)!=tm:raise AssertionError('Footer map codec')
 for game in range(3):
  if out[0x21ba7+game*16:0x21bad+game*16]!=base[0x21ba7+game*16:0x21bad+game*16]:raise AssertionError('Unused stage table slots changed')
 out[0x7fdc:0x7fe0]=bytes(4);s=(sum(out)+510)&65535;out[0x7fdc:0x7fe0]=(s^65535).to_bytes(2,'little')+s.to_bytes(2,'little')
 if any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(base,out))):raise AssertionError('Write escaped spans')
 ips,_=make_ips(clean,out)
 if apply_ips(clean,ips)!=bytes(out):raise AssertionError('IPS replay')
 return ips,{'status':'115_FULL_STAGE_CAPTIONS_IN_PAPER_BINARY_PASS','stages':report,'total_record_bytes':sum(map(len,records)),'footer_map_bytes':len(blob),'native_stage_IDs_and_input_unchanged':True,'IPS_SHA256':hashlib.sha256(ips).hexdigest(),'ROM_SHA256':hashlib.sha256(out).hexdigest(),'whole_game_complete':False}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('original',type=Path);p.add_argument('baseline_ips',type=Path);p.add_argument('--ips',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args();c=a.original.read_bytes();ips,r=build(c,apply_ips(c,a.baseline_ips.read_bytes()));a.ips.write_bytes(ips);a.report.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in r.items() if k!='stages'}))
if __name__=='__main__':main()
