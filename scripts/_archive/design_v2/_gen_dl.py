"""Render Design Locked V2.0."""
from PIL import Image, ImageDraw, ImageFont
import os, math

OUT = r"D:\today\docs\audit\_mockups"

def load_font(size_pt, bold=False, serif=False):
    size_px = max(8, int(size_pt * 1.5))
    cs = []
    if serif:
        cs += [("C:/Windows/Fonts/georgia.ttf","C:/Windows/Fonts/georgiab.ttf")]
    cs += [("C:/Windows/Fonts/segoeui.ttf","C:/Windows/Fonts/segoeuib.ttf"),
           ("C:/Windows/Fonts/arial.ttf","C:/Windows/Fonts/arialbd.ttf"),
           ("C:/Windows/Fonts/msyh.ttc","C:/Windows/Fonts/msyhbd.ttc")]
    for p1,p2 in cs:
        try: return ImageFont.truetype(p2 if (bold and p2) else p1, size_px)
        except: continue
    return ImageFont.load_default()

def center(d,x,y,t,f,c="#1A1B1E"):
    b=f.getbbox(t); tw=b[2]-b[0]; d.text((x-tw/2,y),t,fill=c,font=f)
def right(d,x,y,t,f,c="#1A1B1E"):
    b=f.getbbox(t); tw=b[2]-b[0]; d.text((x-tw,y),t,fill=c,font=f)
def left(d,x,y,t,f,c="#1A1B1E"):
    d.text((x,y),t,fill=c,font=f)

def draw_luoshu(d, cx, cy, scale, highlight=5):
    pos = {4:(-80,-80),9:(0,-80),2:(80,-80),3:(-80,0),5:(0,0),7:(80,0),8:(-80,80),1:(0,80),6:(80,80)}
    for n,(x,y) in pos.items():
        px=cx+x*scale; py=cy+y*scale; r=6*scale
        if n==highlight:
            d.ellipse([px-r,py-r,px+r,py+r], fill="#1A1B1E")
        else:
            d.ellipse([px-r,py-r,px+r,py+r], fill="#F2EFE6", outline="#A9A398", width=1)

def draw_hex(d, cx, cy, lines, scale=1.0):
    width=64*scale; lh=2*scale; gap=8*scale; th=6*lh+5*gap; top=cy-th/2
    for i,ln in enumerate(lines):
        y=top+(5-i)*(lh+gap)
        if ln=="yang":
            d.rectangle([cx-width/2,y,cx+width/2,y+lh], fill="#1A1B1E")
        else:
            sw=(width-gap)/2
            d.rectangle([cx-width/2,y,cx-width/2+sw,y+lh], fill="#1A1B1E")
            d.rectangle([cx+width/2-sw,y,cx+width/2,y+lh], fill="#1A1B1E")

# Sheet 1
def sheet1():
    W,H=1100,800
    img=Image.new("RGB",(W,H),"#F8F5EE"); d=ImageDraw.Draw(img)
    center(d,W//2,40,"Shuntian V2.0 . Design System",load_font(28,False,serif=True))
    center(d,W//2,78,"Luoshu . Hexagram . Hetu . Minimalist",load_font(12,True),"#6E6A5F")
    y=130
    left(d,60,y,"1. COLOR PALETTE",load_font(11,True),"#6E6A5F")
    swatches=[("--bg","#F2EFE6","Cream Paper"),("--bg-elev","#F8F5EE","Card Surface"),
              ("--ink","#1A1B1E","Primary Text"),("--ink-soft","#6E6A5F","Secondary"),
              ("--ink-mute","#96937F","Muted"),("--line","#E3DFD2","Divider"),
              ("--accent","#A34A38","Vermillion")]
    sw=130
    for i,(nm,hx,ds) in enumerate(swatches):
        x=60+i*sw
        d.rounded_rectangle([x,y+20,x+110,y+130],6,fill=hx,outline="#A9A398",width=1)
        left(d,x,y+138,nm,load_font(8,True))
        left(d,x,y+152,hx,load_font(7,False),"#6E6A5F")
        left(d,x,y+168,ds,load_font(7,False),"#96937F")
    y=320
    left(d,60,y,"2. TYPOGRAPHY",load_font(11,True),"#6E6A5F")
    y+=24
    samples=[("Display 36pt Oranienbaum","Clarity . Small things grow"),
             ("Body 15pt Oranienbaum","Move with clarity, not urgency."),
             ("Eyebrow 9pt MiSans UPPERCASE","TODAY'S HEXAGRAM"),
             ("Label 11pt MiSans","Move with clarity, not urgency.")]
    for lb,t in samples:
        left(d,60,y,lb,load_font(9,True),"#96937F")
        left(d,280,y,t,load_font(15,False,serif=True),"#1A1B1E")
        y+=50
    y=570
    left(d,60,y,"3. CORE MOTIFS",load_font(11,True),"#6E6A5F"); y+=30
    center(d,180,y+70,"LuoshuMandala",load_font(11,True),"#1A1B1E")
    center(d,180,y+88,"Luoshu 9 palaces",load_font(8,False),"#6E6A5F")
    draw_luoshu(d,180,y+175,scale=0.4)
    center(d,550,y+70,"HexagramMark",load_font(11,True),"#1A1B1E")
    center(d,550,y+88,"6-yao (T-ai #11)",load_font(8,False),"#6E6A5F")
    draw_hex(d,550,y+175,["yang","yang","yin","yin","yang","yang"],scale=0.7)
    center(d,920,y+70,"HetuSpiral",load_font(11,True),"#1A1B1E")
    center(d,920,y+88,"5 rings + 20 dots",load_font(8,False),"#6E6A5F")
    for r in (60,48,36,24,12):
        d.ellipse([920-r,y+175-r,920+r,y+175+r],outline="#1A1B1E",width=1)
    for x,y2 in [(920,y+175-24),(920+24,y+175),(920,y+175+24),(920-24,y+175)]:
        d.ellipse([x-3,y2-3,x+3,y2+3],fill="#1A1B1E")
    right(d,W-60,770,"2026-08-22 . DESIGN LOCKED v2.0",load_font(9,True),"#96937F")
    img.save(f"{OUT}/DESIGN_LOCKED_V2_1_system.png","PNG")
    print("saved 1")

# Sheet 2
def sheet2():
    W,H=1500,800
    img=Image.new("RGB",(W,H),"#F8F5EE"); d=ImageDraw.Draw(img)
    center(d,W//2,40,"Today Hero . 5.5s State Flow",load_font(28,False,serif=True))
    center(d,W//2,78,"Hetu . Hexagram Transition / 4 stages",load_font(12,True),"#6E6A5F")
    pw,ph=280,580
    states=[("P0 Silent (0-0.5s)",0.5),("P1 Hetu (0.5-1.9s)",1.7),
            ("P2 Hex (3.0-4.2s)",3.6),("P4 Done (5.5s)",5.5)]
    for i,(label,t) in enumerate(states):
        x0=60+i*360
        d.rounded_rectangle([x0,130,x0+pw,130+ph],24,fill="#F2EFE6",outline="#E3DFD2",width=1)
        left(d,x0,100,label,load_font(11,True),"#1A1B1E")
        left(d,x0,116,f"t={t}s",load_font(9,False),"#96937F")
        cy=130+60; cx=x0+pw//2
        if t<1.0:
            for dx,col in [(-12,"#A9A398"),(0,"#6E6A5F"),(12,"#A9A398")]:
                d.ellipse([cx+dx-4,cy-4,cx+dx+4,cy+4],fill=col)
        elif t<2.0:
            for r in (90,70,50,30):
                d.ellipse([cx-r,cy-r,cx+r,cy+r],outline="#1A1B1E",width=1)
            for ang in range(0,360,30):
                rad=math.radians(ang); r_dot=30 if ang<180 else 50
                xd=cx+r_dot*math.cos(rad); yd=cy+r_dot*math.sin(rad)
                if 30<ang<150 or 210<ang<330:
                    d.ellipse([xd-2.5,yd-2.5,xd+2.5,yd+2.5],fill="#1A1B1E")
                else:
                    d.ellipse([xd-2.5,yd-2.5,xd+2.5,yd+2.5],fill="#F2EFE6",outline="#A9A398",width=1)
        elif t<4.5:
            draw_hex(d,cx,cy-20,["yang","yang","yin","yin","yang","yang"],scale=0.65)
            center(d,cx,cy+50,"Clarity",load_font(28,False,serif=True))
        else:
            draw_hex(d,cx,cy-60,["yang","yang","yin","yin","yang","yang"],scale=0.55)
            center(d,cx,cy-18,"Clarity",load_font(24,False,serif=True))
            center(d,cx,cy+16,"Move with clarity, not urgency.",load_font(11,False,serif=True),"#6E6A5F")
            center(d,cx,cy+36,"Clarity about doing what truly matters.",load_font(10,False),"#96937F")
    right(d,W-60,770,"5.5s . 4 stages . DESIGN LOCKED v2.0",load_font(9,True),"#96937F")
    img.save(f"{OUT}/DESIGN_LOCKED_V2_2_hero_states.png","PNG")
    print("saved 2")

# Sheet 3
def sheet3():
    W,H=1500,800
    img=Image.new("RGB",(W,H),"#F8F5EE"); d=ImageDraw.Draw(img)
    center(d,W//2,40,"App . 4 Key Screens",load_font(28,False,serif=True))
    center(d,W//2,78,"5-tab SPA . Minimalist . Bottom Nav",load_font(12,True),"#6E6A5F")
    pw,ph=280,580
    screens=[("Today","Today"),("Calendar","Calendar"),
             ("Personal","Personal"),("Settings","Settings")]
    for i,(title,view) in enumerate(screens):
        x0=60+i*360
        d.rounded_rectangle([x0,130,x0+pw,130+ph],24,fill="#F2EFE6",outline="#E3DFD2",width=1)
        left(d,x0,100,title,load_font(11,True),"#1A1B1E")
        cy=130+40
        left(d,x0+20,cy+6,"*",load_font(14),"#6E6A5F")
        d.rounded_rectangle([x0+60,cy,x0+86,cy+26],3,fill="#A34A38")
        left(d,x0+67,cy+6,"T",load_font(11,True),"#FDF6E8")
        left(d,x0+100,cy+4,"TONGSHU",load_font(10,True),"#1A1B1E")
        left(d,x0+100,cy+16,"Sheng Huo Tong Shu",load_font(7,False),"#6E6A5F")
        d.rounded_rectangle([x0+pw-70,cy,x0+pw-16,cy+20],7,outline="#A9A398",width=1)
        left(d,x0+pw-60,cy+4,"CN BJ",load_font(8,False),"#1A1B1E")
        if i==0:
            draw_luoshu(d,x0+pw//2,130+220,scale=0.4)
            center(d,x0+pw//2,130+320,"TODAYS HEXAGRAM",load_font(8,True),"#96937F")
            center(d,x0+pw//2,130+350,"Clarity",load_font(24,False,serif=True))
            draw_hex(d,x0+80,130+410,["yang","yang","yin","yin","yang","yang"],scale=0.5)
            left(d,x0+130,130+405,"T-ai",load_font(11,True))
            left(d,x0+130,130+425,"TAI . Peace",load_font(9,True),"#6E6A5F")
        elif i==1:
            center(d,x0+pw//2,130+100,"AUGUST 2026",load_font(11,True),"#1A1B1E")
            cy2=130+140
            for row in range(5):
                for col in range(7):
                    xd=x0+30+col*32; yd=cy2+row*36; day=row*7+col+1
                    if day<=31:
                        if day==17:
                            d.ellipse([xd-12,yd-12,xd+12,yd+12],fill="#A34A38")
                            left(d,xd-5,yd-7,str(day),load_font(9,True),"#FDF6E8")
                        else:
                            left(d,xd-5,yd-7,str(day),load_font(9,False),"#1A1B1E")
            center(d,x0+pw//2,130+380,"Li Qiu - yin rises",load_font(9,False),"#6E6A5F")
        elif i==2:
            yp=130+100
            left(d,x0+20,yp,"BIRTH DATE",load_font(8,True),"#96937F")
            d.rounded_rectangle([x0+20,yp+12,x0+pw-20,yp+44],4,fill="#FAF9F5",outline="#A9A398",width=1)
            left(d,x0+30,yp+22,"1990 / 08 / 19",load_font(10,False),"#1A1B1E")
            yp+=60
            left(d,x0+20,yp,"BIRTH TIME",load_font(8,True),"#96937F")
            d.rounded_rectangle([x0+20,yp+12,x0+pw-20,yp+44],4,fill="#FAF9F5",outline="#A9A398",width=1)
            left(d,x0+30,yp+22,"16:00 (Shen)",load_font(10,False),"#1A1B1E")
            yp+=60
            left(d,x0+20,yp,"BIRTH PLACE",load_font(8,True),"#96937F")
            d.rounded_rectangle([x0+20,yp+12,x0+pw-20,yp+44],4,fill="#FAF9F5",outline="#A9A398",width=1)
            left(d,x0+30,yp+22,"Shanghai, China",load_font(10,False),"#1A1B1E")
            yp+=70
            d.rounded_rectangle([x0+20,yp,x0+pw-20,yp+38],19,fill="#1A1B1E")
            center(d,x0+pw//2,yp+11,"GENERATE TONG SHU",load_font(10,True),"#F2EFE6")
        else:
            settings=[("Country","CN"),("Region","Beijing"),
                       ("Language","Simplified Chinese"),
                       ("Day Boundary","Zi-shi swap (system)"),
                       ("Time Zone","Asia/Shanghai"),
                       ("True Solar","Auto (from birthplace)"),
                       ("Engine Ver","v1.0.0")]
            for j,(k,v) in enumerate(settings):
                ys=130+110+j*50
                left(d,x0+20,ys,k,load_font(10,False),"#1A1B1E")
                right(d,x0+pw-20,ys,v,load_font(10,False),"#6E6A5F")
                d.line([(x0+20,ys+16),(x0+pw-20,ys+16)],fill="#E3DFD2",width=1)
        tab_y=130+ph-60; tab_w=(pw-20)//5; tabs=["Today","Cal","You","Log","Set"]
        for j,tname in enumerate(tabs):
            tx=x0+10+j*tab_w; tcolor="#1A1B1E" if tname==tabs[i] else "#6E6A5F"
            if tname=="You":
                d.ellipse([tx+tab_w//2-14,tab_y-12,tx+tab_w//2+14,tab_y+16],fill="#A34A38")
                center(d,tx+tab_w//2,tab_y-3,"*",load_font(14,True),"#FDF6E8")
            else:
                center(d,tx+tab_w//2,tab_y,tname,load_font(8,False),tcolor)
    right(d,W-60,770,"5 tabs . convex center . DESIGN LOCKED v2.0",load_font(9,True),"#96937F")
    img.save(f"{OUT}/DESIGN_LOCKED_V2_3_screens.png","PNG")
    print("saved 3")

sheet1()
sheet2()
sheet3()
print("All done")
