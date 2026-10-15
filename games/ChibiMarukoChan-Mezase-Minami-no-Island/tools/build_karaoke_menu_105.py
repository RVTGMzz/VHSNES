"""Translate native Karaoke title and start choices, preserving the stage art."""
import argparse,csv,hashlib,json
from pathlib import Path
from PIL import Image
from build_native_setup_headings_101 import decoded
from build_font_menu_runtime_090 import raster
from build_g0_first_boot_title_votri_experimental import encode_chibi
from decompress_chibi_resource import decompress_resource
from build_content_first_040_fortune import apply_ips,make_ips
ROOT=Path(__file__).resolve().parent.parent
BASE_SHA='0ba7dd076961cf1d5472f313b9514ecbd915ab83d1d7ff49f879c9bb012e40a8'

def build(clean,base,font,root=ROOT):
 if hashlib.sha256(base).hexdigest()!=BASE_SHA or hashlib.sha256(clean).hexdigest()!='e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956':raise ValueError('Exact104/original required')
 out=bytearray(base);allowed=set(range(0x7fdc,0x7fe0));raw,h,_=decompress_resource(base,0x12de52);old=decoded(base,0x12de52);gfx=bytearray(old)
 title='Rock của ông Harikiri';mask=raster(title,font,11,158,14);im=Image.new('L',(160,16))
 for y in range(14):
  for x in range(158):
   if mask.getpixel((x,y)):
    for dy in (-1,0,1):
     for dx in (-1,0,1):im.putpixel((x+1+dx,y+1+dy),1)
 for y in range(14):
  for x in range(158):
   if mask.getpixel((x,y)):im.putpixel((x+1,y+1),3)
 tids=[0xa0,0xa2,0xa4,0xa6,0xa8,0xaa,0xac,0xae,0xc2,0xc4];changed=set()
 for j,t in enumerate(tids):
  # Encode the styled palette indices directly.
  from build_g0_first_boot_title_votri_experimental import tile_to_4bpp
  for yy in range(2):
   for xx in range(2):
    tid=t+yy*16+xx;gfx[tid*32:(tid+1)*32]=tile_to_4bpp(bytes(im.getpixel((j*16+xx*8+x,yy*8+y)) for y in range(8) for x in range(8)));changed.add(tid)
 for tid in (0xc0,0xc1,0xd0,0xd1):gfx[tid*32:(tid+1)*32]=bytes(32);changed.add(tid)
 if any(gfx[i*32:(i+1)*32]!=old[i*32:(i+1)*32] for i in range(len(gfx)//32) if i not in changed):raise AssertionError('Unrelated Karaoke sprite tile changed')
 if h.postprocess:
  inverse=bytearray(len(gfx));order=(0,8,1,9,2,10,3,11,4,12,5,13,6,14,7,15)
  for pos in range(0,len(gfx),16):
   for dst,src in enumerate(order):inverse[pos+src]=gfx[pos+dst]
 else:inverse=gfx
 packed=encode_chibi(bytes(inverse));blob=(len(packed)+2|(0x8000 if h.postprocess else 0)).to_bytes(2,'little')+packed
 if len(blob)>h.span:raise AssertionError('Karaoke sprite overflow')
 out[0x12de52:0x12de52+h.span]=blob+b'\xff'*(h.span-len(blob));allowed.update(range(0x12de52,0x12de52+h.span))
 if decoded(out,0x12de52)!=gfx:raise AssertionError('Karaoke codec roundtrip')
 cp={r['unicode']:bytes.fromhex(r['code_hex']) for r in csv.DictReader((root/'translation/codepage/vi_codepage_v4_fe4_native.csv').open(encoding='utf-8-sig'))};fields=[]
 for at,jp,vi in [(0x2b7c9,'メロディーありでスタート','Chơi có nhạc'),(0x2b7ef,'メロディーなしでスタート','Chơi không nhạc')]:
  lo=at-8;end=at+len(jp.encode('cp932'))
  if base[lo:at]!=b' '*8 or base[at:end]!=jp.encode('cp932') or base[lo-4:lo][:3]!=bytes([14,0,15]):raise AssertionError('Karaoke option record changed')
  data=b''.join(cp[c] for c in vi);data+=cp[' ']*((end-lo-len(data))//2)
  if len(data)!=end-lo:raise AssertionError('Karaoke option budget')
  out[lo:end]=data;out[lo-3]=3;allowed.update(range(lo,end));allowed.add(lo-3);fields.append(vi)
 out[0x7fdc:0x7fe0]=bytes(4);s=(sum(out)+510)&65535;out[0x7fdc:0x7fe0]=(s^65535).to_bytes(2,'little')+s.to_bytes(2,'little')
 if any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(base,out))):raise AssertionError('Write escaped spans')
 ips,count=make_ips(clean,out)
 if apply_ips(clean,ips)!=bytes(out):raise AssertionError('IPS replay')
 return ips,{'status':'105_KARAOKE_MENU_BINARY_PASS','title':title,'options':fields,'sprite_bytes':len(blob),'sprite_budget':h.span,'all_other_sprite_tiles_unchanged':True,'IPS_SHA256':hashlib.sha256(ips).hexdigest(),'ROM_SHA256':hashlib.sha256(out).hexdigest(),'whole_game_complete':False}

def main():
 p=argparse.ArgumentParser();p.add_argument('original',type=Path);p.add_argument('baseline_ips',type=Path);p.add_argument('--font',type=Path,required=True);p.add_argument('--ips',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args();c=a.original.read_bytes();ips,r=build(c,apply_ips(c,a.baseline_ips.read_bytes()),a.font);a.ips.write_bytes(ips);a.report.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,ensure_ascii=True))
if __name__=='__main__':main()
