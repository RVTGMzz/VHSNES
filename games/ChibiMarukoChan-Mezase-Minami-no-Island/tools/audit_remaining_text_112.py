"""Find unchanged canonical source strings; distinguish candidates from live text."""
import argparse,csv,hashlib,json
from pathlib import Path
from build_content_first_040_fortune import apply_ips
ROOT=Path(__file__).resolve().parent.parent

def audit(clean,rom,root=ROOT):
 candidates=[];credits=[]
 for path in sorted((root/'translation/source').glob('*.csv')):
  for row in csv.DictReader(path.open(encoding='utf-8-sig')):
   try:off=int(row['file_offset'],16);jp=row['source_jp'].encode('cp932')
   except (KeyError,ValueError,UnicodeEncodeError):continue
   if path.name=='credits_vi.csv':
    # Canonical credits rows normalize whitespace and join physical lines.
    # Their original script/source pointers have not been relocated by112.
    end=off
    while end<off+250 and clean[end]>=32:
     if clean[end]==32:end+=1
     elif 0x81<=clean[end]<=0x9f or 0xe0<=clean[end]<=0xfc:end+=2
     else:break
    if rom[off:end]==clean[off:end]:credits.append({'source_offset':hex(off),'original_script_text_unchanged':True})
   if len(jp)<4:continue
   hits=[at for at in range(max(0,off-4),off+17) if clean[at:at+len(jp)]==jp]
   if hits and rom[hits[0]:hits[0]+len(jp)]==jp:candidates.append({'source':path.name,'source_offset':hex(off),'actual_offset':hex(hits[0])})
 return {'ROM_SHA256':hashlib.sha256(rom).hexdigest(),'status':'REVIEW_REMAINING_TEXT_NOT_COMPLETE','credits_records_with_unchanged_native_text':credits,'unchanged_canonical_substring_candidates':candidates,'candidate_count_is_not_visible_missing_count':True,'inactive_fortune_copies_and_internal_debug_strings_not_visible_omissions':True,'intentional_Japanese':['Two Quiz39 Kazuo Kanji choices distinguish identical romanizations','Original Japanese copyright owner notices'],'requires_further_runtime_review':['Ending and credits sequence','All15 stage selectors; binary pointer audit passed, screenshots not yet verified','Paint erase/finish dialogs and mouse device branch','Karaoke meaning and syllable timing; source draft review104 remains applicable'],'whole_game_complete':False}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('original',type=Path);p.add_argument('ips',type=Path);p.add_argument('--report',type=Path,required=True);a=p.parse_args();c=a.original.read_bytes()
 if hashlib.sha256(c).hexdigest()!='e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956':p.error('Exact original required')
 r=audit(c,apply_ips(c,a.ips.read_bytes()));r['IPS_SHA256']=hashlib.sha256(a.ips.read_bytes()).hexdigest();a.report.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'credits_records_unchanged':len(r['credits_records_with_unchanged_native_text']),'substring_candidates_including_inactive_copies':len(r['unchanged_canonical_substring_candidates']),'whole_game_complete':False}))
if __name__=='__main__':main()
