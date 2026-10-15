"""Clear all footer rows before each native stage caption text job."""
import argparse,hashlib,json
from pathlib import Path
from build_content_first_040_fortune import apply_ips,make_ips
BASE_SHA='d5e8ec75406e33d20d60263f519639200a55dc3b423a8b22bc5c1318b286017e'

def build(clean,base):
 if hashlib.sha256(base).hexdigest()!=BASE_SHA or hashlib.sha256(clean).hexdigest()!='e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956':raise ValueError('Exact115/original required')
 if base[0x21b91:0x21b9c]!=bytes.fromhex('a8224b80852260818590fa') or base[0xf080:0xf096]!=bytes.fromhex('08c230da5aa2060048228d8d85681acad0f67afa286b'):raise AssertionError('Native stage job or111 clear helper changed')
 # Preserve A/P and the record pointer in Y;111 helper preserves X/Y.
 # Clear six full-width bitmap rows before the original text job starts.
 stub=bytes.fromhex('08c23048a916002280f0816828224b80856b')
 if base[0xf0c0:0xf0c0+len(stub)]!=b'\xff'*len(stub):raise AssertionError('Owned104 padding collision')
 out=bytearray(base);out[0xf0c0:0xf0c0+len(stub)]=stub;out[0x21b92:0x21b96]=bytes.fromhex('22c0f081')
 out[0x7fdc:0x7fe0]=bytes(4);s=(sum(out)+510)&65535;out[0x7fdc:0x7fe0]=(s^65535).to_bytes(2,'little')+s.to_bytes(2,'little')
 allowed=set(range(0x7fdc,0x7fe0))|set(range(0xf0c0,0xf0c0+len(stub)))|set(range(0x21b92,0x21b96))
 if any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(base,out))):raise AssertionError('Write escaped spans')
 ips,_=make_ips(clean,out)
 if apply_ips(clean,ips)!=bytes(out):raise AssertionError('IPS replay')
 return ips,{'status':'116_STAGE_FOOTER_FULL_WIDTH_CLEAR_BINARY_PASS','cleared_rows':[22,27],'cleared_columns':32,'native_helper':'85:8D8D via81:F080','native_text_job_and_wait_preserved':True,'native_stage_IDs_input_and_timing_unchanged':True,'IPS_SHA256':hashlib.sha256(ips).hexdigest(),'ROM_SHA256':hashlib.sha256(out).hexdigest(),'whole_game_complete':False}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('original',type=Path);p.add_argument('baseline_ips',type=Path);p.add_argument('--ips',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args();c=a.original.read_bytes();ips,r=build(c,apply_ips(c,a.baseline_ips.read_bytes()));a.ips.write_bytes(ips);a.report.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(r))
if __name__=='__main__':main()
