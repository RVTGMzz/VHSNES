"""Replace both native team-selection チーム labels while retaining mascots."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image
from build_content_first_040_fortune import apply_ips,make_ips
from build_native_setup_headings_101 import decoded
from build_font_menu_runtime_090 import raster
from build_fortune_rank_092 import address
from decompress_chibi_resource import cpu_to_file,decompress_resource
from build_g0_first_boot_title_votri_experimental import encode_chibi,tile_to_4bpp
from render_chibi_resource_package import decode_tile
BASE_SHA='6fa7654443c23db2275487c7f32c0d4efb3bb71d51021b1d6fbc2715194d459e'

def build(clean,base,font):
 if hashlib.sha256(clean).hexdigest()!='e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956' or hashlib.sha256(base).hexdigest()!=BASE_SHA:raise ValueError('Exact original and checkpoint101 required')
 go=cpu_to_file(int.from_bytes(base[0x12354:0x12357],'little'));mo=cpu_to_file(int.from_bytes(base[0x1234a:0x1234d],'little'))
 if (go,mo)!=(0x12f490,0x67778):raise AssertionError('Native team selection resource owner changed')
 gfx=bytearray(decoded(base,go));old=bytes(gfx);tm=bytearray(decoded(base,mo));native_map=bytes(tm)
 if len(gfx)!=9344 or len(tm)!=2048:raise AssertionError('101 team resources changed')
 labels=[];clones={}
 for origin in (0,192):
  canvas=Image.new('L',(64,32),0)
  for y in range(32):
   for x in range(64):
    gx=x+origin;gy=y+128;k=gy//8*32+gx//8;w=int.from_bytes(tm[k*2:k*2+2],'little');tile=decode_tile(gfx,(w&1023)*32,4)
    canvas.putpixel((x,y),tile[7-y%8 if w&0x8000 else y%8][7-x%8 if w&0x4000 else x%8])
  image=canvas.copy();erased=0
  # Avatar artwork ends at x24. Font colors3/4/5 occupy x25..59;
  # avatar cheeks and outlines remain entirely outside the erasure mask.
  for y in range(6,27):
   for x in range(25,60):
    if canvas.getpixel((x,y)) not in (3,4,5):continue
    candidates=[]
    for d in range(1,64):
     for xx in (x-d,x+d):
      if 0<=xx<64 and canvas.getpixel((xx,y)) in (0,1,2):candidates.append(canvas.getpixel((xx,y)))
     if candidates:break
    if not candidates:raise AssertionError('No native team strip background')
    image.putpixel((x,y),candidates[0]);erased+=1
  mask=raster('Đội',font,12,32,18)
  for y in range(18):
   for x in range(32):
    if mask.getpixel((x,y)):
     for dy in (-1,0,1):
      for dx in (-1,0,1):image.putpixel((x+26+dx,y+7+dy),5)
  for y in range(18):
   for x in range(32):
    if mask.getpixel((x,y)):image.putpixel((x+26,y+7),15)
  for y in range(32):
   for x in range(25):
    if image.getpixel((x,y))!=canvas.getpixel((x,y)):raise AssertionError('Native mascot pixels changed')
  for yy in range(4):
   for xx in range(8):
    a=bytes(canvas.getpixel((xx*8+x,yy*8+y)) for y in range(8) for x in range(8));b=bytes(image.getpixel((xx*8+x,yy*8+y)) for y in range(8) for x in range(8))
    if a==b:continue
    if b not in clones:
     tid=len(gfx)//32
     if tid>=512:raise AssertionError('Team label atlas exceeds safe BG1 allocation')
     clones[b]=tid;gfx.extend(tile_to_4bpp(b))
    k=(yy+16)*32+xx+origin//8;w=int.from_bytes(tm[k*2:k*2+2],'little');tm[k*2:k*2+2]=((w&0x3c00)|clones[b]).to_bytes(2,'little')
  labels.append({'caption':'Đội','origin_x':origin,'erased_Japanese_ink_pixels':erased,'native_mascot_pixels_preserved':True})
 if bytes(gfx[:len(old)])!=old:raise AssertionError('102 modifies any existing native/header tile')
 for k in range(1024):
  if not(16<=k//32<20 and (3<=k%32<8 or 27<=k%32<32)) and tm[k*2:k*2+2]!=native_map[k*2:k*2+2]:raise AssertionError('102 map writes escape team label cells')
 out=bytearray(base);allowed=set(range(0x7fdc,0x7fe0));resources=[]
 for data,ref,start,end in [(gfx,0x12354,0xf17a,0x10000),(tm,0x1234a,0x57340,0x58000)]:
  packed=encode_chibi(bytes(data));blob=(len(packed)+2).to_bytes(2,'little')+packed
  if start+len(blob)>end or base[start:start+len(blob)]!=b'\xff'*len(blob) or clean[start:start+len(blob)]!=b'\xff'*len(blob):raise AssertionError('102 isolated resource collision')
  out[start:start+len(blob)]=blob;allowed.update(range(start,start+len(blob)));out[ref:ref+3]=address(start).to_bytes(3,'little');allowed.update(range(ref,ref+3))
  rebuilt,h,_=decompress_resource(out,start)
  if rebuilt!=data or h.postprocess:raise AssertionError('102 resource roundtrip failed')
  resources.append({'pointer':hex(ref),'offset':hex(start),'bytes':len(blob)})
 out[0x7fdc:0x7fe0]=bytes(4);s=(sum(out)+0x1fe)&65535;out[0x7fdc:0x7fe0]=(s^65535).to_bytes(2,'little')+s.to_bytes(2,'little')
 if any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(base,out))):raise AssertionError('102 writes escaped guarded spans')
 ips,count=make_ips(clean,out)
 if apply_ips(clean,ips)!=bytes(out):raise AssertionError('102 IPS replay failed')
 return ips,{'status':'102_BOTH_TEAM_SELECTION_LABELS_BINARY_PASS','labels':labels,'new_private_tiles':len(clones),'resources':resources,'IPS_SHA256':hashlib.sha256(ips).hexdigest(),'ROM_SHA256':hashlib.sha256(out).hexdigest(),'IPS_bytes':len(ips),'IPS_records':count,'emulator_tested':False,'whole_game_complete':False}

def main():
 p=argparse.ArgumentParser();p.add_argument('original',type=Path);p.add_argument('baseline_ips',type=Path);p.add_argument('--font',type=Path,required=True);p.add_argument('--ips',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args();clean=a.original.read_bytes();ips,r=build(clean,apply_ips(clean,a.baseline_ips.read_bytes()),a.font);a.ips.write_bytes(ips);a.report.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,ensure_ascii=True))
if __name__=='__main__':main()
