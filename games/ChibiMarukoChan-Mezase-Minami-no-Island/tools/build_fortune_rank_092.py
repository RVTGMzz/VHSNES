"""Translate all five native Fortune rank tilemaps, preserving portraits/frame.

Only the verified five graphics-package pointers own the shared rank tiles.
Use exclusively interior/unused tile IDs and relocate new compressed resources
to exact-base FF space; original assets remain byte-identical.
"""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from build_content_first_040_fortune import apply_ips,make_ips
from build_g0_first_boot_title_votri_experimental import encode_chibi,tile_to_4bpp
from decompress_chibi_resource import decompress_resource

BASE_SHA='7a43ed7d4a949bfadf2653663ca42238f205c11262fe5d4cf5ea4a8989b194ff'
MAPS=(0xc0000,0xf04eb,0x100000,0xb6cef,0xd99b3)
PACKAGES=(0x133dc,0x133fd,0x1341e,0x1343f,0x13460)
LABELS=('Rất may','Khá may','Hơi may','Xui xẻo','Rất xui')

def address(off):
 return (((off//0x8000)|0x80)<<16)|(0x8000|(off%0x8000))

def build(clean,baseline,font):
 if hashlib.sha256(clean).hexdigest()!='e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956' or hashlib.sha256(baseline).hexdigest()!=BASE_SHA:
  raise ValueError('Requires exact clean ROM and 091 baseline')
 needle=address(0xa9713).to_bytes(3,'little')
 owners=[i for i in range(len(clean)) if clean.startswith(needle,i)]
 if owners!=[p+4 for p in PACKAGES]:raise AssertionError('Shared rank tile owners changed')
 maps=[bytearray(decompress_resource(baseline,o)[0]) for o in MAPS]
 if any(len(m)!=2048 for m in maps):raise AssertionError('Rank tilemap shape changed')
 gfx,h,_=decompress_resource(baseline,0xa9713)
 if len(gfx)!=8192 or h.postprocess:raise AssertionError('Rank tile resource changed')
 protected=set()
 for m in maps:
  for k in range(1024):
   if not(9<=k%32<23 and 3<=k//32<10):protected.add(int.from_bytes(m[k*2:k*2+2],'little')&1023)
 pool=iter(sorted(set(range(256))-protected));tiles={};data=bytearray(gfx)
 face=ImageFont.truetype(str(font),18)
 for m,label in zip(maps,LABELS):
  canvas=Image.new('L',(112,56),0);d=ImageDraw.Draw(canvas)
  l,t,r,b=d.textbbox((0,0),label,font=face)
  if r-l>108 or b-t>50:raise ValueError('Rank font exceeds native frame')
  d.text(((112-(r-l))//2-l,(56-(b-t))//2-t),label,font=face,fill=255)
  for y in range(7):
   for x in range(14):
    tile=bytes(0 if canvas.getpixel((x*8+xx,y*8+yy))>=100 else 4 for yy in range(8) for xx in range(8))
    if tile not in tiles:
     try:tid=next(pool)
     except StopIteration:raise AssertionError('Rank unshared tile pool exhausted')
     tiles[tile]=tid;data[tid*32:(tid+1)*32]=tile_to_4bpp(tile)
    k=(y+3)*32+x+9;m[k*2:k*2+2]=(0x800|tiles[tile]).to_bytes(2,'little')
 for tid in protected&set(range(256)):
  if data[tid*32:(tid+1)*32]!=gfx[tid*32:(tid+1)*32]:raise AssertionError('Portrait/frame tile modified')
 output=bytearray(baseline);allowed=set(range(0x7fdc,0x7fe0));cursor=0x5b400;resources=[]
 for off,raw,refs in [(0xa9713,data,owners)]+[(o,m,[p+19]) for o,m,p in zip(MAPS,maps,PACKAGES)]:
  stream=encode_chibi(bytes(raw));blob=(len(stream)+2).to_bytes(2,'little')+stream
  end=cursor+len(blob)
  if end>0x60000 or clean[cursor:end]!=b'\xff'*len(blob) or baseline[cursor:end]!=b'\xff'*len(blob):raise AssertionError('Rank relocation collision')
  output[cursor:end]=blob;allowed.update(range(cursor,end))
  for ref in refs:
   if baseline[ref:ref+3]!=address(off).to_bytes(3,'little'):raise AssertionError(f'Rank pointer anchor {ref:#x}')
   output[ref:ref+3]=address(cursor).to_bytes(3,'little');allowed.update(range(ref,ref+3))
  rebuilt,rh,_=decompress_resource(output,cursor)
  if rebuilt!=raw or rh.postprocess:raise AssertionError('Rank codec round-trip failed')
  resources.append({'original':hex(off),'relocated':hex(cursor),'bytes':len(blob),'pointer_offsets':[hex(r) for r in refs]})
  cursor=(end+1)&~1
 output[0x7fdc:0x7fe0]=bytes(4);checksum=(sum(output)+0x1fe)&0xffff
 output[0x7fdc:0x7fe0]=(checksum^0xffff).to_bytes(2,'little')+checksum.to_bytes(2,'little')
 if any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(baseline,output))):raise AssertionError('Rank patch escaped spans')
 ips,count=make_ips(clean,output)
 if apply_ips(clean,ips)!=bytes(output):raise AssertionError('092 IPS replay failed')
 return ips,{'status':'092_FIVE_FORTUNE_RANK_ASSETS_BINARY_PASS','labels':list(LABELS),'unique_tiles':len(tiles),'protected_tiles':len(protected),'resources':resources,'ROM_SHA256':hashlib.sha256(output).hexdigest(),'IPS_SHA256':hashlib.sha256(ips).hexdigest(),'IPS_bytes':len(ips),'IPS_records':count,'emulator_tested':False}

def main():
 p=argparse.ArgumentParser();p.add_argument('original',type=Path);p.add_argument('baseline_ips',type=Path);p.add_argument('--font',type=Path,required=True);p.add_argument('--ips',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
 clean=a.original.read_bytes();ips,report=build(clean,apply_ips(clean,a.baseline_ips.read_bytes()),a.font)
 a.ips.parent.mkdir(parents=True,exist_ok=True);a.ips.write_bytes(ips);a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,ensure_ascii=True))
if __name__=='__main__':main()
