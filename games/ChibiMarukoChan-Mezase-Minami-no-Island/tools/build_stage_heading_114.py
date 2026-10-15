"""Replace the live Japanese stage-selection heading with a static VI banner."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image
from build_native_setup_headings_101 import decoded
from build_font_menu_runtime_090 import raster
from build_g0_first_boot_title_votri_experimental import encode_chibi,tile_to_4bpp
from build_fortune_rank_092 import address
from render_chibi_resource_package import decode_tile
from build_content_first_040_fortune import apply_ips,make_ips
BASE_SHA='fa9344e48434db72ca595de79e25051d57d5d6c13b7e7da9a3f9a724603ae5db'

def build(clean,base,font):
 if hashlib.sha256(base).hexdigest()!=BASE_SHA or hashlib.sha256(clean).hexdigest()!='e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956':raise ValueError('Exact113/original required')
 out=bytearray(base);allowed=set(range(0x7fdc,0x7fe0))
 def put(at,data):out[at:at+len(data)]=data;allowed.update(range(at,at+len(data)))
 # Tail of the retired intro title resource, after109's complete palette.
 # This is ownership-based reclamation, not a search for FF byte runs.
 if base[0x12290:0x12293]!=address(0xeff0).to_bytes(3,'little') or base[0x121f6:0x121f9]!=address(0xd5d31).to_bytes(3,'little') or base[0x121fb:0x121fe]!=address(0xd61be).to_bytes(3,'little') or base[0xd6512:0xd6d45]!=clean[0xd6512:0xd6d45]:raise AssertionError('Retired intro tail ownership changed')
 if base[0xd6310:0xd6312]!=bytes.fromhex('ff01'):raise AssertionError('109 palette boundary changed')
 cursor=0xd6512;alloc=[]
 def asset(data):
  nonlocal cursor
  packed=encode_chibi(bytes(data));blob=(len(packed)+2).to_bytes(2,'little')+packed;at=cursor;cursor+=len(blob)
  if cursor>0xd6d45:raise AssertionError('Owned intro tail overflow')
  put(at,blob)
  if decoded(out,at)!=data:raise AssertionError('Stage resource codec roundtrip')
  alloc.append({'source':hex(at),'compressed_bytes':len(blob),'decoded_bytes':len(data)});return at
 gfx=decoded(base,0x11a44c);tm=bytearray(decoded(base,0xd802b));oldmap=bytes(tm)
 if len(gfx)!=8192 or len(tm)!=2048:raise AssertionError('Native stage BG1 geometry changed')
 rect={y*32+x for y in range(1,4) for x in range(6,26)}
 protected={int.from_bytes(tm[k*2:k*2+2],'little')&1023 for k in range(1024) if k not in rect}
 if any(t in protected for t in range(151,256)):raise AssertionError('Native BG1 high tiles no longer free')
 canvas=Image.new('L',(160,24))
 for yy in range(3):
  for xx in range(20):
   k=(yy+1)*32+xx+6;w=int.from_bytes(tm[k*2:k*2+2],'little')
   if w>>10&7!=7:raise AssertionError('Stage banner palette changed')
   tile=decode_tile(gfx,(w&1023)*32,4)
   for y in range(8):
    for x in range(8):canvas.putpixel((xx*8+x,yy*8+y),tile[7-y if w&0x8000 else y][7-x if w&0x4000 else x])
 mask=raster('Chọn sân chơi',font,16,156,20)
 for y in range(20):
  for x in range(156):
   if mask.getpixel((x,y)):
    for dy in (-1,0,1):
     for dx in (-1,0,1):canvas.putpixel((x+2+dx,y+2+dy),8)
 for y in range(20):
  for x in range(156):
   if mask.getpixel((x,y)):canvas.putpixel((x+2,y+2),11)
 tiles={};partial=bytearray()
 for yy in range(3):
  for xx in range(20):
   bits=bytes(canvas.getpixel((xx*8+x,yy*8+y)) for y in range(8) for x in range(8))
   if bits not in tiles:tiles[bits]=151+len(tiles);partial.extend(tile_to_4bpp(bits))
   k=(yy+1)*32+xx+6;tm[k*2:k*2+2]=(0x2000|7<<10|tiles[bits]).to_bytes(2,'little')
 if len(tiles)>105 or any(tm[k*2:k*2+2]!=oldmap[k*2:k*2+2] for k in range(1024) if k not in rect):raise AssertionError('Stage heading escaped its tiles')
 fontsrc=asset(partial);mapsrc=asset(tm);refs=[]
 for pkg in (0x122c0,0x122e6,0x1230c):
  mapref=pkg+4+5;objref=pkg+4+6*5
  if base[mapref:mapref+3]!=address(0xd802b).to_bytes(3,'little') or base[objref:objref+3]!=address(0xc706f).to_bytes(3,'little') or base[objref-2:objref]!=bytes.fromhex('0070'):raise AssertionError('Stage native package owner changed')
  put(mapref,address(mapsrc).to_bytes(3,'little'));put(objref,address(fontsrc).to_bytes(3,'little'));put(objref-2,((0x2000+151*32)//2).to_bytes(2,'little'));refs.extend([hex(mapref),hex(objref)])
 if base[0x219c8:0x219d2]!=bytes.fromhex('a96200a0000422dfa684'):raise AssertionError('Stage heading actor62 changed')
 put(0x219c8,b'\xea'*10)
 out[0x7fdc:0x7fe0]=bytes(4);s=(sum(out)+510)&65535;out[0x7fdc:0x7fe0]=(s^65535).to_bytes(2,'little')+s.to_bytes(2,'little')
 if any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(base,out))):raise AssertionError('Write escaped spans')
 ips,_=make_ips(clean,out)
 if apply_ips(clean,ips)!=bytes(out):raise AssertionError('IPS replay')
 return ips,{'status':'114_STAGE_SELECTION_HEADING_BINARY_PASS','heading':'Chọn sân chơi','resources':alloc,'new_BG1_tiles':len(tiles),'native_scene_and_palette_preserved':True,'redirected_package_pointers':refs,'only_native_heading_actor62_disabled':True,'IPS_SHA256':hashlib.sha256(ips).hexdigest(),'ROM_SHA256':hashlib.sha256(out).hexdigest(),'whole_game_complete':False}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('original',type=Path);p.add_argument('baseline_ips',type=Path);p.add_argument('--font',type=Path,required=True);p.add_argument('--ips',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args();c=a.original.read_bytes();ips,r=build(c,apply_ips(c,a.baseline_ips.read_bytes()),a.font);a.ips.write_bytes(ips);a.report.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,ensure_ascii=True))
if __name__=='__main__':main()
