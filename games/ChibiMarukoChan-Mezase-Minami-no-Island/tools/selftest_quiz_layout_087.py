"""ROM-free execution of the emitted Quiz hooks with native fallback checks."""
import json

from build_quiz_layout_087 import spacing_stub, destination_stub, wrap_stub


def execute(code, bank, pointer, column, word=True, incoming=0x2400, carry=0, subroutines=None):
    # Model only emitted instructions; real Snes9x evidence is recorded
    # separately. M16 is required by the native word/ADC/wrap callers.
    mem={0x001f86:bank,0x001f94:pointer,0x001f9a:column}
    for i in range(28):
        mem[0x85fd80+i*2]=16*((12+8*i)//8)
        mem[0x85fdc0+i]=(12+8*i)%8
    for i in range(19):
        mem[0x859670+i*2]=16*((4+13*i)//8)
        mem[0x859696+i]=(4+13*i)%8
    a=incoming; x=column*(2 if word else 1); m=16 if word else 8
    c=carry;z=False;stack=[];ip=0;calls=[]
    for _ in range(300):
        op=code[ip];ip+=1
        if op==0x08:stack.append(('P',m,c,z))
        elif op==0x28:_,m,c,z=stack.pop()
        elif op==0x48:stack.append(a)
        elif op==0x68:a=stack.pop();z=(a==0)
        elif op==0xc2:
            assert code[ip]==0x20;ip+=1;m=16
        elif op in (0xaf,0xbf,0x7f):
            addr=int.from_bytes(code[ip:ip+3],'little');ip+=3
            value=mem[addr+(x if op!=0xaf else 0)]
            mask=(1<<m)-1
            if op==0x7f:
                total=(a&mask)+value+c;c=int(total>mask);a=total&mask
            elif m==8:a=(a&0xff00)|(value&255)
            else:a=value
            z=(a&mask)==0
        elif op in (0x29,0xc9,0xa9):
            assert m==16
            value=int.from_bytes(code[ip:ip+2],'little');ip+=2
            if op==0xa9:a=value;z=a==0
            elif op==0x29:a&=value;z=a==0
            else:c=int(a>=value);z=a==value
        elif op in (0xf0,0xd0,0x90,0xb0,0x80):
            n=code[ip];ip+=1;n=n-256 if n>127 else n
            if op==0x80 or (op==0xf0 and z) or (op==0xd0 and not z) or (op==0x90 and not c) or (op==0xb0 and c):ip+=n
        elif op==0xea:pass
        elif op==0x22:
            addr=int.from_bytes(code[ip:ip+3],'little');ip+=3
            assert subroutines and addr in subroutines
            calls.append((code,ip));code=subroutines[addr];ip=0
        elif op==0x6b:
            if calls:code,ip=calls.pop();continue
            assert not stack
            return a,c,m,x
        else:raise AssertionError(f'Unexpected emitted opcode {op:#x}')
    raise AssertionError('Hook did not return')


def main():
    cases=0
    contexts=((6,0x9d00,True),(0x86,0xffff,True),
              (0x7e,0x8000,True),(0x7e,0x808f,True),
              (0x7e,0x7fff,False),(0x7e,0x8090,False),
              (5,0xa000,False),(3,0x81ce,False))
    for bank,ptr,quiz in contexts:
        for col in range(19):
            pitch,margin=(8,12) if quiz else (13,4)
            pos=margin+pitch*col
            for carry in (0,1):
                a,c,m,x=execute(spacing_stub(True),bank,ptr,col,carry=carry)
                assert (a,c,m,x)==(16*(pos//8),carry,16,col*2)
                a,c,m,x=execute(spacing_stub(False),bank,ptr,col,word=False,carry=carry)
                assert (a&255,c,m,x)==(pos%8,carry,8,col)
                a,c,m,x=execute(destination_stub(),bank,ptr,col,incoming=0x2400,carry=carry)
                assert (a,c,m,x)==(0x2400+16*(pos//8)+carry,0,16,col*2)
                cases+=3
        for col in (18,19,27,28):
            a,c,m,x=execute(wrap_stub(),bank,ptr,col)
            assert a==col and c==int(col >= (28 if quiz else 19)) and m==16
            cases+=1
    for col in range(28):
        a,_,_,_=execute(spacing_stub(True),6,0x9d00,col)
        assert a==16*((12+8*col)//8)
    print(json.dumps({'status':'PASS_EMITTED_QUIZ_HOOKS_NATIVE_FALLBACK',
                      'execution_cases':cases+28,'real_emulator_test':False}))


if __name__=='__main__':main()
