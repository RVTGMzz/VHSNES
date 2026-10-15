"""Rebuild the cumulative 100 candidate from the original ROM and 043 ZIP."""
import argparse, hashlib, json
from pathlib import Path
from build_cumulative_095 import build as previous
from build_content_first_040_fortune import apply_ips
from build_continue_screen_096 import build as continue_screen
from build_scoreboard_heading_097 import build as heading
from build_game_over_098 import build as game_over
from build_scoreboard_team_099 import build as team
from build_fortune_box_100 import build as box

def build(clean,archive,bold,regular):
    ips,report=previous(clean,archive,bold,regular)
    for name,fn in [('096',continue_screen),('097',heading),('098',game_over),('099',team),('100',box)]:
        ips,stage=fn(clean,apply_ips(clean,ips),bold)
        report['stages'][name]=stage
    report.update(status='100_ONE_CUMULATIVE_IPS_BINARY_REBUILD_PASS',IPS_SHA256=hashlib.sha256(ips).hexdigest(),IPS_bytes=len(ips),ROM_SHA256=hashlib.sha256(apply_ips(clean,ips)).hexdigest())
    return ips,report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('original',type=Path);p.add_argument('historical_zip',type=Path)
    p.add_argument('--font-bold',type=Path,required=True);p.add_argument('--font-regular',type=Path,required=True)
    p.add_argument('--ips',type=Path,required=True);p.add_argument('--report',type=Path,required=True)
    a=p.parse_args()
    if len({v.resolve() for v in (a.original,a.historical_zip,a.ips,a.report)})!=4 or a.ips.suffix.lower()!='.ips' or a.report.suffix.lower()!='.json':p.error('Distinct original/archive/IPS/JSON paths required')
    ips,report=build(a.original.read_bytes(),a.historical_zip,a.font_bold,a.font_regular)
    a.ips.parent.mkdir(parents=True,exist_ok=True);a.report.parent.mkdir(parents=True,exist_ok=True)
    a.ips.write_bytes(ips);a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='stages'}))
if __name__=='__main__':main()
