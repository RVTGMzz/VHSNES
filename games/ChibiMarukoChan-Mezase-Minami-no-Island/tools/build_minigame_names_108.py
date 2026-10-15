"""Localize three balloon labels, their intro headings and intro start choices."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image
from build_native_setup_headings_101 import decoded
from build_font_menu_runtime_090 import raster
from build_fortune_rank_092 import address
from render_chibi_resource_package import decode_tile
from build_g0_first_boot_title_votri_experimental import encode_chibi,tile_to_4bpp
from decompress_chibi_resource import decompress_resource
from build_content_first_040_fortune import apply_ips,make_ips
BASE_SHA='6ec69c67cdc6bddef521a11b4c4b20e25be75c4ae4a2733d00148e7f9721e3d0'
LABELS=[('Bóng','Ném bóng',(0x2a,0x2c,0x4a,0x4c)),('Sơn','Trượt sơn',(0x22,0x24,0x42,0x44)),('Hồ','Đẩy xuống hồ',(0x26,0x28,0x46,0x48))]

def build(clean,base,font):
 if hashlib.sha256(base).hexdigest()!=BASE_SHA or hashlib.sha256(clean).hexdigest()!='e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956':raise ValueError('Exact107/original required')
 out=bytearray(base);allowed=set(range(0x7fdc,0x7fe0));alloc=[]
 def put(at,data):out[at:at+len(data)]=data;allowed.update(range(at,at+len(data)))
 # All four allocations are owned unused tails. The first is padding
 # left by104's smaller private character stream; the others follow complete
 #101 player-map and107 Paint-gfx streams.
 _,ch,_=decompress_resource(base,0xe100)
 if 0xe100+ch.span!=0xef83:raise AssertionError('104 character allocation boundary changed')
 _,players,_=decompress_resource(base,0x67960)
 if 0x67960+players.span!=0x67b04:raise AssertionError('101 player-map boundary changed')
 _,paint,_=decompress_resource(base,0x57518)
 if 0x57518+paint.span!=0x57c1a:raise AssertionError('107 Paint allocation boundary changed')
 arenas=iter([(0xeff0,0xf17a),(0x67b04,0x67d60),(0x67d60,0x68000),(0x57c1a,0x58000)])
 def reserve(data):
  at,end=next(arenas)
  if at+len(data)>end or at//32768!=(at+len(data)-1)//32768 or out[at:at+len(data)]!=b'\xff'*len(data) or clean[at:at+len(data)]!=b'\xff'*len(data):raise AssertionError('Intro guarded allocation collision')
  put(at,data);return at
 def resource(data,at=None,span=None):
  packed=encode_chibi(bytes(data));blob=(len(packed)+2).to_bytes(2,'little')+packed
  if at is None:at=reserve(blob)
  else:
   if len(blob)>span:raise AssertionError('Intro guarded resource overflow '+str(len(blob)))
   put(at,blob+b'\xff'*(span-len(blob)))
  if decoded(out,at)!=data:raise AssertionError('Intro codec roundtrip')
  alloc.append({'offset':hex(at),'bytes':len(blob)});return at
 # Both real type0 owners use the same native balloon / start-choice atlas.
 key=address(0x9f18e).to_bytes(3,'little');refs=[i for i in range(0x10000,0x18000) if base[i:i+3]==key]
 if refs!=[0x1224c,0x1228b]:raise AssertionError('Unexpected shared balloon resource owner')
 raw,h,_=decompress_resource(base,0x9f18e);gfx=bytearray(decoded(base,0x9f18e));oldgfx=bytes(gfx);changed=set();reports=[]
 for short,full,tids in LABELS:
  im=Image.new('L',(32,32))
  for y in range(32):
   for x in range(32):
    t=tids[y//16*2+x//16]+(y%16//8)*16+x%16//8;im.putpixel((x,y),decode_tile(gfx,t*32,4)[y%8][x%8])
  before=im.copy()
  for y in range(23,32):
   for x in range(3,29):
    if im.getpixel((x,y)) in (5,7):im.putpixel((x,y),9)
  mask=raster(short,font,8,26,9)
  for y in range(9):
   for x in range(26):
    if mask.getpixel((x,y)):im.putpixel((x+3,y+23),11)
  for y in range(32):
   for x in range(32):
    if not(3<=x<29 and 23<=y<32) and im.getpixel((x,y))!=before.getpixel((x,y)):raise AssertionError('Balloon art outside label changed')
  for yy in range(4):
   for xx in range(4):
    t=tids[yy//2*2+xx//2]+(yy%2)*16+xx%2;gfx[t*32:(t+1)*32]=tile_to_4bpp(bytes(im.getpixel((xx*8+x,yy*8+y)) for y in range(8) for x in range(8)));changed.add(t)
  reports.append({'balloon':short,'intro':full,'protected_number_and_canopy':True})
 # Remove the two Japanese intro options from their exclusive native cells.
 ui=set()
 for t in (0x80,0x82,0x84,0x86,0x88):ui.update((t,t+1,t+16,t+17))
 ui.update((0x6d,0x6e,0x6f,0x7d,0x7e,0x7f))
 for t in ui:gfx[t*32:(t+1)*32]=bytes(32)
 for text,parts,width,size in [('Chơi',(0x80,0x82,0x84),48,11),('Luật chơi',(0x86,0x88,0x6d,0x6f),56,10)]:
  mask=raster(text,font,size,width-2,14);im=Image.new('L',(width,16))
  for y in range(14):
   for x in range(width-2):
    if mask.getpixel((x,y)):
     for dy in (-1,0,1):
      for dx in (-1,0,1):im.putpixel((x+1+dx,y+1+dy),1)
  for y in range(14):
   for x in range(width-2):
    if mask.getpixel((x,y)):im.putpixel((x+1,y+1),3)
  for j,t in enumerate(parts):
   block_width=8 if j==3 else 16
   for yy in range(2):
    for xx in range(block_width//8):
     tid=t+yy*16+xx;gfx[tid*32:(tid+1)*32]=tile_to_4bpp(bytes(im.getpixel((j*16+xx*8+x,yy*8+y)) for y in range(8) for x in range(8)))
 changed|=ui
 if any(gfx[t*32:(t+1)*32]!=oldgfx[t*32:(t+1)*32] for t in range(256) if t not in changed):raise AssertionError('Native actors / balloon controls changed')
 # Emit a normal (non-permuted) stream into the exact original owned span.
 resource(gfx,0x9f18e,h.span)
 blank=resource(bytes(8192))
 if base[0x12290:0x12293]!=address(0xd5d31).to_bytes(3,'little'):raise AssertionError('Intro heading OBJ owner changed')
 put(0x12290,address(blank).to_bytes(3,'little'))
 # The old101 team atlas has no active resource owner since102. Reuse its
 # original private allocation after checking all native bank82 references.
 oldkey=address(0x12f490).to_bytes(3,'little')
 if any(base[i:i+3]==oldkey for i in range(0x10000,0x18000)) or clean[0x12f490:0x12fe2b]!=b'\xff'*(0x99b):raise AssertionError('Retired team atlas is still referenced')
 _,retired,_=decompress_resource(base,0x12f490)
 if retired.span!=2459:raise AssertionError('Retired101 atlas changed')
 originalmap=decoded(base,0x124649);originalBG=decoded(base,0x9e98e);newgfx=bytearray();tiles={};maps=[]
 for _,title,_ in LABELS:
  tm=bytearray(originalmap)
  for text,rect,size in [(title,(80,40,176,24),16)]:
   x0,y0,w,hh=rect;im=Image.new('L',(w,hh));mask=raster(text,font,size,w-2,hh-2)
   for y in range(hh-2):
    for x in range(w-2):
     if mask.getpixel((x,y)):
      for dy in (-1,0,1):
       for dx in (-1,0,1):im.putpixel((x+1+dx,y+1+dy),1)
   for y in range(hh-2):
    for x in range(w-2):
     if mask.getpixel((x,y)):im.putpixel((x+1,y+1),15)
   for yy in range(hh//8):
    for xx in range(w//8):
     k=(y0//8+yy)*32+x0//8+xx;word=int.from_bytes(originalmap[k*2:k*2+2],'little');native=decode_tile(originalBG,(word&1023)*32,4)
     if any(v for row in native for v in row):raise AssertionError('Intro caption would cover original scenery '+str((text,k%32,k//32,hex(word))))
     bits=bytes(im.getpixel((xx*8+x,yy*8+y)) for y in range(8) for x in range(8))
     if bits not in tiles:tiles[bits]=256+len(tiles);newgfx.extend(tile_to_4bpp(bits))
     tm[k*2:k*2+2]=(0x2000|5<<10|tiles[bits]).to_bytes(2,'little')
  maps.append(resource(tm))
 if len(newgfx)>8192:raise AssertionError('Intro font atlas reaches BG2 VRAM')
 ga=resource(newgfx,0x12f490,2459)
 # Three tiny partial packages append the common font atlas then the selected
 # map after the native full resource load. The selection comes from7E2040.
 packages=[];cursor=0x17f9c
 for mp in maps:
  data=bytes([0,0])+bytes.fromhex('0020')+address(ga).to_bytes(3,'little')+bytes(2)+address(mp).to_bytes(3,'little')+b'\xff'
  if base[cursor:cursor+len(data)]!=b'\xff'*len(data) or clean[cursor:cursor+len(data)]!=b'\xff'*len(data):raise AssertionError('Intro partial package collision')
  put(cursor,data);packages.append(cursor);cursor+=len(data)
 at=0xefa0
 stub=bytes.fromhex('a269a22255e280af40207e29ff000aaa')
 table=at+len(stub)+4+1+4+1
 stub+=b'\xbf'+address(table).to_bytes(3,'little')+bytes.fromhex('aa2255e2806b')
 stub+=b''.join((address(p)&65535).to_bytes(2,'little') for p in packages)
 if len(stub)>33 or base[at:at+len(stub)]!=b'\xff'*len(stub) or clean[at:at+len(stub)]!=b'\xff'*len(stub):raise AssertionError('Intro loader stub collision')
 put(at,stub)
 if base[0x203b5:0x203bc]!=bytes.fromhex('a269a22255e280'):raise AssertionError('Intro native loader changed')
 put(0x203b5,b'\x22'+address(at).to_bytes(3,'little')+b'\xea'*3)
 out[0x7fdc:0x7fe0]=bytes(4);s=(sum(out)+510)&65535;out[0x7fdc:0x7fe0]=(s^65535).to_bytes(2,'little')+s.to_bytes(2,'little')
 if any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(base,out))):raise AssertionError('Write escaped spans')
 ips,count=make_ips(clean,out)
 if apply_ips(clean,ips)!=bytes(out):raise AssertionError('IPS replay')
 return ips,{'status':'108_BALLOON_AND_MINIGAME_INTRO_BINARY_PASS','labels':reports,'intro_options':['Chơi','Luật chơi'],'native_scenery_and_actors_preserved':True,'palette_unchanged':True,'retired101_atlas_reused':True,'allocations':alloc,'IPS_SHA256':hashlib.sha256(ips).hexdigest(),'ROM_SHA256':hashlib.sha256(out).hexdigest(),'whole_game_complete':False}

def main():
 p=argparse.ArgumentParser();p.add_argument('original',type=Path);p.add_argument('baseline_ips',type=Path);p.add_argument('--font',type=Path,required=True);p.add_argument('--ips',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args();c=a.original.read_bytes();ips,r=build(c,apply_ips(c,a.baseline_ips.read_bytes()),a.font);a.ips.write_bytes(ips);a.report.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in r.items() if k!='allocations'}))
if __name__=='__main__':main()



