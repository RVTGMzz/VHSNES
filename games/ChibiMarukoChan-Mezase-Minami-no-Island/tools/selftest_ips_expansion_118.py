"""Exercise standard IPS literals, RLE, boundaries and new-bank mapping without ROM."""
import json
from ips_release_118 import apply_ips,make_ips
from decompress_chibi_resource import cpu_to_file

def independent_replay(original,ips):
 # Deliberately parse the exported record framing independently of apply_ips.
 from io import BytesIO
 stream=BytesIO(ips);assert stream.read(5)==b'PATCH';out=bytearray(original)
 while True:
  raw=stream.read(3)
  if raw==b'EOF':break
  assert len(raw)==3;at=int.from_bytes(raw,'big');size=int.from_bytes(stream.read(2),'big')
  if size:payload=stream.read(size);assert len(payload)==size
  else:count=int.from_bytes(stream.read(2),'big');value=stream.read(1);assert len(value)==1;payload=value*count
  out.extend(bytes(max(0,at+len(payload)-len(out))));out[at:at+len(payload)]=payload
 assert not stream.read();return bytes(out)

def main():
 original=bytes(range(256))*2;cases=0
 for length in (512,513,65535,65536,0x200000,0x400000):
  target=bytearray(original)+bytearray(b'\xff'*(length-len(original)));target[17]=255
  if length>0x200000:target[0x200000:0x200006]=b'Latin!'
  patch,_=make_ips(original,target)
  assert apply_ips(original,patch)==target==independent_replay(original,patch);cases+=1
 for patch in (b'',b'PATCH'+b'\x00\x00\x01\x00\x03X'+b'EOF',b'PATCH'+b'\x00\x00\x01\x00\x00\x00\x00X'+b'EOF',b'PATCH'+b'\x40\x00\x00\x00\x01X'+b'EOF'):
  try:apply_ips(original,patch)
  except ValueError:cases+=1
  else:raise AssertionError('Malformed or oversized IPS accepted')
 for bank,expected in ((0x80,0),(0xbf,0x1f8000),(0xc0,0x200000),(0xff,0x3f8000)):
  assert cpu_to_file(bank<<16|0x8000)==expected;cases+=1
 print(json.dumps({'status':'PASS_STANDARD_IPS_EXPANSION_AND_LOROM_MAPPING','cases':cases,'ROM_or_fonts_required':False}))
if __name__=='__main__':main()
