"""Finish live setup time options and disconnected/mouse device strings."""
import argparse,csv,hashlib,json
from pathlib import Path
from build_content_first_040_fortune import apply_ips,make_ips
ROOT=Path(__file__).resolve().parent.parent
BASE_SHA='9e96f9869c2745db33b504ec7a760acf3eb4faba17fc232fcbb61453ec89033f'

def build(clean,base,root=ROOT):
 if hashlib.sha256(base).hexdigest()!=BASE_SHA or hashlib.sha256(clean).hexdigest()!='e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956':raise ValueError('Exact111/original required')
 cp={r['unicode']:bytes.fromhex(r['code_hex']) for r in csv.DictReader((root/'translation/codepage/vi_codepage_v4_fe4_native.csv').open(encoding='utf-8-sig'))};out=bytearray(base);allowed=set(range(0x7fdc,0x7fe0));cursor=0x2f821;report=[]
 if base[cursor:0x2fa00]!=b'\xff'*479 or clean[cursor:0x2fa00]!=b'\xff'*479:raise AssertionError('Setup string arena changed')
 def put(at,data):out[at:at+len(data)]=data;allowed.update(range(at,at+len(data)))
 def enc(text):return b''.join(cp[c] for c in text)
 def allocate(text,data,old,refs):
  nonlocal cursor
  at=cursor;cursor+=len(data)
  if cursor>0x2fa00:raise AssertionError('Setup text arena overflow')
  put(at,data)
  for ptr in refs:
   if int.from_bytes(base[ptr:ptr+2],'little')!=old&65535:raise AssertionError('Setup native pointer changed '+hex(ptr))
   put(ptr,(at&65535).to_bytes(2,'little'))
  report.append({'Vietnamese':text,'record':hex(at),'bytes':len(data),'native_source':hex(old),'pointers':[hex(p) for p in refs]})
 header=b''
 for text,col,row in [('Thắng mấy ván?',2,10),('Độ khó',2,14),('CPU',2,16),('Thời gian',2,20)]:
  if len(text)+col>28:raise AssertionError('Setup label width')
  # The first row has a native face icon occupying columns 2 and 3.
  header+=bytes([14,4 if row==10 else col,15,row])+enc(text)+bytes.fromhex('816f')
 header+=bytes.fromhex('8198');allocate('Thắng mấy ván? / Độ khó CPU / Thời gian',header,0x28a90,[0x20e41])
 for text,old,refs,col in [('180 giây',0x28b1c,[0x21053],14),('Đến khi thắng',0x28b28,[0x21055],14),('180 giây',0x28b34,[0x21057],14),('Đến khi thắng',0x28b40,[0x21059],14),('Không kết nối',0x28bc6,[0x20dff],10),('Chuột',0x28bde,[0x20e03],None)]:
  native_end=base.find(bytes.fromhex('8198'),old,old+24)
  if native_end<0:raise AssertionError('Native setup field terminator changed')
  if old in (0x28b28,0x28b40,0x28bc6,0x28bde) and base[old:native_end+2]!=clean[old:native_end+2]:raise AssertionError('Expected untranslated setup field changed')
  data=(bytes([14,col]) if col is not None else b'')+enc(text)+bytes.fromhex('816f8198');allocate(text,data,old,refs)
  # All native leaf references were redirected. Drop the now-inactive source.
  put(old,bytes(native_end+2-old))
 out[0x7fdc:0x7fe0]=bytes(4);s=(sum(out)+510)&65535;out[0x7fdc:0x7fe0]=(s^65535).to_bytes(2,'little')+s.to_bytes(2,'little')
 if any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(base,out))):raise AssertionError('Write escaped spans')
 ips,count=make_ips(clean,out)
 if apply_ips(clean,ips)!=bytes(out):raise AssertionError('IPS replay')
 return ips,{'status':'112_SETUP_TIME_AND_DEVICE_STRINGS_BINARY_PASS','records':report,'native_duration_values_and_device_detection_unchanged':True,'IPS_SHA256':hashlib.sha256(ips).hexdigest(),'ROM_SHA256':hashlib.sha256(out).hexdigest(),'whole_game_complete':False}

def main():
 p=argparse.ArgumentParser();p.add_argument('original',type=Path);p.add_argument('baseline_ips',type=Path);p.add_argument('--ips',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args();c=a.original.read_bytes();ips,r=build(c,apply_ips(c,a.baseline_ips.read_bytes()));a.ips.write_bytes(ips);a.report.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,ensure_ascii=True))
if __name__=='__main__':main()
