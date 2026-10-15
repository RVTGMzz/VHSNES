"""Translate the carved Fortune box label in all four native draw poses.

Clone changed sprite instances into previously unreferenced OBJ cells. Retain
every original tile, paper/cursor/controls frame and all box pose coordinates.
"""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image
from build_font_menu_runtime_090 import raster
from build_fortune_rank_092 import address
from build_content_first_040_fortune import apply_ips,make_ips
from decompress_chibi_resource import decompress_resource,reorder_flag1_blocks,cpu_to_file
from build_g0_first_boot_title_votri_experimental import encode_chibi,tile_to_4bpp
from build_fortune_paper_094 import tile_pixels
BASE_SHA='94f3224eceb51189fd7aad7bbf5dc7a3ef4248b64ef42ba9c8abcb93e8d717ac'
def face(x,y):return 199<=x+y<=215 and -42<=x-y<=45
def build(clean,base,font):
 if hashlib.sha256(base).hexdigest()!=BASE_SHA or hashlib.sha256(clean).hexdigest()!='e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956':raise ValueError('Requires exact original ROM and 099 baseline')
 oldgfx=cpu_to_file(int.from_bytes(base[0x133b2:0x133b5],'little'));oldmeta=cpu_to_file(int.from_bytes(base[0x13326:0x13329],'little'))
 raw,h,_=decompress_resource(base,oldgfx);original=reorder_flag1_blocks(raw);gfx=bytearray(original);meta,mh,_=decompress_resource(base,oldmeta);m=bytearray(meta)
 if oldgfx!=0x5cc00 or len(gfx)!=8192 or not h.postprocess or len(meta)!=894 or mh.postprocess or meta[:14]!=bytes.fromhex('0BDC003E16181D231C0602060204'):raise AssertionError('Fortune box baseline asset changed')
 a=14;n=220;starts=[sum(meta[3:3+f]) for f in range(11)]
 def sprite(i):
  tid=meta[a+2*n+i];sz=16 if meta[a+3*n+i]&16 else 8
  return (96+int.from_bytes(meta[a+i:a+i+1],'little',signed=True)-(4 if sz==16 else 0),96+int.from_bytes(meta[a+n+i:a+n+i+1],'little',signed=True)-(4 if sz==16 else 0),tid,sz)
 canvas=Image.new('L',(192,192),0);nodes=[sprite(i) for i in range(starts[1],starts[1]+meta[4])]
 for x,y,tid,sz in reversed(nodes):
  for yy in range(sz):
   for xx in range(sz):
    v=tile_pixels(gfx,tid+yy//8*16+xx//8)[yy%8*8+xx%8]
    if v:canvas.putpixel((x+xx,y+yy),v)
 new=canvas.copy();erased=0
 for y in range(192):
  for x in range(192):
   if face(x,y) and canvas.getpixel((x,y)) in (12,13,14,15):
    candidates=[]
    for distance in range(1,9):
     for dy in range(-distance,distance+1):
      dx=distance-abs(dy)
      for xx in ({x-dx,x+dx} if dx else {x}):
       yy=y+dy
       if 0<=xx<192 and 0<=yy<192 and face(xx,yy) and 5<=canvas.getpixel((xx,yy))<=11:candidates.append(canvas.getpixel((xx,yy)))
     if candidates:break
    if not candidates:raise AssertionError('No native wood texture near label ink')
    new.putpixel((x,y),candidates[0]);erased+=1
 mask=raster('Bói vui',font,12,48,14).rotate(45,expand=True,resample=Image.Resampling.NEAREST);left=103-mask.width//2;top=104-mask.height//2
 for y in range(mask.height):
  for x in range(mask.width):
   if mask.getpixel((x,y)):
    xx=left+x;yy=top+y
    if not face(xx,yy) or not canvas.getpixel((xx,yy)):raise AssertionError('Vietnamese box ink escapes carved front face')
    new.putpixel((xx,yy),15)
 used=set()
 for i in range(n):
  _,_,tid,sz=sprite(i);used.add(tid)
  if sz==16:used.update((tid+1,tid+16,tid+17))
 available=set(range(177,256))-used;replacements={};clones=[]
 for key in nodes:
  x,y,tid,sz=key;bits=[];changed=False
  for yy in range(sz):
   for xx in range(sz):
    v=tile_pixels(gfx,tid+yy//8*16+xx//8)[yy%8*8+xx%8]
    if v and canvas.getpixel((x+xx,y+yy))!=new.getpixel((x+xx,y+yy)):v=new.getpixel((x+xx,y+yy));changed=True
    bits.append(v)
  if not changed:continue
  if key in replacements:continue
  if sz==16:
   options=[t for t in sorted(available) if t%16<15 and {t,t+1,t+16,t+17}<=available]
   if not options:raise AssertionError('Fortune box clone quad pool exhausted')
   dst=options[0];occupied={dst,dst+1,dst+16,dst+17}
  else:
   if not available:raise AssertionError('Fortune box clone pool exhausted')
   dst=min(available);occupied={dst}
  available-=occupied;replacements[key]=dst
  for yy in range(sz//8):
   for xx in range(sz//8):
    t=dst+yy*16+xx;gfx[t*32:(t+1)*32]=tile_to_4bpp(bytes(bits[(yy*8+y)*sz+xx*8+x] for y in range(8) for x in range(8)))
  clones.append({'original_tile':tid,'clone':dst,'size':sz})
 changed_entries=0
 for f in range(1,5):
  for i in range(starts[f],starts[f]+meta[3+f]):
   key=sprite(i)
   if key in replacements:m[a+2*n+i]=replacements[key];changed_entries+=1
 for tid in used:
  if gfx[tid*32:(tid+1)*32]!=original[tid*32:(tid+1)*32]:raise AssertionError('Box modifies existing original/paper/control tile')
 for f in (0,5,6,7,8,9,10):
  for arr in range(4):
   l=a+arr*n+starts[f];r=l+meta[3+f]
   if m[l:r]!=meta[l:r]:raise AssertionError('Box modifies paper/bow/control/cursor metadata')
 inverse=bytearray(len(gfx));order=(0,8,1,9,2,10,3,11,4,12,5,13,6,14,7,15)
 for pos in range(0,len(gfx),16):
  for dst,src in enumerate(order):inverse[pos+src]=gfx[pos+dst]
 out=bytearray(base);allowed=set(range(0x7fdc,0x7fe0));cursor=0x126c50;resources=[]
 for decoded,flag,ref,old in [(inverse,True,0x133b2,oldgfx),(m,False,0x13326,oldmeta)]:
  packed=encode_chibi(bytes(decoded));blob=(len(packed)+2|(0x8000 if flag else 0)).to_bytes(2,'little')+packed
  if cursor+len(blob)>0x128000 or base[cursor:cursor+len(blob)]!=b'\xff'*len(blob) or clean[cursor:cursor+len(blob)]!=b'\xff'*len(blob):raise AssertionError('Box private resource relocation collision')
  if base[ref:ref+3]!=address(old).to_bytes(3,'little'):raise AssertionError('Box package pointer changed')
  out[ref:ref+3]=address(cursor).to_bytes(3,'little');allowed.update(range(ref,ref+3));out[cursor:cursor+len(blob)]=blob;allowed.update(range(cursor,cursor+len(blob)))
  rebuilt,rh,_=decompress_resource(out,cursor)
  if rebuilt!=decoded or rh.postprocess!=flag:raise AssertionError('Box codec round-trip failed')
  resources.append({'relocated':hex(cursor),'bytes':len(blob),'pointer':hex(ref)});cursor=(cursor+len(blob)+1)&~1
 out[0x7fdc:0x7fe0]=bytes(4);s=(sum(out)+0x1fe)&65535;out[0x7fdc:0x7fe0]=(s^65535).to_bytes(2,'little')+s.to_bytes(2,'little')
 if any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(base,out))):raise AssertionError('100 changes escaped guarded spans')
 ips,count=make_ips(clean,out)
 if apply_ips(clean,ips)!=bytes(out):raise AssertionError('100 IPS replay failed')
 return ips,{'status':'100_FOUR_FORTUNE_BOX_POSES_BINARY_PASS','caption':'Bói vui','erased_Japanese_ink_pixels':erased,'sprite_clones':clones,'updated_pose_entries':changed_entries,'all_existing_tiles_preserved':True,'resources':resources,'ROM_SHA256':hashlib.sha256(out).hexdigest(),'IPS_SHA256':hashlib.sha256(ips).hexdigest(),'IPS_bytes':len(ips),'IPS_records':count,'emulator_tested':False}
def main():
 p=argparse.ArgumentParser();p.add_argument('original',type=Path);p.add_argument('baseline_ips',type=Path);p.add_argument('--font',type=Path,required=True);p.add_argument('--ips',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args();clean=a.original.read_bytes();ips,r=build(clean,apply_ips(clean,a.baseline_ips.read_bytes()),a.font);a.ips.write_bytes(ips);a.report.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,ensure_ascii=True))
if __name__=='__main__':main()
