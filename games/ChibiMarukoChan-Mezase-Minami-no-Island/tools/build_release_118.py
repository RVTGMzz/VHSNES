"""Remove known remaining Japanese labels over exact116 with owned new banks."""
import argparse,csv,hashlib,json
from pathlib import Path
from collections import Counter
from PIL import Image,ImageDraw,ImageFont
from ips_release_118 import apply_ips,make_ips
from build_native_setup_headings_101 import decoded
from build_fortune_rank_092 import address
from build_g0_first_boot_title_votri_experimental import encode_chibi,tile_to_4bpp
from render_chibi_resource_package import decode_tile
ROOT=Path(__file__).resolve().parent.parent
BASE_SHA='bc381e2bc32df0ee6226d88b7ebcf50b3e8091379a67e2593df66dc3589f2d34'

def build(clean,base,bold,regular,root=ROOT):
 if hashlib.sha256(base).hexdigest()!=BASE_SHA or hashlib.sha256(clean).hexdigest()!='e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956':raise ValueError('Exact116/original required')
 # Explicit new ROM banks, never an FF-run search inside live native data.
 out=bytearray(base)+bytearray(b'\xff'*(0x400000-len(base)));allowed=set();cursor=0x200000;alloc=[];edits=[]
 def put(at,blob):out[at:at+len(blob)]=blob;allowed.update(range(at,at+len(blob)))
 def reserve(blob,label):
  nonlocal cursor
  if cursor//32768!=(cursor+len(blob)-1)//32768:cursor=(cursor+32767)&~32767
  at=cursor;cursor+=len(blob)
  if cursor>0x210000:raise AssertionError('New-bank budget exceeded')
  put(at,blob);alloc.append({'label':label,'offset':hex(at),'bytes':len(blob)});return at
 def resource(data,label):
  packed=encode_chibi(bytes(data));at=reserve((len(packed)+2).to_bytes(2,'little')+packed,label)
  if decoded(out,at)!=data:raise AssertionError('Graphics resource roundtrip failed')
  return at
 cp={r['unicode']:bytes.fromhex(r['code_hex']) for r in csv.DictReader((root/'translation/codepage/vi_codepage_v4_fe4_native.csv').open(encoding='utf-8-sig'))}
 def enc(t):return b''.join(cp[c] for c in t)
 # Full names use the existing8px face in the two native footer rows23/25.
 # The title copyright spells out Sakura Production; only its credits label
 # uses the conventional Prod. abbreviation, keeping all staff names complete.
 pages=json.loads((root/'translation/runtime/credits_latin_118.json').read_text(encoding='utf-8'))['pages'];credits=[];lengths=[]
 for i,lines in enumerate(pages):
  data=b'';start=27-2*len(lines)
  if len(lines)>2 or any(len(t)>28 for t in lines):raise AssertionError('Credit geometry overflow')
  for j,t in enumerate(lines):data+=bytes([14,(28-len(t))//2,15,start+j*2])+enc(t)+bytes.fromhex('816f')
  at=reserve(data+b'\x00',f'credits_{i:02d}');put(0x1dea6+i*2,(address(at)&65535).to_bytes(2,'little'));credits.append({'index':i,'source':hex(at),'lines':lines,'rows':list(range(start,27,2))})
  lengths.append(len(data)+1)
 if max(lengths)>144:raise AssertionError('Credit exceeds the existing Quiz scratch buffer lifetime')
 sizes=reserve(b''.join(n.to_bytes(2,'little') for n in lengths),'credit_lengths')
 # Bank C0 has no low WRAM mirror. Stage each complete page into the existing
 # Quiz answer scratch8000..808F while Quiz is inactive. The already-supported
 # bank7E renderer supplies8px pitch and normal RAM accesses. Preserve DBR/P/X/Y.
 if base[0x46cb9:0x46cbd]!=bytes.fromhex('224b8085'):raise AssertionError('Credits job caller changed')
 # Finish the same native synchronous wait loop which immediately follows
 # the original caller, then restore bank83 before later clearing/story jobs.
 # Native88:C6A3 already clears precisely rows23..26 on a preceding frame.
 # Do not enqueue additional clears on the draw frame: the DMA queue is finite.
 main=bytes.fromhex('8bda5a48bf')+address(sizes).to_bytes(3,'little')+bytes.fromhex('3abba00080547ec06848a97e00222b808568a00080224b80852260818590fa48a98300222b8085687afaab286b')
 native=bytes.fromhex('48a98300222b808568285c4b8085')
 stub=bytes.fromhex('08c230e02600b0')+bytes([len(main)])+main+native
 hook=reserve(stub,'credits_bank_and_clear');put(0x46cb9,b'\x22'+address(hook).to_bytes(3,'little'))
 # Preserve all four trailing native aliases, which refer to the first rule
 # record rather than credits. The wrapper falls back to native bank83 for them.
 if any(int.from_bytes(base[0x1dea6+i*2:0x1dea8+i*2],'little')!=0xe2fb for i in range(19,23)):raise AssertionError('Credits trailing aliases changed')
 # Fixed66-byte WRAM answer copies and native grading/index metadata stay put.
 choices=[(0x372c4,'Kazuo (Nhất Hùng)'),(0x3734c,'Kazuo (Hòa Hùng)')]
 for at,t in choices:
  record=bytes.fromhex('0e040f12')+enc(t)+bytes.fromhex('816f00')
  if len(record)>66:raise AssertionError('Quiz answer copy overflow')
  put(at,record+bytes(66-len(record)));edits.append({'source':hex(at),'text':t})
 # One complete native question span, including the old redundant "Tên?"
 # continuation. Keep the next native choice boundary at33DDF intact.
 question=bytes.fromhex('0e040f0a')+enc('Bố của Nagasawa tên gì?')+bytes.fromhex('816f00')
 put(0x33d7b,question+bytes(0x33ddf-0x33d7b-len(question)))
 # Keep the existing explanation's multi-job source boundaries and meaning.
 # It already names Kazuo; the correct choice now also gives Nhất Hùng.
 # Dedicated BG3 copyright stream/map: retain both owner names and date.
 canvas=Image.new('L',(256,256));d=ImageDraw.Draw(canvas);face=ImageFont.truetype(str(regular),9)
 copyright_lines=['©1995 KONAMI. Bảo lưu mọi quyền.','©1995 Sakura Production / Nippon Animation']
 for text,y in zip(copyright_lines,(190,207)):
  box=d.textbbox((0,0),text,font=face);w=box[2]-box[0];h=box[3]-box[1]
  if w>240 or h>12:raise AssertionError('Copyright exceeds its band')
  mask=Image.new('L',(256,256));ImageDraw.Draw(mask).text(((256-w)//2-box[0],y-box[1]),text,font=face,fill=255)
  mask=mask.point(lambda p:255 if p>=100 else 0)
  for yy in range(256):
   for xx in range(256):
    if mask.getpixel((xx,yy)):
     for dy in (-1,0,1):
      for dx in (-1,0,1):canvas.putpixel((xx+dx,yy+dy),3)
  canvas.paste(1,(0,0),mask)
 tiles={bytes(64):0};gfx=bytearray(16);tm=bytearray(2048)
 for yy in range(32):
  for xx in range(32):
   bits=bytes(canvas.getpixel((xx*8+x,yy*8+y)) for y in range(8) for x in range(8))
   if bits not in tiles:
    tiles[bits]=len(tiles)
    for y in range(8):
     for plane in range(2):gfx.append(sum(((bits[y*8+x]>>plane)&1)<<(7-x) for x in range(8)))
   tm[(yy*32+xx)*2:(yy*32+xx)*2+2]=(0x2000|tiles[bits]).to_bytes(2,'little')
 if len(gfx)>4096:raise AssertionError('Copyright tile budget exceeded')
 gfx+=bytes(4096-len(gfx));gs=resource(gfx,'copyright_BG3_gfx');ms=resource(tm,'copyright_BG3_map')
 for pointer,source,new in [(0x120ae,0x8a2bc,gs),(0x120a9,0xf87d7,ms)]:
  if base[pointer:pointer+3]!=address(source).to_bytes(3,'little'):raise AssertionError('Copyright resource owner changed '+hex(pointer))
  put(pointer,address(new).to_bytes(3,'little'))
 # Known background graphics are handled by an explicit per-tile sign plan.
 # Each edit below changes only the native label tile cells, preserving maps.
 sign_reports=[]
 def revise_tiles(source,groups,label):
  gfx=bytearray(decoded(base,source));before=bytes(gfx);changed=set()
  for group in groups:
   ids,text,size,bg,ink,stroke,outline,*extra=group
   h=len(ids)*8;w=len(ids[0])*8;plane=Image.new('L',(w,h))
   for yy,row in enumerate(ids):
    for xx,t in enumerate(row):
     tile=decode_tile(gfx,t*32,4)
     for y in range(8):
      for x in range(8):plane.putpixel((xx*8+x,yy*8+y),tile[y][x])
   # Explicit source label rectangle: interior tiles, no shop frame changes.
   rect=extra[0] if extra else (0,0,w,h);left,top,right,bottom=rect;pw=right-left;ph=bottom-top
   plane.paste(bg,rect);draw=ImageDraw.Draw(plane);face=ImageFont.truetype(str(regular),size)
   if text=='[bottle]':
    draw.rectangle((3,1,4,2),fill=4);draw.rectangle((2,3,5,6),fill=4);draw.rectangle((3,4,4,5),fill=1)
    text=''
   box=draw.multiline_textbbox((0,0),text,font=face,spacing=0,align='center',stroke_width=stroke)
   if box[2]-box[0]>pw or box[3]-box[1]>ph:raise AssertionError('Sign lettering does not fit '+label)
   pos=(left+(pw-(box[2]-box[0]))//2-box[0],top+(ph-(box[3]-box[1]))//2-box[1])
   mask=Image.new('L',(w,h));ImageDraw.Draw(mask).multiline_text(pos,text,font=face,fill=255,spacing=0,align='center',stroke_width=stroke,stroke_fill=255)
   if stroke:
    for y in range(h):
     for x in range(w):
      if mask.getpixel((x,y))>=100:plane.putpixel((x,y),outline)
   mask=Image.new('L',(w,h));ImageDraw.Draw(mask).multiline_text(pos,text,font=face,fill=255,spacing=0,align='center')
   for y in range(h):
    for x in range(w):
     if mask.getpixel((x,y))>=100:plane.putpixel((x,y),ink)
   for yy,row in enumerate(ids):
    for xx,t in enumerate(row):
     blob=tile_to_4bpp(bytes(plane.getpixel((xx*8+x,yy*8+y)) for y in range(8) for x in range(8)));gfx[t*32:t*32+32]=blob;changed.add(t)
  if any(gfx[i]!=before[i] and i//32 not in changed for i in range(len(gfx))):raise AssertionError('Sign pixels escaped tile ownership')
  new=resource(gfx,label);needle=address(source).to_bytes(3,'little');sites=[i for i in range(0x10000,0x18000) if base[i:i+3]==needle]
  if not sites:raise AssertionError('No native package sign owners')
  for i in sites:put(i,address(new).to_bytes(3,'little'))
  sign_reports.append({'label':label,'source':hex(source),'new':hex(new),'changed_tiles':sorted(changed),'owners':[hex(x) for x in sites]})
 # Color indices/rectangles are measured from native maps and palette states.
 # Filled label tiles are all interior cells; originals remain as inactive copies.
 revise_tiles(0x910fc,[([[8,9,10],[17,18,19]],'Mitsuya',6,15,1,0,0,(0,2,24,13)),([[0x25]],'[bottle]',6,1,4,0,0)],'Mitsuya_preview')
 revise_tiles(0xd9b10,[([[0x68,0x69],[0x6c,0x6d]],'ĐÁ',8,5,8,0,0,(1,0,15,11))],'ice_shop_sign')
 revise_tiles(0xfdee6,[([[0x67,0x68,0x69],[0x6a,0x6b,0x6c],[0x6d,0x6e,0x6f],[0x70,0x71,0x72]],'BẠCH\nTUỘC',6,4,8,1,15,(0,6,24,30))],'octopus_stall_sign')
 # Native small Japanese reading annotations are a separate BG1 tile row,
 # copied from B80A after the lyrics. Tile0 is transparent in this package.
 # Keep its timing/DMA path but upload blanks instead of Japanese ruby tiles.
 if base[0x2d2b4:0x2d2ba]!=bytes.fromhex('b90000090024') or base[0x2d296:0x2d29a]!=bytes.fromhex('22448085'):raise AssertionError('Karaoke lyric/ruby callers changed')
 put(0x2d2b4,bytes.fromhex('a90000'))
 # VI wraps onto19/21/23/25, beyond the Japanese two-line clearing pattern.
 # Clear the whole8-row bitmap in WRAM and queue ONE contiguous DMA, avoiding
 # both stale letters and the finite-queue issue found in credits testing.
 lyric_stub=bytes.fromhex('08c230da5a488ba900008f00e67fa200e6a001e6a9fe0f547f7faba900e68500a97f008502afd41f00186900138504a90010850622cd8d85687afa28224480856b')
 lyric_hook=reserve(lyric_stub,'Karaoke_full_bitmap_clear');put(0x2d296,b'\x22'+address(lyric_hook).to_bytes(3,'little'))
 put(0x7fd7,b'\x0c');put(0x7fdc,bytes(4));s=(sum(out)+510)&65535;put(0x7fdc,(s^65535).to_bytes(2,'little')+s.to_bytes(2,'little'))
 if any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(base,out))):raise AssertionError('Mutation outside explicit spans')
 ips,count=make_ips(clean,out)
 return ips,{'status':'118_RELEASE_BINARY_PASS','credits':credits,'credits_names_reference':'https://www.mobygames.com/game/110305/chibi-maruko-chan-mezase-minami-no-island/credits/snes/','quiz_choices':edits,'quiz_grading_metadata_unchanged':out[0x31487:0x314bf]==base[0x31487:0x314bf],'copyright_lines':copyright_lines,'signs':sign_reports,'Karaoke':{'Japanese_ruby_tiles_blanked':True,'bitmap_rows_cleared':[19,26],'one_contiguous_DMA_bytes':4096,'song_music_animation_and_timing_tables_unchanged':True},'allocations':alloc,'ROM_bytes':len(out),'IPS_records':count,'IPS_SHA256':hashlib.sha256(ips).hexdigest(),'ROM_SHA256':hashlib.sha256(out).hexdigest(),'whole_game_complete':False}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('original',type=Path);p.add_argument('baseline',type=Path);p.add_argument('--font-bold',type=Path,required=True);p.add_argument('--font-regular',type=Path,required=True);p.add_argument('--ips',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args();c=a.original.read_bytes();ips,r=build(c,apply_ips(c,a.baseline.read_bytes()),a.font_bold,a.font_regular);a.ips.write_bytes(ips);a.report.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in r.items() if k not in ('credits','allocations')},ensure_ascii=True))
if __name__=='__main__':main()
