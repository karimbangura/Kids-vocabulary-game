# ============================================
# minigames/balloon_pop.py
# Mini-Game 3: Balloon Pop
# Tap the balloon with the correct word
# ============================================
import pygame
import random
import math
from settings import *
from components.button          import Button
from components.confetti        import Confetti
from components.speech_listener import SpeechListener


class Balloon:
    COLORS = [
        (255,  80,  80), (80,  180, 255),
        (255, 220,  50), (150, 255, 100),
        (220, 100, 255), (255, 150, 100),
        (255, 120, 180), (80,  220, 200),
    ]

    def __init__(self, x, word, speed, is_correct):
        self.x          = float(x)
        self.y          = float(820 + random.randint(0, 120))
        self.base_x     = float(x)
        self.word       = word
        self.speed      = speed
        self.is_correct = is_correct
        self.color      = random.choice(self.COLORS)
        self.radius     = 58
        self.popped     = False
        self.missed     = False
        self.pop_timer  = 0
        self.pop_parts  = []
        self.sway_t     = random.uniform(0, math.pi * 2)
        self.font       = pygame.font.SysFont(
            "comicsansms", 26, bold=True)
        self._make_pop_parts()

    def _make_pop_parts(self):
        for _ in range(14):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(4, 10)
            self.pop_parts.append({
                "x": self.x, "y": self.y,
                "dx": math.cos(angle) * speed,
                "dy": math.sin(angle) * speed,
                "r": random.randint(5, 14),
                "col": random.choice(Balloon.COLORS),
                "life": 30,
            })

    def update(self):
        if self.popped:
            self.pop_timer += 1
            for p in self.pop_parts:
                p["x"] += p["dx"]
                p["y"] += p["dy"]
                p["dy"] += 0.3
                p["life"] -= 1
            return
        self.sway_t += 0.03
        self.x = self.base_x + math.sin(self.sway_t) * 14
        self.y -= self.speed
        if self.y < -self.radius * 2:
            self.missed = True

    def draw(self, surface, hint_level, correct_word):
        if self.popped:
            for p in self.pop_parts:
                if p["life"] > 0:
                    pygame.draw.circle(
                        surface, p["col"],
                        (int(p["x"]), int(p["y"])), p["r"])
            return
        if self.missed:
            return

        cx = int(self.x)
        cy = int(self.y)
        r  = self.radius

        if hint_level >= 1 and self.is_correct:
            glow_r = r + 18
            gs = pygame.Surface(
                (glow_r * 2, glow_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                gs, (255, 255, 100, 90), (glow_r, glow_r), glow_r)
            surface.blit(gs, (cx - glow_r, cy - glow_r))

        pygame.draw.circle(surface, (0,0,0), (cx+5, cy+5), r)
        pygame.draw.circle(surface, self.color, (cx, cy), r)
        pygame.draw.circle(
            surface, (255,255,255), (cx - r//4, cy - r//3), r//3)

        pts = []
        for i in range(20):
            t  = i / 19
            sx = cx + math.sin(t * math.pi * 2) * 4
            sy = cy + r + t * 50
            pts.append((int(sx), int(sy)))
        if len(pts) >= 2:
            pygame.draw.lines(surface, (120,80,40), False, pts, 2)

        pygame.draw.circle(
            surface,
            (max(0, self.color[0]-40),
             max(0, self.color[1]-40),
             max(0, self.color[2]-40)),
            (cx, cy + r), 7)

        lbl = self.font.render(self.word, True, WHITE)
        lb_rect = pygame.Rect(
            cx - lbl.get_width()//2 - 6,
            cy - lbl.get_height()//2 - 3,
            lbl.get_width() + 12,
            lbl.get_height() + 6)
        pygame.draw.rect(surface, (0,0,0), lb_rect, border_radius=8)
        surface.blit(lbl, (cx - lbl.get_width()//2,
                            cy - lbl.get_height()//2))

        if hint_level >= 2 and self.is_correct:
            af  = pygame.font.SysFont("segoeuiemoji", 40)
            arr = af.render("👆", True, BLACK)
            surface.blit(arr, (cx - arr.get_width()//2, cy + r + 55))

    def is_hit(self, pos):
        dx = pos[0] - self.x
        dy = pos[1] - self.y
        return (dx*dx + dy*dy) <= (self.radius ** 2)


class BalloonPop:

    RAINBOW = [
        (255, 80,  80), (255,160,  40),
        (255,220,  40), ( 80,210,  80),
        ( 60,180, 255), (180, 80, 255),
        (255,100, 200),
    ]

    def __init__(self, manager):
        self.manager     = manager
        self.ai          = manager.ai
        self.is_complete = False
        self.q_count     = 0
        self.answered    = False
        self.ans_timer   = 0
        self.message     = ""
        self.msg_color   = CORRECT_GREEN
        self.balloons    = []
        self.confetti    = Confetti(SCREEN_WIDTH, SCREEN_HEIGHT)

        self.f_msg       = pygame.font.SysFont(
            "comicsansms", FONT_LARGE,  bold=True)
        self.f_prompt    = pygame.font.SysFont(
            "comicsansms", FONT_MEDIUM, bold=True)
        self.f_title     = pygame.font.SysFont(
            "comicsansms", FONT_SMALL,  bold=True)
        self.f_msg_xl    = pygame.font.SysFont(
            "comicsansms", 72, bold=True)
        self.f_emoji_big = pygame.font.SysFont(
            "segoeuiemoji", 90)
        self.f_emoji_med = pygame.font.SysFont(
            "segoeuiemoji", 56)

        self.celebrate   = False
        self.cel_t       = 0
        self.flash_alpha = 0
        self.msg_scale   = 1.0
        self.rainbow_t   = 0.0
        self.cel_emoji   = "🎈"

        self.clouds  = [
            (100, 90, 1.0), (380, 55, 0.8),
            (680, 80, 1.1), (920,110, 0.9),
        ]
        self.cloud_t = 0.0

        # Speak game-type instruction once at load
        manager.voice.say_game_intro("balloon")

        # Replay button — lets child replay the
        # balloon instruction and target word
        self.replay_btn = Button(
            x=SCREEN_WIDTH - 80, y=72,
            width=62, height=52,
            text="🔊",
            font_size=26,
            color=(80, 160, 255),
            hover_color=(50, 120, 220),
            text_color=WHITE)

        # ── Voice input (say the target word) ────
        self.speech = SpeechListener()
        self.mic_t  = 0.0
        self.mic_listen_frames = 0
        if self.speech.available:
            self.mic_btn = Button(
                x=SCREEN_WIDTH // 2 - 105,
                y=692,
                width=210, height=52,
                text="🎤  SAY WORD!",
                font_size=22,
                color=(80, 160, 255),
                hover_color=(50, 120, 220),
                text_color=WHITE)
        else:
            self.mic_btn = None

        self._new_question()

    def _new_question(self):
        self.answered    = False
        self.ans_timer   = 0
        self.message     = ""
        self.balloons    = []
        self.celebrate   = False
        self.cel_t       = 0
        self.flash_alpha = 0
        self.msg_scale   = 1.0
        self.speech.reset()

        diff = self.ai.get_difficulty()
        pool = VOCAB[diff]
        lang = getattr(self.manager, 'language', 'en')
        self.correct = random.choice(pool)

        self.ai.new_question(self.correct["word"])

        hint   = self.ai.get_hint_level()
        speeds = {1: 1.3, 2: 1.9, 3: 2.6}
        speed  = 0.8 if hint >= 2 else speeds[diff]

        others = [v for v in pool
                  if v["word"] != self.correct["word"]]
        random.shuffle(others)
        choices = [self.correct] + others[:3]
        random.shuffle(choices)

        spacing = SCREEN_WIDTH // (len(choices) + 1)
        for i, ch in enumerate(choices):
            word = ch["malay"] if lang == "ms" else ch["word"]
            b = Balloon(
                x=spacing * (i + 1),
                word=word,
                speed=speed + random.uniform(-0.2, 0.2),
                is_correct=(ch["word"] == self.correct["word"]))
            self.balloons.append(b)

        # Use Malay word in prompt when player chose Malay
        spoken = (self.correct["malay"]
                  if lang == "ms"
                  else self.correct["word"])
        self.manager.voice.say_balloon_prompt(spoken)

    def _start_celebration(self):
        self.celebrate   = True
        self.cel_t       = 0
        self.flash_alpha = 200
        self.msg_scale   = 0.3
        self.rainbow_t   = 0.0
        self.cel_emoji   = random.choice(
            ["🎈","⭐","🎉","🌟","🎊","🏆"])
        self.confetti.trigger(180)

    # ── Replay current question audio ─────────
    def _replay_audio(self):
        lang   = getattr(self.manager, 'language', 'en')
        spoken = (self.correct["malay"]
                  if lang == "ms"
                  else self.correct["word"])
        self.manager.voice.stop_voice()
        self.manager.voice.say_balloon_prompt(spoken)

    # ── Process spoken word ───────────────────
    def _check_speech(self):
        lang   = getattr(self.manager, 'language', 'en')
        target = (self.correct["malay"]
                  if lang == "ms"
                  else self.correct["word"])

        print(f"[BalloonPop] Speech done — "
              f"result='{self.speech.result}' "
              f"error='{self.speech.error}' "
              f"expected='{target}'")

        if self.speech.error == "unclear":
            msg = ("Hmm, say the word louder! 🎤"
                   if lang == "en"
                   else "Hmm, sebut perkataan lebih kuat! 🎤")
            self.manager.voice.speak(msg)
            self.mic_listen_frames = 0
            self.speech.reset()
            return

        if self.speech.error == "timeout":
            msg = ("No sound! Tap 🎤 and say the word!"
                   if lang == "en"
                   else "Tiada suara! Ketuk 🎤 dan sebut perkataan!")
            self.manager.voice.speak(msg)
            self.mic_listen_frames = 0
            self.speech.reset()
            return

        if self.speech.matches(target):
            # Pop the correct balloon visually, then check
            self.speech.reset()
            correct_b = next(
                (b for b in self.balloons if b.is_correct), None)
            if correct_b and not correct_b.popped:
                correct_b.popped = True
            self._check_correct_by_voice()
        else:
            if lang == "en":
                self.manager.voice.speak(
                    f"Not that one! The word is "
                    f"{target.capitalize()}! Say it!")
            else:
                self.manager.voice.speak(
                    f"Bukan itu! Perkataannya ialah "
                    f"{target.capitalize()}! Sebut!")
            self.mic_listen_frames = 0
            self.speech.reset()
            self.ai.update(False, self.correct["word"])
            self.msg_color = WRONG_PINK
            self.manager.play_sfx("wrong")
            self.answered  = True
            self.ans_timer = 90 if self.ai.should_retry else 110
            if not self.ai.should_retry:
                self.q_count += 1

    def _check_correct_by_voice(self):
        """Register a correct answer triggered by voice."""
        lang   = getattr(self.manager, 'language', 'en')
        spoken = (self.correct["malay"]
                  if lang == "ms"
                  else self.correct["word"])
        msgs = [
            UI_TEXT[lang].get("great_job", "GREAT JOB!"),
            UI_TEXT[lang].get("awesome",   "AWESOME!"),
            UI_TEXT[lang].get("well_done", "WELL DONE!"),
        ]
        self.message   = random.choice(msgs)
        self.msg_color = CORRECT_GREEN
        self.answered  = True
        self.ai.update(True, self.correct["word"])
        self.manager.add_stars(STARS_PER_CORRECT)
        self.manager.play_sfx("star")
        self.manager.voice.say_correct_balloon()
        self.manager.voice.say_word(spoken)
        self._start_celebration()
        self.ans_timer = 120
        self.q_count  += 1

    def handle_event(self, event):
        # Replay button always active
        if self.replay_btn.is_clicked(event):
            self._replay_audio()
            return
        if self.answered:
            return
        if event.type == pygame.MOUSEBUTTONDOWN:
            for b in self.balloons:
                if b.is_hit(event.pos) and not b.popped:
                    b.popped = True
                    self._check(b)
                    break

        # Mic button
        if (self.mic_btn
                and self.speech.is_idle
                and self.mic_btn.is_clicked(event)):
            lang = getattr(self.manager, 'language', 'en')
            self.speech.start_listening(lang=lang, timeout=7)
            self.manager.play_sfx("click")

    def _check(self, balloon):
        self.answered = True
        correct = balloon.is_correct
        self.ai.update(correct, self.correct["word"])
        lang = getattr(self.manager, 'language', 'en')

        # Word to pronounce (Malay if in Malay mode)
        spoken = (self.correct["malay"]
                  if lang == "ms"
                  else self.correct["word"])

        if correct:
            msgs = [
                UI_TEXT[lang].get("great_job", "GREAT JOB!"),
                UI_TEXT[lang].get("awesome",   "AWESOME!"),
                UI_TEXT[lang].get("well_done", "WELL DONE!"),
            ]
            self.message   = random.choice(msgs)
            self.msg_color = CORRECT_GREEN
            self.manager.add_stars(STARS_PER_CORRECT)
            self.manager.play_sfx("star")
            # Praise then pronounce the correct word
            self.manager.voice.say_correct_balloon()
            self.manager.voice.say_word(spoken)
            self._start_celebration()
            self.ans_timer = 120
            self.q_count  += 1
        else:
            attempt    = self.ai.get_attempts()
            wrong_opts = {
                1: ["Oops! Wrong balloon! Try again! 💪",
                    "Not that one! Find the right word! 🎈"],
                2: ["Almost! Check the glowing one! ✨",
                    "Look for the hint! 👀"],
                3: ["Last try! Find the right balloon! 🔍",
                    "Final chance! Look carefully! ⭐"],
            }
            self.message   = random.choice(
                wrong_opts.get(attempt, wrong_opts[1]))
            self.msg_color = WRONG_PINK
            self.manager.play_sfx("wrong")
            # Pronounce the target word so child knows
            # which balloon to pop on the next try
            if lang == "en":
                self.manager.voice.speak(
                    f"Try again! "
                    f"Pop the balloon "
                    f"{spoken.capitalize()}!")
            else:
                self.manager.voice.speak(
                    f"Cuba lagi! "
                    f"Pecahkan belon "
                    f"{spoken.capitalize()}!")

            if self.ai.should_retry:
                self.ans_timer = 90
            else:
                self.ans_timer = 110
                self.q_count  += 1

    def update(self):
        mouse = pygame.mouse.get_pos()
        self.replay_btn.update(mouse)

        self.mic_t += 0.08
        if (self.mic_btn
                and not self.answered
                and self.speech.is_idle):
            self.mic_btn.update(mouse)

        # Auto-reset mic if frozen > 8 seconds
        if self.speech.is_listening or self.speech.is_processing:
            self.mic_listen_frames += 1
            if self.mic_listen_frames > 8 * 60:
                self.speech.reset()
                self.mic_listen_frames = 0
                lang = getattr(self.manager, 'language', 'en')
                self.manager.voice.speak(
                    "Microphone timed out! Tap the button and try again!"
                    if lang == 'en'
                    else "Masa tamat! Ketuk butang dan cuba lagi!")
        else:
            self.mic_listen_frames = 0

        # Check speech result when ready
        if not self.answered and self.speech.is_done:
            self._check_speech()

        self.cloud_t += 0.008
        for b in self.balloons:
            b.update()
        self.confetti.update()

        # Missed balloon → treat as wrong, respawn
        if not self.answered:
            correct_b = next(
                (b for b in self.balloons if b.is_correct), None)
            if correct_b and correct_b.missed:
                self.ai.update(False, self.correct["word"])
                lang   = getattr(self.manager, 'language', 'en')
                spoken = (self.correct["malay"]
                          if lang == "ms"
                          else self.correct["word"])
                self.message   = (
                    UI_TEXT[lang].get("try_again","TRY AGAIN!")
                    + " 💨")
                self.msg_color = WRONG_PINK
                self.manager.play_sfx("wrong")
                # Tell child which balloon floated away
                if lang == "en":
                    self.manager.voice.speak(
                        f"Oh no! The balloon flew away! "
                        f"Find {spoken.capitalize()}!")
                else:
                    self.manager.voice.speak(
                        f"Aduh! Belon terbang! "
                        f"Cari {spoken.capitalize()}!")
                self.answered  = True
                self.ans_timer = 90
                self.q_count  += 1

        if self.celebrate:
            self.cel_t     += 1
            self.rainbow_t += 0.12
            if self.flash_alpha > 0:
                self.flash_alpha = max(0, self.flash_alpha - 16)
            if self.msg_scale < 1.15:
                self.msg_scale = min(1.15, self.msg_scale + 0.09)
            else:
                self.msg_scale = (
                    1.1 + 0.05 * math.sin(self.cel_t * 0.12))

        if self.answered:
            self.ans_timer -= 1
            if self.ans_timer <= 0:
                if self.celebrate:
                    if self.q_count >= QUESTIONS_PER_GAME:
                        self.is_complete = True
                    else:
                        self._new_question()
                else:
                    if self.ai.should_retry:
                        self._new_question()
                    else:
                        if self.q_count >= QUESTIONS_PER_GAME:
                            self.is_complete = True
                        else:
                            self._new_question()

    def _draw_cloud(self, surface, cx, cy, scale):
        for ox, oy, r in [
            (-35,5,28),(0,0,38),(35,5,28),
            (-18,-12,22),(18,-12,22)]:
            pygame.draw.circle(
                surface, WHITE,
                (int(cx+ox*scale), int(cy+oy*scale)),
                int(r*scale))

    def _blit_scaled(self, surface, src, cx, cy, scale):
        if scale <= 0:
            return
        w = max(1, int(src.get_width()  * scale))
        h = max(1, int(src.get_height() * scale))
        s = pygame.transform.smoothscale(src, (w, h))
        surface.blit(s, (cx - w//2, cy - h//2))

    def draw(self, surface):
        for y in range(SCREEN_HEIGHT):
            r = max(0, min(255, int(135 + y*0.04)))
            g = max(0, min(255, int(206 + y*0.02)))
            b = max(0, min(255, int(235 - y*0.05)))
            pygame.draw.line(
                surface, (r,g,b), (0,y), (SCREEN_WIDTH,y))

        for i, (cx, cy, sc) in enumerate(self.clouds):
            drift = math.sin(self.cloud_t + i) * 20
            self._draw_cloud(surface, cx+drift, cy, sc)

        # Replay button
        self.replay_btn.draw(surface)

        lang      = getattr(self.manager, 'language', 'en')
        word_show = (self.correct["malay"]
                     if lang == "ms"
                     else self.correct["word"])
        prompt    = self.f_prompt.render(
            f"Pop the '{word_show}' balloon! 🎈",
            True, PURPLE_TEXT)
        pr = pygame.Rect(
            SCREEN_WIDTH//2 - prompt.get_width()//2 - 18,
            72, prompt.get_width()+36, 54)
        pygame.draw.rect(surface, CREAM_CARD, pr, border_radius=18)
        pygame.draw.rect(surface, YELLOW_BTN, pr, 3, border_radius=18)
        surface.blit(prompt,
                     (SCREEN_WIDTH//2 - prompt.get_width()//2, 78))

        hint = self.ai.get_hint_level()
        for b in self.balloons:
            b.draw(surface, hint, self.correct["word"])

        # ── Mic button / listening indicator ─────
        if self.mic_btn and not self.celebrate:
            cx = SCREEN_WIDTH // 2
            f_small = pygame.font.SysFont(
                "comicsansms", FONT_TINY, bold=True)
            if self.speech.is_listening:
                pulse = int(
                    (math.sin(self.mic_t * 5) + 1) / 2 * 55)
                pygame.draw.circle(
                    surface, (255, 70 + pulse, 70),
                    (cx, 718), 30)
                pygame.draw.circle(
                    surface, WHITE, (cx, 718), 30, 3)
                ls = f_small.render(
                    "🎤  LISTENING...", True, (210, 40, 40))
                surface.blit(ls,
                    (cx - ls.get_width() // 2, 703))
            elif self.speech.is_processing:
                ts = f_small.render(
                    "⏳  THINKING...", True, PURPLE_TEXT)
                surface.blit(ts,
                    (cx - ts.get_width() // 2, 703))
            elif not self.answered:
                self.mic_btn.draw(surface)

        ctr = self.f_title.render(
            f"Q {min(self.q_count+1, QUESTIONS_PER_GAME)}"
            f"/{QUESTIONS_PER_GAME}",
            True, PURPLE_TEXT)
        surface.blit(ctr, (16, 75))

        self.confetti.draw(surface)

        if self.celebrate and self.message:
            cx = SCREEN_WIDTH  // 2
            cy = SCREEN_HEIGHT // 2
            overlay = pygame.Surface(
                (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,85))
            surface.blit(overlay, (0,0))

            card_w, card_h = 580, 260
            card_x = cx - card_w//2
            card_y = cy - card_h//2 - 20

            sh = pygame.Surface(
                (card_w+12, card_h+12), pygame.SRCALPHA)
            pygame.draw.rect(sh, (0,0,0,80),
                             (0,0,card_w+12,card_h+12),
                             border_radius=40)
            surface.blit(sh, (card_x-4, card_y+8))

            ri0 = int(self.rainbow_t*2) % len(self.RAINBOW)
            ri1 = (ri0+2) % len(self.RAINBOW)
            pygame.draw.rect(surface, self.RAINBOW[ri0],
                             (card_x,card_y,card_w,card_h),
                             border_radius=36)
            inner = pygame.Surface(
                (card_w-16,card_h-16), pygame.SRCALPHA)
            inner.fill((255,255,255,228))
            surface.blit(inner, (card_x+8, card_y+8))
            pygame.draw.rect(surface, self.RAINBOW[ri1],
                             (card_x,card_y,card_w,card_h),
                             6, border_radius=36)

            try:
                e1  = self.f_emoji_big.render(
                    self.cel_emoji, True, WHITE)
                bob = int(8*math.sin(self.cel_t*0.18))
                surface.blit(e1,
                    (card_x-80,
                     card_y+card_h//2-e1.get_height()//2+bob))
                surface.blit(e1,
                    (card_x+card_w+8,
                     card_y+card_h//2-e1.get_height()//2-bob))
            except Exception:
                pass

            ri_m = int(self.rainbow_t*4) % len(self.RAINBOW)
            ms   = self.f_msg_xl.render(
                self.message, True, self.RAINBOW[ri_m])
            self._blit_scaled(
                surface, ms, cx, card_y+72, self.msg_scale)

            try:
                sw  = 5 * 50
                sx0 = cx - sw//2
                for i, em in enumerate(
                        ["⭐","🌟","✨","🌟","⭐"]):
                    bob_i = int(7*math.sin(
                        self.cel_t*0.22+i*0.9))
                    es = self.f_emoji_med.render(em, True, WHITE)
                    surface.blit(es, (sx0+i*50, card_y+140+bob_i))
            except Exception:
                pass

            sub = self.f_title.render(
                "Keep going! 🚀", True, PURPLE_TEXT)
            surface.blit(sub,
                         (cx-sub.get_width()//2,
                          card_y+card_h-40))

        elif self.message and not self.celebrate:
            ms = self.f_msg.render(
                self.message, True, self.msg_color)
            backing = pygame.Surface(
                (ms.get_width()+36, ms.get_height()+18),
                pygame.SRCALPHA)
            backing.fill((255,255,255,180))
            bx = SCREEN_WIDTH//2 - ms.get_width()//2 - 18
            by = SCREEN_HEIGHT//2 - 30
            surface.blit(backing, (bx, by))
            surface.blit(ms,
                         (SCREEN_WIDTH//2 - ms.get_width()//2,
                          by+9))

        if self.flash_alpha > 0:
            flash = pygame.Surface(
                (SCREEN_WIDTH,SCREEN_HEIGHT), pygame.SRCALPHA)
            flash.fill((255,255,255,self.flash_alpha))
            surface.blit(flash, (0,0))
