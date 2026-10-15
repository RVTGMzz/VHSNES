"""Compare active type0 resource owners against103 to catch shared-asset corruption."""
import argparse,hashlib,json
from pathlib import Path
from render_chibi_resource_package import parse_type0_package
from build_native_setup_headings_101 import decoded
from build_content_first_040_fortune import apply_ips

def audit(clean,old,new):
 packages={}
 for off in range(0x10000,0x17736):
  if clean[off]!=0 or clean[off+2]==255:continue
  try:_,_,recs,_=parse_type0_package(old,0x828000|(off&0x7fff))
  except Exception:continue
  if recs:packages[off]=recs
 cache1={};cache2={};same=set();changes=[];errors=[]
 allowed_sources={0xe100,0x17d1c,0x9f18e,0x12de52}
 allowed_pointers={0x1262b,0x12630,0x12635,0x12621,0x1263d,0x12626,0x12642,0x12290,0x121f6,0x121fb,0x122c9,0x122e2,0x122ef,0x12308,0x12315,0x1232e}
 for package,recs in packages.items():
  for rec in recs:
   ref=package+4+rec.index*5;src=rec.source_file;cpu=int.from_bytes(new[ref:ref+3],'little');at=((cpu>>16)&0x7f)*0x8000+(cpu&0x7fff)
   try:
    if src not in cache1:cache1[src]=decoded(old,src)
    if at not in cache2:cache2[at]=decoded(new,at)
   except Exception as e:errors.append({'pointer':hex(ref),'reason':str(e)});continue
   if src==at and cache1[src]==cache2[at]:same.add(src)
   else:
    change={'package':hex(package),'pointer':hex(ref),'old':hex(src),'new':hex(at)};changes.append(change)
    if not(src==at and src in allowed_sources) and ref not in allowed_pointers:errors.append(change)
 if errors:raise AssertionError(json.dumps(errors))
 return {'status':'PASS_ACTIVE_RESOURCE_REGRESSION','ROM_SHA256':hashlib.sha256(new).hexdigest(),'native_type0_candidates_checked':len(packages),'unchanged_decoded_sources':len(same),'intentional_owner_changes':changes,'unexpected_changes':errors,'original_resource_68066_preserved':decoded(old,0x68066)==decoded(new,0x68066),'rule_resource_17736_preserved':decoded(old,0x17736)==decoded(new,0x17736),'scope':'native bank82 type0 resource candidates; not complete playthrough coverage'}

def main():
 p=argparse.ArgumentParser();p.add_argument('original',type=Path);p.add_argument('baseline_ips',type=Path);p.add_argument('ips',type=Path);p.add_argument('--report',type=Path,required=True);a=p.parse_args();c=a.original.read_bytes();r=audit(c,apply_ips(c,a.baseline_ips.read_bytes()),apply_ips(c,a.ips.read_bytes()));a.report.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in r.items() if k!='intentional_owner_changes'}))
if __name__=='__main__':main()

