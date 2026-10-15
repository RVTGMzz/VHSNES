"""Replace five native selection/setup headings with isolated BG1/OBJ assets."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image
from build_font_menu_runtime_090 import raster
from build_fortune_rank_092 import address
from build_content_first_040_fortune import apply_ips,make_ips
from decompress_chibi_resource import decompress_resource,reorder_flag1_blocks
from build_g0_first_boot_title_votri_experimental import encode_chibi,tile_to_4bpp
from render_chibi_resource_package import decode_tile
BASE_SHA='eeb16eb623568b8c28294af602726a2e9c2e2bc8a80f85a525245c908f2b5de6'
# Exact native package source pointers; each redirected owner is independent.
PLANS=[
 ('Chọn trò chơi',0x12256,0x12251,0x1225b,0x11ae92,None,4,15,3,
  [(0x22,16),(0x0a,16),(0x06,16),(0x24,16),(0xe2,16),(0xec,8),(0xe4,16),(0xea,16),(0xcc,16),(0xce,16)]),
 ('Người chơi',0x1235c,0x1237a,0x12366,0x8fd08,0x8fe7c,0,2,1,
  [(0x0c,16),(0x0e,16),(0x2a,16),(0x7e,8),(0x40,16),(0xc2,16),(0x60,8),(0x70,8),(0x80,8),(0x74,8),(0x64,8),(0x84,8),(0x75,16),(0x65,8),(0x66,8)]),
 ('Thiết lập luật',0x12382,0x123a0,0x1238c,0x8fb8b,0x8fe7c,0,2,1,
  [(0x26,16),(0xc2,16),(0xc6,16),(0xc8,16),(0xed,8),(0xfd,8),(0xca,16),(0xcc,16),(0xce,16),(0xee,16)]),
 ('Chọn nhân vật',0x122b6,0x1229d,0x122ac,0x117c1d,0xd72be,0,3,1,
  [(0xe0,16),(0xe2,16),(0xe4,16),(0xe6,16),(0xe8,16),(0xea,16),(0xec,8)]),
 ('Chia đội',0x12354,0x1233b,0x1234a,0xf82a6,0x1176e9,7,14,15,
  [(0xc0,16),(0xc2,16),(0xc4,16),(0xc6,16),(0xc8,16),(0xed,8),(0xfd,8),(0xca,16),(0xcc,16),(0xce,16),(0xee,16)]),
]
ARENAS=[(0xe100,0x10000),(0x57340,0x58000),(0x5f37e,0x60000),(0x67374,0x68000),(0x12f490,0x130000),(0x17736,0x18000),(0x7720,0x7f90)]
INITIALIZERS={0x12256:(0x20318,0xbe2c,8,0x10b3a5),0x1235c:(0x20a06,0xbe69,8,0x8f825),0x12382:(0x20e4e,0xbe71,8,0x8f825),0x122b6:(0x210a9,0xbe34,8,0xcdd18),0x12354:(0x2161d,0xbe5a,15,0xcdd18)}

def decoded(rom,off):
 raw,h,_=decompress_resource(rom,off)
 return reorder_flag1_blocks(raw) if h.postprocess else raw

def build(clean,base,font):
 if hashlib.sha256(clean).hexdigest()!='e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956' or hashlib.sha256(base).hexdigest()!=BASE_SHA:raise ValueError('Exact original and checkpoint100 required')
 native=bytes.fromhex('dabb0abf00008129ff009003090080fa95009406c894047408186b')
 if clean[0x44eb:0x44eb+len(native)]!=native or base[0x44eb:0x44eb+len(native)]!=native:raise AssertionError('Native palette-job interpreter entry changed')
 common=decoded(base,0xb936a);obj=decoded(base,0xc706f)
 if len(common)!=1376 or len(obj)!=8192 or decoded(clean,0xc706f)!=obj:raise AssertionError('Shared native asset changed')
 pending=[];reports=[];private=bytearray(obj);cleared_union=set()
 for plan in PLANS:
  for tid,size in plan[-1]:
   cleared_union.add(tid)
   if size==16:cleared_union.update((tid+1,tid+16,tid+17))
 for tid in cleared_union:private[tid*32:(tid+1)*32]=bytes(32)
 for caption,gref,oref,mref,mapoff,extra,pal,white,dark,glyphs in PLANS:
  for ref,off in [(gref,0xb936a),(oref,0xc706f),(mref,mapoff)]:
   if base[ref:ref+3]!=address(off).to_bytes(3,'little'):raise AssertionError('Native package pointer changed')
  # BG1 NameBase is VRAM byte2000. Original caption-free graphics end at
  # byte4000; append our atlas there, below the BG2 data starting byte6000.
  gfx=bytearray(0x3000);gfx[:len(common)]=common
  if extra is not None:
   original=decoded(base,extra)
   if 0x560+len(original)>0x2000:raise AssertionError('Caption atlas overlaps native BG1 tiles')
   gfx[0x560:0x560+len(original)]=original
  tm=bytearray(decoded(base,mapoff));cleared=set()
  if len(tm)!=2048:raise AssertionError('Native setup map size changed')
  for tid,size in glyphs:
   cleared.add(tid)
   if size==16:cleared.update((tid+1,tid+16,tid+17))
  # The banner is BG1 itself. Composite the new ink with its original pixels;
  # transparent replacements would punch holes in the native ribbon.
  pal,white,dark=7,14,15
  im=Image.new('L',(160,24),0);mask=raster(caption,font,15,156,20)
  for yy in range(3):
   for xx in range(20):
    k=(yy+1)*32+xx+6;word=int.from_bytes(tm[k*2:k*2+2],'little');tid=word&1023
    tile=decode_tile(gfx,tid*32,4)
    if tid and (word>>10&7)!=7:raise AssertionError('Unexpected banner palette')
    for y in range(8):
     for x in range(8):
      value=tile[7-y if word&0x8000 else y][7-x if word&0x4000 else x]
      if value in (14,15):raise AssertionError('New ink palette slots are used by original banner')
      im.putpixel((xx*8+x,yy*8+y),value)
  for y in range(20):
   for x in range(156):
    if mask.getpixel((x,y)):
     for dy in (-1,0,1):
      for dx in (-1,0,1):im.putpixel((x+2+dx,y+2+dy),dark)
  for y in range(20):
   for x in range(156):
    if mask.getpixel((x,y)):im.putpixel((x+2,y+2),white)
  tiles={};protected={int.from_bytes(tm[k*2:k*2+2],'little')&1023 for k in range(1024) if not(6<=k%32<26 and 1<=k//32<4)}
  if any(t>=256 for t in protected):raise AssertionError('Native BG1 already references reserved atlas')
  for yy in range(3):
   for xx in range(20):
    k=(yy+1)*32+xx+6
    tile=bytes(im.getpixel((xx*8+x,yy*8+y)) for y in range(8) for x in range(8))
    if tile not in tiles:
     tid=256+len(tiles);tiles[tile]=tid;gfx[tid*32:(tid+1)*32]=tile_to_4bpp(tile)
    tm[k*2:k*2+2]=(0x2000|pal<<10|tiles[tile]).to_bytes(2,'little')
  gfx=gfx[:(256+len(tiles))*32]
  if gfx[:len(common)]!=common:raise AssertionError('Common BG1 pixels changed')
  if extra is not None and gfx[0x560:0x560+len(original)]!=original:raise AssertionError('Native BG1 pixels changed')
  for kind,data,ref in [('BG1',gfx,gref),('map',tm,mref)]:
   packed=encode_chibi(bytes(data));blob=(len(packed)+2).to_bytes(2,'little')+packed
   pending.append((blob,ref,caption,kind,bytes(data)))
  reports.append({'caption':caption,'private_heading_tiles':sorted(cleared),'unique_caption_tiles':len(tiles)})
 out=bytearray(base);allowed=set(range(0x7fdc,0x7fe0));spaces=[list(a) for a in ARENAS];alloc=[]
 packed=encode_chibi(bytes(private));pending.append(((len(packed)+2).to_bytes(2,'little')+packed,[p[2] for p in PLANS],'All five','OBJ',bytes(private)))
 # Clone palette jobs in their native bank81, and change only the five
 # initializers. Other users (including the minigame intro) retain originals.
 palette_refs={};script_at=0xdfb0
 for plan in PLANS:
  site,script,size,palette=INITIALIZERS[plan[1]]
  old=b'\xa0'+script.to_bytes(2,'little')+bytes.fromhex('227dc480')
  if base[site:site+7]!=old or clean[script:script+size]!=base[script:script+size]:raise AssertionError('Native palette initializer changed')
  data=base[script:script+size]
  if data[:4]!=bytes.fromhex('28000000') or data[4:7]!=address(palette).to_bytes(3,'little') or data[-1]!=0x12:raise AssertionError('Native palette job format changed')
  if base[script_at:script_at+size]!=b'\xff'*size or clean[script_at:script_at+size]!=b'\xff'*size:raise AssertionError('Private palette job collision')
  out[script_at:script_at+size]=data;allowed.update(range(script_at,script_at+size))
  palette_refs.setdefault(palette,[]).append(script_at+4)
  job=script_at;stub_at=(script_at+size+1)&~1
  # C47D infers interpreter type from the original script address range.
  # C4EB is its native low-range path: select the first byte opcode and set
  # both script-origin and parameter pointers. Reapply it after allocation.
  stub=b'\xa0'+job.to_bytes(2,'little')+bytes.fromhex('227dc480b00422ebc4806b')
  if base[stub_at:stub_at+len(stub)]!=b'\xff'*len(stub) or clean[stub_at:stub_at+len(stub)]!=b'\xff'*len(stub):raise AssertionError('Palette initializer stub collision')
  out[stub_at:stub_at+len(stub)]=stub;allowed.update(range(stub_at,stub_at+len(stub)))
  out[site:site+7]=b'\x22'+address(stub_at).to_bytes(3,'little')+b'\xea'*3;allowed.update(range(site,site+7))
  script_at=(stub_at+len(stub)+1)&~1
 if script_at>0xe100:raise AssertionError('Private palette jobs overflow')
 for palette,refs in palette_refs.items():
  data=bytearray(base[palette:palette+514])
  if data[:2]!=bytes.fromhex('ff01') or bytes(data)!=clean[palette:palette+514]:raise AssertionError('Native palette table changed')
  data[254:258]=bytes.fromhex('ff7f0000')
  pending.append((bytes(data),refs,'Private setup palette','palette',None))
 for blob,ref,caption,kind,data in sorted(pending,key=lambda x:len(x[0]),reverse=True):
  fits=[s for s in spaces if s[1]-s[0]>=len(blob)]
  if not fits:raise AssertionError(f'No guarded allocation for {caption} {kind}: {len(blob)}')
  slot=min(fits,key=lambda s:s[1]-s[0]);at=slot[0];end=at+len(blob)
  if at//0x8000!=(end-1)//0x8000 or base[at:end]!=b'\xff'*len(blob) or clean[at:end]!=b'\xff'*len(blob):raise AssertionError('Private resource allocation collision')
  out[at:end]=blob;allowed.update(range(at,end));refs=ref if isinstance(ref,list) else [ref]
  for ptr in refs:out[ptr:ptr+3]=address(at).to_bytes(3,'little');allowed.update(range(ptr,ptr+3))
  slot[0]=(end+1)&~1
  if data is not None:
   raw,h,_=decompress_resource(out,at)
   if raw!=data or h.postprocess:raise AssertionError('Private resource roundtrip failed')
  alloc.append({'caption':caption,'kind':kind,'pointers':[hex(r) for r in refs],'offset':hex(at),'bytes':len(blob)})
 out[0x7fdc:0x7fe0]=bytes(4);s=(sum(out)+0x1fe)&65535;out[0x7fdc:0x7fe0]=(s^65535).to_bytes(2,'little')+s.to_bytes(2,'little')
 if any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(base,out))):raise AssertionError('101 writes escaped guarded spans')
 ips,count=make_ips(clean,out)
 if apply_ips(clean,ips)!=bytes(out):raise AssertionError('101 IPS replay failed')
 return ips,{'status':'101_FIVE_NATIVE_SETUP_HEADINGS_BINARY_PASS','headings':reports,'allocations':alloc,'original_palettes_preserved':True,'IPS_SHA256':hashlib.sha256(ips).hexdigest(),'ROM_SHA256':hashlib.sha256(out).hexdigest(),'IPS_bytes':len(ips),'IPS_records':count,'emulator_tested':False,'whole_game_complete':False}

def main():
 p=argparse.ArgumentParser();p.add_argument('original',type=Path);p.add_argument('baseline_ips',type=Path);p.add_argument('--font',type=Path,required=True);p.add_argument('--ips',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args();clean=a.original.read_bytes();ips,r=build(clean,apply_ips(clean,a.baseline_ips.read_bytes()),a.font);a.ips.write_bytes(ips);a.report.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,ensure_ascii=True))
if __name__=='__main__':main()
