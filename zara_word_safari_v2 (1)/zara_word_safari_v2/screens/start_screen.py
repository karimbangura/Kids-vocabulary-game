# ============================================
# screens/start_screen.py
# Animated start screen with 2D Zara
# NEW: Nickname input with on-screen keyboard
#      Voice greets child by name
# ============================================
import pygame
import math
from settings import *
from components.button   import Button
from components.confetti import Confetti
from components.animator import FloatAnim, PulseAnim


# ── On-screen keyboard rows ───────────────────
KB_ROWS = [
    ["Q","W","E","R","T","Y","U","I","O","P"],
    ["A","S","D","F","G","H","J","K","L"],
    ["Z","X","C","V","B","N","M","⌫"],
]


class StartScreen:

    def __init__(self, manager):
        self.manager = manager

        self.f_huge  = pygame.font.SysFont(
            "comicsansms", FONT_HUGE,  bold=True)
        self.f_large = pygame.font.SysFont(
            "comicsansms", FONT_LARGE, bold=True)
        self.f_med   = pygame.font.SysFont(
            "comicsansms", FONT_MEDIUM,bold=True)
        self.f_small = pygame.font.SysFont(
            "comicsansms", FONT_SMALL, bold=True)
        self.f_tiny  = pygame.font.SysFont(
            "comicsansms", FONT_TINY,  bold=True)
        self.f_emoji = pygame.font.SysFont(
            "segoeuiemoji", 50)
        self.f_kb    = pygame.font.SysFont(
            "comicsansms", 26, bold=True)
        self.f_name  = pygame.font.SysFont(
            "comicsansms", 52, bold=True)

        lang = getattr(manager, 'language', 'en')

        # ── State machine ─────────────────────
        # "title"  = main start screen
        # "name"   = nickname input overlay
        self.state   = "title"
        self.nickname = ""          # typed so far
        self.cursor_t = 0           # cursor blink
        self.name_done= False       # name confirmed

        # Welcome flash after name entered
        self.welcome_flash   = 0
        self.welcome_text    = ""
        self.welcome_scale   = 0.0
        self.welcome_rainbow = 0.0

        # Language button
        lbl = ("🇲🇾 MELAYU"
               if lang == "en"
               else "🇬🇧 ENGLISH")
        self.lang_btn = Button(
            x=10, y=10,
            width=200, height=56,
            text=lbl,
            font_size=22,
            color=SKY_BLUE,
            hover_color=SKY_DARK,
            text_color=WHITE)

        play_lbl = UI_TEXT[lang]["play"]
        self.play_btn = Button(
            x=SCREEN_WIDTH//2 - 160,
            y=600,
            width=320, height=110,
            text=f"🦁  {play_lbl}",
            font_size=52)

        # Name screen buttons
        self.ok_btn = Button(
            x=SCREEN_WIDTH//2 - 130,
            y=368,
            width=260, height=64,
            text="✅  LET'S GO!",
            font_size=30,
            color=CORRECT_GREEN,
            hover_color=(80,200,80),
            text_color=WHITE)

        # Build keyboard buttons
        self._build_keyboard()

        # Animations
        self.zara_float  = FloatAnim(
            base_y=200, amplitude=18, speed=0.04)
        self.title_pulse = PulseAnim(
            base=1.0, amplitude=0.04, speed=0.03)
        self.confetti    = Confetti(
            SCREEN_WIDTH, SCREEN_HEIGHT)
        self.confetti.trigger(80)

        self.stars = [
            {"x": x, "y": y, "s": s, "t": t}
            for x, y, s, t in [
                (100,100,20,0.0),(900,150,16,1.0),
                (200,600,14,2.0),(800,500,18,0.5),
                (500, 80,22,1.5),( 50,400,12,3.0),
                (950,600,16,2.5),
            ]
        ]
        self.zara_t   = 0.0
        self.tail_wag = 0.0

        manager.voice.say_welcome()

    # ── Build on-screen keyboard ──────────────
    def _build_keyboard(self):
        self.kb_buttons = []
        key_w = 72
        key_h = 58
        gap   = 8
        start_y = 450

        for row_i, row in enumerate(KB_ROWS):
            row_w = len(row) * key_w + (len(row)-1) * gap
            sx    = SCREEN_WIDTH//2 - row_w//2
            for col_i, ch in enumerate(row):
                bx = sx + col_i*(key_w+gap)
                by = start_y + row_i*(key_h+gap)
                w  = key_w*2 if ch == "⌫" else key_w
                col_btn = (WRONG_PINK
                           if ch == "⌫"
                           else CREAM_CARD)
                hov     = ((255,150,150)
                           if ch == "⌫"
                           else YELLOW_BTN)
                btn = Button(
                    x=bx, y=by,
                    width=w, height=key_h,
                    text=ch,
                    font_size=22,
                    color=col_btn,
                    hover_color=hov,
                    text_color=PURPLE_TEXT)
                self.kb_buttons.append(
                    (ch, btn))

    # ── Speak personalised welcome ────────────
    def _speak_welcome(self):
        lang = getattr(
            self.manager, 'language', 'en')
        name = self.nickname.strip() or "Explorer"
        if lang == "ms":
            phrases = [
                f"Selamat datang {name}! Jom main!",
                f"Hei {name}! Jom pergi safari!",
                f"Wah {name}! Jom belajar!",
            ]
        else:
            phrases = [
                f"Welcome {name}! Let's start learning!",
                f"Hey {name}! Get ready to play!",
                f"Woohoo {name}! Word Safari time! Let's go!",
                f"Hello {name}! Choose a game to begin!",
            ]
        import random
        self.manager.voice.speak(
            random.choice(phrases))

    # ── Events ───────────────────────────────
    def handle_event(self, event):
        lang = getattr(
            self.manager, 'language', 'en')

        if self.state == "title":
            # PLAY button → go to name entry
            if self.play_btn.is_clicked(event):
                self.manager.play_sfx("click")
                self.state    = "name"
                self.nickname = ""
                prompt = (
                    "Enter your nickname! "
                    "Type it and press Let's Go!"
                    if lang == "en"
                    else
                    "Masukkan nama panggilan kamu! "
                    "Taip dan tekan Jom Pergi!")
                self.manager.voice.speak(prompt)
                return

            # Language toggle
            if self.lang_btn.is_clicked(event):
                self.manager.play_sfx("click")
                if lang == "en":
                    self.manager.language = "ms"
                    self.manager.voice.set_language("ms")
                    self.lang_btn.text = "🇬🇧 ENGLISH"
                    self.play_btn.text = (
                        f"🦁  {UI_TEXT['ms']['play']}")
                else:
                    self.manager.language = "en"
                    self.manager.voice.set_language("en")
                    self.lang_btn.text = "🇲🇾 MELAYU"
                    self.play_btn.text = (
                        f"🦁  {UI_TEXT['en']['play']}")
                self.manager.voice.say_welcome()

        elif self.state == "name":
            # Language toggle works on name screen too
            if self.lang_btn.is_clicked(event):
                self.manager.play_sfx("click")
                if lang == "en":
                    self.manager.language = "ms"
                    self.manager.voice.set_language("ms")
                    self.lang_btn.text = "🇬🇧 ENGLISH"
                    self.play_btn.text = (
                        f"🦁  {UI_TEXT['ms']['play']}")
                else:
                    self.manager.language = "en"
                    self.manager.voice.set_language("en")
                    self.lang_btn.text = "🇲🇾 MELAYU"
                    self.play_btn.text = (
                        f"🦁  {UI_TEXT['en']['play']}")
                return

            # Physical keyboard typing
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.nickname = \
                        self.nickname[:-1]
                elif event.key == pygame.K_RETURN:
                    if self.nickname.strip():
                        self._confirm_name()
                elif (event.unicode.isalpha()
                      and len(self.nickname) < 12):
                    self.nickname += \
                        event.unicode.upper()

            # On-screen keyboard
            for ch, btn in self.kb_buttons:
                if btn.is_clicked(event):
                    self.manager.play_sfx("click")
                    if ch == "⌫":
                        self.nickname = \
                            self.nickname[:-1]
                    elif len(self.nickname) < 12:
                        self.nickname += ch

            # OK button
            if (self.ok_btn.is_clicked(event)
                    and self.nickname.strip()):
                self._confirm_name()

    def _confirm_name(self):
        # Save nickname to manager
        name = self.nickname.strip() or "Explorer"
        self.manager.player_name = name
        self.state         = "welcome_anim"
        # Use wall-clock time so the animation is
        # always 2 seconds regardless of frame rate
        self.welcome_end_ms  = pygame.time.get_ticks() + 2000
        self.welcome_scale   = 0.2
        self.welcome_rainbow = 0.0
        lang = getattr(
            self.manager, 'language', 'en')
        self.welcome_text = f"🦁 {name}!"
        self._speak_welcome()
        self.confetti.trigger(160)
        self.manager.play_sfx("star")

    # ── Update ───────────────────────────────
    def update(self):
        mouse = pygame.mouse.get_pos()
        self.cursor_t    += 1
        self.zara_t      += 0.03
        self.confetti.update()
        self.zara_float.update()
        self.title_pulse.update()

        if self.state == "title":
            self.play_btn.update(mouse)
            self.lang_btn.update(mouse)

        elif self.state == "name":
            for _, btn in self.kb_buttons:
                btn.update(mouse)
            self.lang_btn.update(mouse)
            if self.nickname.strip():
                self.ok_btn.update(mouse)

        elif self.state == "welcome_anim":
            self.welcome_rainbow += 0.15
            if self.welcome_scale < 1.1:
                self.welcome_scale = min(
                    1.1,
                    self.welcome_scale + 0.07)
            # Switch after exactly 2 seconds
            # regardless of frame rate
            if pygame.time.get_ticks() >= \
                    self.welcome_end_ms:
                self.manager.switch_screen(
                    "instructions")

    # ── Draw Zara ─────────────────────────────
    def _draw_zara(self, surface, cx, cy):
        t = self.zara_t
        self.tail_wag += 0.08
        tail_angle = math.sin(self.tail_wag)*30

        body_rect = pygame.Rect(
            cx-70, cy-20, 140, 110)
        pygame.draw.ellipse(
            surface,(255,180,40),body_rect)
        pygame.draw.ellipse(
            surface,(220,140,20),body_rect,3)
        pygame.draw.ellipse(
            surface,(255,210,120),
            (cx-40,cy+10,80,60))

        tail_x = cx+70; tail_y = cy+30
        tex = tail_x+50*math.cos(
            math.radians(tail_angle))
        tey = tail_y+30*math.sin(
            math.radians(tail_angle))
        pygame.draw.line(surface,(220,140,20),
            (tail_x,tail_y),(int(tex),int(tey)),8)
        pygame.draw.circle(surface,(180,100,10),
            (int(tex),int(tey)),10)

        pygame.draw.circle(
            surface,(255,180,40),(cx,cy-60),72)
        pygame.draw.circle(
            surface,(220,140,20),(cx,cy-60),72,3)
        mane_pts=[]
        for i in range(12):
            a=math.radians(i*30+t*20)
            r=78+math.sin(a*3+t)*6
            mane_pts.append((cx+r*math.cos(a),
                              cy-60+r*math.sin(a)))
        if len(mane_pts)>=3:
            pygame.draw.polygon(
                surface,(180,100,10),mane_pts)
        pygame.draw.circle(
            surface,(255,180,40),(cx,cy-60),68)
        for ex,ey,sign in [
                (cx-52,cy-118,-1),
                (cx+52,cy-118,1)]:
            pygame.draw.polygon(surface,
                (220,140,20),[(ex,ey),
                (ex+sign*22,ey-30),
                (ex+sign*42,ey-5)])
            pygame.draw.polygon(surface,PINK,
                [(ex+sign*5,ey-5),
                (ex+sign*22,ey-22),
                (ex+sign*35,ey-5)])
        eye_y=cy-70
        for ex in [cx-28,cx+28]:
            pygame.draw.ellipse(surface,WHITE,
                (ex-14,eye_y-12,28,24))
            pygame.draw.circle(
                surface,BLACK,(ex+2,eye_y),8)
            pygame.draw.circle(
                surface,WHITE,(ex+5,eye_y-3),3)
        pygame.draw.ellipse(surface,(180,80,80),
            (cx-16,cy-45,32,20))
        pygame.draw.arc(surface,(140,60,60),
            pygame.Rect(cx-25,cy-38,50,25),
            math.pi,0,3)
        for wy in [cy-42,cy-35]:
            pygame.draw.line(surface,(200,160,100),
                (cx-16,wy),(cx-50,wy-5),2)
            pygame.draw.line(surface,(200,160,100),
                (cx+16,wy),(cx+50,wy-5),2)
        wave=math.sin(t*3)*25
        px=cx+80; py=cy-10+int(wave)
        pygame.draw.line(surface,(255,180,40),
            (cx+65,cy+10),(px,py),14)
        pygame.draw.circle(
            surface,(255,200,80),(px,py),18)
        for tx,ty in [(-8,-10),(0,-13),(8,-10)]:
            pygame.draw.circle(surface,(255,200,80),
                (px+tx,py+ty),7)
        pygame.draw.line(surface,(255,180,40),
            (cx-65,cy+10),(cx-85,cy+20),14)
        pygame.draw.circle(surface,(255,200,80),
            (cx-85,cy+20),16)
        for fx in [cx-35,cx+35]:
            pygame.draw.ellipse(surface,(220,140,20),
                (fx-22,cy+80,44,22))

    def _draw_bg_stars(self, surface):
        for star in self.stars:
            star["t"] += 0.04
            alpha=(math.sin(star["t"])+1)/2
            s=int(star["s"]*(0.7+alpha*0.5))
            if s<4: continue
            f=pygame.font.SysFont("segoeuiemoji",s)
            img=f.render("⭐",True,ORANGE_STAR)
            surface.blit(img,(star["x"],star["y"]))

    RAINBOW = [
        (255,80,80),(255,160,40),(255,220,40),
        (80,210,80),(60,180,255),(180,80,255),
        (255,100,200),
    ]

    def _blit_scaled(self, surface, src,
                     cx, cy, scale):
        if scale<=0: return
        w=max(1,int(src.get_width()*scale))
        h=max(1,int(src.get_height()*scale))
        s=pygame.transform.smoothscale(src,(w,h))
        surface.blit(s,(cx-w//2,cy-h//2))

    # ── Draw ─────────────────────────────────
    def draw(self, surface):
        # Background gradient
        for y in range(SCREEN_HEIGHT):
            ratio=y/SCREEN_HEIGHT
            r=int(100+ratio*23)
            g=int(180+ratio*18)
            b=int(80 +ratio*46)
            pygame.draw.line(surface,(r,g,b),
                (0,y),(SCREEN_WIDTH,y))

        self._draw_bg_stars(surface)

        pygame.draw.ellipse(surface,DARK_GREEN,
            (-50,SCREEN_HEIGHT-80,
             SCREEN_WIDTH+100,160))
        deco=["🌴","🌿","🌺","🦋","🌸","🌴","🌿"]
        df=pygame.font.SysFont("segoeuiemoji",44)
        for i,ic in enumerate(deco):
            s=df.render(ic,True,WHITE)
            surface.blit(s,(i*150-10,
                            SCREEN_HEIGHT-75))

        # Title
        scale=self.title_pulse.scale
        for line,base_y in [
                ("WORD",35),("SAFARI! 🦁",115)]:
            surf=self.f_huge.render(
                line,True,PURPLE_TEXT)
            w=int(surf.get_width()*scale)
            h=int(surf.get_height()*scale)
            scaled=pygame.transform.scale(surf,(w,h))
            shad=self.f_huge.render(line,True,BLACK)
            shad_s=pygame.transform.scale(shad,(w,h))
            x=SCREEN_WIDTH//2-w//2
            surface.blit(shad_s,(x+4,base_y+4))
            surface.blit(scaled,(x,base_y))

        zy=self.zara_float.y
        self._draw_zara(
            surface,SCREEN_WIDTH//2,int(zy)+80)

        # ══ STATE: TITLE ═════════════════════
        if self.state == "title":
            self.play_btn.draw(surface)
            self.lang_btn.draw(surface)
            self.confetti.draw(surface)

        # ══ STATE: NAME INPUT ════════════════
        elif self.state == "name":
            lang = getattr(
                self.manager,'language','en')

            # Language button always visible
            self.lang_btn.draw(surface)

            # Dark overlay
            ov=pygame.Surface(
                (SCREEN_WIDTH,SCREEN_HEIGHT),
                pygame.SRCALPHA)
            ov.fill((0,0,0,160))
            surface.blit(ov,(0,0))

            # Input card
            card_w,card_h=640,290
            card_x=SCREEN_WIDTH//2-card_w//2
            card_y=60

            pygame.draw.rect(surface,WHITE,
                (card_x,card_y,card_w,card_h),
                border_radius=28)
            pygame.draw.rect(surface,YELLOW_BTN,
                (card_x,card_y,card_w,card_h),
                5,border_radius=28)

            # Prompt
            prompt=(
                "🦁  Enter your nickname!"
                if lang=="en"
                else "🦁  Masukkan nama panggilan kamu!")
            ps=self.f_small.render(
                prompt,True,PURPLE_TEXT)
            surface.blit(ps,
                (SCREEN_WIDTH//2
                 -ps.get_width()//2,
                 card_y+22))

            # Name input box
            box_w,box_h=420,72
            box_x=SCREEN_WIDTH//2-box_w//2
            box_y=card_y+80
            pygame.draw.rect(surface,
                (240,240,255),
                (box_x,box_y,box_w,box_h),
                border_radius=16)
            pygame.draw.rect(surface,
                PURPLE_TEXT,
                (box_x,box_y,box_w,box_h),
                3,border_radius=16)

            # Name text + cursor
            cursor=("|"
                    if self.cursor_t%60<30
                    else " ")
            display=(self.nickname+cursor
                     if len(self.nickname)<12
                     else self.nickname)
            ns=self.f_name.render(
                display,True,PURPLE_TEXT)
            surface.blit(ns,
                (SCREEN_WIDTH//2
                 -ns.get_width()//2,
                 box_y+10))

            # Char counter
            cc=self.f_tiny.render(
                f"{len(self.nickname)}/12",
                True,(160,160,160))
            surface.blit(cc,
                (box_x+box_w
                 -cc.get_width()-8,
                 box_y+box_h+4))

            # Hint
            hint=(
                "Enter any fun nickname to play!"
                if lang=="en"
                else "Masukkan nama panggilan untuk bermain!")
            hs=self.f_tiny.render(
                hint,True,(120,120,120))
            surface.blit(hs,
                (SCREEN_WIDTH//2
                 -hs.get_width()//2,
                 card_y+165))

            # OK button (only if name entered)
            if self.nickname.strip():
                ok_lbl=(
                    "✅  LET'S GO!"
                    if lang=="en"
                    else "✅  JOM PERGI!")
                self.ok_btn.text=ok_lbl
                self.ok_btn.draw(surface)

            # On-screen keyboard
            for _,btn in self.kb_buttons:
                btn.draw(surface)

        # ══ STATE: WELCOME ANIMATION ══════════
        elif self.state == "welcome_anim":
            self.confetti.draw(surface)

            # Big welcome card
            cx=SCREEN_WIDTH//2
            cy=SCREEN_HEIGHT//2

            ov=pygame.Surface(
                (SCREEN_WIDTH,SCREEN_HEIGHT),
                pygame.SRCALPHA)
            ov.fill((0,0,0,100))
            surface.blit(ov,(0,0))

            card_w,card_h=600,220
            cax=cx-card_w//2
            cay=cy-card_h//2-20

            ri0=int(self.welcome_rainbow*2) \
                % len(self.RAINBOW)
            ri1=(ri0+2)%len(self.RAINBOW)
            pygame.draw.rect(surface,
                self.RAINBOW[ri0],
                (cax,cay,card_w,card_h),
                border_radius=36)
            inner=pygame.Surface(
                (card_w-16,card_h-16),
                pygame.SRCALPHA)
            inner.fill((255,255,255,230))
            surface.blit(inner,(cax+8,cay+8))
            pygame.draw.rect(surface,
                self.RAINBOW[ri1],
                (cax,cay,card_w,card_h),
                6,border_radius=36)

            # Welcome text
            lang=getattr(
                self.manager,'language','en')
            w_top=(
                "WELCOME!"
                if lang=="en"
                else "SELAMAT DATANG!")
            wts=self.f_large.render(
                w_top,True,
                self.RAINBOW[ri0])
            self._blit_scaled(surface,wts,
                cx,cay+55,self.welcome_scale)

            # Name in big text
            ns=self.f_huge.render(
                self.welcome_text,True,
                PURPLE_TEXT)
            self._blit_scaled(surface,ns,
                cx,cay+130,self.welcome_scale)
