"""ROM/font-independent source-context selector shared by109 and later hooks."""
def rules_selector(a,stage=False):
 a.emit(0xAF,0x86,0x1F,0,0x29,0x7F,0)
 for bank in (3,6):a.cmp16(bank);a.branch(0xF0,'quiz')
 a.cmp16(5);a.branch(0xF0,'bank5')
 a.cmp16(0x7e);a.branch(0xD0,'native');a.emit(0xAF,0x94,0x1F,0)
 a.cmp16(0x8000);a.branch(0x90,'native');a.cmp16(0x8090);a.branch(0x90,'quiz');a.branch(0x80,'native')
 a.label('bank5');a.emit(0xAF,0x94,0x1F,0)
 for lo,hi,label in [(0x88be,0x8a90,'lyrics1'),(0xb37a,0xb80a,'fortune'),(0xbd24,0xcd74 if stage else 0xcb9b,'lyrics2'),(0xf272,0xf800,'rules'),(0xf821,0xfa00,'relocated')]:
  a.cmp16(lo);a.branch(0x90,label);a.cmp16(hi);a.branch(0x90,'quiz');a.label(label)
 a.cmp16(0xff20);a.branch(0x90,'native');a.cmp16(0xffa0);a.branch(0x90,'quiz')
