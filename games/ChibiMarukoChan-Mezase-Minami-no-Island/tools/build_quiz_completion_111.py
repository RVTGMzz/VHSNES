"""Localize actual Quiz completion statistics and the remaining No option."""
import argparse,csv,hashlib,json
from pathlib import Path
from build_content_first_040_fortune import apply_ips,make_ips
ROOT=Path(__file__).resolve().parent.parent
BASE_SHA='0114ab2c5fed3d589221a80ecb45f81a6c83fd05c04b146bd6d7253cc9c0994d'

def build(clean,base,root=ROOT):
 if hashlib.sha256(base).hexdigest()!=BASE_SHA or hashlib.sha256(clean).hexdigest()!='e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956':raise ValueError('Exact110/original required')
 cp={r['unicode']:bytes.fromhex(r['code_hex']) for r in csv.DictReader((root/'translation/codepage/vi_codepage_v4_fe4_native.csv').open(encoding='utf-8-sig'))};out=bytearray(base);allowed=set(range(0x7fdc,0x7fe0));report=[]
 def put(at,data):out[at:at+len(data)]=data;allowed.update(range(at,at+len(data)))
 def enc(t):return b''.join(cp[c] for c in t)
 def record(t,row,col=1,style=None):
  if len(t)+col>28:raise AssertionError('Quiz result row exceeds28columns')
  return (bytes([16,style]) if style is not None else b'')+bytes([14,col,15,row])+enc(t)+bytes.fromhex('816f00')
 plans=[('Mừng bạn qua hết câu hỏi!',10,2,2,0x31c4c),('Tổng câu',9,2,3,0x31c6d),('Lượt trả lời',11,2,None,0x31c90),('Tỷ lệ đúng',13,2,None,0x31cb1),('Đúng lần đầu',23,2,1,0x31cd2),('Không',18,6,None,0x31d36)]
 # One complete unused tail after087's66-byte relocated allowance record.
 if base[0x31c4c:0x31cf5]!=clean[0x31c4c:0x31cf5] or base[0x37fc6:0x38000]!=b'\xff'*58 or clean[0x37fc6:0x38000]!=b'\xff'*58:raise AssertionError('Quiz completion text pools changed')
 if base[0x31d36:0x31d43]!=bytes.fromhex('0e060f12')+'いいえ'.encode('cp932')+bytes.fromhex('816f00'):raise AssertionError('Quiz No source changed')
 payloads=[]
 for text,row,col,style,source in plans:
  data=record(text,row,col,style)
  if source==0x31cb1:data=data[:-1]+bytes([14,25,15,row])+bytes.fromhex('8193816f00')
  payloads.append(data)
 put(0x31c4c,bytes(169));put(0x31d36,bytes(13));pools=[[0x31c4c,0x31cf5],[0x37fc6,0x38000]];placements={}
 for i in sorted(range(len(plans)),key=lambda i:len(payloads[i]),reverse=True):
  fits=[p for p in pools if p[1]-p[0]>=len(payloads[i])]
  if not fits:raise AssertionError('Quiz completion allocation exhausted')
  slot=min(fits,key=lambda p:p[1]-p[0]);at=slot[0];put(at,payloads[i]);slot[0]+=len(payloads[i]);placements[plans[i][-1]]=at;report.append({'text':plans[i][0],'record':hex(at),'bytes':len(payloads[i])})
 # Native bank86 callers pass these complete records to85:804B.
 # Scan executable Quiz code only, and require the observed caller inventory.
 expected={0x31c4c:1,0x31c6d:1,0x31c90:1,0x31cb1:1,0x31cd2:1,0x31d36:3};pointers=[]
 for source,new in placements.items():
  needle=b'\xa0'+((source&32767)|32768).to_bytes(2,'little')+bytes.fromhex('224b8085');sites=[i for i in range(0x30000,0x31147) if base[i:i+7]==needle]
  if len(sites)!=expected[source]:raise AssertionError('Quiz completion caller inventory changed '+hex(source)+' '+str(sites))
  for i in sites:put(i+1,((new&32767)|32768).to_bytes(2,'little'));pointers.append(hex(i+1))
 # Keep counter values, formulas and native formatting. Move only the column
 # from13 to20, leaving labels and the percentage unit separate.
 digits=[]
 for row in (9,11,13,23):
  needle=bytes([169,row,13,133,0]);sites=[i for i in range(0x30c90,0x30d05) if base[i:i+5]==needle]
  if len(sites)!=1:raise AssertionError('Quiz dynamic counter position changed')
  put(sites[0]+2,b'\x14');digits.append({'row':row,'column':20,'operand':hex(sites[0]+2)})
 # Native blanking records contain17 blank glyphs per row. At8px pitch
 # that clears only136px and leaves old text at the right. Keep the native
 # three-step countdown, but clear all32 bitmap tiles in each of its six-row
 # bands using the cartridge's own clear-and-DMA helper85:8D8D.
 stub=bytes.fromhex('08c230da5aa2060048228d8d85681acad0f67afa286b')
 if base[0xf080:0xf080+len(stub)]!=b'\xff'*len(stub) or clean[0xf080:0xf080+len(stub)]!=b'\xff'*len(stub):raise AssertionError('Quiz clear helper padding collision')
 if clean[0x28d8d:0x28d97]!=bytes.fromhex('8bda5a2fe01f00480aeb') or base[0x28d8d:0x28d97]!=clean[0x28d8d:0x28d97]:raise AssertionError('Native bitmap clear-and-DMA helper changed')
 put(0xf080,stub);clear_sites=[]
 for source,row in [(0x9af9,8),(0x9b6a,14),(0x9bdb,20)]:
  old=b'\xa0'+source.to_bytes(2,'little')+bytes.fromhex('224b80852260818590fa');sites=[i for i in range(0x30ff8,0x31040) if base[i:i+len(old)]==old]
  if len(sites)!=1:raise AssertionError('Quiz blanking caller changed')
  put(sites[0],bytes([169,row,0])+bytes.fromhex('2280f081')+b'\xea'*6);clear_sites.append(hex(sites[0]))
 out[0x7fdc:0x7fe0]=bytes(4);s=(sum(out)+510)&65535;out[0x7fdc:0x7fe0]=(s^65535).to_bytes(2,'little')+s.to_bytes(2,'little')
 if any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(base,out))):raise AssertionError('Write escaped spans')
 ips,count=make_ips(clean,out)
 if apply_ips(clean,ips)!=bytes(out):raise AssertionError('IPS replay')
 return ips,{'status':'111_QUIZ_COMPLETION_AND_NO_BINARY_PASS','records':report,'callers':pointers,'dynamic_counters':digits,'native_grading_and_statistics_math_unchanged':True,'full_width_bitmap_clear':{'native_helper':'85:8D8D','rows':[8,25],'columns':32,'three_native_steps_preserved':True,'callers':clear_sites},'retained_native_punctuation':['％'],'IPS_SHA256':hashlib.sha256(ips).hexdigest(),'ROM_SHA256':hashlib.sha256(out).hexdigest(),'whole_game_complete':False}

def main():
 p=argparse.ArgumentParser();p.add_argument('original',type=Path);p.add_argument('baseline_ips',type=Path);p.add_argument('--ips',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args();c=a.original.read_bytes();ips,r=build(c,apply_ips(c,a.baseline_ips.read_bytes()));a.ips.write_bytes(ips);a.report.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,ensure_ascii=True))
if __name__=='__main__':main()

