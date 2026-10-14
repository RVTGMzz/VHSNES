"""Replace the native 第/問 Quiz counter with Câu and keep dynamic digits."""
import hashlib
from pathlib import Path

from build_quiz_relocated_81_jobwait_075 import read_codepage
from build_content_first_040_fortune import make_ips, apply_ips

BASE_SHA='a8a6c028b2cff5d1daf3410768fae0c1309dddfb694142fcf682ca763fd4081f'


def build(clean,baseline,root:Path):
    if hashlib.sha256(clean).hexdigest()!='e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956':
        raise ValueError('Requires original ROM identity')
    if hashlib.sha256(baseline).hexdigest()!=BASE_SHA:
        raise ValueError('Requires the exact readable-title 088 baseline')
    mapping=read_codepage(root)
    label=b''.join(bytes.fromhex(mapping[ch]) for ch in 'Câu')
    output=bytearray(baseline);allowed=set(range(0x7fdc,0x7fe0))
    def write(at,old,new):
        if len(old)!=len(new) or baseline[at:at+len(old)]!=old:
            raise AssertionError(f'Counter anchor changed at {at:#x}')
        output[at:at+len(new)]=new;allowed.update(range(at,at+len(new)))
    write(0x31536,bytes.fromhex('0E080F0891E6202096E2816F00'),
          bytes.fromhex('0E0C0F08')+label+bytes.fromhex('816F00'))
    write(0x31543,bytes.fromhex('0E070F0891E62020202096E2816F00'),
          bytes.fromhex('0E0C0F08')+label+bytes.fromhex('8440816F00'))
    at=clean.index(bytes.fromhex('A908088500'),0x30656,0x30680)
    # DP $01 is column, DP $00 is row. Native decimal helper adds one
    # column for a single digit and leaves the two-digit starting column.
    write(at,bytes.fromhex('A908088500'),bytes.fromhex('A9080F8500'))
    output[0x7fdc:0x7fe0]=bytes(4)
    checksum=(sum(output)+0x1fe)&0xffff
    output[0x7fdc:0x7fde]=(checksum^0xffff).to_bytes(2,'little')
    output[0x7fde:0x7fe0]=checksum.to_bytes(2,'little')
    if any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(baseline,output))):
        raise AssertionError('Counter mutation escaped approved fields')
    ips,count=make_ips(clean,output)
    if apply_ips(clean,ips)!=bytes(output):raise AssertionError('Counter IPS replay failed')
    return ips,{
        'status':'089_VIETNAMESE_QUIZ_COUNTER_BINARY_PASS',
        'counter_label':'Câu','native_decimal_formatting_retained':True,
        'IPS_SHA256':hashlib.sha256(ips).hexdigest(),'IPS_bytes':len(ips),'IPS_records':count,
        'candidate_ROM_SHA256':hashlib.sha256(output).hexdigest(),'checksum':hex(checksum),
        'quiz_answer_tables_and_grading_unchanged':True,'whole_game_complete':False,
    }
