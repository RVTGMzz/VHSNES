"""Localize Paint help/buttons and replace the native pen-drawn Japanese splash."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image
from build_native_setup_headings_101 import decoded
from build_font_menu_runtime_090 import raster
from build_g0_first_boot_title_votri_experimental import encode_chibi,tile_to_4bpp
from build_fortune_rank_092 import address
from render_chibi_resource_package import decode_tile
from decompress_chibi_resource import decompress_resource
from build_content_first_040_fortune import apply_ips,make_ips
BASE_SHA='c9138747b7e3f53b5676d110061e96a8d19dc577b1c4676fb5f7e0b259872459'

def tile2(bits):
 return bytes(sum(((bits[y*8+x]>>p)&1)<<(7-x) for x in range(8)) for y in range(8) for p in range(2))

def apply_labels(gfx,maps,bpp,base,plans):
 original=bytes(gfx);outmaps=[];tiles={};packed=bytearray();changes=[]
 for idx,tm in enumerate(maps):
  canvas=Image.new('L',(256,256));attrs=[]
  for k in range(1024):
   w=int.from_bytes(tm[k*2:k*2+2],'little');attrs.append(w&0x3c00);tid=(w&1023)-base
   if tid<0:tile=[[0]*8 for _ in range(8)]
   else:tile=decode_tile(gfx,tid*8*bpp,bpp)
   for y in range(8):
    for x in range(8):canvas.putpixel((k%32*8+x,k//32*8+y),tile[7-y if w&0x8000 else y][7-x if w&0x4000 else x])
  before=canvas.copy()
  for mi,text,rect,size,pal,ink,outline in plans:
   if mi!=idx:continue
   x0,y0,w,h=rect
   for y in range(y0,y0+h):
    for x in range(x0,x0+w):
     if bpp==2:canvas.putpixel((x,y),0)
     elif canvas.getpixel((x,y)) in (11,12,13):canvas.putpixel((x,y),3)
   if text:
    mask=raster(text,FONT,size,w-2,h-2)
    for y in range(h-2):
     for x in range(w-2):
      if mask.getpixel((x,y)):
       for dy in (-1,0,1):
        for dx in (-1,0,1):canvas.putpixel((x0+1+x+dx,y0+1+y+dy),outline)
    for y in range(h-2):
     for x in range(w-2):
      if mask.getpixel((x,y)):canvas.putpixel((x0+1+x,y0+1+y),ink)
   for yy in range(y0//8,(y0+h+7)//8):
    for xx in range(x0//8,(x0+w+7)//8):attrs[yy*32+xx]=(attrs[yy*32+xx]&0x2000)|(pal<<10)
   changes.append({'map':idx,'text':text,'rect':rect})
  result=bytearray()
  for k in range(1024):
   bits=bytes(canvas.getpixel((k%32*8+x,k//32*8+y)) for y in range(8) for x in range(8))
   if bits not in tiles:
    tiles[bits]=len(tiles);packed.extend(tile2(bits) if bpp==2 else tile_to_4bpp(bits))
   result.extend((attrs[k]|(base+tiles[bits])).to_bytes(2,'little'))
  outmaps.append(result)
 return packed,outmaps,changes

def build(clean,base,font):
 global FONT
 FONT=font
 if hashlib.sha256(base).hexdigest()!=BASE_SHA or hashlib.sha256(clean).hexdigest()!='e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956':raise ValueError('Exact106/original required')
 out=bytearray(base);allowed=set(range(0x7fdc,0x7fe0));alloc=[]
 def put(at,data):
  out[at:at+len(data)]=data;allowed.update(range(at,at+len(data)))
 # These are complete unused tails after known resource/code boundaries,
 # not runs ofFF discovered inside compressed resources.
 arenas=iter([(0x124a84,0x125000),(0x127e7f,0x128000),(0x5cb23,0x5cc00),(0x57518,0x58000),(0x5a2bd,0x5a44a),(0x27b14,0x28000),(0x13791f,0x138000)])
 for source,end in [(0x127c98,0x127e7f),(0x5c940,0x5cb23),(0x57340,0x57518),(0x596fe,0x5a2bd)]:
  _,header,_=decompress_resource(base,source)
  if source+header.span!=end:raise AssertionError('Known private allocation boundary changed')
 def reserve(data,low=0x18000,high=0x200000):
  at,end=next(arenas)
  if at+len(data)>end or at//32768!=(at+len(data)-1)//32768 or out[at:at+len(data)]!=b'\xff'*len(data) or clean[at:at+len(data)]!=b'\xff'*len(data):raise AssertionError('Paint guarded allocation collision')
  put(at,data);return at
 def resource(data,refs=(),old=None):
  pack=encode_chibi(bytes(data));blob=(len(pack)+2).to_bytes(2,'little')+pack;at=reserve(blob)
  for ref in refs:
   if base[ref:ref+3]!=address(old).to_bytes(3,'little'):raise AssertionError('Paint resource owner changed')
   put(ref,address(at).to_bytes(3,'little'))
  if decoded(out,at)!=data:raise AssertionError('Paint codec roundtrip')
  alloc.append({'source':hex(old) if old else None,'offset':hex(at),'bytes':len(blob),'pointers':[hex(r) for r in refs]});return at
 # Both BG3 scroll pages share one2bpp atlas. Preserve the character icons.
 plans=[(0,'',(16,48,224,128),9,0,3,1)]
 for text,y in [('Âm bút: ON/OFF',48),('Đổi nhạc',64),('Chế độ: A/B',80),('Đổi tranh',96)]:plans.append((0,text,(72,y,128,16),10,0,3,1))
 for text,x in [('Thoát vẽ?',16),('Xóa tranh?',136)]:plans.append((0,text,(x,128,104,16),10,0,3,1))
 for y in (144,160):
  for text,x in [('Có',16),('Không',80),('Có',136),('Không',200)]:plans.append((0,text,(x,y,40,16),10,0,3,1))
 plans.append((1,'Nhấn START để vẽ',(56,176,144,16),10,0,3,1))
 gfx,maps,changes=apply_labels(decoded(base,0x105816),[decoded(base,0x12f2c6),decoded(base,0xe7f32)],2,256,plans)
 if len(gfx)>4096:raise AssertionError('Paint BG3 atlas reaches OBJ VRAM')
 resource(gfx,[0x1262b],0x105816);resource(maps[0],[0x12630],0x12f2c6);resource(maps[1],[0x12635],0xe7f32)
 # The finish button lives in BG2; both Paint UI packages use the same map.
 gfx,maps,button=apply_labels(decoded(base,0xdd4b8),[decoded(base,0x90efb)],4,0,[(0,'Thoát',(216,12,32,16),9,7,15,11)])
 if len(gfx)>0x3000:raise AssertionError('Paint BG2 VRAM overflow')
 resource(gfx,[0x12621,0x1263d],0xdd4b8);resource(maps[0],[0x12626,0x12642],0x90efb)
 # Keep native input handling and the transition which clears the canvas on
 # START. Replace only phase0 of the four-pen Japanese splash animation.
 im=Image.new('L',(256,256))
 for text,y,size,ink,dark in [('Maruko',32,28,6,4),('Tập vẽ',88,24,11,4)]:
  mask=raster(text,font,size,200,40)
  for yy in range(40):
   for xx in range(200):
    if mask.getpixel((xx,yy)):
     for dy in (-1,0,1):
      for dx in (-1,0,1):im.putpixel((xx+28+dx,yy+y+dy),dark)
  for yy in range(40):
   for xx in range(200):
    if mask.getpixel((xx,yy)):im.putpixel((xx+28,yy+y),ink)
 # Native drawing/erase code uses768 consecutive bitmap tiles and its
 # fixed palette5 map. Keep that geometry so START can clear the entire title.
 gfx=bytearray();tm=bytearray()
 for k in range(1024):
  if k<768:
   bits=bytes(im.getpixel((k%32*8+x,k//32*8+y)) for y in range(8) for x in range(8))
   gfx.extend(tile_to_4bpp(bits));tm.extend((0x1400|k).to_bytes(2,'little'))
  else:tm.extend(bytes(2))
 gr=resource(gfx);mp=resource(tm)
 package=bytes([0,0])+bytes.fromhex('0010')+address(gr).to_bytes(3,'little')+bytes(2)+address(mp).to_bytes(3,'little')+b'\xff'
 if out[0x17f8e:0x17f8e+len(package)]!=b'\xff'*len(package) or clean[0x17f8e:0x17f8e+len(package)]!=b'\xff'*len(package):raise AssertionError('Paint title package collision')
 put(0x17f8e,package)
 stub=b'\xa2\x8e\xff'+bytes.fromhex('2255e280a901008d14145c1be089')
 if out[0xef84:0xef84+len(stub)]!=b'\xff'*len(stub) or clean[0xef84:0xef84+len(stub)]!=b'\xff'*len(stub):raise AssertionError('Paint title stub collision')
 if base[0x4e01b:0x4e022]!=bytes.fromhex('2220e289ee1414'):raise AssertionError('Native splash completion changed')
 put(0xef84,stub)
 if base[0x4dfcf:0x4dfd3]!=bytes.fromhex('ee14149c'):raise AssertionError('Paint splash phase0 changed')
 put(0x4dfcf,b'\x5c'+address(0xef84).to_bytes(3,'little'))
 out[0x7fdc:0x7fe0]=bytes(4);s=(sum(out)+510)&65535;out[0x7fdc:0x7fe0]=(s^65535).to_bytes(2,'little')+s.to_bytes(2,'little')
 if any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(base,out))):raise AssertionError('Write escaped spans')
 ips,count=make_ips(clean,out)
 if apply_ips(clean,ips)!=bytes(out):raise AssertionError('IPS replay')
 return ips,{'status':'107_PAINT_UI_BINARY_PASS','labels':changes+button,'title':['Maruko','Tập vẽ'],'allocations':alloc,'native_input_and_Start_clear_preserved':True,'IPS_SHA256':hashlib.sha256(ips).hexdigest(),'ROM_SHA256':hashlib.sha256(out).hexdigest(),'whole_game_complete':False}

def main():
 p=argparse.ArgumentParser();p.add_argument('original',type=Path);p.add_argument('baseline_ips',type=Path);p.add_argument('--font',type=Path,required=True);p.add_argument('--ips',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args();c=a.original.read_bytes();ips,r=build(c,apply_ips(c,a.baseline_ips.read_bytes()),a.font);a.ips.write_bytes(ips);a.report.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in r.items() if k not in ('labels','allocations')}))
if __name__=='__main__':main()
