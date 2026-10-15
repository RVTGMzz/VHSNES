"""Execute all emitted106 layout consumers at native and lyric boundaries."""
import json
from build_karaoke_lyrics_106 import lyric_selector
from build_quiz_layout_087 import spacing_stub,destination_stub,wrap_stub
from selftest_quiz_layout_087 import execute

def main():
 contexts=[(5,p,0xb37a<=p<0xb80a or 0xbd24<=p<0xcb9b or 0xf272<=p<0xf800 or 0xff20<=p<0xffa0) for p in (0xb379,0xb37a,0xb7bb,0xb809,0xb80a,0xbd23,0xbd24,0xcb9a,0xcb9b,0xf271,0xf272,0xf7ff,0xf800,0xff1f,0xff20,0xff9f,0xffa0)]
 contexts += [(0x85,p,v) for b,p,v in contexts]+[(3,0x9250,True),(6,0x9d00,True),(0x7e,0x8000,True),(0x7e,0x808f,True),(0x7e,0x8090,False),(4,0x8100,False)]
 cases=0
 for bank,ptr,compact in contexts:
  for col in range(28 if compact else 19):
   pos=(12+8*col) if compact else (4+13*col)
   for carry in (0,1):
    assert execute(spacing_stub(True,lyric_selector),bank,ptr,col,carry=carry)==(16*(pos//8),carry,16,col*2)
    a,c,m,x=execute(spacing_stub(False,lyric_selector),bank,ptr,col,word=False,carry=carry)
    assert (a&255,c,m,x)==(pos%8,carry,8,col)
    assert execute(destination_stub(lyric_selector),bank,ptr,col,incoming=0x2400,carry=carry)==(0x2400+16*(pos//8)+carry,0,16,col*2)
    cases+=3
  for col in (18,19,27,28):
   a,c,m,x=execute(wrap_stub(lyric_selector),bank,ptr,col);assert (a,c,m)==(col,int(col>=(28 if compact else 19)),16);cases+=1
 print(json.dumps({'status':'PASS_KARAOKE_STORY_QUIZ_FORTUNE_NATIVE_LAYOUT','execution_cases':cases,'real_emulator_test':False}))
if __name__=='__main__':main()
