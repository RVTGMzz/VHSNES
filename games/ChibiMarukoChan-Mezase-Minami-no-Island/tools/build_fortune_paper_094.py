"""Translate native Fortune paper lettering with isolated cloned OBJ tiles."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image
from build_font_menu_runtime_090 import raster
from build_fortune_rank_092 import address
from build_content_first_040_fortune import apply_ips,make_ips
from decompress_chibi_resource import decompress_resource,reorder_flag1_blocks
from build_g0_first_boot_title_votri_experimental import encode_chibi,tile_to_4bpp
BASE_SHA='7e5833eab2cf215d93d3a55380acebf3005bca5e9d990e5ab6ef5ed7ace938c0'
def tile_pixels(raw,t):
 b=raw[t*32:(t+1)*32]
 return [sum(((b[y*2+(bit//2)*16+bit%2]>>(7-x))&1)<<bit for bit in range(4)) for y in range(8) for x in range(8)]
def build(clean,base,font):
 if hashlib.sha256(base).hexdigest()!=BASE_SHA or hashlib.sha256(clean).hexdigest()!='e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956':raise ValueError('Requires exact clean ROM and 093 baseline')
 raw,h,_=decompress_resource(base,0x104bb3);original=reorder_flag1_blocks(raw);gfx=bytearray(original+b'\x00'*(8192-len(original)))
 original_meta=decompress_resource(base,0x5c940)[0];m=bytearray(original_meta);a=14;n=220;canvas=Image.new('L',(192,192),0);sprites=[]
 for i in range(62):
  tid=m[a+2*n+i];sz=16 if m[a+3*n+i]&16 else 8
  x=96+int.from_bytes(m[a+i:a+i+1],'little',signed=True)-(4 if sz==16 else 0)
  y=96+int.from_bytes(m[a+n+i:a+n+i+1],'little',signed=True)-(4 if sz==16 else 0)
  sprites.append((x,y,tid,sz))
 for x,y,tid,sz in reversed(sprites):
  for yy in range(sz):
   for xx in range(sz):
    v=tile_pixels(gfx,tid+yy//8*16+xx//8)[yy%8*8+xx%8]
    if v:canvas.putpixel((x+xx,y+yy),v)
 new=canvas.copy()
 # Original brush lettering uses only these colors in this isolated paper
 # frame. Preserve paper/edge colors 1/2/3 and every other animation frame.
 removed=0
 for y in range(192):
  for x in range(192):
   if new.getpixel((x,y)) in (4,5,8,9,10):new.putpixel((x,y),1);removed+=1
 # The native bow/fold covers the middle of the paper. Place each word on a
 # visible half so the fold cannot hide a letter or Vietnamese accent.
 for label,cx,cy in [('Bói',82,114),('vui',120,76)]:
  mask=raster(label,font,14,32,20).rotate(45,expand=True,resample=Image.Resampling.NEAREST)
  left=cx-mask.width//2;top=cy-mask.height//2
  for y in range(mask.height):
   for x in range(mask.width):
    if mask.getpixel((x,y)):
     xx=left+x;yy=top+y
     if not canvas.getpixel((xx,yy)):raise AssertionError('Vietnamese paper ink escapes existing paper')
     new.putpixel((xx,yy),4)
 available=set(range(177,256));clones=[]
 for i,(x,y,tid,sz) in enumerate(sprites):
  pix=[];changed=False
  for yy in range(sz):
   for xx in range(sz):
    v=tile_pixels(gfx,tid+yy//8*16+xx//8)[yy%8*8+xx%8]
    if canvas.getpixel((x+xx,y+yy))!=new.getpixel((x+xx,y+yy)) and v:
     v=new.getpixel((x+xx,y+yy));changed=True
    pix.append(v)
  if not changed:continue
  if sz==16:
   options=[t for t in sorted(available) if t%16<15 and {t,t+1,t+16,t+17}<=available]
   if not options:raise AssertionError('Paper 16px clone pool exhausted')
   dst=options[0];used={dst,dst+1,dst+16,dst+17}
  else:
   if not available:raise AssertionError('Paper clone pool exhausted')
   dst=min(available);used={dst}
  available-=used;m[a+2*n+i]=dst
  for yy in range(sz//8):
   for xx in range(sz//8):
    t=dst+yy*16+xx;gfx[t*32:(t+1)*32]=tile_to_4bpp(bytes(pix[(yy*8+y)*sz+xx*8+x] for y in range(8) for x in range(8)))
  clones.append({'frame_entry':i,'source':tid,'clone':dst,'size':sz})
 if gfx[:len(original)]!=original:raise AssertionError('Paper modifies shared source tiles')
 for arr in range(4):
  if m[a+arr*n+62:a+(arr+1)*n]!=original_meta[a+arr*n+62:a+(arr+1)*n]:raise AssertionError('Paper modifies other Fortune frames')
 inverse=bytearray(len(gfx));order=(0,8,1,9,2,10,3,11,4,12,5,13,6,14,7,15)
 for pos in range(0,len(gfx),16):
  for dst,src in enumerate(order):inverse[pos+src]=gfx[pos+dst]
 out=bytearray(base);allowed=set(range(0x7fdc,0x7fe0));cursor=0x5cc00;resources=[]
 for raw,flag,ref,old in [(inverse,True,0x133b2,0x104bb3),(m,False,0x13326,0x5c940)]:
  packed=encode_chibi(bytes(raw));blob=(len(packed)+2|(0x8000 if flag else 0)).to_bytes(2,'little')+packed
  if cursor+len(blob)>0x60000 or base[cursor:cursor+len(blob)]!=b'\xff'*len(blob) or clean[cursor:cursor+len(blob)]!=b'\xff'*len(blob):raise AssertionError('Paper asset relocation collision')
  if base[ref:ref+3]!=address(old).to_bytes(3,'little'):raise AssertionError('Paper package pointer changed')
  out[ref:ref+3]=address(cursor).to_bytes(3,'little');allowed.update(range(ref,ref+3))
  out[cursor:cursor+len(blob)]=blob;allowed.update(range(cursor,cursor+len(blob)))
  rebuilt,rh,_=decompress_resource(out,cursor)
  if rebuilt!=raw or rh.postprocess!=flag:raise AssertionError('Paper codec round-trip failed')
  resources.append({'relocated':hex(cursor),'bytes':len(blob),'decoded':len(raw),'pointer':hex(ref)})
  cursor=(cursor+len(blob)+1)&~1
 out[0x7fdc:0x7fe0]=bytes(4);s=(sum(out)+0x1fe)&65535;out[0x7fdc:0x7fe0]=(s^65535).to_bytes(2,'little')+s.to_bytes(2,'little')
 if any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(base,out))):raise AssertionError('Paper writes escaped guarded spans')
 ips,count=make_ips(clean,out)
 if apply_ips(clean,ips)!=bytes(out):raise AssertionError('094 IPS replay failed')
 return ips,{'status':'094_FORTUNE_PAPER_BINARY_PASS','caption':'Bói vui','removed_Japanese_ink_pixels':removed,'sprite_clones':clones,'resources':resources,'ROM_SHA256':hashlib.sha256(out).hexdigest(),'IPS_SHA256':hashlib.sha256(ips).hexdigest(),'IPS_bytes':len(ips),'IPS_records':count,'emulator_tested':False}
def main():
 p=argparse.ArgumentParser();p.add_argument('original',type=Path);p.add_argument('baseline_ips',type=Path);p.add_argument('--font',type=Path,required=True);p.add_argument('--ips',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args();clean=a.original.read_bytes();ips,r=build(clean,apply_ips(clean,a.baseline_ips.read_bytes()),a.font);a.ips.write_bytes(ips);a.report.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,ensure_ascii=True))
if __name__=='__main__':main()
