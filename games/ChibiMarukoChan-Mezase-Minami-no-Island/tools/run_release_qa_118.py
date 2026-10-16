"""Fresh native boot, Quiz39 three choices, and explicit ending fixture on118."""
from pathlib import Path
source=Path(__file__).with_name('run_snes9x_qa_087.py')
exec(source.read_text(encoding='utf-8').split('run(600);')[0])
run(600);run(2,[3]);run(1920);snap('title');save('release_title')
run(2,[3]);run(180);snap('menu');save('release_menu')
for _ in range(3):run(2,[5]);run(10)
run(2,[8]);run(480);run(2,[3])
for _ in range(500):
 run(1)
 if ram[0x1480] or ram[0x1482]:break
else:raise AssertionError('Quiz initialization failed')
ram[0x1480]=78;ram[0x1481]=0;ram[0x1410]=ram[0x1411]=0
run(300);snap('quiz39');save('release_quiz39');choices=[]
for choice in range(3):
 load('release_quiz39')
 for _ in range(choice):run(2,[5]);run(8)
 run(2,[0]);run(45);snap(f'quiz39_grade_{choice}');choice_ram=bytes(ram[0x1400:0x1424]).hex()
 run(180);snap(f'quiz39_explain_{choice}');choices.append({'row':choice,'grade_RAM_1400':choice_ram})
load('release_menu')
ram[0x70]=0xae;ram[0x71]=0;ram[0x72]=ram[0x73]=0
for at in (0x20b0,0x20b2,0x20b4):ram[at]=1;ram[at+1]=0
report=json.loads(args.ips.with_name('chibi_118_QA.json').read_text(encoding='utf-8'));credit_ranges=[]
for c in report['credits']:
 at=int(c['source'],16);end=at+next(a['bytes'] for a in report['allocations'] if a['label']==f'credits_{c["index"]:02d}')-1
 credit_ranges.append((c['index'],0x8000,0x8000+end-at+1,rom[at:end+1]))
seen={};events=[]
for step in range(24000):
 run(1,[8] if step%40<2 else ())
 bank=int.from_bytes(bytes(ram[0x1f86:0x1f88]),'little');ptr=int.from_bytes(bytes(ram[0x1f94:0x1f96]),'little')
 if bank==0x83:
  for index,start,end,payload in credit_ranges:
   if start<=ptr<=end and bytes(ram[start:start+len(payload)])==payload and index not in seen and ram[0x1f80]==0:
    seen[index]=frame;run(60);snap(f'credit_{index:02d}');save(f'release_credit_{index:02d}')
 if step%1600==0:events.append({'step':step,'controller':ram[0x70],'phase':ram[0x72],'ending_state':ram[0x1400],'bank':bank,'pointer':hex(ptr)})
 if len(seen)==19 and ram[0x70]!=0xae:break
assert len(seen)==19,('Missing native credits',seen,events[-5:])
assert ram[0x70]!=0xae,('Ending did not finish',events[-3:])
ending_controller=ram[0x70]
result={'IPS_SHA256':hashlib.sha256(args.ips.read_bytes()).hexdigest(),'ROM_SHA256':hashlib.sha256(rom).hexdigest(),'ROM_bytes':len(rom),'native_credits_seen':seen,'quiz39_choices':choices,'events':events,'ending_dispatch_reached_completion':True,'ending_final_controller':ending_controller,'fixture':'Fresh native ending dispatcher AE plus three completion flags20B0/20B2/20B4','natural_full_story_playthrough':False}
(ROOT/'outputs/release_runtime.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
core.retro_unload_game();core.retro_deinit()
