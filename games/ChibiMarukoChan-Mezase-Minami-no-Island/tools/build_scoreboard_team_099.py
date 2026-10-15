"""Translate the repeated チーム BG1 label in the native VS result board."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image
from build_font_menu_runtime_090 import raster
from build_fortune_rank_092 import address
from build_content_first_040_fortune import apply_ips,make_ips
from decompress_chibi_resource import decompress_resource,reorder_flag1_blocks
from build_g0_first_boot_title_votri_experimental import encode_chibi,tile_to_4bpp
BASE_SHA='1e4eebdc08a626e3e6ada3f6d6a77c1d6d9984bc14b00f59accf1f37ba3fb543'
def build(clean,base,font):
 if hashlib.sha256(base).hexdigest()!=BASE_SHA or hashlib.sha256(clean).hexdigest()!='e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956':raise ValueError('Requires exact original ROM and 098 baseline')
 refs=[i for i in range(len(clean)) if clean.startswith(address(0xed347).to_bytes(3,'little'),i)]
 if refs!=[0x123a8,0x123fb]:raise AssertionError('Scoreboard BG1 resource owners changed')
 raw,h,_=decompress_resource(base,0xed347)
 if len(raw)!=8192 or h.span!=4251 or not h.postprocess:raise AssertionError('Scoreboard BG1 resource shape changed')
 original=reorder_flag1_blocks(raw);data=bytearray(original);im=Image.new('L',(32,24),0);mask=raster('Đội',font,16,30,22)
 for y in range(22):
  for x in range(30):
   if mask.getpixel((x,y)):
    for dy in (-1,0,1):
     for dx in (-1,0,1):im.putpixel((x+1+dx,y+1+dy),12)
 for y in range(22):
  for x in range(30):
   if mask.getpixel((x,y)):im.putpixel((x+1,y+1),14)
 changed_tiles=set()
 # Rabbit and cat labels use distinct native tile sets. The second label
 # cannot be inferred from the synthetic Story-to-VS diagnostic state.
 for start in (0x5d,0x7b):
  for yy in range(3):
   for xx in range(4):
    tid=start+yy*4+xx;changed_tiles.add(tid)
    data[tid*32:(tid+1)*32]=tile_to_4bpp(bytes(im.getpixel((xx*8+x,yy*8+y)) for y in range(8) for x in range(8)))
 for tid in range(256):
  if tid not in changed_tiles and data[tid*32:(tid+1)*32]!=original[tid*32:(tid+1)*32]:raise AssertionError('Team label modifies original frame/portraits')
 inverse=bytearray(len(data));order=(0,8,1,9,2,10,3,11,4,12,5,13,6,14,7,15)
 for pos in range(0,len(data),16):
  for dst,src in enumerate(order):inverse[pos+src]=data[pos+dst]
 packed=encode_chibi(bytes(inverse));blob=(len(packed)+2|0x8000).to_bytes(2,'little')+packed;dest=0xed347
 # Both and only both owners are native result boards; they intentionally
 # share this one label. The new stream fits its original guarded allocation.
 if len(blob)>h.span:raise AssertionError('Team label exceeds original allocation')
 packed_size=len(blob);blob+=b'\xff'*(h.span-len(blob))
 out=bytearray(base);allowed=set(range(0x7fdc,0x7fe0));out[dest:dest+len(blob)]=blob;allowed.update(range(dest,dest+len(blob)))
 for ref in refs:
  if base[ref:ref+3]!=address(0xed347).to_bytes(3,'little'):raise AssertionError('Scoreboard BG1 pointer changed')
 rebuilt,rh,_=decompress_resource(out,dest)
 if rebuilt!=inverse or not rh.postprocess:raise AssertionError('Team label codec round-trip failed')
 out[0x7fdc:0x7fe0]=bytes(4);s=(sum(out)+0x1fe)&65535;out[0x7fdc:0x7fe0]=(s^65535).to_bytes(2,'little')+s.to_bytes(2,'little')
 if any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(base,out))):raise AssertionError('099 writes escaped guarded spans')
 ips,count=make_ips(clean,out)
 if apply_ips(clean,ips)!=bytes(out):raise AssertionError('099 IPS replay failed')
 return ips,{'status':'099_NATIVE_SCOREBOARD_BOTH_TEAM_LABELS_BINARY_PASS','caption':'Đội','changed_tiles':sorted(changed_tiles),'team_labels':2,'frame_and_portraits_preserved':True,'resource':hex(dest),'resource_bytes':packed_size,'allocation_bytes':h.span,'only_two_native_scoreboard_owners':True,'ROM_SHA256':hashlib.sha256(out).hexdigest(),'IPS_SHA256':hashlib.sha256(ips).hexdigest(),'IPS_bytes':len(ips),'IPS_records':count,'emulator_tested':False}
def main():
 p=argparse.ArgumentParser();p.add_argument('original',type=Path);p.add_argument('baseline_ips',type=Path);p.add_argument('--font',type=Path,required=True);p.add_argument('--ips',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args();clean=a.original.read_bytes();ips,r=build(clean,apply_ips(clean,a.baseline_ips.read_bytes()),a.font);a.ips.write_bytes(ips);a.report.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,ensure_ascii=True))
if __name__=='__main__':main()
