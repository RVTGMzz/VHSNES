"""Install all28 Vietnamese lyric fields with relocated native page pointers."""
import argparse,csv,hashlib,json
from pathlib import Path
from build_story_spacing_095 import story_selector
from build_quiz_layout_087 import spacing_stub,destination_stub,wrap_stub
from build_content_first_040_fortune import apply_ips,make_ips
ROOT=Path(__file__).resolve().parent.parent
BASE_SHA='45a90fceffbc786eed40d00e51ed9dbf7ebb03afca8f263fc9d26a62f1d2e150'

def lyric_selector(a):
 a.emit(0xAF,0x86,0x1F,0,0x29,0x7F,0)
 for bank in (3,6):a.cmp16(bank);a.branch(0xF0,'quiz')
 a.cmp16(5);a.branch(0xF0,'bank5')
 a.cmp16(0x7e);a.branch(0xD0,'native');a.emit(0xAF,0x94,0x1F,0)
 a.cmp16(0x8000);a.branch(0x90,'native');a.cmp16(0x8090);a.branch(0x90,'quiz');a.branch(0x80,'native')
 a.label('bank5');a.emit(0xAF,0x94,0x1F,0)
 for lo,hi,label in [(0xb37a,0xb80a,'fortune'),(0xbd24,0xcb9b,'lyrics'),(0xf272,0xf800,'relocated')]:
  a.cmp16(lo);a.branch(0x90,label);a.cmp16(hi);a.branch(0x90,'quiz');a.label(label)
 a.cmp16(0xff20);a.branch(0x90,'native');a.cmp16(0xffa0);a.branch(0x90,'quiz')

def build(clean,base,root=ROOT):
 if hashlib.sha256(base).hexdigest()!=BASE_SHA or hashlib.sha256(clean).hexdigest()!='e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956':raise ValueError('Exact105/original required')
 out=bytearray(base);allowed=set(range(0x7fdc,0x7fe0));cp={r['unicode']:bytes.fromhex(r['code_hex']) for r in csv.DictReader((root/'translation/codepage/vi_codepage_v4_fe4_native.csv').open(encoding='utf-8-sig'))};rows=list(csv.DictReader((root/'translation/source/karaoke_batch01_vi.csv').open(encoding='utf-8-sig')))
 starts=[int.from_bytes(clean[i:i+2],'little')+0x20000 for i in range(0x2b35e,0x2b37a,2)]
 if starts!=[0x2b37a,0x2b3cf,0x2b422,0x2b477,0x2b4cc,0x2b51f,0x2b572,0x2b5c7,0x2b61c,0x2b66f,0x2b6c2,0x2b715,0x2b768,0x2b7bb]:raise AssertionError('Native14page table changed')
 if base[0x2b37a:0x2b7bb]!=clean[0x2b37a:0x2b7bb] or base[0x2f272:0x2f800]!=b'\xff'*(0x58e):raise AssertionError('Lyric arenas changed')
 pending=[];fields=[]
 for page,(lo,hi) in enumerate(zip(starts,starts[1:])):
  parts=[];cursor=lo;col=1;line=19
  for row in rows:
   at=int(row['file_offset'],16)
   if not lo<=at<hi:continue
   actual=at
   while clean[actual]==32:actual+=1
   jp=row['source_jp'].encode('cp932')
   if clean[actual:actual+len(jp)]!=jp:raise AssertionError('Lyric source mismatch '+hex(at))
   end=actual+len(jp)
   while clean[end]==32:end+=1
   prefix=clean[cursor:at];q=0;reset=False
   while q<len(prefix):
    value=prefix[q]
    if value in (14,15,16):
     if value==14:col=prefix[q+1];reset=True
     if value==15:line=prefix[q+1]
     q+=2
    elif prefix[q:q+2]==bytes.fromhex('816f'):q+=2
    elif value==32:q+=1
    else:raise AssertionError('Unknown lyric prefix control')
   payload=bytearray()
   for word in row['vi_full'].split(' '):
    need_space=col>1
    if col+len(word)+int(need_space)>28:
     line+=2
     if line not in (21,25):raise AssertionError('Lyric word wrap exceeds two rows')
     payload.extend(bytes.fromhex('816f')+bytes([14,1,15,line]));col=1;need_space=False
    if need_space:payload.extend(cp[' ']);col+=1
    payload.extend(b''.join(cp[c] for c in word));col+=len(word)
   parts.extend((prefix,bytes(payload)));cursor=end
   if len(row['vi_full'])>54:raise AssertionError('Lyric exceeds two compact rows')
   fields.append({'source_offset':hex(at),'actual_original_text':hex(actual),'Vietnamese':row['vi_full'],'page':page})
  parts.append(clean[cursor:hi]);data=b''.join(parts)
  if data[-1]!=0 or data[:2]!=clean[lo:lo+2]:raise AssertionError('Lyric controls changed')
  pending.append((page,data))
 if len(fields)!=28:raise AssertionError('Lyric inventory changed')
 # Only the13 native lyric pages and one guarded unused bank85 area are reused.
 # The original menu page and all timing/music/animation tables stay byte-identical.
 out[0x2b37a:0x2b7bb]=bytes(0x441);allowed.update(range(0x2b37a,0x2b7bb));spaces=[[0x2b37a,0x2b7bb],[0x2f272,0x2f800]];pages=[]
 for page,data in sorted(pending,key=lambda p:len(p[1]),reverse=True):
  fits=[s for s in spaces if s[1]-s[0]>=len(data)]
  if not fits:raise AssertionError('Lyric allocation exhausted')
  slot=min(fits,key=lambda s:s[1]-s[0]);at=slot[0];out[at:at+len(data)]=data;allowed.update(range(at,at+len(data)));slot[0]+=len(data)
  ptr=0x2b35e+page*2;out[ptr:ptr+2]=(at&65535).to_bytes(2,'little');allowed.update(range(ptr,ptr+2));pages.append({'page':page,'record':hex(at),'bytes':len(data)})
 for at,old,new in [(0x2fb80,spacing_stub(True,story_selector),spacing_stub(True,lyric_selector)),(0x2fc00,spacing_stub(False,story_selector),spacing_stub(False,lyric_selector)),(0x2fc80,wrap_stub(story_selector),wrap_stub(lyric_selector)),(0x2fe00,destination_stub(story_selector),destination_stub(lyric_selector))]:
  if len(new)>128 or base[at:at+len(old)]!=old or base[at+len(old):at+len(new)]!=b'\xff'*(len(new)-len(old)):raise AssertionError('Karaoke spacing hook collision')
  out[at:at+len(new)]=new;allowed.update(range(at,at+len(new)))
 if out[0x2b7bb:0x2ce00]!=base[0x2b7bb:0x2ce00]:raise AssertionError('Menu/timing/music changed')
 out[0x7fdc:0x7fe0]=bytes(4);s=(sum(out)+510)&65535;out[0x7fdc:0x7fe0]=(s^65535).to_bytes(2,'little')+s.to_bytes(2,'little')
 if any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(base,out))):raise AssertionError('Write escaped spans')
 ips,count=make_ips(clean,out)
 if apply_ips(clean,ips)!=bytes(out):raise AssertionError('IPS replay')
 return ips,{'status':'106_KARAOKE_28_LYRIC_FIELDS_BINARY_PASS','fields':fields,'pages':sorted(pages,key=lambda r:r['page']),'timing_music_and_animation_tables_unchanged':True,'lyric_pitch':8,'lyric_columns':28,'IPS_SHA256':hashlib.sha256(ips).hexdigest(),'ROM_SHA256':hashlib.sha256(out).hexdigest(),'runtime_highlight_certified':False,'whole_game_complete':False}

def main():
 p=argparse.ArgumentParser();p.add_argument('original',type=Path);p.add_argument('baseline_ips',type=Path);p.add_argument('--ips',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args();c=a.original.read_bytes();ips,r=build(c,apply_ips(c,a.baseline_ips.read_bytes()));a.ips.write_bytes(ips);a.report.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in r.items() if k not in ('fields','pages')}))
if __name__=='__main__':main()

