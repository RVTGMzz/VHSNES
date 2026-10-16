"""Fresh native Paint/Fortune/Karaoke smoke and all13 lyric pages."""
import sys,json
from pathlib import Path
source=Path(__file__).with_name('run_snes9x_qa_087.py');sys.path.insert(0,str(source.parent.resolve()))
exec(source.read_text(encoding='utf-8').split('run(600);')[0])
run(600);run(2,[3]);run(1920);run(2,[3]);run(180);save('menu')
for menu in (4,5,6):
 load('menu')
 for _ in range(menu):run(2,[5]);run(10)
 run(2,[8]);run(480);snap(f'mode_{menu}_entry');save(f'mode_{menu}_entry')
 if menu!=6:run(2,[3]);run(400);save(f'mode_{menu}_start')
load('mode_4_start');run(192,[4]);run(28,[7]);run(2,[8]);run(60);snap('paint_quit_dialog')
run(2,[7]);run(10);run(2,[8]);run(400);snap('paint_return_menu');assert ram[0x70]==15,('Paint did not return',ram[0x70])
load('mode_5_start')
fortune=[]
for step in range(2200):
 run(1,[8] if step%80<2 else ())
 if step in (0,300,800,1400,2199):snap(f'fortune_{step}');fortune.append({'step':step,'controller':ram[0x70],'phase':ram[0x72]})
run(300);snap('fortune_complete');save('fortune_complete')
load('mode_6_entry');run(2,[3])
pages=[]
for index in range(13):
 start=0x20000+int.from_bytes(rom[0x2b35e+index*2:0x2b360+index*2],'little');end=start
 while rom[end]:end+=2 if rom[end] in (14,15,16) or rom[end]>=128 else 1
 pages.append({'page':index,'record':hex(start),'bytes':end-start+1})
seen={}
for step in range(10000):
 run(1);bank=int.from_bytes(bytes(ram[0x1f86:0x1f88]),'little');ptr=int.from_bytes(bytes(ram[0x1f94:0x1f96]),'little')
 if bank==0x85 and ram[0x1f80]==0:
  for page in pages:
   at=int(page['record'],16)&65535
   if at<ptr<=at+page['bytes'] and page['page'] not in seen:
    index=page['page'];run(60);seen[index]=frame;snap(f'karaoke_{index:02d}');save(f'karaoke_{index:02d}')
 if len(seen)==13:break
assert len(seen)==13,('Missing lyric pages',seen)
report={'IPS_SHA256':hashlib.sha256(args.ips.read_bytes()).hexdigest(),'ROM_SHA256':hashlib.sha256(rom).hexdigest(),'native_paint_quit_returns_to_menu':True,'Fortune_native_inputs':fortune,'Karaoke_native_pages_completed':seen,'mouse_motion_or_hardware_certified':False,'Karaoke_singability_timing_certified':False}
(ROOT/'outputs/side_runtime.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
core.retro_unload_game();core.retro_deinit()
