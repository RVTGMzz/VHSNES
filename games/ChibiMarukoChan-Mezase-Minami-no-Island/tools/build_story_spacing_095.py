"""Compact Story font spacing and integrate the preserved 087 Quiz captions."""
import argparse,hashlib,json
from pathlib import Path
from build_content_first_040_fortune import apply_ips,make_ips
from build_fortune_full_layout_091 import compact_selector
from build_quiz_layout_087 import spacing_stub,destination_stub,wrap_stub
from build_content_first_057_quiz_50 import native_frames
from build_quiz_parent_semantic_restore_080 import read_codepage,encode
BASE_SHA='ca9ae1ba8f808a70c4b55ac2f1af5e1ea956e6e2ea3db8dd8ddd3573bdf78179'
ROOT=Path(__file__).resolve().parent.parent
def story_selector(a):compact_selector(a,story=True)
def build(clean,base,root):
 if hashlib.sha256(base).hexdigest()!=BASE_SHA or hashlib.sha256(clean).hexdigest()!='e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956':raise ValueError('Requires exact clean ROM and 094 baseline')
 out=bytearray(base);allowed=set(range(0x7fdc,0x7fe0))
 for at,old,new in [(0x2fb80,spacing_stub(True,compact_selector),spacing_stub(True,story_selector)),(0x2fc00,spacing_stub(False,compact_selector),spacing_stub(False,story_selector)),(0x2fc80,wrap_stub(compact_selector),wrap_stub(story_selector)),(0x2fe00,destination_stub(compact_selector),destination_stub(story_selector))]:
  if base[at:at+len(old)]!=old or len(new)>128 or base[at+len(old):at+len(new)]!=b'\xff'*max(0,len(new)-len(old)):raise AssertionError('Story spacing stub collision')
  if at==0x2fe00 and at+len(new)>0x2fe80:raise AssertionError('Story spacing overlaps menu initializer')
  out[at:at+len(new)]=new;allowed.update(range(at,at+len(new)))
 cp=read_codepage(root);manifest=json.loads((root/'translation/runtime/quiz_context_semantics_087.json').read_text(encoding='utf-8'));lines=0
 for row in manifest['records']:
  at=int(row['off'],16);frames,markers,stop=native_frames(clean,at)
  if len(frames)!=len(row['caps']):raise AssertionError('087 physical frames changed')
  for (l,r),cap,old,new in zip(frames,row['caps'],row['old'],row['new']):
   physical=clean[l:r];lead=len(physical)-len(physical.lstrip(b' '));tail=len(physical)-len(physical.rstrip(b' ')) if lead<len(physical) else 0;left=l+lead;right=r-tail
   before=encode(old,cap,cp);after=encode(new,cap,cp)
   if right-left!=cap*2 or base[left:right]!=before:raise AssertionError('087 actual baseline text mismatch')
   if before!=after:out[left:right]=after;allowed.update(range(left,right));lines+=1
  for marker in markers:
   if base[marker:marker+2]!=clean[marker:marker+2]:raise AssertionError('087 native text controls changed')
 if lines!=5:raise AssertionError('087 caption count changed')
 out[0x7fdc:0x7fe0]=bytes(4);s=(sum(out)+0x1fe)&65535;out[0x7fdc:0x7fe0]=(s^65535).to_bytes(2,'little')+s.to_bytes(2,'little')
 if any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(base,out))):raise AssertionError('095 writes escaped guarded spans')
 ips,count=make_ips(clean,out)
 if apply_ips(clean,ips)!=bytes(out):raise AssertionError('095 IPS replay failed')
 return ips,{'status':'095_STORY_SPACING_AND_087_QUIZ_CAPTIONS_BINARY_PASS','Story_pitch':8,'Story_columns':28,'other_native_menu_geometry_preserved':True,'087_preserved_manifest_caption_frames_integrated':lines,'new_source_IDs':0,'ROM_SHA256':hashlib.sha256(out).hexdigest(),'IPS_SHA256':hashlib.sha256(ips).hexdigest(),'IPS_bytes':len(ips),'IPS_records':count,'emulator_tested':False}
def main():
 p=argparse.ArgumentParser();p.add_argument('original',type=Path);p.add_argument('baseline_ips',type=Path);p.add_argument('--ips',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args();clean=a.original.read_bytes();ips,r=build(clean,apply_ips(clean,a.baseline_ips.read_bytes()),ROOT);a.ips.write_bytes(ips);a.report.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(r))
if __name__=='__main__':main()
