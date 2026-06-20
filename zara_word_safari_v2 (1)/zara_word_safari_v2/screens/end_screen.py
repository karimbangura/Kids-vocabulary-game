# ============================================
# screens/end_screen.py
# Final reward screen — NICKNAME EDITION
# Nickname is the star of the show!
# Disco name banner, personalised voice,
# score card with nickname, dancing Zara
# ============================================
import pygame
import math
import random
import os
from settings import *
from components.button   import Button
from components.confetti import Confetti
from leaderboard         import save_score, load_top


RAINBOW = [
    (255,  80,  80), (255, 160,  40),
    (255, 220,  40), ( 80, 210,  80),
    ( 60, 180, 255), (180,  80, 255),
    (255, 100, 200),
]


class EndScreen:

    TIERS = [
        (16, "👑", "SAFARI CROWN!",   (255,215,  0), "MAHKOTA SAFARI!"),
        (11, "🥇", "AMAZING!",        (255,215,  0), "HEBAT!"),
        ( 6, "🥈", "WELL DONE!",      (192,192,192), "SYABAS!"),
        ( 0, "🥉", "GOOD TRY!",       (205,127, 50), "CUBA LAGI!"),
    ]

    def __init__(self, manager):
        self.manager  = manager
        lang          = getattr(manager, 'language', 'en')
        self.nickname = getattr(
            manager, 'player_name', 'Explorer')

        # Scores
        self.stars    = manager.stars
        self.correct  = getattr(manager, 'score_correct',  0)
        self.wrong    = getattr(manager, 'score_wrong',    0)
        self.accuracy = getattr(manager, 'score_accuracy', 0)
        self.streak   = getattr(manager, 'score_streak',   0)

        # Fonts
        self.f_huge   = pygame.font.SysFont(
            "comicsansms", FONT_HUGE,   bold=True)
        self.f_large  = pygame.font.SysFont(
            "comicsansms", FONT_LARGE,  bold=True)
        self.f_med    = pygame.font.SysFont(
            "comicsansms", FONT_MEDIUM, bold=True)
        self.f_small  = pygame.font.SysFont(
            "comicsansms", FONT_SMALL,  bold=True)
        self.f_tiny   = pygame.font.SysFont(
            "comicsansms", FONT_TINY,   bold=True)
        self.f_name   = pygame.font.SysFont(
            "comicsansms", 88,          bold=True)
        self.f_score  = pygame.font.SysFont(
            "comicsansms", 28,          bold=True)
        self.f_emoji  = pygame.font.SysFont(
            "segoeuiemoji", 44)
        self.f_disco  = pygame.font.SysFont(
            "comicsansms", 72,          bold=True)
        self.f_lb     = pygame.font.SysFont(
            "comicsansms", 19,          bold=True)

        # Buttons
        pa_txt = UI_TEXT[lang]["play_again"]
        q_txt  = UI_TEXT[lang]["quit"]
        self.play_btn = Button(
            x=SCREEN_WIDTH//2 - 280, y=638,
            width=250, height=70,
            text=f"🔄 {pa_txt}", font_size=26)
        self.quit_btn = Button(
            x=SCREEN_WIDTH//2 + 30,  y=638,
            width=250, height=70,
            text=f"👋 {q_txt}", font_size=26,
            color=WRONG_PINK,
            hover_color=(255,120,120),
            text_color=WHITE)

        # Confetti — massive burst
        self.confetti = Confetti(
            SCREEN_WIDTH, SCREEN_HEIGHT)
        self.confetti.trigger(300)

        # Save this run and load updated leaderboard
        self.lb_entries = save_score(
            self.nickname, self.stars,
            self.accuracy, self.streak)

        # Trophy tier
        self.trophy_emoji = "🥉"
        self.trophy_msg   = "GOOD TRY!"
        self.trophy_col   = (205,127,50)
        for thresh, emoji, msg_en, col, msg_ms \
                in self.TIERS:
            if self.stars >= thresh:
                self.trophy_emoji = emoji
                self.trophy_msg   = (
                    msg_ms if lang=="ms" else msg_en)
                self.trophy_col   = col
                break

        # AI weak words
        summary    = manager.ai.get_summary()
        self.weak  = summary["weak_words"][:3]

        # Animation state
        self.t          = 0.0        # master timer
        self.rainbow_t  = 0.0
        self.zara_t     = 0.0
        self.zara_x     = float(SCREEN_WIDTH//2)
        self.zara_dx    = 2.5
        self.trophy_sc  = 0.05
        self.card_sc    = 0.05
        self.name_sc    = 0.0        # name banner scale-in
        self.name_bounce= 0.0

        # Disco letter colours cycle per frame
        self.disco_cols  = [
            random.choice(RAINBOW)
            for _ in self.nickname]
        self.disco_t     = 0

        # Floating emoji burst around name
        self.floaters = [
            {
                "x": random.randint(50, SCREEN_WIDTH-50),
                "y": random.randint(50, 300),
                "t": random.uniform(0, 6),
                "s": random.randint(28,44),
                "em": random.choice(
                    ["⭐","🎉","🌟","✨","🎊","🏆"])
            }
            for _ in range(12)
        ]

        # Background particles
        self.particles = [
            {"x":x,"y":y,"t":t,"s":s}
            for x,y,t,s in [
                (100, 80,0.0,24),(300, 50,1.0,18),
                (600, 90,2.0,22),(850, 60,0.5,20),
                (950,200,1.5,16),( 50,400,3.0,14),
                (500, 30,2.5,20),
            ]
        ]

        # Keep background music playing on the end screen.
        # We no longer load celebration.wav because even a
        # silent/broken file loads without raising an
        # exception — which kills background music with no
        # way to detect it.  Just keep whatever is already
        # playing, and restart it if it somehow stopped.
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.set_volume(0.4)
        else:
            self._restore_bg_music()

        # Personalised voice callout
        self._speak_end(lang)

    # ── Restore background music ─────────────
    def _restore_bg_music(self):
        for bg in [
            "assets/sounds/music/background.wav",
            "assets/sounds/music/background.mp3",
        ]:
            if os.path.exists(bg):
                try:
                    if not pygame.mixer.music.get_busy():
                        pygame.mixer.music.load(bg)
                        pygame.mixer.music.play(-1)
                    pygame.mixer.music.set_volume(0.4)
                    print(f"[Music] End screen using: {bg}")
                    return
                except Exception:
                    pass

    # ── Personalised end speech ───────────────
    def _speak_end(self, lang):
        name = self.nickname
        if lang == "ms":
            opts = [
                f"Tahniah {name}! "
                f"Kamu telah selesaikan safari! "
                f"Kamu memang juara!",
                f"Wuhuu {name}! "
                f"Kamu luar biasa! "
                f"Saya sangat bangga dengan kamu!",
                f"Syabas {name}! "
                f"Kamu bintang safari perkataan!",
            ]
        else:
            opts = [
                f"Amazing job {name}! "
                f"You finished the whole safari! "
                f"You are a legend!",
                f"Woohoo {name}! "
                f"You are incredible! "
                f"I am so proud of you!",
                f"Congratulations {name}! "
                f"You completed Word Safari! "
                f"You are a champion!",
                f"Yes {name}! "
                f"You did it! "
                f"What an amazing explorer you are!",
            ]
        # Clear queue then speak so nothing blocks it
        try:
            while not self.manager.voice._q.empty():
                self.manager.voice._q.get_nowait()
        except Exception:
            pass
        self.manager.voice.speak_priority(
            random.choice(opts))

    # ── Helpers ───────────────────────────────
    def _blit_scaled(self, surface, src, cx, cy, scale):
        if scale <= 0:
            return
        w = max(1, int(src.get_width()  * scale))
        h = max(1, int(src.get_height() * scale))
        s = pygame.transform.smoothscale(src, (w, h))
        surface.blit(s, (cx-w//2, cy-h//2))

    # ── Dancing Zara ──────────────────────────
    def _draw_zara(self, surface):
        cx   = int(self.zara_x)
        t    = self.zara_t
        bob  = int(math.sin(t * 3) * 12)
        cy   = 400 + bob
        flip = 1 if self.zara_dx > 0 else -1

        # Colours — deliberately varied so it's
        # NOT all yellow
        BODY   = (220, 105,  35)   # warm orange
        BELLY  = (255, 195, 130)   # light peach
        MANE   = (130,  45,  10)   # dark auburn
        FACE   = (235, 145,  55)   # amber
        EAR_O  = (200,  85,  25)   # ear outer
        EAR_I  = (255, 160, 180)   # ear inner pink
        FOOT   = (180,  70,  20)   # dark orange feet
        HAND   = (240, 160,  70)   # lighter paw
        BOW_A  = ( 80, 180, 200)   # teal bow
        BOW_B  = ( 40, 140, 160)   # darker teal

        # Ground shadow
        pygame.draw.ellipse(surface, (0, 0, 0),
            (cx-50, cy+74, 100, 18))

        # Body
        pygame.draw.ellipse(surface, BODY,
            (cx-50, cy-5, 100, 80))
        # Belly highlight
        pygame.draw.ellipse(surface, BELLY,
            (cx-28, cy+10, 56, 46))

        # Bow tie (centre of chest — eye-catching teal)
        bow_y = cy + 18
        for bx, bsign in [(cx-22, -1), (cx+6, 1)]:
            pts = [
                (cx, bow_y),
                (bx + bsign*0,  bow_y - 10),
                (bx + bsign*14, bow_y),
                (bx + bsign*0,  bow_y + 10),
            ]
            pygame.draw.polygon(surface, BOW_A, pts)
            pygame.draw.polygon(surface, BOW_B, pts, 2)
        pygame.draw.circle(surface, BOW_B, (cx, bow_y), 5)

        # Head — auburn mane ring first
        for i in range(12):
            a  = math.radians(i * 30 + t * 18)
            mr = 62 + math.sin(a * 2 + t) * 5
            mx = int(cx + mr * math.cos(a))
            my = int(cy - 58 + mr * math.sin(a))
            pygame.draw.circle(surface, MANE,
                (mx, my), 10)

        # Face
        pygame.draw.circle(surface, FACE,
            (cx, cy - 58), 54)

        # Ears
        for ex, sign in [(cx - 40, -1), (cx + 40, 1)]:
            pygame.draw.polygon(surface, EAR_O,
                [(ex, cy-98),
                 (ex + sign*16, cy-124),
                 (ex + sign*32, cy-96)])
            pygame.draw.polygon(surface, EAR_I,
                [(ex + sign*4,  cy-100),
                 (ex + sign*16, cy-118),
                 (ex + sign*28, cy-100)])

        # Eyes — big and round (friendly)
        ey = cy - 68
        for ex in [cx - 22, cx + 22]:
            pygame.draw.ellipse(surface, WHITE,
                (ex - 11, ey - 10, 22, 20))
            pygame.draw.circle(surface, (40, 20, 80),
                (ex + 2, ey), 7)          # purple iris
            pygame.draw.circle(surface, BLACK,
                (ex + 2, ey), 4)          # pupil
            pygame.draw.circle(surface, WHITE,
                (ex + 5, ey - 3), 2)      # shine

        # Nose
        pygame.draw.ellipse(surface, (180, 70, 70),
            (cx - 12, cy - 46, 24, 14))

        # Big happy smile
        pygame.draw.arc(surface, (140, 50, 50),
            pygame.Rect(cx - 20, cy - 38, 40, 22),
            math.pi, 0, 4)

        # Whisker dots
        for wx, wy in [
                (cx - 36, cy - 44), (cx - 32, cy - 38),
                (cx + 32, cy - 44), (cx + 28, cy - 38)]:
            pygame.draw.circle(surface, MANE, (wx, wy), 3)

        # Dancing arms
        w1 = math.sin(t * 3) * 30
        w2 = math.sin(t * 3 + math.pi) * 30
        for ax, wave in [
                (cx + 55 * flip,  w1),
                (cx - 55 * flip,  w2)]:
            ey2 = int(cy + wave)
            pygame.draw.line(surface, BODY,
                (cx + 46 * flip, cy + 10),
                (ax, ey2), 10)
            pygame.draw.circle(surface, HAND,
                (ax, ey2), 13)

        # Feet
        for fx in [cx - 26, cx + 26]:
            pygame.draw.ellipse(surface, FOOT,
                (fx - 18, cy + 72, 36, 16))

    # ── Floating bg stars ─────────────────────
    def _draw_bg_stars(self, surface):
        for p in self.particles:
            p["t"] += 0.05
            alpha = (math.sin(p["t"])+1)/2
            s = int(p["s"]*(0.6+alpha*0.5))
            if s < 6: continue
            f   = pygame.font.SysFont("segoeuiemoji",s)
            img = f.render("⭐",True,ORANGE_STAR)
            surface.blit(img,(p["x"],p["y"]))

    # ── Disco nickname banner ─────────────────
    def _draw_disco_name(self, surface):
        """
        Each letter of the nickname cycles
        through rainbow colours independently
        and bobs up and down on its own wave.
        """
        if self.name_sc < 1.0:
            self.name_sc = min(
                1.0, self.name_sc + 0.06)

        # Update disco colours every 4 frames
        self.disco_t += 1
        if self.disco_t % 4 == 0:
            self.disco_cols = [
                RAINBOW[(RAINBOW.index(c)+1)
                        % len(RAINBOW)]
                for c in self.disco_cols]

        # Measure total width first
        letters = list(self.nickname.upper())
        surfs   = []
        for i, ch in enumerate(letters):
            col = self.disco_cols[
                i % len(self.disco_cols)]
            s   = self.f_name.render(
                ch, True, col)
            surfs.append(s)

        gap       = 4
        total_w   = sum(s.get_width()
                        for s in surfs) \
                    + gap*(len(surfs)-1)
        sx        = SCREEN_WIDTH//2 - total_w//2
        base_y    = 38

        # Draw each letter with outline + bob
        x = sx
        for i, (ch, s) in enumerate(
                zip(letters, surfs)):
            col = self.disco_cols[
                i % len(self.disco_cols)]
            bob = int(10*math.sin(
                self.t*0.12 + i*0.7))
            cy  = base_y + bob

            # Scale-in
            if self.name_sc < 1.0:
                self._blit_scaled(
                    surface, s,
                    x + s.get_width()//2,
                    cy + s.get_height()//2,
                    self.name_sc)
            else:
                # Outline
                for ox,oy in [
                        (-3,0),(3,0),(0,-3),(0,3)]:
                    out = self.f_name.render(
                        ch, True, BLACK)
                    surface.blit(out,
                        (x+ox, cy+oy))
                surface.blit(s, (x, cy))
            x += s.get_width() + gap

        # Floating emojis around the name
        for fl in self.floaters:
            fl["t"] += 0.04
            alpha = (math.sin(fl["t"])+1)/2
            sz    = int(fl["s"]*(0.7+alpha*0.4))
            if sz < 10: continue
            try:
                f   = pygame.font.SysFont(
                    "segoeuiemoji", sz)
                img = f.render(fl["em"],True,WHITE)
                img.set_alpha(int(100+alpha*155))
                surface.blit(img,(fl["x"],fl["y"]))
            except Exception:
                pass

    # ── Score card ────────────────────────────
    def _draw_score_card(self, surface):
        if self.card_sc < 1.0:
            self.card_sc = min(
                1.0, self.card_sc+0.05)

        card_w = 680
        card_h = 160
        card_x = SCREEN_WIDTH//2 - card_w//2
        card_y = 310

        sc = self.card_sc
        dw = int(card_w*sc)
        dh = int(card_h*sc)
        dx = SCREEN_WIDTH//2 - dw//2
        dy = card_y + card_h//2 - dh//2

        pygame.draw.rect(surface,(0,0,0),
            (dx+4,dy+6,dw,dh),border_radius=22)
        pygame.draw.rect(surface,WHITE,
            (dx,dy,dw,dh),border_radius=22)

        # Rainbow border
        ri = int(self.rainbow_t*3)%len(RAINBOW)
        pygame.draw.rect(surface,RAINBOW[ri],
            (dx,dy,dw,dh),5,border_radius=22)

        if sc < 0.5:
            return

        lang = getattr(self.manager,'language','en')

        # Nickname label inside card
        name_lbl = self.f_small.render(
            f"🏆 {self.nickname}'s Score",
            True, PURPLE_TEXT)
        surface.blit(name_lbl,
            (SCREEN_WIDTH//2
             - name_lbl.get_width()//2,
             dy+8))

        # Four stats
        cols = [
            ("✅", str(self.correct),
             CORRECT_GREEN,
             "Correct" if lang=="en"
             else "Betul"),
            ("❌", str(self.wrong),
             WRONG_PINK,
             "Wrong" if lang=="en"
             else "Silap"),
            ("🎯", f"{self.accuracy}%",
             PURPLE_TEXT,
             "Accuracy" if lang=="en"
             else "Ketepatan"),
            ("🔥", f"x{self.streak}",
             ORANGE_STAR,
             "Best Streak" if lang=="en"
             else "Streak Terbaik"),
        ]
        col_w = dw // len(cols)
        for i,(icon,val,color,lbl) in \
                enumerate(cols):
            cx = dx + i*col_w + col_w//2
            try:
                fi  = pygame.font.SysFont(
                    "segoeuiemoji",22)
                ics = fi.render(icon,True,BLACK)
                surface.blit(ics,
                    (cx-ics.get_width()//2,dy+36))
            except Exception:
                pass
            fv = pygame.font.SysFont(
                "comicsansms",30,bold=True)
            vs = fv.render(val,True,color)
            surface.blit(vs,
                (cx-vs.get_width()//2,dy+62))
            fl2 = pygame.font.SysFont(
                "comicsansms",14,bold=True)
            ls  = fl2.render(lbl,True,(120,120,120))
            surface.blit(ls,
                (cx-ls.get_width()//2,dy+100))
            if i < len(cols)-1:
                pygame.draw.line(surface,
                    (220,220,220),
                    (dx+(i+1)*col_w, dy+30),
                    (dx+(i+1)*col_w, dy+dh-14),2)

    # ── Leaderboard panel ─────────────────────
    def _draw_leaderboard(self, surface):
        lang   = getattr(self.manager, 'language', 'en')
        card_w = 680
        card_h = 148
        card_x = SCREEN_WIDTH // 2 - card_w // 2
        card_y = 478

        # Shadow
        pygame.draw.rect(surface, (0, 0, 0),
            (card_x+4, card_y+6, card_w, card_h),
            border_radius=18)
        # Card body
        pygame.draw.rect(surface, WHITE,
            (card_x, card_y, card_w, card_h),
            border_radius=18)
        # Animated rainbow border
        ri = int(self.rainbow_t * 3) % len(RAINBOW)
        pygame.draw.rect(surface, RAINBOW[ri],
            (card_x, card_y, card_w, card_h),
            4, border_radius=18)

        # Header
        hdr = ("🏆  LEADERBOARD"
               if lang == "en"
               else "🏆  PAPAN MARKAH")
        hs = self.f_small.render(hdr, True, PURPLE_TEXT)
        surface.blit(hs, (card_x + 14, card_y + 7))

        # Divider
        pygame.draw.line(surface, (210, 210, 210),
            (card_x + 8,         card_y + 30),
            (card_x + card_w - 8, card_y + 30), 1)

        RANK_COLS = [
            (255, 200,  40),   # gold
            (192, 192, 192),   # silver
            (205, 127,  50),   # bronze
            (180, 180, 200),
            (180, 180, 200),
        ]
        RANK_LABELS = ["1st", "2nd", "3rd", "4th", "5th"]

        for i, entry in enumerate(self.lb_entries[:5]):
            ry  = card_y + 37 + i * 22
            col = RANK_COLS[i]

            # Highlight current player's row
            is_me = (entry.get("name") == self.nickname
                     and entry.get("stars") == self.stars
                     and entry.get("accuracy") == self.accuracy)
            if is_me:
                hi = pygame.Surface(
                    (card_w - 16, 20), pygame.SRCALPHA)
                hi.fill((255, 220, 40, 70))
                surface.blit(hi, (card_x + 8, ry))

            # Rank badge
            rs = self.f_lb.render(
                RANK_LABELS[i], True, col)
            surface.blit(rs, (card_x + 10, ry + 1))

            # Name (truncate to 10 chars)
            name_str = entry.get("name", "?")[:10]
            if is_me:
                name_str = f"★ {name_str}"
            ns = self.f_lb.render(name_str, True, PURPLE_TEXT)
            surface.blit(ns, (card_x + 70, ry + 1))

            # Stars
            ss = self.f_lb.render(
                f"⭐ {entry.get('stars', 0)}",
                True, ORANGE_STAR)
            surface.blit(ss, (card_x + 290, ry + 1))

            # Accuracy
            acs = self.f_lb.render(
                f"🎯 {entry.get('accuracy', 0)}%",
                True, DARK_GREEN)
            surface.blit(acs, (card_x + 400, ry + 1))

            # Date
            ds = self.f_lb.render(
                entry.get("date", ""),
                True, (150, 150, 150))
            surface.blit(ds, (card_x + 530, ry + 1))

        # Empty state
        if not self.lb_entries:
            empty = self.f_lb.render(
                "No scores yet — you're first! 🎉"
                if lang == "en"
                else "Tiada markah lagi — kamu yang pertama! 🎉",
                True, (160, 160, 160))
            surface.blit(empty,
                (SCREEN_WIDTH // 2 - empty.get_width() // 2,
                 card_y + 60))

    # ── Events ───────────────────────────────
    def handle_event(self, event):
        if self.play_btn.is_clicked(event):
            self.manager.play_sfx("click")
            self.manager.ai.reset()
            self.manager.stars          = 0
            self.manager.score_correct  = 0
            self.manager.score_wrong    = 0
            self.manager.score_accuracy = 0
            self.manager.score_streak   = 0
            self.manager.switch_screen("start")

        if self.quit_btn.is_clicked(event):
            pygame.quit()
            import sys; sys.exit()

    # ── Update ───────────────────────────────
    def update(self):
        mouse = pygame.mouse.get_pos()
        self.play_btn.update(mouse)
        self.quit_btn.update(mouse)

        self.t         += 1
        self.rainbow_t += 0.08
        self.zara_t    += 0.04
        self.zara_x    += self.zara_dx
        if (self.zara_x > SCREEN_WIDTH-70
                or self.zara_x < 70):
            self.zara_dx *= -1

        self.trophy_sc = min(
            1.0, self.trophy_sc+0.035)

        self.confetti.update()
        if not self.confetti.active:
            self.confetti.trigger(120)

    # ── Draw ─────────────────────────────────
    def draw(self, surface):
        # Cool purple → blue → pink gradient
        # Much more fun and child-friendly!
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            # Top: deep purple, bottom: hot pink
            r = int(120 + ratio * 135)
            g = int(40 + ratio * 60)
            b = int(180 - ratio * 60)
            pygame.draw.line(surface,
                (max(0, min(255, r)),
                 max(0, min(255, g)),
                 max(0, min(255, b))),
                (0, y), (SCREEN_WIDTH, y))

        self._draw_bg_stars(surface)

        lang = getattr(
            self.manager,'language','en')

        # ── DISCO NICKNAME BANNER ─────────────
        self._draw_disco_name(surface)

        # ── Subtitle under name ───────────────
        sub = ("kamu berjaya! 🎊"
               if lang=="ms"
               else "you did it! 🎊")
        ss  = self.f_small.render(
            sub, True, WHITE)
        # Outline
        for ox,oy in [(-2,0),(2,0),(0,-2),(0,2)]:
            so = self.f_small.render(
                sub,True,PURPLE_TEXT)
            surface.blit(so,
                (SCREEN_WIDTH//2
                 -so.get_width()//2+ox,
                 132+oy))
        surface.blit(ss,
            (SCREEN_WIDTH//2
             -ss.get_width()//2, 132))

        # ── Trophy (scales in) ────────────────
        if self.trophy_sc > 0.1:
            ts  = int(90*self.trophy_sc)
            tf  = pygame.font.SysFont(
                "segoeuiemoji",ts)
            ti  = tf.render(
                self.trophy_emoji,True,BLACK)
            surface.blit(ti,
                (SCREEN_WIDTH//2
                 -ti.get_width()//2, 160))

        # Trophy message with nickname
        trophy_with_name = (
            f"{self.nickname}... "
            f"{self.trophy_msg}")
        ri  = int(self.rainbow_t*4)%len(RAINBOW)
        msg = self.f_med.render(
            trophy_with_name,True,
            self.trophy_col)
        # Outline
        for ox,oy in [(-2,0),(2,0),(0,-2),(0,2)]:
            mo = self.f_med.render(
                trophy_with_name,True,BLACK)
            surface.blit(mo,
                (SCREEN_WIDTH//2
                 -mo.get_width()//2+ox,
                 252+oy))
        surface.blit(msg,
            (SCREEN_WIDTH//2
             -msg.get_width()//2, 252))

        # ── Stars row ─────────────────────────
        sf    = pygame.font.SysFont(
            "segoeuiemoji",32)
        s_row = "⭐"*min(self.stars,14)
        if not s_row:
            s_row = "☆☆☆"
        si = sf.render(s_row,True,ORANGE_STAR)
        surface.blit(si,
            (SCREEN_WIDTH//2
             -si.get_width()//2, 285))

        # ── Score card ────────────────────────
        self._draw_score_card(surface)

        # ── Leaderboard ───────────────────────
        self._draw_leaderboard(surface)

        # ── Weak words (small hint below lb) ──
        if self.weak:
            wtx = (("Cuba lagi: " if lang=="ms"
                    else "Practice: ")
                   + "  ".join(self.weak))
            ws = self.f_tiny.render(
                wtx, True, PURPLE_TEXT)
            surface.blit(ws,
                (SCREEN_WIDTH//2
                 - ws.get_width()//2, 630))

        # ── Dancing Zara ──────────────────────
        self._draw_zara(surface)

        # ── Buttons ───────────────────────────
        self.play_btn.draw(surface)
        self.quit_btn.draw(surface)

        # ── Confetti on top ───────────────────
        self.confetti.draw(surface)
