"""Normalize both team-selection words to white/black with transparent strips."""
from collections import deque
from build_native_setup_headings_101 import decoded
from decompress_chibi_resource import decompress_resource
from render_chibi_resource_package import decode_tile
from build_g0_first_boot_title_votri_experimental import encode_chibi,tile_to_4bpp

def revise(clean,base,out):
 gfx=bytearray(decoded(base,0xf17a));tm=bytearray(decoded(base,0x57340));original=bytes(gfx);oldmap=bytes(tm)
 if len(gfx)!=9760 or len(tm)!=2048:raise AssertionError('102 label resource shape changed')
 def canvas(origin):
  image=[]
  for y in range(32):
   row=[]
   for x in range(64):
    k=(y//8+16)*32+x//8+origin//8;w=int.from_bytes(tm[k*2:k*2+2],'little');tile=decode_tile(gfx,(w&1023)*32,4)
    row.append(tile[7-y%8 if w&0x8000 else y%8][7-x%8 if w&0x4000 else x%8])
   image.append(row)
  return image
 left=canvas(0);ink={(x,y) for y in range(6,27) for x in range(28,60) if left[y][x]==15}
 if len(ink)<20:raise AssertionError('Native102 word mask not found')
 xmin=min(x for x,y in ink);xmax=max(x for x,y in ink);ymin=min(y for x,y in ink);ymax=max(y for x,y in ink)
 if xmin<28 or xmax-xmin>27:raise AssertionError('102 word mask overlaps mascot or exceeds label')
 clones={};reports=[]
 for origin in (0,192):
  old=canvas(origin);im=[r[:] for r in old]
  background=set();queue=deque((x,y) for y in range(32) for x in range(64) if x in (0,63) or y in (0,31))
  while queue:
   x,y=queue.popleft()
   if not(0<=x<64 and 0<=y<32) or (x,y) in background or old[y][x] not in (0,1,2):continue
   background.add((x,y));queue.extend(((x-1,y),(x+1,y),(x,y-1),(x,y+1)))
  for x,y in background:im[y][x]=0
  for y in range(ymin-1,ymax+2):
   for x in range(xmin-1,xmax+2):
    if im[y][x] in (5,15):im[y][x]=0
  relocated={(x-xmin+33,y) for x,y in ink}
  for x,y in relocated:
   for dy in (-1,0,1):
    for dx in (-1,0,1):im[y+dy][x+dx]=15
  for x,y in relocated:im[y][x]=14
  for y in range(32):
   for x in range(25):
    if (x,y) not in background and im[y][x]!=old[y][x]:raise AssertionError('Native mascot foreground changed')
  for yy in range(4):
   for xx in range(8):
    before=bytes(old[yy*8+y][xx*8+x] for y in range(8) for x in range(8));after=bytes(im[yy*8+y][xx*8+x] for y in range(8) for x in range(8))
    if before==after:continue
    if after not in clones:
     clones[after]=len(gfx)//32;gfx.extend(tile_to_4bpp(after))
    k=(yy+16)*32+xx+origin//8;w=int.from_bytes(tm[k*2:k*2+2],'little');is_word=any(im[yy*8+y][xx*8+x] in (14,15) for y in range(8) for x in range(8)) and xx>=4
    attrs=(w&0x3c00) if not is_word else (w&0x2000)|(7<<10)
    tm[k*2:k*2+2]=(attrs|clones[after]).to_bytes(2,'little')
  reports.append({'origin_x':origin,'word_left_x':33+origin,'foreground_mascot_pixels_preserved':True,'native_strip_background_removed':True,'word_palette':7,'white_index':14,'black_outline_index':15})
 if gfx[:len(original)]!=original:raise AssertionError('Existing native or header atlas changed')
 allowed=set();resources=[]
 for data,start,limit in [(gfx,0xf17a,0x10000),(tm,0x57340,0x58000)]:
  old,h,_=decompress_resource(base,start);packed=encode_chibi(bytes(data));blob=(len(packed)+2).to_bytes(2,'little')+packed;span=max(h.span,len(blob))
  if start+span>limit or clean[start:start+span]!=b'\xff'*span or base[start+h.span:start+span]!=b'\xff'*(span-h.span):raise AssertionError('103 label resource expansion collision')
  out[start:start+span]=blob+b'\xff'*(span-len(blob));allowed.update(range(start,start+span))
  rebuilt,rh,_=decompress_resource(out,start)
  if rebuilt!=data or rh.postprocess:raise AssertionError('103 label codec roundtrip failed')
  resources.append({'offset':hex(start),'bytes':len(blob)})
 return allowed,{'labels':reports,'new_private_tiles':len(clones),'resources':resources}
