"""Rebuild one clean-relative localization IPS through checkpoint 112."""
import argparse, hashlib, json
from pathlib import Path
from build_cumulative_103 import build as previous
from build_content_first_040_fortune import apply_ips
from build_character_names_104 import build as names
from build_karaoke_menu_105 import build as karaoke_menu
from build_karaoke_lyrics_106 import build as lyrics
from build_paint_ui_107 import build as paint
from build_minigame_names_108 import build as games
from build_rules_explanations_109 import build as rules
from build_stage_titles_110 import build as stages
from build_quiz_completion_111 import build as quiz
from build_setup_strings_112 import build as setup

def build(clean,archive,bold,regular):
 ips,report=previous(clean,archive,bold,regular)
 for number,fn,needs_font in [(104,names,True),(105,karaoke_menu,True),(106,lyrics,False),(107,paint,True),(108,games,True),(109,rules,True),(110,stages,False),(111,quiz,False),(112,setup,False)]:
  args=(clean,apply_ips(clean,ips))+( (bold,) if needs_font else () )
  ips,stage=fn(*args);report['stages'][str(number)]=stage
 report.update(status='112_CUMULATIVE_BINARY_REBUILD_PASS',IPS_SHA256=hashlib.sha256(ips).hexdigest(),IPS_bytes=len(ips),ROM_SHA256=hashlib.sha256(apply_ips(clean,ips)).hexdigest(),whole_game_complete=False)
 return ips,report

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('original',type=Path);p.add_argument('historical_zip',type=Path)
 p.add_argument('--font-bold',type=Path,required=True);p.add_argument('--font-regular',type=Path,required=True);p.add_argument('--ips',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
 if len({x.resolve() for x in (a.original,a.historical_zip,a.ips,a.report)})!=4 or a.ips.suffix.lower()!='.ips' or a.report.suffix.lower()!='.json':p.error('Distinct original/archive/IPS/JSON paths required')
 ips,r=build(a.original.read_bytes(),a.historical_zip,a.font_bold,a.font_regular)
 a.ips.parent.mkdir(parents=True,exist_ok=True);a.report.parent.mkdir(parents=True,exist_ok=True);a.ips.write_bytes(ips);a.report.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:v for k,v in r.items() if k!='stages'}))
if __name__=='__main__':main()
