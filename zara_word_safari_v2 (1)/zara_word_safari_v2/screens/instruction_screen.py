# ============================================
# screens/instruction_screen.py
# Clear, fun instruction screen
# Shows all 4 minigames with icons
# Fast exciting audio — not slow/robotic
# Child navigates with big arrows or LET'S GO
# ============================================
import pygame
import math
import random
from settings import *
from components.button import Button


# ── One page per minigame ────────────────────
PAGES = [
    {
        "icon"    : "🔍",
        "color"   : (255, 140, 80),
        "en_title": "FIND THE WORD!",
        "ms_title": "CARI PERKATAAN!",
        "en_lines": ["Look at the picture!", "Tap the matching word!"],
        "ms_lines": ["Lihat gambar!", "Ketuk perkataan yang sepadan!"],
        "en_audio": "Look at the picture and tap the matching word!",
        "ms_audio": "Lihat gambar dan ketuk perkataan yang sepadan!",
        "demo_img" : "🐶",
        "demo_opts": ["CAT", "DOG", "SUN"],
        "demo_ans" : 1,
    },
    {
        "icon"    : "✏️",
        "color"   : (100, 180, 255),
        "en_title": "FILL THE BLANK!",
        "ms_title": "ISI TEMPAT KOSONG!",
        "en_lines": ["See the picture!", "Find the missing letter!"],
        "ms_lines": ["Lihat gambar!", "Cari huruf yang hilang!"],
        "en_audio": "Look at the picture and find the missing letter to complete the word!",
        "ms_audio": "Lihat gambar dan cari huruf yang hilang untuk lengkapkan perkataan!",
        "demo_img" : "🐱",
        "demo_word": "C_T",
        "demo_opts": ["A", "B", "E"],
        "demo_ans" : 0,
    },
    {
        "icon"    : "🎈",
        "color"   : (150, 220, 100),
        "en_title": "POP THE BALLOON!",
        "ms_title": "PECAHKAN BELON!",
        "en_lines": ["Listen to the word!", "Pop the right balloon!"],
        "ms_lines": ["Dengar perkataan!", "Pecahkan belon yang betul!"],
        "en_audio": "Listen to the word then pop the balloon that shows the right word!",
        "ms_audio": "Dengar perkataan kemudian pecahkan belon yang menunjukkan perkataan yang betul!",
        "demo_img" : "🎈",
        "demo_opts": ["BIRD", "FISH", "SUN"],
        "demo_ans" : 1,
    },
    {
        "icon"    : "🃏",
        "color"   : (220, 120, 255),
        "en_title": "MEMORY MATCH!",
        "ms_title": "PADANKAN KAD!",
        "en_lines": ["Flip the cards!", "Find the matching pairs!"],
        "ms_lines": ["Balikkan kad!", "Cari pasangan yang sama!"],
        "en_audio": "Flip the cards and find all the matching pairs. Remember where they are!",
        "ms_audio": "Balikkan kad dan cari semua pasangan yang sama. Ingat di mana mereka!",
        "demo_img" : "🃏",
        "demo_opts": ["🐶", "❓", "🐶"],
        "demo_ans" : -1,
    },
]

RAINBOW = [
    (255, 80,  80), (255,160,  40),
    (255,220,  40), ( 80,210,  80),
    ( 60,180, 255), (180, 80, 255),
]


class InstructionScreen:

    def __init__(self, manager):
        self.manager   = manager
        self.lang      = getattr(
            manager, 'language', 'en')

        self.page      = 0          # current page 0-3
        self.page_t    = 0.0        # animation timer
        self.slide_x   = float(SCREEN_WIDTH)  # slides in from right
        self.sliding   = True
        self.rainbow_t = 0.0
        self.star_t    = 0.0
        self.card_t    = 0.0

        # Demo animation
        self.demo_t    = 0
        self.demo_tap  = False
        self.demo_tap_t= 0

        # Floating stars
        self.stars = [
            {"x": random.randint(0, SCREEN_WIDTH),
             "y": random.randint(0, SCREEN_HEIGHT),
             "t": random.uniform(0, 6),
             "s": random.randint(16, 32)}
            for _ in range(8)
        ]

        # Fonts
        self.f_title  = pygame.font.SysFont(
            "comicsansms", 52, bold=True)
        self.f_sub    = pygame.font.SysFont(
            "comicsansms", FONT_SMALL, bold=True)
        self.f_small  = pygame.font.SysFont(
            "comicsansms", FONT_TINY, bold=True)
        self.f_icon   = pygame.font.SysFont(
            "segoeuiemoji", 110)
        self.f_icon_sm= pygame.font.SysFont(
            "segoeuiemoji", 56)
        self.f_icon_xs= pygame.font.SysFont(
            "segoeuiemoji", 38)
        self.f_demo   = pygame.font.SysFont(
            "comicsansms", 32, bold=True)
        self.f_demo_w = pygame.font.SysFont(
            "comicsansms", 44, bold=True)
        self.f_num    = pygame.font.SysFont(
            "comicsansms", FONT_HUGE, bold=True)

        # Navigation buttons
        self.next_btn = Button(
            x=SCREEN_WIDTH - 190, y=640,
            width=170, height=80,
            text="NEXT ▶",
            font_size=30,
            color=(80, 200, 100),
            hover_color=(60, 180, 80),
            text_color=WHITE)
        self.prev_btn = Button(
            x=20, y=640,
            width=170, height=80,
            text="◀ BACK",
            font_size=30,
            color=(150, 150, 200),
            hover_color=(120, 120, 180),
            text_color=WHITE)
        self.go_btn = Button(
            x=SCREEN_WIDTH // 2 - 180, y=640,
            width=360, height=80,
            text="🚀 LET'S PLAY!",
            font_size=38,
            color=YELLOW_BTN,
            hover_color=YELLOW_HOVER,
            text_color=PURPLE_TEXT)

        # Speak first page immediately
        self._speak_page()

    # ── Speak current page audio ──────────────
    def _speak_page(self):
        p    = PAGES[self.page]
        lang = getattr(self.manager, 'language', 'en')
        key  = "en_audio" if lang == "en" else "ms_audio"
        text = p[key]
        self.manager.voice.speak(text)

    # ── Events ───────────────────────────────
    def handle_event(self, event):
        mouse = pygame.mouse.get_pos()

        if self.next_btn.is_clicked(event):
            self.manager.play_sfx("click")
            if self.page < len(PAGES) - 1:
                self.page   += 1
                self.slide_x = float(SCREEN_WIDTH)
                self.sliding = True
                self.demo_t  = 0
                self.demo_tap= False
                self._speak_page()
            else:
                self._go_play()

        if self.page > 0 and \
                self.prev_btn.is_clicked(event):
            self.manager.play_sfx("click")
            self.page   -= 1
            self.slide_x = float(-SCREEN_WIDTH)
            self.sliding = True
            self.demo_t  = 0
            self.demo_tap= False
            self._speak_page()

        if self.page == len(PAGES) - 1 and \
                self.go_btn.is_clicked(event):
            self._go_play()

    def _go_play(self):
        lang = getattr(self.manager, 'language', 'en')
        # Play a sparkle welcome — not a correct-answer sound
        self.manager.play_sfx("star")
        self.manager.voice.speak(
            "Safari starting! Good luck explorer!"
            if lang == 'en'
            else "Safari bermula! Semoga berjaya penjelajah!")
        self.manager.switch_screen("game")

    # ── Update ───────────────────────────────
    def update(self):
        mouse = pygame.mouse.get_pos()
        self.page_t    += 0.05
        self.rainbow_t += 0.08
        self.star_t    += 0.03
        self.card_t    += 0.04
        self.demo_t    += 1

        # Slide animation — ease in
        if self.sliding:
            target = 0.0
            self.slide_x += (target
                             - self.slide_x) * 0.18
            if abs(self.slide_x - target) < 1:
                self.slide_x = target
                self.sliding  = False

        # Demo tap animation every 2.5 seconds
        if self.demo_t % 150 == 100:
            self.demo_tap  = True
            self.demo_tap_t= 0
        if self.demo_tap:
            self.demo_tap_t += 1
            if self.demo_tap_t > 30:
                self.demo_tap = False

        self.next_btn.update(mouse)
        self.prev_btn.update(mouse)
        self.go_btn.update(mouse)

    # ── Draw background ───────────────────────
    def _draw_bg(self, surface):
        # Gradient based on page colour
        col = PAGES[self.page]["color"]
        for y in range(SCREEN_HEIGHT):
            r = int(col[0]*0.3 + 180 * (1-y/SCREEN_HEIGHT))
            g = int(col[1]*0.3 + 220 * (1-y/SCREEN_HEIGHT))
            b = int(col[2]*0.3 + 255 * (1-y/SCREEN_HEIGHT))
            pygame.draw.line(
                surface,
                (max(0,min(255,r)),
                 max(0,min(255,g)),
                 max(0,min(255,b))),
                (0, y), (SCREEN_WIDTH, y))

        # Floating stars
        for s in self.stars:
            s["t"] += 0.04
            alpha = (math.sin(s["t"]) + 1) / 2
            sz    = int(s["s"] * (0.7 + alpha*0.4))
            if sz < 8:
                continue
            try:
                f   = pygame.font.SysFont(
                    "segoeuiemoji", sz)
                img = f.render("⭐", True, YELLOW_BTN)
                img.set_alpha(int(120 + alpha*100))
                surface.blit(img, (s["x"], s["y"]))
            except Exception:
                pass

    # ── Draw page dots ────────────────────────
    def _draw_dots(self, surface):
        total = len(PAGES)
        gap   = 28
        sx    = SCREEN_WIDTH//2 - (total*gap)//2
        for i in range(total):
            col = (YELLOW_BTN
                   if i == self.page
                   else (180,180,180))
            r   = 10 if i == self.page else 7
            pygame.draw.circle(
                surface, col,
                (sx + i*gap, 622), r)
            pygame.draw.circle(
                surface, WHITE,
                (sx + i*gap, 622), r, 2)

    # ── Draw demo for each page ───────────────
    def _draw_demo(self, surface, p, ox):
        """
        Small interactive demo showing how
        each game works — child sees it and
        instantly understands.
        """
        cx   = int(SCREEN_WIDTH//2 + ox)
        demo_y = 370

        if self.page == 0:
            # Show image + 3 word choices
            try:
                img_s = self.f_icon.render(
                    p["demo_img"], True, BLACK)
                # Image card
                pygame.draw.rect(
                    surface, WHITE,
                    (cx-65, demo_y-10, 130, 130),
                    border_radius=16)
                pygame.draw.rect(
                    surface, YELLOW_BTN,
                    (cx-65, demo_y-10, 130, 130),
                    4, border_radius=16)
                surface.blit(img_s,
                    (cx - img_s.get_width()//2,
                     demo_y))
            except Exception:
                pass

            # Word buttons
            opts  = p["demo_opts"]
            bw    = 110
            gap   = 12
            total = len(opts)*bw + (len(opts)-1)*gap
            sx0   = cx - total//2
            for i, opt in enumerate(opts):
                bx  = sx0 + i*(bw+gap)
                col = (CORRECT_GREEN
                       if (i == p["demo_ans"]
                           and self.demo_tap)
                       else CREAM_CARD)
                pygame.draw.rect(
                    surface, col,
                    (bx, demo_y+140, bw, 52),
                    border_radius=12)
                pygame.draw.rect(
                    surface, PURPLE_TEXT,
                    (bx, demo_y+140, bw, 52),
                    3, border_radius=12)
                ws = self.f_demo.render(
                    opt, True, PURPLE_TEXT)
                surface.blit(ws,
                    (bx + bw//2 - ws.get_width()//2,
                     demo_y+152))
                # Tap indicator
                if (i == p["demo_ans"]
                        and self.demo_tap):
                    ts = self.f_icon_xs.render(
                        "👆", True, BLACK)
                    surface.blit(ts,
                        (bx+bw//2-ts.get_width()//2,
                         demo_y+105))

        elif self.page == 1:
            # Show image + word with blank
            try:
                img_s = self.f_icon.render(
                    p["demo_img"], True, BLACK)
                pygame.draw.rect(
                    surface, WHITE,
                    (cx-65, demo_y-10, 130, 130),
                    border_radius=16)
                pygame.draw.rect(
                    surface, YELLOW_BTN,
                    (cx-65, demo_y-10, 130, 130),
                    4, border_radius=16)
                surface.blit(img_s,
                    (cx - img_s.get_width()//2,
                     demo_y))
            except Exception:
                pass

            # Word with blank
            word_s = self.f_demo_w.render(
                p.get("demo_word","C_T"),
                True, PURPLE_TEXT)
            pygame.draw.rect(
                surface, WHITE,
                (cx - word_s.get_width()//2 - 12,
                 demo_y+138,
                 word_s.get_width()+24, 48),
                border_radius=10)
            surface.blit(word_s,
                (cx - word_s.get_width()//2,
                 demo_y+142))

            # Letter tiles
            opts = p["demo_opts"]
            bw   = 70
            gap  = 10
            tot  = len(opts)*bw+(len(opts)-1)*gap
            sx0  = cx - tot//2
            for i, opt in enumerate(opts):
                bx  = sx0 + i*(bw+gap)
                col = (CORRECT_GREEN
                       if (i == p["demo_ans"]
                           and self.demo_tap)
                       else YELLOW_BTN)
                pygame.draw.rect(
                    surface, col,
                    (bx, demo_y+200, bw, bw),
                    border_radius=10)
                ls = self.f_demo_w.render(
                    opt, True, PURPLE_TEXT)
                surface.blit(ls,
                    (bx+bw//2-ls.get_width()//2,
                     bx+bw//2-ls.get_height()//2
                     +demo_y+200-bx+10))

        elif self.page == 2:
            # Balloons floating up
            balloon_cols = [
                (255,80,80),(100,180,255),
                (150,255,100)]
            opts = p["demo_opts"]
            bw   = 90
            gap  = 20
            tot  = len(opts)*bw+(len(opts)-1)*gap
            sx0  = cx - tot//2
            for i, opt in enumerate(opts):
                bx  = sx0 + i*(bw+gap)
                bob = int(math.sin(
                    self.card_t + i*1.2)*8)
                by  = demo_y + 30 + bob
                col = balloon_cols[
                    i % len(balloon_cols)]
                # Glow on correct
                if i == p["demo_ans"] and \
                        self.demo_tap:
                    pygame.draw.circle(
                        surface,
                        (255,255,100),
                        (bx+bw//2, by+bw//2),
                        bw//2+12)
                pygame.draw.circle(
                    surface, col,
                    (bx+bw//2, by+bw//2), bw//2)
                pygame.draw.circle(
                    surface, WHITE,
                    (bx+bw//4, by+bw//4),
                    bw//6)
                ws = self.f_small.render(
                    opt, True, WHITE)
                surface.blit(ws,
                    (bx+bw//2-ws.get_width()//2,
                     by+bw//2-ws.get_height()//2))
                if i == p["demo_ans"] and \
                        self.demo_tap:
                    ts = self.f_icon_xs.render(
                        "👆", True, BLACK)
                    surface.blit(ts,
                        (bx+bw//2-ts.get_width()//2,
                         by-38))

        elif self.page == 3:
            # Memory cards — 3 face down, 1 flipped
            card_data = [
                ("❓", False),
                ("🐶", True),
                ("❓", False),
                ("🐶",
                 self.demo_tap),
            ]
            cw, ch = 90, 90
            gap    = 10
            tot    = 4*cw + 3*gap
            sx0    = cx - tot//2
            for i, (emoji, flipped) in \
                    enumerate(card_data):
                bx  = sx0 + i*(cw+gap)
                by  = demo_y + 30
                col = (CREAM_CARD
                       if flipped
                       else SKY_BLUE)
                pygame.draw.rect(
                    surface, col,
                    (bx, by, cw, ch),
                    border_radius=12)
                pygame.draw.rect(
                    surface, PURPLE_TEXT,
                    (bx, by, cw, ch),
                    3, border_radius=12)
                if flipped:
                    try:
                        es = self.f_icon_sm.render(
                            emoji, True, BLACK)
                        surface.blit(es,
                            (bx+cw//2
                             -es.get_width()//2,
                             by+ch//2
                             -es.get_height()//2))
                    except Exception:
                        pass

    # ── Draw main page card ───────────────────
    def _draw_page_card(self, surface, ox):
        p    = PAGES[self.page]
        lang = getattr(
            self.manager, 'language', 'en')
        col  = p["color"]

        card_w = 760
        card_h = 500
        card_x = int(SCREEN_WIDTH//2
                     - card_w//2 + ox)
        card_y = 95

        # Shadow
        sh = pygame.Surface(
            (card_w+10, card_h+10),
            pygame.SRCALPHA)
        pygame.draw.rect(
            sh, (0,0,0,60),
            (0,0,card_w+10,card_h+10),
            border_radius=36)
        surface.blit(sh, (card_x+4, card_y+8))

        # Card body
        pygame.draw.rect(
            surface, WHITE,
            (card_x, card_y, card_w, card_h),
            border_radius=32)

        # Colour header strip
        pygame.draw.rect(
            surface, col,
            (card_x, card_y, card_w, 90),
            border_radius=32)
        pygame.draw.rect(
            surface, col,
            (card_x, card_y+60, card_w, 30))

        # Card border
        pygame.draw.rect(
            surface, col,
            (card_x, card_y, card_w, card_h),
            5, border_radius=32)

        # Page number badge
        ri  = int(self.rainbow_t*3) % len(RAINBOW)
        pygame.draw.circle(
            surface, RAINBOW[ri],
            (card_x+50, card_y+45), 28)
        num_s = self.f_sub.render(
            str(self.page+1), True, WHITE)
        surface.blit(num_s,
            (card_x+50-num_s.get_width()//2,
             card_y+45-num_s.get_height()//2))

        # Icon
        try:
            icon_s = self.f_icon.render(
                p["icon"], True, WHITE)
            bob = int(6*math.sin(
                self.page_t))
            surface.blit(icon_s,
                (SCREEN_WIDTH//2
                 - icon_s.get_width()//2
                 + int(ox),
                 card_y + 5 + bob))
        except Exception:
            pass

        # Title
        title_key = ("ms_title"
                     if lang == "ms"
                     else "en_title")
        title_s = self.f_title.render(
            p[title_key], True, WHITE)
        surface.blit(title_s,
            (SCREEN_WIDTH//2
             - title_s.get_width()//2
             + int(ox),
             card_y + 100))

        # Instruction lines
        lines_key = ("ms_lines"
                     if lang == "ms"
                     else "en_lines")
        for i, line in enumerate(p[lines_key]):
            prefix = "👉 "
            ls = self.f_sub.render(
                prefix + line,
                True, PURPLE_TEXT)
            surface.blit(ls,
                (SCREEN_WIDTH//2
                 - ls.get_width()//2
                 + int(ox),
                 card_y + 155 + i*42))

        # Demo area
        self._draw_demo(surface, p, ox)

    # ── Draw ─────────────────────────────────
    def draw(self, surface):
        self._draw_bg(surface)

        # Main card with slide offset
        self._draw_page_card(surface, self.slide_x)

        # Page indicator dots
        self._draw_dots(surface)

        # Navigation buttons
        lang = getattr(
            self.manager, 'language', 'en')
        if self.page < len(PAGES) - 1:
            # Next button
            nxt = ("SETERUSNYA ▶"
                   if lang == "ms"
                   else "NEXT ▶")
            self.next_btn.text = nxt
            self.next_btn.draw(surface)
        else:
            # Last page — big GO button
            go = ("🚀 JOM MAIN!"
                  if lang == "ms"
                  else "🚀 LET'S PLAY!")
            self.go_btn.text = go
            self.go_btn.draw(surface)

        if self.page > 0:
            bk = ("◀ KEMBALI"
                  if lang == "ms"
                  else "◀ BACK")
            self.prev_btn.text = bk
            self.prev_btn.draw(surface)

        # Top hint
        hint = ("Ketuk SETERUSNYA untuk teruskan!"
                if lang == "ms"
                else "Tap NEXT to see each game!")
        hs = self.f_small.render(
            hint, True, PURPLE_TEXT)
        surface.blit(hs,
            (SCREEN_WIDTH//2
             - hs.get_width()//2, 68))
