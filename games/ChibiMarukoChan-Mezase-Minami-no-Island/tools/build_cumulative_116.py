"""Build one cumulative IPS including the final full-width stage-caption clear."""
import argparse,hashlib,json
from pathlib import Path
from build_cumulative_115 import build as previous
from build_stage_caption_clear_116 import build as final
from build_content_first_040_fortune import apply_ips

def build(clean,archive,bold,regular):
 ips,r=previous(clean,archive,bold,regular);ips,s=final(clean,apply_ips(clean,ips));r['stages']['116']=s
 r.update(status='116_CUMULATIVE_BINARY_REBUILD_PASS',IPS_SHA256=hashlib.sha256(ips).hexdigest(),IPS_bytes=len(ips),ROM_SHA256=hashlib.sha256(apply_ips(clean,ips)).hexdigest(),whole_game_complete=False)
 return ips,r

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('original',type=Path);p.add_argument('historical_zip',type=Path);p.add_argument('--font-bold',type=Path,required=True);p.add_argument('--font-regular',type=Path,required=True);p.add_argument('--ips',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
 if len({x.resolve() for x in (a.original,a.historical_zip,a.ips,a.report)})!=4 or a.ips.suffix.lower()!='.ips' or a.report.suffix.lower()!='.json':p.error('Distinct original/archive/IPS/JSON paths required')
 ips,r=build(a.original.read_bytes(),a.historical_zip,a.font_bold,a.font_regular);a.ips.parent.mkdir(parents=True,exist_ok=True);a.report.parent.mkdir(parents=True,exist_ok=True);a.ips.write_bytes(ips);a.report.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in r.items() if k!='stages'}))
if __name__=='__main__':main()
