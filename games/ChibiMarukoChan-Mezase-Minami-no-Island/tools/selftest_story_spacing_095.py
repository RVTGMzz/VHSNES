import json
from build_story_spacing_095 import story_selector
from build_quiz_layout_087 import spacing_stub,destination_stub,wrap_stub
from selftest_quiz_layout_087 import execute
def main():
 contexts=[(3,0x83a2,True),(0x83,0x9250,True),(3,0xdfff,True),(6,0x9d00,True),(0x7e,0x8000,True),(0x7e,0x8090,False),(5,0xbd24,True),(5,0xcb9b,False),(5,0xff20,True),(5,0xffa0,False),(5,0xff00,False),(4,0x8100,False)]
 cases=0
 for bank,ptr,compact in contexts:
  for col in range(28 if compact else 19):
   pos=(12+8*col) if compact else (4+13*col)
   for carry in (0,1):
    assert execute(spacing_stub(True,story_selector),bank,ptr,col,carry=carry)==(16*(pos//8),carry,16,col*2)
    a,c,m,x=execute(spacing_stub(False,story_selector),bank,ptr,col,word=False,carry=carry)
    assert (a&255,c,m,x)==(pos%8,carry,8,col)
    assert execute(destination_stub(story_selector),bank,ptr,col,incoming=0x2400,carry=carry)==(0x2400+16*(pos//8)+carry,0,16,col*2)
    cases+=3
  for col in (18,19,27,28):
   a,c,m,x=execute(wrap_stub(story_selector),bank,ptr,col);assert (a,c,m)==(col,int(col>=(28 if compact else 19)),16);cases+=1
 print(json.dumps({'status':'PASS_STORY_QUIZ_FORTUNE_GEOMETRY_NATIVE_MENUS','execution_cases':cases,'real_emulator_test':False}))
if __name__=='__main__':main()
