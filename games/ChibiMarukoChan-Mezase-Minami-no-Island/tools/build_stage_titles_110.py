"""Install all15 full Vietnamese stage titles through their actual native table."""
import argparse,csv,hashlib,json
from pathlib import Path
from build_rules_explanations_109 import rules_selector
from build_quiz_layout_087 import spacing_stub,destination_stub,wrap_stub
from build_content_first_040_fortune import apply_ips,make_ips
ROOT=Path(__file__).resolve().parent.parent
BASE_SHA='ae80e44c995f1c2eb209974dd7594c974c380a8edd490df02c80efa8fdf28770'

def stage_selector(a):rules_selector(a,stage=True)

def build(clean,base,root=ROOT):
 if hashlib.sha256(base).hexdigest()!=BASE_SHA or hashlib.sha256(clean).hexdigest()!='e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956':raise ValueError('Exact109/original required')
 cp={r['unicode']:bytes.fromhex(r['code_hex']) for r in csv.DictReader((root/'translation/codepage/vi_codepage_v4_fe4_native.csv').open(encoding='utf-8-sig'))};rows=list(csv.DictReader((root/'translation/source/stage_names_batch01_vi.csv').open(encoding='utf-8-sig')))
 if len(rows)!=15 or base[0x2cba3:0x2cd74]!=clean[0x2cba3:0x2cd74] or base[0x2f67e:0x2f800]!=b'\xff'*0x182:raise AssertionError('Stage source/pool identity changed')
 out=bytearray(base);allowed=set(range(0x7fdc,0x7fe0));records=[];report=[]
 def put(at,data):out[at:at+len(data)]=data;allowed.update(range(at,at+len(data)))
 def enc(text):return b''.join(cp[c] for c in text)
 for i,row in enumerate(rows):
  at=0x2cba3+i*31;jp=row['source_jp'];vi=row['vi_full'];mode,stage=divmod(i,5);ptr=0x21b9d+mode*16+stage*2
  if int.from_bytes(base[ptr:ptr+2],'little')!=(at&65535) or int(row['file_offset'],16)!=at+10 or clean[at:at+6]!=bytes.fromhex('10020e050f18') or clean[at+12:at+28].decode('cp932').rstrip(' ')!=jp or clean[at+28:at+31]!=bytes.fromhex('816f00'):raise AssertionError('Native stage record/table changed '+hex(at))
  if len(vi)+3>28:raise AssertionError('Stage title would wrap beyond footer')
  data=bytes.fromhex('10020e010f18')+enc(str(stage+1))+bytes.fromhex('1001')+enc(' '+vi)+bytes.fromhex('816f00');records.append(data);report.append({'game':mode,'stage':stage,'Vietnamese':vi,'pointer':hex(ptr),'source':hex(at),'bytes':len(data)})
 put(0x2cba3,bytes(465));pools=[[0x2cba3,0x2cd74],[0x2f67e,0x2f800]]
 for i in sorted(range(15),key=lambda i:len(records[i]),reverse=True):
  fits=[p for p in pools if p[1]-p[0]>=len(records[i])]
  if not fits:raise AssertionError('Stage pool exhausted')
  slot=min(fits,key=lambda p:p[1]-p[0]);at=slot[0];put(at,records[i]);slot[0]+=len(records[i]);put(int(report[i]['pointer'],16),(at&65535).to_bytes(2,'little'));report[i]['record']=hex(at)
 for mode in range(3):
  if out[0x21ba7+mode*16:0x21bad+mode*16]!=base[0x21ba7+mode*16:0x21bad+mode*16]:raise AssertionError('Native three unused stage-table slots changed')
 for at,old,new in [(0x2fb80,spacing_stub(True,rules_selector),spacing_stub(True,stage_selector)),(0x2fc00,spacing_stub(False,rules_selector),spacing_stub(False,stage_selector)),(0x2fc80,wrap_stub(rules_selector),wrap_stub(stage_selector)),(0x2fe00,destination_stub(rules_selector),destination_stub(stage_selector))]:
  if base[at:at+len(old)]!=old or len(new)!=len(old) or len(new)>128:raise AssertionError('Stage compact geometry anchor changed')
  put(at,new)
 out[0x7fdc:0x7fe0]=bytes(4);s=(sum(out)+510)&65535;out[0x7fdc:0x7fe0]=(s^65535).to_bytes(2,'little')+s.to_bytes(2,'little')
 if any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(base,out))):raise AssertionError('Write escaped spans')
 ips,count=make_ips(clean,out)
 if apply_ips(clean,ips)!=bytes(out):raise AssertionError('IPS replay')
 return ips,{'status':'110_ALL_15_STAGE_TITLES_BINARY_PASS','stages':report,'native_table_order_and_unused_slots_preserved':True,'IPS_SHA256':hashlib.sha256(ips).hexdigest(),'ROM_SHA256':hashlib.sha256(out).hexdigest(),'whole_game_complete':False}

def main():
 p=argparse.ArgumentParser();p.add_argument('original',type=Path);p.add_argument('baseline_ips',type=Path);p.add_argument('--ips',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args();c=a.original.read_bytes();ips,r=build(c,apply_ips(c,a.baseline_ips.read_bytes()));a.ips.write_bytes(ips);a.report.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in r.items() if k!='stages'}))
if __name__=='__main__':main()
