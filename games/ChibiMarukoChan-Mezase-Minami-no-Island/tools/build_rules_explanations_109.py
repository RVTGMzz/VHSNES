"""Translate all three live rules pages and the native rules-screen heading."""
import argparse,csv,hashlib,json,textwrap
from pathlib import Path
from PIL import Image
from build_karaoke_lyrics_106 import lyric_selector
from build_quiz_layout_087 import spacing_stub,destination_stub,wrap_stub
from build_native_setup_headings_101 import decoded
from build_font_menu_runtime_090 import raster
from build_fortune_rank_092 import address
from build_g0_first_boot_title_votri_experimental import encode_chibi,tile_to_4bpp
from render_chibi_resource_package import decode_tile
from build_content_first_040_fortune import apply_ips,make_ips
ROOT=Path(__file__).resolve().parent.parent
BASE_SHA='697a9d220e5adb315ea7699dd9791409d34d4fb45385aaafef1d2b15f0f12a93'

from layout_contexts_109 import rules_selector

def build(clean,base,font,root=ROOT):
 if hashlib.sha256(base).hexdigest()!=BASE_SHA or hashlib.sha256(clean).hexdigest()!='e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956':raise ValueError('Exact108/original required')
 out=bytearray(base);allowed=set(range(0x7fdc,0x7fe0));cp={r['unicode']:bytes.fromhex(r['code_hex']) for r in csv.DictReader((root/'translation/codepage/vi_codepage_v4_fe4_native.csv').open(encoding='utf-8-sig'))}
 def put(at,data):out[at:at+len(data)]=data;allowed.update(range(at,at+len(data)))
 def encode(text):return b''.join(cp[c] for c in text)
 def line(text,col,row):
  if col+len(text)>28:raise AssertionError('Rules row exceeds28columns')
  return bytes([14,col,15,row])+encode(text)+bytes.fromhex('816f')
 records=[];report=[]
 paragraphs=['Ném bóng trúng đối thủ. Cúi xuống để né bóng.','Sơn thật khéo để đối thủ giẫm phải. Có thể dùng máy sấy làm khô sơn.','Đẩy hoặc hất đối thủ xuống hồ!']
 controls=[[('Cúi',18,19),('Đi',2,21),('Ném',18,23),('bóng',18,25)],[('Sấy',18,19),('Đi',2,21),('Giữ nút',18,23),('Sơn',18,25)],[('Ném',18,19),('Đi',2,21),('Húc',18,23)]]
 for i,(paragraph,labels) in enumerate(zip(paragraphs,controls)):
  lines=(["Ném bóng trúng đối thủ.","Cúi xuống để né bóng."] if i==0 else ["Đẩy hoặc hất đối thủ","xuống hồ!"] if i==2 else textwrap.wrap(paragraph,width=27,break_long_words=False,break_on_hyphens=False))
  if len(lines)>3:raise AssertionError('Rules body exceeds three rows')
  rec=b''.join(line(t,1,9+j*2) for j,t in enumerate(lines))+b''.join(line(*v) for v in labels)+bytes.fromhex('8198')
  records.append(rec);report.append({'game':i,'paragraph':paragraph,'body_lines':lines,'controls':[v[0] for v in labels],'bytes':len(rec)})
 expected_native=bytearray(clean[0x288be:0x28a90]);expected_native[0x1c8:0x1ce]=encode('Húc')
 if base[0x288be:0x28a90]!=expected_native or base[0x2f821:0x2fa00]!=b'\xff'*(0x1df):raise AssertionError('Native rules text pools changed')
 put(0x288be,bytes(0x1d2));pools=[[0x288be,0x28a90],[0x2f821,0x2fa00]];placed={}
 for i in sorted(range(3),key=lambda i:len(records[i]),reverse=True):
  fits=[p for p in pools if p[1]-p[0]>=len(records[i])]
  if not fits:raise AssertionError('Rules text pool exhausted')
  slot=min(fits,key=lambda p:p[1]-p[0]);at=slot[0];put(at,records[i]);slot[0]+=len(records[i]);placed[i]=at;report[i]['record']=hex(at)
 expected=[0x88be,0x8954,0x8a1a,0x8a1a]
 for j,i in enumerate((0,1,2,2)):
  ptr=0x21c15+j*2
  if int.from_bytes(base[ptr:ptr+2],'little')!=expected[j]:raise AssertionError('Rules page pointer table changed')
  put(ptr,(placed[i]&65535).to_bytes(2,'little'))
 for at,old,new in [(0x2fb80,spacing_stub(True,lyric_selector),spacing_stub(True,rules_selector)),(0x2fc00,spacing_stub(False,lyric_selector),spacing_stub(False,rules_selector)),(0x2fc80,wrap_stub(lyric_selector),wrap_stub(rules_selector)),(0x2fe00,destination_stub(lyric_selector),destination_stub(rules_selector))]:
  if len(new)>128 or base[at:at+len(old)]!=old or base[at+len(old):at+len(new)]!=b'\xff'*(len(new)-len(old)):raise AssertionError('Rules spacing stub collision')
  put(at,new)
 #108 detached the sole original OBJ owner fromD5D31. Reuse its complete
 #4116-byte allocation, after proving no remaining ROM pointer references it.
 key=address(0xd5d31).to_bytes(3,'little')
 if base.count(key)!=0 or base[0xd5d31:0xd6d45]!=clean[0xd5d31:0xd6d45]:raise AssertionError('Retired native intro atlas is still owned or changed')
 cursor=0xd5d31;resources=[]
 def asset(data,compressed=True):
  nonlocal cursor
  if compressed:
   packed=encode_chibi(bytes(data));blob=(len(packed)+2).to_bytes(2,'little')+packed
  else:blob=bytes(data)
  at=cursor;cursor=(cursor+len(blob)+1)&~1
  if cursor>0xd6d45:raise AssertionError('Retired intro resource allocation exhausted')
  put(at,blob);resources.append({'offset':hex(at),'bytes':len(blob),'compressed':compressed})
  if compressed and decoded(out,at)!=data:raise AssertionError('Rules asset codec roundtrip')
  return at
 gfx=bytearray(8192);common=decoded(base,0xb936a);gfx[:len(common)]=common;tm=bytearray(decoded(base,0x11ae92));im=Image.new('L',(160,24));mask=raster('Luật chơi',font,15,156,20)
 for yy in range(3):
  for xx in range(20):
   k=(yy+1)*32+xx+6;w=int.from_bytes(tm[k*2:k*2+2],'little');tile=decode_tile(gfx,(w&1023)*32,4)
   for y in range(8):
    for x in range(8):
     v=tile[7-y if w&0x8000 else y][7-x if w&0x4000 else x]
     if v in (14,15):raise AssertionError('Original banner uses new ink slots')
     im.putpixel((xx*8+x,yy*8+y),v)
 for y in range(20):
  for x in range(156):
   if mask.getpixel((x,y)):
    for dy in (-1,0,1):
     for dx in (-1,0,1):im.putpixel((x+2+dx,y+2+dy),15)
 for y in range(20):
  for x in range(156):
   if mask.getpixel((x,y)):im.putpixel((x+2,y+2),14)
 tiles={}
 for yy in range(3):
  for xx in range(20):
   bits=bytes(im.getpixel((xx*8+x,yy*8+y)) for y in range(8) for x in range(8))
   if bits not in tiles:tiles[bits]=256+len(tiles);gfx.extend(tile_to_4bpp(bits))
   k=(yy+1)*32+xx+6;tm[k*2:k*2+2]=(0x2000|7<<10|tiles[bits]).to_bytes(2,'little')
 gr=asset(gfx);mp=asset(tm)
 for ref,old,new in [(0x121f6,0xb936a,gr),(0x121fb,0x11ae92,mp)]:
  if base[ref:ref+3]!=address(old).to_bytes(3,'little'):raise AssertionError('Rules resource owner changed')
  put(ref,address(new).to_bytes(3,'little'))
 palette=bytearray(base[0xc8081:0xc8081+514])
 if palette[:2]!=bytes.fromhex('ff01') or palette!=clean[0xc8081:0xc8081+514]:raise AssertionError('Rules palette changed')
 palette[254:258]=bytes.fromhex('ff7f0000');pa=asset(palette,False)
 script=bytearray(base[0xbe24:0xbe2c])
 if script!=bytes.fromhex('2800000081809912'):raise AssertionError('Native rules palette job changed')
 script[4:7]=address(pa).to_bytes(3,'little')
 for at,data in [(0xf040,script),(0xf04a,b'\xa0\x40\xf0'+bytes.fromhex('227dc480b00422ebc4806b'))]:
  if base[at:at+len(data)]!=b'\xff'*len(data) or clean[at:at+len(data)]!=b'\xff'*len(data):raise AssertionError('Rules palette-job padding collision')
  put(at,data)
 if base[0x21c0b:0x21c12]!=bytes.fromhex('a024be227dc480') or base[0x21c57:0x21c61]!=bytes.fromhex('a96500a0600422dfa684'):raise AssertionError('Native rules heading initializer changed')
 put(0x21c0b,b'\x22'+address(0xf04a).to_bytes(3,'little')+b'\xea'*3);put(0x21c57,b'\xea'*10)
 out[0x7fdc:0x7fe0]=bytes(4);s=(sum(out)+510)&65535;out[0x7fdc:0x7fe0]=(s^65535).to_bytes(2,'little')+s.to_bytes(2,'little')
 if any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(base,out))):raise AssertionError('Write escaped spans')
 ips,count=make_ips(clean,out)
 if apply_ips(clean,ips)!=bytes(out):raise AssertionError('IPS replay')
 return ips,{'status':'109_ALL_THREE_RULES_EXPLANATIONS_BINARY_PASS','rules':report,'heading':'Luật chơi','resources':resources,'native_controller_picture_and_input_preserved':True,'IPS_SHA256':hashlib.sha256(ips).hexdigest(),'ROM_SHA256':hashlib.sha256(out).hexdigest(),'whole_game_complete':False}

def main():
 p=argparse.ArgumentParser();p.add_argument('original',type=Path);p.add_argument('baseline_ips',type=Path);p.add_argument('--font',type=Path,required=True);p.add_argument('--ips',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args();c=a.original.read_bytes();ips,r=build(c,apply_ips(c,a.baseline_ips.read_bytes()),a.font);a.ips.write_bytes(ips);a.report.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in r.items() if k!='resources'}))
if __name__=='__main__':main()



