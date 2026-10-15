import ctypes as C
import sys
import os
from pathlib import Path
import numpy as np
from PIL import Image

import argparse
import hashlib
import json
ap=argparse.ArgumentParser(description='Snes9x/libretro headless Quiz QA, using a user-owned ROM and supplied core')
ap.add_argument('original_rom',type=Path)
ap.add_argument('ips',type=Path)
ap.add_argument('core',type=Path)
ap.add_argument('--out',type=Path,required=True)
ap.add_argument('--sweep',action='store_true')
ap.add_argument('--stage-sweep',action='store_true',help='Visit all15 actual stage selectors and exercise each match entry')
ap.add_argument('--full-stage-matches',action='store_true',help='Also wait for one complete timed match in each minigame family')
args=ap.parse_args()
ROOT=args.out.resolve(); ROOT.mkdir(parents=True,exist_ok=True)
(ROOT/'work').mkdir(exist_ok=True);(ROOT/'outputs').mkdir(exist_ok=True)
GAME=Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GAME / 'tools'))
from build_content_first_040_fortune import apply_ips

core = C.CDLL(str(args.core.resolve()))
ENV=C.CFUNCTYPE(C.c_bool,C.c_uint,C.c_void_p)
VIDEO=C.CFUNCTYPE(None,C.c_void_p,C.c_uint,C.c_uint,C.c_size_t)
AUDIO=C.CFUNCTYPE(None,C.c_int16,C.c_int16)
BATCH=C.CFUNCTYPE(C.c_size_t,C.POINTER(C.c_int16),C.c_size_t)
POLL=C.CFUNCTYPE(None)
INPUT=C.CFUNCTYPE(C.c_int16,C.c_uint,C.c_uint,C.c_uint,C.c_uint)
class Variable(C.Structure):
    _fields_=[('key',C.c_char_p),('value',C.c_char_p)]
class GameInfo(C.Structure):
    _fields_=[('path',C.c_char_p),('data',C.c_void_p),('size',C.c_size_t),('meta',C.c_char_p)]
options={}; pixel=0; last=None; buttons=set(); frame=0
@ENV
def environment(cmd,data):
    global pixel
    if cmd==10:
        pixel=C.cast(data,C.POINTER(C.c_int)).contents.value
        return pixel in (0,1,2)
    if cmd==3:
        C.cast(data,C.POINTER(C.c_bool))[0]=True; return True
    if cmd in (17,):
        C.cast(data,C.POINTER(C.c_bool))[0]=False; return True
    if cmd in (52,59):
        C.cast(data,C.POINTER(C.c_uint))[0]=0; return True
    if cmd==16:
        array=C.cast(data,C.POINTER(Variable)); i=0
        while array[i].key:
            options[array[i].key]=array[i].value.split(b';',1)[1].strip().split(b'|')[0]; i+=1
        return True
    if cmd==15:
        v=C.cast(data,C.POINTER(Variable)); v[0].value=options.get(v[0].key); return bool(v[0].value)
    if cmd==39:
        C.cast(data,C.POINTER(C.c_uint))[0]=0; return True
    return False
@VIDEO
def video(data,w,h,pitch):
    global last
    if not data:return
    raw=C.string_at(data,pitch*h)
    if pixel==1:
        a=np.frombuffer(raw,dtype=np.uint8).reshape(h,pitch)[:,:w*4].reshape(h,w,4)
        last=Image.fromarray(a[:,:,[2,1,0]],'RGB')
    else:
        a=np.frombuffer(raw,dtype=np.uint16).reshape(h,pitch//2)[:,:w].astype(np.uint32)
        if pixel==2:r=(a>>11)&31;g=(a>>5)&63;b=a&31;gs=63
        else:r=(a>>10)&31;g=(a>>5)&31;b=a&31;gs=31
        last=Image.fromarray(np.stack([r*255//31,g*255//gs,b*255//31],axis=2).astype('uint8'),'RGB')
@AUDIO
def audio(l,r):pass
@BATCH
def batch(data,n):return n
@POLL
def poll():pass
@INPUT
def input_state(port,device,index,id):return int(port==0 and id in buttons)
for name,callback in [('environment',environment),('video_refresh',video),('audio_sample',audio),('audio_sample_batch',batch),('input_poll',poll),('input_state',input_state)]:
    fn=getattr(core,'retro_set_'+name);fn.argtypes=[type(callback)];fn(callback)
core.retro_load_game.argtypes=[C.POINTER(GameInfo)];core.retro_load_game.restype=C.c_bool
core.retro_serialize_size.restype=C.c_size_t
core.retro_serialize.argtypes=[C.c_void_p,C.c_size_t];core.retro_serialize.restype=C.c_bool
core.retro_unserialize.argtypes=[C.c_void_p,C.c_size_t];core.retro_unserialize.restype=C.c_bool
core.retro_get_memory_data.argtypes=[C.c_uint];core.retro_get_memory_data.restype=C.c_void_p
core.retro_get_memory_size.argtypes=[C.c_uint];core.retro_get_memory_size.restype=C.c_size_t
core.retro_init()
original=args.original_rom.read_bytes()
assert hashlib.sha256(original).hexdigest()=='e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956'
patch=args.ips
rom=apply_ips(original,patch.read_bytes())
buf=C.create_string_buffer(rom); info=GameInfo(b'chibi.sfc',C.cast(buf,C.c_void_p),len(rom),None)
assert core.retro_load_game(C.byref(info))
ram=(C.c_ubyte*core.retro_get_memory_size(2)).from_address(core.retro_get_memory_data(2))
def run(n,keys=()):
    global buttons,frame
    buttons=set(keys)
    for _ in range(n):core.retro_run();frame+=1
    buttons=set()
def snap(name):
    assert last is not None
    last.resize((last.width*3,last.height*3),Image.Resampling.NEAREST).save(ROOT/'outputs'/('QA087_'+os.environ.get('CHIBI_QA_LABEL','')+name+'.png'))
    print(name,frame,last.size,flush=True)
def save(name):
    n=core.retro_serialize_size(); b=C.create_string_buffer(n)
    assert core.retro_serialize(b,n)
    (ROOT/'work'/('state_'+name+'.bin')).write_bytes(b.raw)
def load(name):
    data=(ROOT/'work'/('state_'+name+'.bin')).read_bytes();b=C.create_string_buffer(data)
    assert core.retro_unserialize(b,len(data))
run(600);snap('publisher_logo')
run(2,[3]);run(1920);snap('localized_title')
run(2,[3]);run(180);snap('mode_menu');save('mode_menu')
for _ in range(3):run(2,[5]);run(10)
run(2,[8]);run(480);snap('quiz_title')
run(2,[3])
for _ in range(500):
    run(1)
    if ram[0x1480] or ram[0x1482]:break
else:raise AssertionError('Quiz initialization not reached')
save('quiz_initialized')
if not args.sweep:
    ram[0x1480]=0;ram[0x1481]=0;ram[0x1410]=0;ram[0x1411]=0
    run(300);snap('quiz_allowance_smoke')
    run(2,[0]);run(225);snap('quiz_response_smoke')
if args.sweep:
    shots=ROOT/'outputs/quiz';shots.mkdir(exist_ok=True)
    results=[]
    for slot in range(50):
        load('quiz_initialized')
        ram[0x1480]=slot*2;ram[0x1481]=0;ram[0x1410]=0;ram[0x1411]=0
        run(300);last.save(shots/f'slot_{slot:02d}.png');save('question')
        item={'table_slot':slot,'answer_selections':[]}
        for choice in range(3):
            load('question')
            for _ in range(choice):run(2,[5]);run(8)
            last.save(shots/f'slot_{slot:02d}_highlight_{choice+1}.png')
            run(2,[0]);run(45)
            last.save(shots/f'slot_{slot:02d}_grade_{choice+1}.png')
            run(180)
            last.save(shots/f'slot_{slot:02d}_response_{choice+1}.png')
            item['answer_selections'].append({'selected_row':choice+1,
                'quiz_control_WRAM_1400_1424':bytes(ram[0x1400:0x1424]).hex(),
                'response_image_SHA256':hashlib.sha256(last.tobytes()).hexdigest()})
        results.append(item)
        if slot%10==9:print('Quiz sweep',slot+1,'/50',flush=True)
    (ROOT/'outputs/runtime_sweep.json').write_text(json.dumps({
        'method':'Snes9x CPU/PPU emulation, savestates, injected WRAM question slot; no ROM edits by harness',
        'original_SHA256':hashlib.sha256(original).hexdigest(),
        'IPS_SHA256':hashlib.sha256(patch.read_bytes()).hexdigest(),
        'core_DLL_SHA256':hashlib.sha256(args.core.read_bytes()).hexdigest(),
        'question_slots_exercised':50,'answer_selections_exercised':150,
        'natural_full_game_playthrough':False,'grading_correctness_certified':False,
        'visual_acceptance_requires_review':True,'results':results},indent=2),encoding='utf-8')
if args.stage_sweep:
    shots=ROOT/'outputs/stages';shots.mkdir(exist_ok=True)
    load('mode_menu');run(4,[5]);run(30);run(4,[8]);run(240);save('stage_game_base')
    results=[];matches=[]
    for game in range(3):
        load('stage_game_base')
        for _ in range(game):run(4,[7]);run(40)
        run(4,[8]);run(300);run(4,[8]);run(400)
        run(4,[5]);run(20);run(4,[7]);run(20);run(4,[3]);run(300)
        run(4,[3]);run(300);run(4,[8]);run(200)
        for stage in range(5):
            if stage:run(4,[7]);run(100)
            assert ram[0x70]==0x14 and ram[0x2048]==stage
            name=f'114_stage_{game}_{stage}'
            last.save(shots/f'game_{game}_stage_{stage}.png');save(name)
            results.append({'game':game,'ordinal':stage,'selected':ram[0x2048],'control':ram[0x70],'actor_state':ram[0xa2]})
            run(4,[3]);run(300)
            for key in (6,8,7,8):run(30,[key]);run(10)
            last.save(shots/f'gameplay_{game}_{stage}.png')
            if stage==4 and args.full_stage_matches:
                run(14000)
                assert ram[0x70] in (0x35,0x55,0x79) and ram[0xa2]==7
                last.save(shots/f'full_match_result_{game}.png');matches.append({'game':game,'controller':ram[0x70],'result_state':ram[0xa2]})
            if stage<4:load(name);run(2)
    (ROOT/'outputs/stage_runtime.json').write_text(json.dumps({'ROM_SHA256':hashlib.sha256(rom).hexdigest(),'IPS_SHA256':hashlib.sha256(patch.read_bytes()).hexdigest(),'core_SHA256':hashlib.sha256(args.core.read_bytes()).hexdigest(),'method':'Native controller flow through solo setup, CPU selection, all15 stage selectors and match entry; no WRAM injection','events':results,'completed_timed_matches':matches,'natural_full_game_playthrough':False},indent=2),encoding='utf-8')
core.retro_unload_game();core.retro_deinit()
