"""Rebuild one cumulative clean-ROM-relative IPS from the original 043 ZIP.

Requires local Tahoma/Tahoma Bold used by the tested reference candidate.
ROMs, font files, emulator libraries and intermediate patches stay local.
"""
import argparse,hashlib,json
from pathlib import Path
from build_content_first_040_fortune import apply_ips
from recover_merge_061_81_one_ips_076 import rebuild_one_patch
from build_title_readable_088 import build as title
from build_quiz_counter_089 import build as counter
from build_font_menu_runtime_090 import build as font_menu
from build_fortune_full_layout_091 import build as fortune
from build_fortune_rank_092 import build as ranks
from build_fortune_controls_093 import build as controls
from build_fortune_paper_094 import build as paper
from build_story_spacing_095 import build as spacing
ROOT=Path(__file__).resolve().parent.parent
def build(clean,archive,bold,regular,root=ROOT):
 ips,recovery=rebuild_one_patch(clean,archive,root);reports={'087':recovery}
 stages=[('088',lambda b:title(clean,b,str(bold),str(regular))),('089',lambda b:counter(clean,b,root)),('090',lambda b:font_menu(clean,b,root,bold)),('091',lambda b:fortune(clean,b,root)),('092',lambda b:ranks(clean,b,bold)),('093',lambda b:controls(clean,b,bold)),('094',lambda b:paper(clean,b,bold)),('095',lambda b:spacing(clean,b,root))]
 for stage,fn in stages:
  ips,report=fn(apply_ips(clean,ips));reports[stage]=report
 return ips,{'status':'095_ONE_CUMULATIVE_IPS_BINARY_REBUILD_PASS','IPS_SHA256':hashlib.sha256(ips).hexdigest(),'IPS_bytes':len(ips),'ROM_SHA256':hashlib.sha256(apply_ips(clean,ips)).hexdigest(),'stages':reports,'source_only_no_ROM_or_font_output':True,'whole_game_complete':False,'runtime_QA_recorded_separately':True}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('original',type=Path);p.add_argument('historical_zip',type=Path);p.add_argument('--font-bold',type=Path,required=True);p.add_argument('--font-regular',type=Path,required=True);p.add_argument('--ips',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
 if len({v.resolve() for v in (a.original,a.historical_zip,a.ips,a.report)})!=4 or a.ips.suffix.lower()!='.ips' or a.report.suffix.lower()!='.json':p.error('Distinct original/archive/IPS/JSON paths required')
 ips,r=build(a.original.read_bytes(),a.historical_zip,a.font_bold,a.font_regular);a.ips.parent.mkdir(parents=True,exist_ok=True);a.report.parent.mkdir(parents=True,exist_ok=True);a.ips.write_bytes(ips);a.report.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in r.items() if k!='stages'}))
if __name__=='__main__':main()
