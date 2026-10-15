"""Localize both result-board headings with private assets and 2bpp BG3 ink.

Retain every other owner of the common C706F OBJ resource. Hide only native
heading sprites in the private score-board copy; render a complete Vietnamese
line in the verified empty header region of both native BG3 tilemaps.
"""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image
from build_font_menu_runtime_090 import raster
from build_fortune_rank_092 import address
from build_content_first_040_fortune import apply_ips,make_ips
from decompress_chibi_resource import decompress_resource
from build_g0_first_boot_title_votri_experimental import encode_chibi
BASE_SHA='1e50d81d35da2738dea29e0e8a1d19a010a6f9561665419ccc59b0223df98dfb'
MAPS=(0xee7f3,0x8e8e1)
def region(k):return 7<=k%32<25 and 1<=k//32<5
def two_bpp(tile):
 out=bytearray(16)
 for y in range(8):
  for x in range(8):
   for bit in range(2):out[y*2+bit]|=((tile[y*8+x]>>bit)&1)<<(7-x)
 return bytes(out)
def build(clean,base,font):
 if hashlib.sha256(base).hexdigest()!=BASE_SHA or hashlib.sha256(clean).hexdigest()!='e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956':raise ValueError('Requires exact original ROM and 096 baseline')
 obj,h,_=decompress_resource(base,0xc706f);bg,bh,_=decompress_resource(base,0xee674);maps=[bytearray(decompress_resource(base,o)[0]) for o in MAPS]
 if len(obj)!=8192 or h.postprocess or len(bg)!=4096 or bh.postprocess or any(len(m)!=2048 for m in maps):raise AssertionError('Result resource format changed')
 if base[0xc706f:0xc706f+h.span]!=clean[0xc706f:0xc706f+h.span]:raise AssertionError('Shared original OBJ source is not restored')
 title=bytearray(obj);cleared=set()
 # Real OAM for 結果発表だよ!: seven glyph groups and small pieces.
 for tid in (0xee,0xcc,0x7c,0x7a,0x79,0x77,0xe0):cleared.update((tid,tid+1,tid+16,tid+17))
 cleared.update((0x6d,0x6c,0x6b,0x6a,0x89,0x69,0x79,0x68,0x67,0xec))
 for tid in cleared:title[tid*32:(tid+1)*32]=bytes(32)
 protected={int.from_bytes(m[k*2:k*2+2],'little')&1023 for m in maps for k in range(1024) if not region(k)}
 if any(t>=256 for t in protected):raise AssertionError('BG3 references beyond verified 2bpp asset')
 pool=iter(sorted(set(range(256))-protected));tiles={};data=bytearray(bg)
 im=Image.new('L',(144,32),0);mask=raster('Bảng kết quả!',font,18,140,28)
 for y in range(28):
  for x in range(140):
   if mask.getpixel((x,y)):
    for dy in (-1,0,1):
     for dx in (-1,0,1):im.putpixel((x+2+dx,y+2+dy),1)
 for y in range(28):
  for x in range(140):
   if mask.getpixel((x,y)):im.putpixel((x+2,y+2),2)
 for yy in range(4):
  for xx in range(18):
   tile=bytes(im.getpixel((xx*8+x,yy*8+y)) for y in range(8) for x in range(8))
   if tile not in tiles:
    try:tid=next(pool)
    except StopIteration:raise AssertionError('Result heading 2bpp pool exhausted')
    tiles[tile]=tid;data[tid*16:(tid+1)*16]=two_bpp(tile)
   k=(yy+1)*32+xx+7
   for m in maps:m[k*2:k*2+2]=(0x2000|tiles[tile]).to_bytes(2,'little')
 for tid in protected:
  if data[tid*16:(tid+1)*16]!=bg[tid*16:(tid+1)*16]:raise AssertionError('Result rank/score tile changed')
 out=bytearray(base);allowed=set(range(0x7fdc,0x7fe0));cursor=0x125800;resources=[]
 plans=[(0xc706f,title,[0x123c1,0x12414]),(0xee674,data,[0x123c6,0x12419]),(MAPS[0],maps[0],[0x123cb]),(MAPS[1],maps[1],[0x1241e])]
 for old,decoded,refs in plans:
  packed=encode_chibi(bytes(decoded));blob=(len(packed)+2).to_bytes(2,'little')+packed
  if cursor+len(blob)>0x128000 or base[cursor:cursor+len(blob)]!=b'\xff'*len(blob) or clean[cursor:cursor+len(blob)]!=b'\xff'*len(blob):raise AssertionError('Private scoreboard resource collision')
  for ref in refs:
   if base[ref:ref+3]!=address(old).to_bytes(3,'little'):raise AssertionError('Native scoreboard package pointer changed')
   out[ref:ref+3]=address(cursor).to_bytes(3,'little');allowed.update(range(ref,ref+3))
  out[cursor:cursor+len(blob)]=blob;allowed.update(range(cursor,cursor+len(blob)))
  rebuilt,rh,_=decompress_resource(out,cursor)
  if rebuilt!=decoded or rh.postprocess:raise AssertionError('Result heading codec round-trip failed')
  resources.append({'original':hex(old),'relocated':hex(cursor),'bytes':len(blob),'pointers':[hex(p) for p in refs]});cursor=(cursor+len(blob)+1)&~1
 if out[0xc706f:0xc706f+h.span]!=clean[0xc706f:0xc706f+h.span]:raise AssertionError('Global shared menu/result OBJ changed')
 out[0x7fdc:0x7fe0]=bytes(4);s=(sum(out)+0x1fe)&65535;out[0x7fdc:0x7fe0]=(s^65535).to_bytes(2,'little')+s.to_bytes(2,'little')
 if any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(base,out))):raise AssertionError('097 changes escaped guarded spans')
 ips,count=make_ips(clean,out)
 if apply_ips(clean,ips)!=bytes(out):raise AssertionError('097 IPS replay failed')
 return ips,{'status':'097_TWO_NATIVE_RESULT_HEADINGS_BINARY_PASS','heading':'Bảng kết quả!','unique_2bpp_tiles':len(tiles),'isolated_heading_OBJ_tiles':sorted(cleared),'resources':resources,'shared_original_OBJ_preserved':True,'ROM_SHA256':hashlib.sha256(out).hexdigest(),'IPS_SHA256':hashlib.sha256(ips).hexdigest(),'IPS_bytes':len(ips),'IPS_records':count,'emulator_tested':False}
def main():
 p=argparse.ArgumentParser();p.add_argument('original',type=Path);p.add_argument('baseline_ips',type=Path);p.add_argument('--font',type=Path,required=True);p.add_argument('--ips',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args();clean=a.original.read_bytes();ips,r=build(clean,apply_ips(clean,a.baseline_ips.read_bytes()),a.font);a.ips.write_bytes(ips);a.report.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,ensure_ascii=True))
if __name__=='__main__':main()
