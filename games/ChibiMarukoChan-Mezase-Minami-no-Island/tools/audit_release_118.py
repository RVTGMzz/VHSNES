"""Audit active text and completed native credits DMA, excluding retired copies."""
import argparse,csv,hashlib,json
from pathlib import Path
from ips_release_118 import apply_ips
from audit_active_text_103 import audit as active_audit
from build_content_first_042_story_safe_segments import physical_segments
from audit_stage_caption_runtime_116 import block
ROOT=Path(__file__).resolve().parent.parent

def audit(clean,rom,build,states,root=ROOT,lyric_states=None):
 cp={bytes.fromhex(r['code_hex']):r['unicode'] for r in csv.DictReader((root/'translation/codepage/vi_codepage_v4_fe4_native.csv').open(encoding='utf-8-sig'))}
 fields=active_audit(rom,root)
 if fields['unexpected_native_text'] or fields['intentional_Kazuo_Kanji_choices']:raise AssertionError('Active Quiz/Fortune still contains native Japanese glyphs')
 def read(at,limit=1024):
  start=at;parts=[];text=''
  while at<start+limit:
   b=rom[at];pair=bytes(rom[at:at+2])
   if b in (14,15,16):at+=2;continue
   if b==0 or pair==bytes.fromhex('8198'):break
   if b==32:text+=' ';at+=1;continue
   if pair in (bytes.fromhex('816f'),bytes.fromhex('81a5')):
    parts.append(text);text='';at+=2;continue
   if pair not in cp:raise AssertionError(f'Native/non-VI glyph in active field {at:X}: {pair.hex()}')
   text+=cp[pair];at+=2
  else:raise AssertionError('Unterminated text field')
  if text:parts.append(text)
  return parts
 offsets={};prefixes={}
 for name in ('story_batch01_safe_segments_042.json','story_batch01_02_content_first_044.json','story_batch02_03_content_first_045.json','story_special_cp932_alignment_046.json'):
  data=json.loads((root/'translation/runtime'/name).read_text(encoding='utf-8'))
  for r in data['records']:
   at=int(r.get('physical_record_start',r.get('file_offset','0')),16);offsets[at]=name
   if r.get('preserve_leading_cp932_hex'):prefixes[at]=bytes.fromhex(r['preserve_leading_cp932_hex'])
 story_glyphs=0
 for at in offsets:
  _,spans,_=physical_segments(clean,at)
  for lo,hi in spans:
   i=lo
   if i==at and at in prefixes:
    if rom[i:i+len(prefixes[at])]!=prefixes[at]:raise AssertionError('Protected native script prefix changed')
    i+=len(prefixes[at])
   while i<hi:
    if rom[i]==32:i+=1;continue
    if bytes(rom[i:i+2]) not in cp:raise AssertionError(f'Story native text at {i:X}')
    story_glyphs+=1;i+=2
 lyrics=[]
 for i in range(13):
  at=0x20000+int.from_bytes(rom[0x2b35e+i*2:0x2b360+i*2],'little');lyrics.append({'page':i,'source':hex(at),'lines':read(at)})
 rules=[]
 for game in range(3):
  at=0x20000+int.from_bytes(rom[0x21c15+game*2:0x21c17+game*2],'little');rules.append({'game':game,'source':hex(at),'lines':read(at)})
 credits=[]
 for credit in build['credits']:
  i=credit['index'];at=int(credit['source'],16)
  if int.from_bytes(rom[0x1dea6+i*2:0x1dea8+i*2],'little')!=((at&32767)|32768):raise AssertionError('Credits pointer mismatch')
  if read(at)!=credit['lines']:raise AssertionError('Credits source differs from approved names')
  data=(states/f'state_release_credit_{i:02d}.bin').read_bytes();p=block(data,'PPU',2652);v=block(data,'VRA',65536);ram=block(data,'RAM',131072)
  # Detect the exact truncation bug: both bitmap and attribute DMA must match
  # the completed WRAM font buffers, including the second line atrow25.
  for row in (23,24,25,26):
   a=0x1c000+row*512;b=0x8000+row*512
   if ram[a:a+512]!=v[b:b+512]:raise AssertionError(f'Credits DMA incomplete: page{i}, row{row}')
  for row in credit['rows']:
   if not any(v[0x8000+row*512:0x8000+(row+1)*512]):raise AssertionError('Credits line missing')
  # Entire font tilemap upload must be committed after its native wait.
  if ram[0x1b800:0x1c000]!=v[0x1800:0x2000]:raise AssertionError(f'Credits palette/tilemap DMA incomplete: {i}')
  credits.append({'page':i,'lines':credit['lines'],'native_full_lines_and_DMA_verified':True,'state_SHA256':hashlib.sha256(data).hexdigest()})
 lyric_runtime=[]
 if lyric_states:
  for i in range(13):
   data=(lyric_states/f'state_karaoke_{i:02d}.bin').read_bytes();v=block(data,'VRA',65536);ram=block(data,'RAM',131072);ppu=block(data,'PPU',2652)
   name=int.from_bytes(ppu[21:23],'big')*2
   for row in (18,22):
    words=[int.from_bytes(v[2*(row*32+x):2*(row*32+x)+2],'little')&1023 for x in range(32)]
    # The opening scene uses transparent tile256; later scenes use tile0.
    for tile in set(words):
     if any(v[(name+tile*32+k)&65535] for k in range(32)):raise AssertionError(f'Japanese ruby ink remains on Karaoke{i}, row{row}')
   for row in range(19,27):
    a=0x1c000+row*512;b=0x8000+row*512
    if ram[a:a+512]!=v[b:b+512]:raise AssertionError(f'Karaoke bitmap DMA incomplete: page{i}, row{row}')
   if not any(v[0xa600:0xb600]):raise AssertionError(f'Karaoke lyrics missing on page{i}')
   lyric_runtime.append({'page':i,'Japanese_ruby_rows_blank':True,'all8_bitmap_rows_transferred':True,'state_SHA256':hashlib.sha256(data).hexdigest()})
 return {'status':'PASS_RELEASE_ACTIVE_TEXT_AND_19_CREDITS_DMA','ROM_SHA256':hashlib.sha256(rom).hexdigest(),'active_Quiz_Fortune_fields':sum(fields['scope_counts'].values()),'remaining_native_Quiz_Fortune_glyphs':0,'Story_manifest_records':len(offsets),'Story_VI_glyphs_checked':story_glyphs,'protected_nontext_prefixes_046':len(prefixes),'Karaoke_pages':lyrics,'Karaoke_native_bitmap_and_ruby_audit':lyric_runtime,'rules_pages':rules,'credits':credits,'known_Japanese_sites_replaced':build['signs'],'copyright_lines':build['copyright_lines'],'scope_limits':['Graphics require runtime screenshot review; a byte scan cannot certify every scenery pixel','No natural full winning Story playthrough certified','Inactive original Japanese source copies and debug data intentionally excluded'],'whole_game_complete':False}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('original',type=Path);p.add_argument('ips',type=Path);p.add_argument('--build-report',type=Path,required=True);p.add_argument('--credit-states',type=Path,required=True);p.add_argument('--lyric-states',type=Path);p.add_argument('--report',type=Path,required=True);a=p.parse_args();c=a.original.read_bytes();r=audit(c,apply_ips(c,a.ips.read_bytes()),json.loads(a.build_report.read_text(encoding='utf-8')),a.credit_states,lyric_states=a.lyric_states);r['IPS_SHA256']=hashlib.sha256(a.ips.read_bytes()).hexdigest();a.report.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:r[k] for k in ('status','active_Quiz_Fortune_fields','Story_manifest_records','Story_VI_glyphs_checked','protected_nontext_prefixes_046','whole_game_complete')}))
if __name__=='__main__':main()
