"""Translate the live Story play-again BG artwork, retaining stage and actors.

Native $88:FB24 loads package $82:B481. The seven-record package owns one
isolated BG glyph resource and one tilemap; actor OBJ assets remain intact.
"""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image
from build_font_menu_runtime_090 import raster
from build_fortune_rank_092 import address
from build_content_first_040_fortune import apply_ips,make_ips
from decompress_chibi_resource import decompress_resource,reorder_flag1_blocks
from build_g0_first_boot_title_votri_experimental import encode_chibi,tile_to_4bpp
BASE_SHA='f92ab44009ec5ff4e0c0d0bb11ed75cd3520462c46299867b9ad4bcbc0b61207'
def pixels(b):return bytes(sum(((b[y*2+bit//2*16+bit%2]>>(7-x))&1)<<bit for bit in range(4)) for y in range(8) for x in range(8))
def edited(x,y):return y<10 or (15<=y<20 and (3<=x<11 or 21<=x<29))
def build(clean,base,font):
 if hashlib.sha256(base).hexdigest()!=BASE_SHA or hashlib.sha256(clean).hexdigest()!='e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956':raise ValueError('Requires exact original ROM and 095 baseline')
 if clean[0x47b24:0x47b2b]!=bytes.fromhex('A281B42255E280') or base[0x47b24:0x47b2b]!=clean[0x47b24:0x47b2b]:raise AssertionError('Native play-again package caller changed')
 for off,ptr in [(0xc5f3e,0x1348a),(0xe875b,0x13494)]:
  owners=[i for i in range(len(clean)) if clean.startswith(address(off).to_bytes(3,'little'),i)]
  if owners!=[ptr]:raise AssertionError('Play-again asset ownership changed')
 raw,h,_=decompress_resource(base,0xc5f3e);original=reorder_flag1_blocks(raw);gfx=bytearray(original+bytes(8192-len(raw)))
 tm,mh,_=decompress_resource(base,0xe875b);m=bytearray(tm)
 if len(raw)!=5056 or not h.postprocess or len(tm)!=2048 or mh.postprocess or base[0xc5f3e:0xc5f3e+h.span]!=clean[0xc5f3e:0xc5f3e+h.span] or base[0xe875b:0xe875b+mh.span]!=clean[0xe875b:0xe875b+mh.span]:raise AssertionError('Original play-again asset changed')
 protected={int.from_bytes(tm[k*2:k*2+2],'little')&1023 for k in range(1024) if not edited(k%32,k//32)}
 pool=iter(sorted(set(range(256,512))-protected));unique={}
 def store(canvas,x0,y0,pal):
  for yy in range(canvas.height//8):
   for xx in range(canvas.width//8):
    x=x0+xx;y=y0+yy
    if not edited(x,y):raise AssertionError('Play-again art escapes isolated text region')
    tile=bytes(canvas.getpixel((xx*8+x,yy*8+y)) for y in range(8) for x in range(8))
    if tile not in unique:
     try:tid=next(pool)
     except StopIteration:raise AssertionError('Play-again unshared tile pool exhausted')
     unique[tile]=tid;gfx[(tid-256)*32:(tid-255)*32]=tile_to_4bpp(tile)
    k=y*32+x;m[k*2:k*2+2]=(pal*1024+unique[tile]).to_bytes(2,'little')
 def ink(canvas,label,size):
  mask=raster(label,font,size,canvas.width-4,canvas.height-4)
  for y in range(mask.height):
   for x in range(mask.width):
    if mask.getpixel((x,y)):
     for dy in (-1,0,1):
      for dx in (-1,0,1):canvas.putpixel((x+2+dx,y+2+dy),1)
  for y in range(mask.height):
   for x in range(mask.width):
    if mask.getpixel((x,y)):canvas.putpixel((x+2,y+2),15)
 header=Image.new('P',(256,80),0);line=Image.new('P',(256,32),0);ink(line,'Chơi tiếp nhé?',22);header.paste(line,(0,0));store(header,0,0,3)
 for x0,label,size,pal in [(3,'Có',20,3),(21,'Thoát',16,4)]:
  board=Image.new('P',(64,40),0)
  for yy in range(5):
   for xx in range(8):
    k=(15+yy)*32+x0+xx;w=int.from_bytes(tm[k*2:k*2+2],'little');tid=w&1023
    if not 256<=tid<414:raise AssertionError('Play-again sign references outside isolated asset')
    # Read original asset, not the pool data already replaced by the header.
    tile=pixels(original[(tid-256)*32:(tid-255)*32])
    for y in range(8):
     for x in range(8):board.putpixel((xx*8+x,yy*8+y),tile[(7-y if w&0x8000 else y)*8+(7-x if w&0x4000 else x)])
  for y in range(2,38):
   for x in range(2,62):
    if board.getpixel((x,y)) in (1,2,6,15):board.putpixel((x,y),11+((x+y)%2))
  ink(board,label,size);store(board,x0,15,pal)
 for tid in protected:
  if 256<=tid<414 and gfx[(tid-256)*32:(tid-255)*32]!=original[(tid-256)*32:(tid-255)*32]:raise AssertionError('Play-again pole/frame tile changed')
 inverse=bytearray(len(gfx));order=(0,8,1,9,2,10,3,11,4,12,5,13,6,14,7,15)
 for pos in range(0,len(gfx),16):
  for dst,src in enumerate(order):inverse[pos+src]=gfx[pos+dst]
 out=bytearray(base);allowed=set(range(0x7fdc,0x7fe0));cursor=0x5db00;resources=[]
 for decoded,flag,ref,old in [(inverse,True,0x1348a,0xc5f3e),(m,False,0x13494,0xe875b)]:
  packed=encode_chibi(bytes(decoded));blob=(len(packed)+2|(0x8000 if flag else 0)).to_bytes(2,'little')+packed
  if cursor+len(blob)>0x60000 or clean[cursor:cursor+len(blob)]!=b'\xff'*len(blob) or base[cursor:cursor+len(blob)]!=b'\xff'*len(blob):raise AssertionError('Play-again relocation collision')
  if base[ref:ref+3]!=address(old).to_bytes(3,'little'):raise AssertionError('Play-again native package pointer changed')
  out[ref:ref+3]=address(cursor).to_bytes(3,'little');allowed.update(range(ref,ref+3));out[cursor:cursor+len(blob)]=blob;allowed.update(range(cursor,cursor+len(blob)))
  rebuilt,rh,_=decompress_resource(out,cursor)
  if rebuilt!=decoded or rh.postprocess!=flag:raise AssertionError('Play-again codec round-trip failed')
  resources.append({'relocated':hex(cursor),'bytes':len(blob),'pointer':hex(ref)});cursor=(cursor+len(blob)+1)&~1
 out[0x7fdc:0x7fe0]=bytes(4);s=(sum(out)+0x1fe)&65535;out[0x7fdc:0x7fe0]=(s^65535).to_bytes(2,'little')+s.to_bytes(2,'little')
 if any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(base,out))):raise AssertionError('Play-again writes escaped guarded spans')
 ips,count=make_ips(clean,out)
 if apply_ips(clean,ips)!=bytes(out):raise AssertionError('096 IPS replay failed')
 return ips,{'status':'096_NATIVE_PLAY_AGAIN_GRAPHICS_BINARY_PASS','labels':['Chơi tiếp nhé?','Có','Thoát'],'unique_tiles':len(unique),'resources':resources,'actors_and_original_animations_preserved':True,'ROM_SHA256':hashlib.sha256(out).hexdigest(),'IPS_SHA256':hashlib.sha256(ips).hexdigest(),'IPS_bytes':len(ips),'IPS_records':count,'emulator_tested':False}
def main():
 p=argparse.ArgumentParser();p.add_argument('original',type=Path);p.add_argument('baseline_ips',type=Path);p.add_argument('--font',type=Path,required=True);p.add_argument('--ips',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args();clean=a.original.read_bytes();ips,r=build(clean,apply_ips(clean,a.baseline_ips.read_bytes()),a.font);a.ips.write_bytes(ips);a.report.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,ensure_ascii=True))
if __name__=='__main__':main()
