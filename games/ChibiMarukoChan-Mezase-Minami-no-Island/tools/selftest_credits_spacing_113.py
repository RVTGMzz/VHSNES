"""Execute the final selectors and far helper at all changed range boundaries."""
import json
from build_completion_113 import credit_selector,credit_bank_helper
from build_quiz_layout_087 import spacing_stub,destination_stub,wrap_stub
from selftest_quiz_layout_087 import execute

def main():
 contexts=[]
 for bank in (3,0x83):
  contexts += [(bank,p,not 0xded4<=p<0xe2fb) for p in (0x8000,0xded3,0xded4,0xdf00,0xe2fa,0xe2fb,0xffff)]
 for bank in (5,0x85):
  contexts += [(bank,p,0x88be<=p<0x8a90 or 0xb37a<=p<0xb80a or 0xbd24<=p<0xcd74 or 0xf272<=p<0xf800 or 0xf821<=p<0xfa00 or 0xff20<=p<0xffa0) for p in (0x88bd,0x88be,0x8a8f,0x8a90,0xb379,0xb37a,0xb809,0xb80a,0xbd23,0xbd24,0xcd73,0xcd74,0xf271,0xf272,0xf7ff,0xf800,0xf820,0xf821,0xf9ff,0xfa00,0xff1f,0xff20,0xff9f,0xffa0)]
 contexts += [(6,0x9d00,True),(0x86,0xffff,True),(0x7e,0x8000,True),(0x7e,0x808f,True),(0x7e,0x8090,False),(4,0x8100,False)]
 cases=0;subs={0x81f096:credit_bank_helper()}
 for bank,ptr,compact in contexts:
  for col in range(28 if compact else 19):
   pos=(12+8*col) if compact else (4+13*col)
   for carry in (0,1):
    assert execute(spacing_stub(True,credit_selector),bank,ptr,col,carry=carry,subroutines=subs)==(16*(pos//8),carry,16,col*2)
    a,c,m,x=execute(spacing_stub(False,credit_selector),bank,ptr,col,word=False,carry=carry,subroutines=subs);assert (a&255,c,m,x)==(pos%8,carry,8,col)
    assert execute(destination_stub(credit_selector),bank,ptr,col,incoming=0x2400,carry=carry,subroutines=subs)==(0x2400+16*(pos//8)+carry,0,16,col*2)
    cases+=3
  for col in (18,19,27,28):
   a,c,m,x=execute(wrap_stub(credit_selector),bank,ptr,col,subroutines=subs);assert (a,c,m)==(col,int(col>=(28 if compact else 19)),16);cases+=1
 print(json.dumps({'status':'PASS_CREDITS_NATIVE_AND_ALL_FINAL_COMPACT_CONTEXTS','execution_cases':cases,'real_emulator_test':False}))
if __name__=='__main__':main()
