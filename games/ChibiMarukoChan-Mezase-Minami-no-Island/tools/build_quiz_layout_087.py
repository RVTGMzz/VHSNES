"""Quiz layout correction after the exact integrated 086 candidate.

Use the parser's stored source bank instead of its transient DBR. Quiz bank06
and the three answer WRAM buffers get 8px/28-column layout; other text retains
the original tables and 19-column wrap. Keep font bitmaps and answer metadata.
"""
import hashlib
from pathlib import Path

from build_g2_probe008_line_scoped_9px_diagnostic import Assembly
from plan_quiz_bankcopy_slots_073 import plan
from build_quiz_relocated_81_jobwait_075 import read_codepage, encode_full, KANJI
from build_content_first_040_fortune import apply_ips, make_ips

BASE_SHA = "9e7e3caf356a0630da4872e400b1ded40e3854992464d003bc166fe0684e988f"
WORD_STUB, BYTE_STUB, WRAP_STUB = 0x2FB80, 0x2FC00, 0x2FC80
WORD_TABLE, BYTE_TABLE = 0x2FD80, 0x2FDC0


def selector(a):
    a.emit(0xAF, 0x86, 0x1F, 0x00, 0x29, 0x7F, 0x00)
    a.cmp16(6)
    a.branch(0xF0, 'quiz')
    a.cmp16(0x7e)
    a.branch(0xD0, 'native')
    a.emit(0xAF, 0x94, 0x1F, 0x00)
    a.cmp16(0x8000)
    a.branch(0x90, 'native')
    a.cmp16(0x8090)
    a.branch(0x90, 'quiz')


def spacing_stub(word, selector_factory=None):
    a = Assembly()
    a.emit(0x08, 0xC2, 0x20)  # preserve P; M16 for source-bank comparisons
    (selector_factory or selector)(a)
    a.label('native')
    a.emit(0x28)
    a.load_long_x(0x859670 if word else 0x859696)
    a.emit(0x6B)
    a.label('quiz')
    a.emit(0x28)
    a.load_long_x(0x85FD80 if word else 0x85FDC0)
    a.emit(0x6B)
    return a.assemble()


def destination_stub(selector_factory=None):
    # The bitmap destination uses ADC long,X from the SAME position table.
    # Preserve the incoming A and carry while checking the source context.
    a = Assembly()
    a.emit(0x48, 0x08)
    (selector_factory or selector)(a)
    a.label('native')
    a.emit(0x28, 0x68, 0x7F, 0x70, 0x96, 0x85, 0x6B)
    a.label('quiz')
    a.emit(0x28, 0x68, 0x7F, 0x80, 0xFD, 0x85, 0x6B)
    return a.assemble()


def wrap_stub(selector_factory=None):
    a = Assembly()  # caller has M16; return the original A/compare flags
    (selector_factory or selector)(a)
    a.label('native')
    a.emit(0xAF, 0x9A, 0x1F, 0x00)
    a.cmp16(19)
    a.emit(0x6B)
    a.label('quiz')
    a.emit(0xAF, 0x9A, 0x1F, 0x00)
    a.cmp16(28)
    a.emit(0x6B)
    return a.assemble()


def build(clean, baseline, root: Path):
    if hashlib.sha256(baseline).hexdigest() != BASE_SHA:
        raise AssertionError('Requires the exact recovered 086 + title relocation baseline')
    if hashlib.sha256(clean).hexdigest() != 'e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956':
        raise ValueError('Original ROM identity mismatch')
    output = bytearray(baseline)
    allowed = set(range(0x7fdc, 0x7fe0))
    def write(at, old, new):
        if len(old) != len(new) or baseline[at:at+len(old)] != old:
            raise AssertionError(f'Layout anchor changed at {at:#x}')
        output[at:at+len(new)] = new
        allowed.update(range(at, at+len(new)))
    for at, blob in ((WORD_STUB, spacing_stub(True)), (BYTE_STUB, spacing_stub(False)),
                     (WRAP_STUB, wrap_stub()), (0x2FE00, destination_stub())):
        if len(blob) > 0x80:
            raise AssertionError('Spacing code exceeds reserved span')
        write(at, b'\xff'*len(blob), blob)
    words = b''.join((16*((12+8*i)//8)).to_bytes(2,'little') for i in range(28))
    shifts = bytes((12+8*i)%8 for i in range(28))
    write(WORD_TABLE, b'\xff'*len(words), words)
    write(BYTE_TABLE, b'\xff'*len(shifts), shifts)
    write(0x28E0C, bytes.fromhex('BF709685'), bytes.fromhex('2280FB85'))
    write(0x290EE, bytes.fromhex('BF969685'), bytes.fromhex('2200FC85'))
    write(0x2841B, bytes.fromhex('AD9A1FC91300'), bytes.fromhex('2280FC85EAEA'))
    write(0x28335, bytes.fromhex('AD9A1FC91300'), bytes.fromhex('2280FC85EAEA'))
    write(0x291DF, bytes.fromhex('7F709685'), bytes.fromhex('2200FE85'))
    # This loader creates only the Quiz question portrait. Put its sprite
    # offscreen so long answer labels have the full paper width. Explanations
    # and other modes use their original portrait loaders.
    write(0x2FD00, b'\xff'*7, bytes.fromhex('A900018D94086B'))
    write(0x306BC, bytes.fromhex('B906008D9408'), bytes.fromhex('2200FD85EAEA'))
    # All three original answer tables, 50 entries each. Keep table ordering,
    # grading metadata and original JP source copies for the 81 moved choices.
    seen = set()
    for table in (0x31217, 0x3127f, 0x312e7):
        for slot in range(50):
            ptr = int.from_bytes(baseline[table+slot*2:table+slot*2+2], 'little')
            at = 0x30000 + ptr - 0x8000
            if at in seen:
                raise AssertionError('Answer tables contain duplicate allocation')
            seen.add(at)
            write(at, bytes.fromhex('0E060F12'), bytes.fromhex('0E040F12'))
    number_headers = (0x314CF,0x314DB,0x314E7,0x314F6,0x31500,0x3150A,
                      0x31517,0x31521,0x3152B)
    for at in number_headers:
        write(at, bytes.fromhex('0E04'), bytes.fromhex('0E02'))
    # The parent already names Maruko: retain the full daily allowance meaning
    # naturally in one line, with a left inset that stays inside the paper.
    at = 0x37f84
    old = baseline[at:at+66]
    if old[:10] != bytes.fromhex('0E000F0E202020202020') or old[60:63] != bytes.fromhex('816F00'):
        raise AssertionError('Allowance continuation layout changed')
    mapping = read_codepage(root)
    continuation = 'Mỗi ngày được mấy yên?'
    payload, _ = encode_full(continuation,mapping,0x320E8)
    record = bytes.fromhex('0E040F0E')+payload+bytes.fromhex('816F00')
    write(at, old, record+bytes(66-len(record)))
    # Leave a V2 space after each native 12px Kanji so its ink cannot collide
    # with the next glyph at the compact pitch. These are display spaces only.
    native_padding = 0
    for option in plan(root,clean)['slots']:
        text = option['source_full_vietnamese']
        if not any(ch in KANJI for ch in text):
            continue
        off = int(option['source_offset'],16)
        dst = int(option['experimental_dest_ROM'],16)
        padded = ''.join(ch+' ' if ch in KANJI else ch for ch in text)
        payload, count = encode_full(padded,mapping,off)
        native_padding += count
        record = bytes.fromhex('0E040F12')+payload+bytes.fromhex('816F00')
        if len(record)>66:
            raise AssertionError('Padded native Kanji exceeds the answer copy')
        write(dst,baseline[dst:dst+66],record+bytes(66-len(record)))
    # Restore the age-nine fact with a new complete two-line main question in
    # the FF gap freed by moving G0. The caller reads this bank06 record
    # directly; the 66-byte answer-copy limit does not apply to questions.
    pointer_at = 0x31147+18*2
    old_ptr = int.from_bytes(baseline[pointer_at:pointer_at+2],'little')
    if old_ptr != int.from_bytes(clean[pointer_at:pointer_at+2],'little'):
        raise AssertionError('Age-nine question pointer already changed')
    original_at = 0x30000+old_ptr-0x8000
    if original_at != 0x31F1F or clean[0x31F33:0x31F33+8] != '９才にな'.encode('cp932'):
        raise AssertionError('Age-nine source identity changed')
    age_lines = ('Maruko cung Kim Ngưu,','lên 9 tuổi ngày nào?')
    first,_ = encode_full(age_lines[0],mapping,0x31F33)
    second,_ = encode_full(age_lines[1],mapping,0x31F33)
    record = (bytes.fromhex('0E040F0A')+first+bytes.fromhex('816F')+
              bytes.fromhex('8440')*4+second+bytes.fromhex('816F00'))
    if len(record)>0x36A00-0x36907:
        raise AssertionError('Age question exceeds the freed title gap')
    write(0x36907,b'\xff'*len(record),record)
    write(pointer_at,baseline[pointer_at:pointer_at+2],bytes.fromhex('07E9'))
    for table in (0x31217,0x3127f,0x312e7):
        if output[table:table+100]!=baseline[table:table+100]:
            raise AssertionError('Layout changed answer pointer ordering')
    if output[0x310df:0x31147]!=baseline[0x310df:0x31147]:
        raise AssertionError('Layout changed Quiz grading metadata pointers')
    output[0x7fdc:0x7fe0] = bytes(4)
    checksum = (sum(output)+0x1fe)&0xffff
    output[0x7fdc:0x7fde] = (checksum^0xffff).to_bytes(2,'little')
    output[0x7fde:0x7fe0] = checksum.to_bytes(2,'little')
    if any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(baseline,output))):
        raise AssertionError('Unexpected byte mutation outside Quiz layout')
    ips, records = make_ips(clean, output)
    if apply_ips(clean,ips) != bytes(output):
        raise AssertionError('Layout IPS replay failed')
    return ips, {
        'status':'QUIZ_LAYOUT_BINARY_PASS_REQUIRES_RUNTIME_QA',
        'candidate_ROM_sha256':hashlib.sha256(output).hexdigest(),
        'cumulative_IPS_sha256':hashlib.sha256(ips).hexdigest(),
        'cumulative_IPS_bytes':len(ips), 'cumulative_IPS_records':records,
        'checksum':hex(checksum), 'answer_headers_adjusted':len(seen),
        'source_bank_selector':'bank06 or bank7E answer buffer $8000..$808F',
        'quiz_pitch_pixels':8, 'quiz_wrap_columns':28,
        'native_Kanji_display_padding_added':native_padding,
        'allowance_question_continuation':continuation,
        'age_nine_question_lines':age_lines,
        'original_font_bitmaps_changed':False,
        'question_portrait_hidden_for_answer_legibility':True,
        'emulator_acceptance_passed':False,
    }
