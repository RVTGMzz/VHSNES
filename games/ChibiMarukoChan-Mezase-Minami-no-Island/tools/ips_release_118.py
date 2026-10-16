"""Standard IPS replay and 4MiB LoROM expansion for release118; no dependencies."""
import argparse,hashlib
from pathlib import Path
from build_content_first_040_fortune import make_ips as fixed_size_ips
LIMIT=0x400000

def apply_ips(original,patch):
 if not patch.startswith(b'PATCH') or not patch.endswith(b'EOF'):raise ValueError('Invalid IPS framing')
 out=bytearray(original);p=5;end=len(patch)-3
 while p<end:
  if p+5>end:raise ValueError('Truncated IPS header')
  at=int.from_bytes(patch[p:p+3],'big');n=int.from_bytes(patch[p+3:p+5],'big');p+=5
  if n:
   if p+n>end:raise ValueError('Truncated IPS literal')
   blob=patch[p:p+n];p+=n
  else:
   if p+3>end:raise ValueError('Truncated IPS RLE')
   n=int.from_bytes(patch[p:p+2],'big')
   if not n:raise ValueError('Empty IPS RLE')
   blob=bytes([patch[p+2]])*n;p+=3
  if at+len(blob)>LIMIT:raise ValueError('IPS exceeds 4MiB LoROM contract')
  if at+len(blob)>len(out):out.extend(bytes(at+len(blob)-len(out)))
  out[at:at+len(blob)]=blob
 if p!=end:raise ValueError('Invalid IPS boundary')
 return bytes(out)

def make_ips(original,patched):
 if not len(original)<=len(patched)<=LIMIT:raise ValueError('Invalid expansion size')
 fixed,count=fixed_size_ips(original,patched[:len(original)]);out=bytearray(fixed[:-3]);p=len(original)
 while p<len(patched):
  n=min(65535,len(patched)-p);blob=patched[p:p+n]
  if blob==blob[:1]*n:out+=p.to_bytes(3,'big')+b'\x00\x00'+n.to_bytes(2,'big')+blob[:1]
  else:out+=p.to_bytes(3,'big')+n.to_bytes(2,'big')+blob
  count+=1;p+=n
 out+=b'EOF';assert apply_ips(original,out)==patched
 return bytes(out),count

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('original',type=Path);p.add_argument('ips',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
 if a.output.resolve() in (a.original.resolve(),a.ips.resolve()):p.error('Output must be a separate file')
 clean=a.original.read_bytes()
 if hashlib.sha256(clean).hexdigest()!='e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956':p.error('Exact Japanese unheadered original required')
 rom=apply_ips(clean,a.ips.read_bytes());a.output.write_bytes(rom);print('ROM SHA256:',hashlib.sha256(rom).hexdigest())
if __name__=='__main__':main()
