"""Measure actual BG3 caption ink in15 Snes9x snapshots, including scroll."""
import argparse,hashlib,json
from pathlib import Path
from ips_release_118 import apply_ips

def block(data,tag,size):
 marker=f'{tag}:{size:06d}:'.encode();at=data.index(marker)+11;return data[at:at+size]

def ink_bbox(data):
 p=block(data,'PPU',2652);v=block(data,'VRA',65536)
 def word(at):return int.from_bytes(p[at:at+2],'big')
 at=14+11*2;sc=word(at)*2;h=word(at+2);vert=word(at+4);name=word(at+7)*2
 if p[58]&7!=1 or p[at+6]!=0 or word(at+9)!=0:raise AssertionError('Unexpected native BG3 geometry')
 points=[]
 for sy in range(180,224):
  for sx in range(256):
   x=(sx+h)&255;y=(sy+vert)&255;k=(y//8)*32+x//8;w=v[(sc+k*2)&65535]|v[(sc+k*2+1)&65535]<<8;t=w&1023
   tx=x%8;ty=y%8
   if w&0x4000:tx=7-tx
   if w&0x8000:ty=7-ty
   addr=(name+t*16+ty*2)&65535
   if ((v[addr]|v[(addr+1)&65535])>>(7-tx))&1:points.append((sx,sy))
 if not points:raise AssertionError('Stage caption was not rendered')
 return [min(x for x,y in points),min(y for x,y in points),max(x for x,y in points)+1,max(y for x,y in points)+1]

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('original',type=Path);p.add_argument('ips',type=Path);p.add_argument('--states',type=Path,required=True);p.add_argument('--runtime-report',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
 sha=hashlib.sha256(apply_ips(a.original.read_bytes(),a.ips.read_bytes())).hexdigest();runtime=json.loads(a.runtime_report.read_text(encoding='utf-8'))
 if runtime['ROM_SHA256']!=sha or len(runtime['events'])!=15 or any(e['selected']!=e['ordinal'] for e in runtime['events']):raise AssertionError('Runtime stage identity/order mismatch')
 records=[]
 for game in range(3):
  for stage in range(5):
   path=a.states/f'state_114_stage_{game}_{stage}.bin';bbox=ink_bbox(path.read_bytes())
   if bbox[0]<58 or bbox[2]>202 or bbox[1]<186 or bbox[3]>218:raise AssertionError(f'Caption touches decoration or footer boundary: {game}/{stage} {bbox}')
   records.append({'game':game,'stage':stage,'actual_screen_ink_bbox':bbox,'snapshot_SHA256':hashlib.sha256(path.read_bytes()).hexdigest()})
 r={'status':'PASS_15_NATIVE_STAGE_CAPTIONS_INSIDE_PAPER','ROM_SHA256':sha,'IPS_SHA256':hashlib.sha256(a.ips.read_bytes()).hexdigest(),'stage_count':15,'method':'Decode all native Snes9x PPU BG3 footer pixels and apply actual scroll; both ordinal and full title must fit','paper_acceptance_box':[58,186,202,218],'records':records,'natural_full_game_playthrough':False};a.report.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in r.items() if k!='records'}))
if __name__=='__main__':main()
