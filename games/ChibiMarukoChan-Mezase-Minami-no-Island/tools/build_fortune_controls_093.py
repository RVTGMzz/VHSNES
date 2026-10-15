"""Vietnamese native Fortune sprite labels and exact metasprite reflow.

The FF package at 0x13325 loads a planar metasprite resource: frame counts,
signed x/y arrays, tile IDs, attributes. Translate frames 6-9 without adding
renderer hooks; retain animated paper/box frames 0-5 and cursor frame 10.
"""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image
from build_font_menu_runtime_090 import raster
from build_fortune_rank_092 import address
from build_content_first_040_fortune import apply_ips,make_ips
from decompress_chibi_resource import decompress_resource,reorder_flag1_blocks
from build_g0_first_boot_title_votri_experimental import encode_chibi,tile_to_4bpp
BASE_SHA='94db0ef41b7ec236ae3b132a792db0777d89d1c572c63d2ce26b59c3a4025e4f'

def build(clean,base,font):
 if hashlib.sha256(clean).hexdigest()!='e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956' or hashlib.sha256(base).hexdigest()!=BASE_SHA:raise ValueError('Requires exact clean ROM and 092 baseline')
 raw,h,_=decompress_resource(base,0x104bb3)
 if len(raw)!=5664 or h.span!=3171 or not h.postprocess:raise AssertionError('Fortune OBJ asset changed')
 original=reorder_flag1_blocks(raw);gfx=bytearray(original)
 meta,mh,_=decompress_resource(base,0xe8c36);m=bytearray(meta)
 if mh.postprocess or len(meta)!=894 or meta[:14]!=bytes.fromhex('0BDC003E16181D231C0602060204'):raise AssertionError('Fortune metasprite schema changed')
 n=220;a=14;starts=[sum(meta[3:3+i]) for i in range(11)]
 protected=set()
 for f in list(range(6))+[10]:
  for i in range(starts[f],starts[f]+meta[3+f]):
   tid=meta[a+2*n+i];protected.add(tid)
   if meta[a+3*n+i]&16:protected.update((tid+1,tid+16,tid+17))
 changes=set()
 # Palette0 existing native labels use yellow index3; preserve their native
 # dark outline by adding index1 around every binary ink pixel.
 def styled(im):
  out=Image.new('P',im.size,0)
  for y in range(im.height):
   for x in range(im.width):
    if im.getpixel((x,y)):
     for yy in range(max(0,y-1),min(im.height,y+2)):
      for xx in range(max(0,x-1),min(im.width,x+2)):out.putpixel((xx,yy),1)
  for y in range(im.height):
   for x in range(im.width):
    if im.getpixel((x,y)):out.putpixel((x,y),3)
  return out
 def write_block(tid,im):
  for yy in range(2):
   for xx in range(im.width//8):
    tile=tid+yy*16+xx
    if tile in protected:raise AssertionError('UI shares an animated/cursor tile')
    gfx[tile*32:(tile+1)*32]=tile_to_4bpp(bytes(im.getpixel((xx*8+x,yy*8+y)) for y in range(8) for x in range(8)));changes.add(tile)
 # One cleared 8x8 cell for surplus no-choice parts; it belongs only to frame8.
 gfx[0x6d*32:0x6e*32]=bytes(32);changes.add(0x6d)
 for label,tids in [('Chơi',(0x77,0x79)),('Thoát',(0x7b,0x7d)),('Lắc',(0x75,0x90))]:
  im=styled(raster(label,font,11,32,16))
  for x,tid in enumerate(tids):write_block(tid,im.crop((x*16,0,x*16+16,16)))
 im=styled(raster('Rút',font,11,24,16));ruttids=(0x82,0x83,0x84,0x92,0x93,0x94)
 for k,tid in enumerate(ruttids):
  if tid in protected:raise AssertionError('Pull word tile shares animation')
  gfx[tid*32:(tid+1)*32]=tile_to_4bpp(bytes(im.getpixel(((k%3)*8+x,(k//3)*8+y)) for y in range(8) for x in range(8)));changes.add(tid)
 def entry(f,j,x,y,tid,attr):
  i=starts[f]+j
  for arr,v in enumerate((x&255,y&255,tid,attr)):m[a+arr*n+i]=v
 for j in range(4):entry(6,j,0,-7,0x6d,0)
 for j,tid in enumerate((0x7b,0x7d)):entry(6,j+4,-16+j*16,-7,tid,16)
 for j,tid in enumerate((0x77,0x79)):entry(7,j,-16+j*16,-7,tid,16)
 for j,tid in enumerate(ruttids):entry(8,j,-12+j%3*8,-11+j//3*8,tid,0)
 for j,tid in enumerate((0x75,0x90)):entry(9,j,-16+j*16,-7,tid,16)
 for tid in protected:
  if gfx[tid*32:(tid+1)*32]!=original[tid*32:(tid+1)*32]:raise AssertionError('Animated/cursor ink changed')
 for f in list(range(6))+[10]:
  for arr in range(4):
   l=a+arr*n+starts[f];r=l+meta[3+f]
   if m[l:r]!=meta[l:r]:raise AssertionError('Animated/cursor metasprite changed')
 inverse=bytearray(len(gfx));order=(0,8,1,9,2,10,3,11,4,12,5,13,6,14,7,15)
 for at in range(0,len(gfx),16):
  for dst,src in enumerate(order):inverse[at+src]=gfx[at+dst]
 out=bytearray(base);allowed=set(range(0x7fdc,0x7fe0));resources=[]
 for source,decoded,flag,dest,ref,span in [(0x104bb3,inverse,True,0x104bb3,None,h.span),(0xe8c36,m,False,0x5c940,0x13326,None)]:
  packed=encode_chibi(bytes(decoded));blob=(len(packed)+2|(0x8000 if flag else 0)).to_bytes(2,'little')+packed
  if span:
   if len(blob)>span:raise AssertionError('Fortune controls compressed overflow')
   blob+=b'\xff'*(span-len(blob))
  elif clean[dest:dest+len(blob)]!=b'\xff'*len(blob) or base[dest:dest+len(blob)]!=b'\xff'*len(blob):raise AssertionError('Fortune metadata relocation collision')
  out[dest:dest+len(blob)]=blob;allowed.update(range(dest,dest+len(blob)))
  if ref:
   if base[ref:ref+3]!=address(source).to_bytes(3,'little'):raise AssertionError('Fortune metadata owner changed')
   out[ref:ref+3]=address(dest).to_bytes(3,'little');allowed.update(range(ref,ref+3))
  rebuilt,rh,_=decompress_resource(out,dest)
  if rebuilt!=decoded or rh.postprocess!=flag:raise AssertionError('Fortune UI codec round-trip failed')
  resources.append({'source':hex(source),'destination':hex(dest),'span':len(blob),'roundtrip':True})
 out[0x7fdc:0x7fe0]=bytes(4);s=(sum(out)+0x1fe)&65535;out[0x7fdc:0x7fe0]=(s^65535).to_bytes(2,'little')+s.to_bytes(2,'little')
 if any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(base,out))):raise AssertionError('UI writes escaped guarded spans')
 ips,count=make_ips(clean,out)
 if apply_ips(clean,ips)!=bytes(out):raise AssertionError('093 IPS replay failed')
 return ips,{'status':'093_FORTUNE_NATIVE_CONTROLS_BINARY_PASS','labels':['Chơi','Thoát','Lắc','Rút'],'resources':resources,'changed_gfx_tiles':sorted(changes),'preserved_frames':[0,1,2,3,4,5,10],'ROM_SHA256':hashlib.sha256(out).hexdigest(),'IPS_SHA256':hashlib.sha256(ips).hexdigest(),'IPS_bytes':len(ips),'IPS_records':count,'emulator_tested':False}

def main():
 p=argparse.ArgumentParser();p.add_argument('original',type=Path);p.add_argument('baseline_ips',type=Path);p.add_argument('--font',type=Path,required=True);p.add_argument('--ips',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args();clean=a.original.read_bytes();ips,r=build(clean,apply_ips(clean,a.baseline_ips.read_bytes()),a.font);a.ips.write_bytes(ips);a.report.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,ensure_ascii=True))
if __name__=='__main__':main()
