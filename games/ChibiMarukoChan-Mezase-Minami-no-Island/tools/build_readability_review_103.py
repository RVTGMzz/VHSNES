"""Strengthen L/horn strokes and repair one missed native Quiz mother line."""
import argparse,csv,hashlib,json,unicodedata
from pathlib import Path
from build_content_first_040_fortune import apply_ips,make_ips
from build_font_menu_runtime_090 import glyph_locations
from review_team_labels_103 import revise
BASE_SHA='94f7ae442b8efe8fe0bcf74fdb79c0540054374ae411774903080660e78bef34'
ROOT=Path(__file__).resolve().parent.parent

def glyph(rom,gid):
 dots=bytearray(144)
 for at,bit,x,y in glyph_locations(gid):dots[y*12+x]=int(bool(rom[at]&bit))
 return bytes(dots)

def build(clean,base,root=ROOT):
 if hashlib.sha256(clean).hexdigest()!='e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956' or hashlib.sha256(base).hexdigest()!=BASE_SHA:raise ValueError('Exact original and checkpoint102 required')
 rows=list(csv.DictReader((root/'translation/codepage/vi_codepage_v4_fe4_native.csv').open(encoding='utf-8-sig')))
 out=bytearray(base);allowed=set(range(0x7fdc,0x7fe0));masks={};changes=[];before={}
 for row in rows:
  ch=row['unicode'];code=int(row['code_hex'],16);at=0x29a74+((code&255)-0x40)*2;gid=int.from_bytes(base[at:at+2],'little');old=glyph(base,gid);before[ch]=old;new=bytearray(old)
  nfd=unicodedata.normalize('NFD',ch)
  if ch=='L':
   if [sum(old[y*12+x] for y in range(3,9)) for x in (2,3)]!=[6,0]:raise AssertionError('Thin-L baseline changed')
   for y in range(3,9):new[y*12+3]=1
   for x in range(2,6):new[8*12+x]=1
  elif nfd.startswith(('o','u')) and '\u031b' in nfd:
   for x,y in (((6,3),(6,4),(5,4)) if nfd[0]=='o' else ((7,3),(7,4),(6,4))):new[y*12+x]=1
  else:continue
  if new==old:raise AssertionError('Expected readability adjustment is empty')
  if any(new[y*12+x] for y in range(12) for x in range(9,12)):raise AssertionError('Revised glyph exceeds8px-pitch safe cell')
  for off,bit,x,y in glyph_locations(gid):
   if new[y*12+x]:out[off]|=bit
   else:out[off]&=255^bit
   allowed.add(off);masks[off]=masks.get(off,0)|bit
  changes.append({'unicode':ch,'gid':hex(gid),'added_ink_pixels':sum(new)-sum(old)})
 if len(changes)!=13:raise AssertionError('Readability glyph inventory changed')
 signatures={}
 for row in rows:
  code=int(row['code_hex'],16);at=0x29a74+((code&255)-0x40)*2;gid=int.from_bytes(out[at:at+2],'little');dots=glyph(out,gid);signatures.setdefault(dots,set()).add(row['unicode'])
  if row['unicode'] not in {v['unicode'] for v in changes} and dots!=before[row['unicode']]:raise AssertionError('Unrelated glyph changed')
 collisions=[sorted(v) for v in signatures.values() if len(v)>1 and not v<=set('"“”')]
 if collisions:raise AssertionError('Vietnamese glyph collision: '+repr(collisions))
 for off,mask in masks.items():
  if (base[off]^out[off])&(~mask&255):raise AssertionError('Neighboring font-cell bits changed')
 # All150 native explanation-page pointers were audited, not just the main
 # questions. Page1 of slot20 still contained a Japanese mother-intro prefix.
 pointer=0x3134f+20*2;start=0x32874;stop=0x32896
 if int.from_bytes(base[pointer:pointer+2],'little')!=0xa870 or base[0x32870:start]!=bytes.fromhex('0e000f08') or base[start:start+26]!=b' '*8+'母、さくらすみれは'.encode('cp932') or base[stop:stop+2]!=bytes.fromhex('816f'):raise AssertionError('Native mother explanation identity changed')
 cp={r['unicode']:bytes.fromhex(r['code_hex']) for r in rows};caption='Mẹ Sumire 40 tuổi';payload=b''.join(cp[c] for c in caption)
 if len(payload)!=stop-start:raise AssertionError('Full mother caption does not fit original physical frame')
 out[start:stop]=payload;allowed.update(range(start,stop));out[0x32871]=4;allowed.add(0x32871)
 label_spans,label_report=revise(clean,base,out);allowed.update(label_spans)
 out[0x7fdc:0x7fe0]=bytes(4);s=(sum(out)+0x1fe)&65535;out[0x7fdc:0x7fe0]=(s^65535).to_bytes(2,'little')+s.to_bytes(2,'little')
 if any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(base,out))):raise AssertionError('103 writes escaped font/checksum spans')
 ips,count=make_ips(clean,out)
 if apply_ips(clean,ips)!=bytes(out):raise AssertionError('103 IPS replay failed')
 return ips,{'status':'103_USER_SCREENSHOT_REVIEW_BINARY_PASS','glyph_changes':changes,'distinct_Vietnamese_bitmap_collisions':0,'all_other_glyphs_identical':True,'neighboring_font_cell_bits_preserved':True,'team_label_readability':label_report,'quiz_mother_intro':{'pointer':hex(pointer),'source_frame':hex(start),'full_Vietnamese':caption,'original_physical_bytes':stop-start,'native_line_markers_and_following_rows_preserved':True},'IPS_SHA256':hashlib.sha256(ips).hexdigest(),'ROM_SHA256':hashlib.sha256(out).hexdigest(),'IPS_bytes':len(ips),'IPS_records':count,'emulator_tested':False,'whole_game_complete':False}

def main():
 p=argparse.ArgumentParser();p.add_argument('original',type=Path);p.add_argument('baseline_ips',type=Path);p.add_argument('--ips',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args();clean=a.original.read_bytes();ips,r=build(clean,apply_ips(clean,a.baseline_ips.read_bytes()));a.ips.write_bytes(ips);a.report.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,ensure_ascii=True))
if __name__=='__main__':main()
