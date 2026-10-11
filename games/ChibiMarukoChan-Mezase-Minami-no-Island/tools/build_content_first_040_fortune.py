#!/usr/bin/env python3
"""Content-first 040: 33 Fortune translations over exact G0/G1 + UI 039.

Existing V2 glyph/codepage bytes are REUSED, not modified. Validate all 33
canonical Japanese and Vietnamese source rows, CP932 bytes, source controls,
live V2 0x84 mappings, and original field budgets. Apply exact 039 IPS to
exact clean ROM; release an experimental clean-ROM IPS, not a ROM on GitHub.
NO SNES emulator runtime evidence or whole-game completion claim.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import unicodedata
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
CLEAN_SHA='e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956'
BASE_SHA='a1f4459942e3a757cc314d12c959168046b4a6dd66018d55b014c70d052e98ce'
BASE_IPS_SHA='97c0e41b354b0dda3ea7c0c292b5aef236586e279870962fd0d4f3398285008c'
FINAL_SHA='d892c51576c103f5881f1481c65fd2746635d222b1d387f9666cd7f44b1da3ac'
FINAL_IPS_SHA='2bfdcc64973bc31ce268fa7e68a6118808c633b10d1437b7f811ac290616e580'


def sha(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path:Path)->list[dict[str,str]]:
    with path.open(encoding='utf-8-sig',newline='') as source:
        return list(csv.DictReader(source))


def apply_ips(original:bytes,ips:bytes)->bytes:
    if not ips.startswith(b'PATCH') or not ips.endswith(b'EOF'):
        raise ValueError('Bad IPS framing')
    result=bytearray(original)
    p=5
    end=len(ips)-3
    while p<end:
        if p+5>end:
            raise ValueError('Truncated IPS record')
        off=int.from_bytes(ips[p:p+3],'big')
        size=int.from_bytes(ips[p+3:p+5],'big')
        p+=5
        if size:
            if p+size>end:
                raise ValueError('Truncated IPS payload')
            payload=ips[p:p+size]
            p+=size
        else:
            if p+3>end:
                raise ValueError('Truncated IPS RLE')
            count=int.from_bytes(ips[p:p+2],'big')
            payload=bytes([ips[p+2]])*count
            p+=3
        if off+len(payload)>len(result):
            raise ValueError('IPS writes beyond 2MiB input')
        result[off:off+len(payload)]=payload
    if p!=end:
        raise ValueError('Malformed IPS trailing data')
    return bytes(result)


def make_ips(original:bytes,patched:bytes)->tuple[bytes,int]:
    if len(original)!=len(patched):
        raise ValueError('IPS input length mismatch')
    output=bytearray(b'PATCH')
    count=p=0
    while p<len(original):
        if original[p]==patched[p]:
            p+=1
            continue
        start=p
        changed=bytearray()
        while (p<len(original) and original[p]!=patched[p]
               and len(changed)<65535):
            changed.append(patched[p])
            p+=1
        output+=start.to_bytes(3,'big')+len(changed).to_bytes(2,'big')+changed
        count+=1
    return bytes(output+b'EOF'),count


def build(clean:bytes,patch039:bytes,root:Path):
    if len(clean)!=0x200000 or sha(clean)!=CLEAN_SHA:
        raise ValueError('Wrong clean Japanese 2MiB ROM')
    if len(patch039)!=21130 or sha(patch039)!=BASE_IPS_SHA:
        raise ValueError('Wrong exact checkpoint039 IPS')
    previous=apply_ips(clean,patch039)
    if sha(previous)!=BASE_SHA:
        raise AssertionError('Baseline 039 IPS replay does not match its SHA')

    proposed=read_csv(root/'translation/runtime/fortune_exact_fit_040.csv')
    if len(proposed)!=33 or len({r['file_offset'] for r in proposed})!=33:
        raise AssertionError('Expected precisely 33 unique reviewed Fortune rows')
    canonical={}
    for file in ('fortune_batch01_part1_vi.csv','fortune_batch01_part2_vi.csv',
                 'fortune_batch01_part3_vi.csv'):
        for row in read_csv(root/'translation/source'/file):
            key=row['file_offset'].upper()
            if key in canonical:
                raise AssertionError(f'Duplicate source {key}')
            canonical[key]=row
    codepage={row['unicode']:row['code_hex'] for row in
              read_csv(root/'translation/codepage/vi_codepage_v4_fe4_native.csv')}
    if codepage.get(' ')!='8440':
        raise AssertionError('Existing codepage space entry changed')
    ptr=int.from_bytes(previous[0x2975E:0x29760],'little')
    if ptr!=0x9A74:
        raise AssertionError('Existing V2 codepage pointer moved')

    output=bytearray(previous)
    allowed=set()
    translations=[]
    for row in proposed:
        key=row['file_offset'].upper()
        pos=int(row['file_offset'],16)
        original=row['source_jp']
        full=row['vi_full_reference']
        compact=row['vi_runtime']
        source=canonical.get(key)
        if source is None or (source['source_jp'],source['vi_full'])!=(original,full):
            raise AssertionError(f'Canonical Japanese/meaning drift at {key}')
        if row['status']!='runtime_candidate_exact_fit':
            raise AssertionError(f'Unapproved compact text at {key}')
        if unicodedata.normalize('NFC',compact)!=compact:
            raise AssertionError(f'Non-NFC compact Vietnamese at {key}')
        raw=original.encode('cp932')
        units=int(row['max_units'])
        if len(raw)!=2*units or len(compact)>units:
            raise AssertionError(f'Invalid 2-byte unit budget at {key}')
        if (clean[pos:pos+len(raw)]!=raw or previous[pos:pos+len(raw)]!=raw):
            raise AssertionError(f'Exact original Japanese bytes changed at {key}')
        if (clean[pos+len(raw):pos+len(raw)+2]!=b'\x81\x6f'
            or previous[pos+len(raw):pos+len(raw)+2]!=b'\x81\x6f'):
            raise AssertionError(f'Original line terminator missing at {key}')
        region=set(range(pos,pos+len(raw)))
        if allowed&region:
            raise AssertionError(f'Overlapping translation rows at {key}')
        allowed.update(region)
        encoded=bytearray()
        for char in compact+' '*(units-len(compact)):
            code=codepage.get(char)
            if code is None or len(code)!=4 or not code.startswith('84'):
                raise AssertionError(f'Missing codepage glyph {char!r} at {key}')
            low=int(code[-2:],16)
            table=0x28000+(ptr&0x7fff)+2*(low-0x40)
            if int.from_bytes(previous[table:table+2],'little')==0:
                raise AssertionError(f'Existing font has no glyph {char!r}')
            encoded.extend(bytes.fromhex(code))
        if len(encoded)!=len(raw):
            raise AssertionError('Encoded field byte count mismatch')
        output[pos:pos+len(raw)]=encoded
        if output[pos+len(raw):pos+len(raw)+2]!=b'\x81\x6f':
            raise AssertionError('Corrupted original terminator')
        translations.append({
            'offset':row['file_offset'],'source_jp':original,
            'vi_full':full,'vi_runtime':compact,'capacity':units,
            'category':row['category'],
        })

    output[0x7FDC:0x7FE0]=bytes(4)
    checksum=(sum(output)+0x1FE)&0xFFFF
    output[0x7FDC:0x7FDE]=(checksum^0xFFFF).to_bytes(2,'little')
    output[0x7FDE:0x7FE0]=checksum.to_bytes(2,'little')
    output=bytes(output)
    if sha(output)!=FINAL_SHA:
        raise AssertionError(f'Unexpected output ROM SHA {sha(output)}')
    differences={i for i,(a,b) in enumerate(zip(previous,output)) if a!=b}
    if differences-(allowed|set(range(0x7FDC,0x7FE0))):
        raise AssertionError('ROM diff escaped translated fields')

    ips,records=make_ips(clean,output)
    if sha(ips)!=FINAL_IPS_SHA or len(ips)!=21727 or records!=707:
        raise AssertionError('Unexpected generated clean-ROM IPS')
    if apply_ips(clean,ips)!=output:
        raise AssertionError('Independent clean-ROM IPS replay failed')
    groups=('fortune_heading','fortune_message','lucky_color')
    report={
        'status':'040_FORTUNE_EXACTFIT_STATIC_PASS_NOT_RUNTIME',
        'clean_rom_sha256':CLEAN_SHA,
        'previous_039_rom_sha256':BASE_SHA,
        'new_040_rom_sha256':FINAL_SHA,
        'new_040_ips_sha256':FINAL_IPS_SHA,
        'new_Fortune_Vietnamese_fields':len(translations),
        'category_counts':{g:sum(t['category']==g for t in translations) for g in groups},
        'CP932_source_and_terminator_verified':len(translations),
        'existing_039_binary_bytes_preserved_outside_fields':True,
        'existing_V2_font_modified':False,
        'full_canonical_vi_full_modified':False,
        'changed_rom_bytes_vs_039':len(differences),
        'checksum':f'0x{checksum:04X}',
        'complement':f'0x{checksum^0xFFFF:04X}',
        'ips_bytes':len(ips),
        'ips_records':records,
        'all_Story_Quiz_Fortune_translated':False,
        'SNES_emulator':'NOT_TESTED',
        'release_ready':False,
        'translations':translations,
    }
    return output,ips,report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('exact_clean_japanese_rom',type=Path)
    parser.add_argument('exact_039_ips',type=Path)
    parser.add_argument('--project-root',type=Path,default=ROOT)
    parser.add_argument('--ips',type=Path,required=True)
    parser.add_argument('--report',type=Path,required=True)
    parser.add_argument('--output-rom',type=Path,help='optional local debug ROM; never push to GitHub')
    parser.add_argument('--allow-untested',action='store_true')
    args=parser.parse_args()
    if not args.allow_untested:
        parser.error('Static-only candidate; pass --allow-untested explicitly')
    paths=[args.exact_clean_japanese_rom,args.exact_039_ips,args.ips,args.report]
    if args.output_rom:
        paths.append(args.output_rom)
    if len({p.resolve() for p in paths})!=len(paths):
        parser.error('Inputs and outputs must all have distinct paths')
    result,ips,report=build(args.exact_clean_japanese_rom.read_bytes(),
                            args.exact_039_ips.read_bytes(),args.project_root)
    for path,data in ((args.ips,ips),
                      (args.report,(json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))):
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(data)
    if args.output_rom:
        args.output_rom.parent.mkdir(parents=True,exist_ok=True)
        args.output_rom.write_bytes(result)
    print(json.dumps({k:v for k,v in report.items() if k!='translations'},
                     ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
