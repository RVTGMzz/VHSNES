"""Romanize the four character nameplates in the native selection screen."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image
from build_native_setup_headings_101 import decoded
from build_font_menu_runtime_090 import raster
from build_g0_first_boot_title_votri_experimental import encode_chibi,tile_to_4bpp
from render_chibi_resource_package import decode_tile
from decompress_chibi_resource import decompress_resource
from build_content_first_040_fortune import apply_ips,make_ips
BASE_SHA='10975990b087348e48c080d7891721eccef0fdb2d5ed6c108e404cb37bef5eef'
NAMES=[('Maruko',48,120),('Tama',160,120),('Hamaji',48,200),('Nagasawa',160,200)]

def build(clean,base,font):
 if hashlib.sha256(base).hexdigest()!=BASE_SHA or hashlib.sha256(clean).hexdigest()!='e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956':raise ValueError('Exact103/original required')
 out=bytearray(base);gfx=bytearray(decoded(base,0xe100));tm=bytearray(decoded(base,0x17d1c));bg2=decoded(base,0x90000);oldgfx=bytes(gfx);oldmap=bytes(tm)
 if len(gfx)!=9824 or len(tm)!=2048 or len(bg2)!=2048:raise AssertionError('Character resources changed')
 rects={((y//8+yy)*32+x//8+xx) for _,x,y in NAMES for yy in range(2) for xx in range(6)}
 protected={int.from_bytes(m[k*2:k*2+2],'little')&1023 for m in (tm,bg2) for k in range(1024) if m is bg2 or k not in rects}
 free=[i for i in range(len(gfx)//32) if i not in protected];clones={};report=[]
 for name,x0,y0 in NAMES:
  im=Image.new('L',(48,16))
  for y in range(16):
   for x in range(48):
    k=(y0//8+y//8)*32+x0//8+x//8;w=int.from_bytes(tm[k*2:k*2+2],'little');tile=decode_tile(oldgfx,(w&1023)*32,4)
    if (w>>10)&7!=5:raise AssertionError('Unexpected nameplate palette')
    im.putpixel((x,y),11 if 3<=x<45 and 2<=y<14 else tile[7-y%8 if w&0x8000 else y%8][7-x%8 if w&0x4000 else x%8])
  mask=raster(name,font,9,42,12)
  for y in range(12):
   for x in range(42):
    if mask.getpixel((x,y)):im.putpixel((x+3,y+2),9)
  for yy in range(2):
   for xx in range(6):
    bits=bytes(im.getpixel((xx*8+x,yy*8+y)) for y in range(8) for x in range(8))
    if bits not in clones:
     if not free:raise AssertionError('No exclusively owned nameplate tiles')
     tid=free.pop(0);clones[bits]=tid;gfx[tid*32:(tid+1)*32]=tile_to_4bpp(bits)
    k=(y0//8+yy)*32+x0//8+xx;w=int.from_bytes(tm[k*2:k*2+2],'little');tm[k*2:k*2+2]=((w&0x3c00)|clones[bits]).to_bytes(2,'little')
  report.append({'name':name,'native_rect':[x0,y0,48,16],'palette_preserved':5})
 used=protected|set(clones.values())
 for i in range(len(gfx)//32):
  if i not in used:gfx[i*32:(i+1)*32]=bytes(32)
 for tid in protected:
  if gfx[tid*32:(tid+1)*32]!=oldgfx[tid*32:(tid+1)*32]:raise AssertionError('Other BG1/BG2 tile changed')
 if any(tm[k*2:k*2+2]!=oldmap[k*2:k*2+2] for k in range(1024) if k not in rects):raise AssertionError('Unrelated map cell changed')
 allowed=set(range(0x7fdc,0x7fe0));resources=[]
 for data,at,limit in [(gfx,0xe100,0xf17a),(tm,0x17d1c,0x18000)]:
  _,h,_=decompress_resource(base,at);packed=encode_chibi(bytes(data));blob=(len(packed)+2).to_bytes(2,'little')+packed;span=max(h.span,len(blob))
  if at+span>limit or clean[at:at+span]!=b'\xff'*span or base[at+h.span:at+span]!=b'\xff'*(span-h.span):raise AssertionError(f'Resource collision: {at:x}, {len(blob)}')
  out[at:at+span]=blob+b'\xff'*(span-len(blob));allowed.update(range(at,at+span))
  if decoded(out,at)!=data:raise AssertionError('Codec roundtrip')
  resources.append({'offset':hex(at),'bytes':len(blob),'old_bytes':h.span})
 out[0x7fdc:0x7fe0]=bytes(4);s=(sum(out)+510)&65535;out[0x7fdc:0x7fe0]=(s^65535).to_bytes(2,'little')+s.to_bytes(2,'little')
 if any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(base,out))):raise AssertionError('Write escaped guarded spans')
 ips,count=make_ips(clean,out)
 if apply_ips(clean,ips)!=bytes(out):raise AssertionError('IPS replay')
 return ips,{'status':'104_CHARACTER_NAMES_BINARY_PASS','names':report,'resources':resources,'protected_BG1_BG2_tiles':len(protected),'all_other_map_cells_preserved':True,'palette_unchanged':True,'IPS_SHA256':hashlib.sha256(ips).hexdigest(),'ROM_SHA256':hashlib.sha256(out).hexdigest(),'whole_game_complete':False}

def main():
 p=argparse.ArgumentParser();p.add_argument('original',type=Path);p.add_argument('baseline_ips',type=Path);p.add_argument('--font',type=Path,required=True);p.add_argument('--ips',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args();c=a.original.read_bytes();ips,r=build(c,apply_ips(c,a.baseline_ips.read_bytes()),a.font);a.ips.write_bytes(ips);a.report.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(r))
if __name__=='__main__':main()
