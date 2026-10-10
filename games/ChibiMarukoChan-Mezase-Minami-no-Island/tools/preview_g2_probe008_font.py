#!/usr/bin/env python3
"""Offline glyph preview, NOT an emulator screenshot. Pillow needed only here."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from generate_g2_probe008_font import ROOT,FAMILIES,SAMPLES,generate

def main():
    data=generate();out=ROOT/'docs/previews/probe008';out.mkdir(parents=True,exist_ok=True)
    label=ImageFont.truetype('DejaVuSans.ttf',16)
    small=ImageFont.truetype('DejaVuSans.ttf',12)
    def tile(ch,scale=5):
        bits=f"{int(data[ch]['bitmap_hex'],16):0144b}"
        im=Image.new('RGB',(12,12),'#fff7e0');im.putdata([(31,38,47) if b=='1' else (255,247,224) for b in bits])
        return im.resize((12*scale,12*scale),Image.Resampling.NEAREST)
    def sheet(rows,name):
        im=Image.new('RGB',(1050,64+len(rows)*100),'#e7ecef');d=ImageDraw.Draw(im)
        d.text((18,12),'PROBE 008 | original 12 x 12 pixels | offline preview, not runtime',font=label,fill='#132330')
        for y,row in enumerate(rows):
            for x,ch in enumerate(row):
                px=18+x*80;py=52+y*100
                d.text((px,py),ch,font=label,fill='#132330');im.paste(tile(ch),(px,py+24))
        im.save(out/name)
    sheet(FAMILIES,'vietnamese-families.png')
    sheet(['ảẳẩẻểỉỏổởủửỷ','ãẵẫẽễĩõỗỡũữỹ','ơớờởỡợ','ưứừửữự'],'tone-horn-review.png')
    chars=list(data)
    sheet([chars[i:i+12] for i in range(0,len(chars),12)],'full-codepage.png')
    im=Image.new('RGB',(1050,700),'#e7ecef');d=ImageDraw.Draw(im)
    d.text((18,12),'Actual dialogue strings | 1x and 4x | offline cell layout',font=label,fill='#132330')
    for y,s in enumerate(SAMPLES):
        py=52+y*125;d.text((18,py),s,font=label,fill='#132330')
        for x,ch in enumerate(s):
            im.paste(tile(ch,1),(18+x*12,py+28));im.paste(tile(ch,4),(18+x*48,py+48))
    d.text((18,680),'Cell advance 12 px is a preview assumption; in-game spacing still needs verification.',font=small,fill='#132330')
    im.save(out/'dialogue-samples.png')
    print(out)
if __name__=='__main__':main()
