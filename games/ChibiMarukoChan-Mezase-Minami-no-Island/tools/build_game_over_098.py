"""Localize the native Game Over title without altering Maruko animation.

Frame2 of the sole $82:B302 metasprite package is the 36-part title. Frames
0/1 and actor glyph tiles40..FF stay intact. Only the Game Over owner of the
three-way shared OBJ source is redirected to the private title copy.
"""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image
from build_font_menu_runtime_090 import raster
from build_fortune_rank_092 import address
from build_content_first_040_fortune import apply_ips,make_ips
from decompress_chibi_resource import decompress_resource,reorder_flag1_blocks
from build_g0_first_boot_title_votri_experimental import encode_chibi,tile_to_4bpp
BASE_SHA='f9c109ae3f0d661ceabbb7ab827007b94d5e0688107bbe6727c4cc67c6009c79'
def build(clean,base,font):
 if hashlib.sha256(base).hexdigest()!=BASE_SHA or hashlib.sha256(clean).hexdigest()!='e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956':raise ValueError('Requires exact original ROM and 097 baseline')
 caller=bytes.fromhex('A202B32255E280')
 if [i for i in range(len(clean)) if clean.startswith(caller,i)]!=[0x47749] or base[0x47749:0x47750]!=caller:raise AssertionError('Game Over metasprite caller changed')
 raw,h,_=decompress_resource(base,0xbd0bd);original=reorder_flag1_blocks(raw);gfx=bytearray(original)
 meta,mh,_=decompress_resource(base,0xf991b);m=bytearray(meta)
 if len(raw)!=8192 or not h.postprocess or meta[:6]!=bytes.fromhex('035C001F1924') or len(meta)!=374 or mh.postprocess:raise AssertionError('Game Over actor/title resource shape changed')
 if [i for i in range(len(clean)) if clean.startswith(address(0xbd0bd).to_bytes(3,'little'),i)]!=[0x120d2,0x120ee,0x12d39]:raise AssertionError('Game Over OBJ ownership changed')
 if [i for i in range(len(clean)) if clean.startswith(address(0xf991b).to_bytes(3,'little'),i)]!=[0x13303]:raise AssertionError('Game Over metadata ownership changed')
 # Palette0 index3 is white, 11 black; preserve the native palette and actors.
 im=Image.new('L',(96,24),0);mask=raster('Hết lượt!',font,18,94,22)
 for y in range(22):
  for x in range(94):
   if mask.getpixel((x,y)):
    for dy in (-1,0,1):
     for dx in (-1,0,1):im.putpixel((x+1+dx,y+1+dy),11)
 for y in range(22):
  for x in range(94):
   if mask.getpixel((x,y)):im.putpixel((x+1,y+1),3)
 gfx[:0x40*32]=bytes(0x40*32)
 a=6;n=92;start=56
 for k in range(36):
  xx=k%12;yy=k//12;i=start+k
  tile=bytes(im.getpixel((xx*8+x,yy*8+y)) for y in range(8) for x in range(8));gfx[k*32:(k+1)*32]=tile_to_4bpp(tile)
  for arr,v in enumerate(((-48+xx*8)&255,(-12+yy*8)&255,k,0)):m[a+arr*n+i]=v
 if gfx[0x40*32:]!=original[0x40*32:]:raise AssertionError('Game Over Maruko bitmap changed')
 for arr in range(4):
  if m[a+arr*n:a+arr*n+56]!=meta[a+arr*n:a+arr*n+56]:raise AssertionError('Game Over Maruko metasprite changed')
 inverse=bytearray(len(gfx));order=(0,8,1,9,2,10,3,11,4,12,5,13,6,14,7,15)
 for pos in range(0,len(gfx),16):
  for dst,src in enumerate(order):inverse[pos+src]=gfx[pos+dst]
 out=bytearray(base);allowed=set(range(0x7fdc,0x7fe0));cursor=0x5e700;resources=[]
 for decoded,flag,ref,old in [(inverse,True,0x120ee,0xbd0bd),(m,False,0x13303,0xf991b)]:
  packed=encode_chibi(bytes(decoded));blob=(len(packed)+2|(0x8000 if flag else 0)).to_bytes(2,'little')+packed
  if cursor+len(blob)>0x60000 or base[cursor:cursor+len(blob)]!=b'\xff'*len(blob) or clean[cursor:cursor+len(blob)]!=b'\xff'*len(blob):raise AssertionError('Game Over private resource collision')
  if base[ref:ref+3]!=address(old).to_bytes(3,'little'):raise AssertionError('Game Over package pointer changed')
  out[ref:ref+3]=address(cursor).to_bytes(3,'little');allowed.update(range(ref,ref+3));out[cursor:cursor+len(blob)]=blob;allowed.update(range(cursor,cursor+len(blob)))
  rebuilt,rh,_=decompress_resource(out,cursor)
  if rebuilt!=decoded or rh.postprocess!=flag:raise AssertionError('Game Over codec round-trip failed')
  resources.append({'relocated':hex(cursor),'bytes':len(blob),'pointer':hex(ref)});cursor=(cursor+len(blob)+1)&~1
 for ref in (0x120d2,0x12d39):
  if out[ref:ref+3]!=base[ref:ref+3]:raise AssertionError('Other Game Over OBJ owner changed')
 out[0x7fdc:0x7fe0]=bytes(4);s=(sum(out)+0x1fe)&65535;out[0x7fdc:0x7fe0]=(s^65535).to_bytes(2,'little')+s.to_bytes(2,'little')
 if any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(base,out))):raise AssertionError('098 writes escaped guarded spans')
 ips,count=make_ips(clean,out)
 if apply_ips(clean,ips)!=bytes(out):raise AssertionError('098 IPS replay failed')
 return ips,{'status':'098_NATIVE_GAME_OVER_TITLE_BINARY_PASS','caption':'Hết lượt!','preserved_actor_frames':[0,1],'other_shared_gfx_owners_preserved':2,'resources':resources,'ROM_SHA256':hashlib.sha256(out).hexdigest(),'IPS_SHA256':hashlib.sha256(ips).hexdigest(),'IPS_bytes':len(ips),'IPS_records':count,'emulator_tested':False}
def main():
 p=argparse.ArgumentParser();p.add_argument('original',type=Path);p.add_argument('baseline_ips',type=Path);p.add_argument('--font',type=Path,required=True);p.add_argument('--ips',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args();clean=a.original.read_bytes();ips,r=build(clean,apply_ips(clean,a.baseline_ips.read_bytes()),a.font);a.ips.write_bytes(ips);a.report.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,ensure_ascii=True))
if __name__=='__main__':main()
