"""Execute emitted selector at both Fortune range boundaries and native modes."""
import json
from build_fortune_full_layout_091 import compact_selector
from build_quiz_layout_087 import spacing_stub,destination_stub,wrap_stub
from selftest_quiz_layout_087 import execute

def main():
 contexts=[(5,p,0xbd24<=p<0xcb9b or 0xff20<=p<0xffa0) for p in (0xbd23,0xbd24,0xcb9a,0xcb9b,0xff00,0xff1f,0xff20,0xff9f,0xffa0,0xffff)]
 contexts += [(0x85,p,v) for b,p,v in contexts]+[(6,0x9d00,True),(0x86,0xffff,True),(0x7e,0x8000,True),(0x7e,0x808f,True),(0x7e,0x8090,False),(3,0x81ce,False),(5,0xbe0c,True)]
 cases=0
 for bank,ptr,compact in contexts:
  for col in range(28 if compact else 19):
   pos=(12+8*col) if compact else (4+13*col)
   for carry in (0,1):
    assert execute(spacing_stub(True,compact_selector),bank,ptr,col,carry=carry)==(16*(pos//8),carry,16,col*2)
    a,c,m,x=execute(spacing_stub(False,compact_selector),bank,ptr,col,word=False,carry=carry)
    assert (a&255,c,m,x)==(pos%8,carry,8,col)
    assert execute(destination_stub(compact_selector),bank,ptr,col,incoming=0x2400,carry=carry)==(0x2400+16*(pos//8)+carry,0,16,col*2)
    cases+=3
  for col in (18,19,27,28):
   a,c,m,x=execute(wrap_stub(compact_selector),bank,ptr,col)
   assert (a,c,m)==(col,int(col>=(28 if compact else 19)),16);cases+=1
 print(json.dumps({'status':'PASS_FORTUNE_AND_QUIZ_SELECTOR_NATIVE_FALLBACK','execution_cases':cases,'real_emulator_test':False}))
if __name__=='__main__':main()
