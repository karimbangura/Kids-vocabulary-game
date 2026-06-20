# ============================================
# minigames/find_the_word.py
# Mini-Game 1: Find the Word
# Shows picture, tap matching word card
# ADAPTIVE: same question repeats up to 3x
#   with escalating hints each wrong try
# ============================================
import pygame
import random
import math
from settings import *
from components.button          import Button
from components.confetti        import Confetti
from components.speech_listener import SpeechListener

CELEBRATE_EMOJIS = ["🎉","⭐","🌟","🎊","✨","🏆","🎈","💫"]
RAINBOW = [
    (255, 80,  80),
    (255,160,  40),
    (255,220,  40),
    ( 80,210,  80),
    ( 60,180, 255),
    (180, 80, 255),
    (255,100, 200),
]

# Wrong-answer encouragement per attempt number
WRONG_MSGS = {
    "en": {
        1: ["Oops! Try again! 💪",
            "Not quite! Have another go! 🌈",
            "Keep trying! You can do it! 😊"],
        2: ["Almost! Look at the hint! 👀",
            "So close! Check the glowing card! ✨",
            "Use the hint! I believe in you! 🦁"],
        3: ["Last try! Look carefully! 🔍",
            "One more chance! You've got this! ⭐",
            "Final try! The arrow will help! 👇"],
    },
    "ms": {
        1: ["Aduh! Cuba lagi! 💪",
            "Hampir! Cuba sekali lagi! 🌈"],
        2: ["Hampir! Lihat petunjuk! 👀",
            "Dekat! Semak kad yang bersinar! ✨"],
        3: ["Peluang terakhir! Lihat baik-baik! 🔍",
            "Cuba terakhir! Anak panah akan bantu! 👇"],
    },
}


class FindTheWord:

    MSG_EMOJIS = ["⭐","🎉","🌟","🎊","🏆","✨","🥳","🦁"]

    def __init__(self, manager):
        self.manager      = manager
        self.ai           = manager.ai
        self.is_complete  = False
        self.q_count      = 0
        self.answered     = False
        self.ans_timer    = 0
        self.message      = ""
        self.msg_color    = CORRECT_GREEN
        self.confetti     = Confetti(SCREEN_WIDTH, SCREEN_HEIGHT)

        self.glow_t       = 0.0
        self.celebrate    = False
        self.cel_t        = 0
        self.flash_alpha  = 0
        self.msg_scale    = 1.0
        self.rainbow_t    = 0.0
        self.cel_emoji    = ""
        self.cel_emoji2   = ""

        # Shake animation on wrong answer
        self.shake_t      = 0
        self.shake_x      = 0

        # Fonts
        self.f_word      = pygame.font.SysFont("comicsansms", FONT_MEDIUM, bold=True)
        self.f_msg       = pygame.font.SysFont("comicsansms", FONT_LARGE,  bold=True)
        self.f_msg_xl    = pygame.font.SysFont("comicsansms", 72,           bold=True)
        self.f_title     = pygame.font.SysFont("comicsansms", FONT_SMALL,  bold=True)
        self.f_small     = pygame.font.SysFont("comicsansms", FONT_TINY,   bold=True)
        self.f_emoji     = pygame.font.SysFont("segoeuiemoji", 160)
        self.f_emoji_big = pygame.font.SysFont("segoeuiemoji", 110)
        self.f_emoji_med = pygame.font.SysFont("segoeuiemoji", 64)
        self.f_heart     = pygame.font.SysFont("segoeuiemoji", 32)
        self.f_arr       = pygame.font.SysFont("segoeuiemoji", 52)

        self._img_cache  = {}

        # ── Speak game-type instruction once ──
        manager.voice.say_game_intro("find")

        # ── Skip recently failed words ─────────
        # word → number of questions left to skip
        self.recent_fails     = {}

        # ── Mic listening timeout ──────────────
        # Counts frames while mic is active;
        # auto-resets after ~8 seconds so a
        # frozen PyAudio thread never locks the UI
        self.mic_listen_frames = 0

        # ── Speech recognition (VUI bonus) ────
        self.speech = SpeechListener()
        self.mic_t  = 0.0
        if self.speech.available:
            self.mic_btn = Button(
                x=SCREEN_WIDTH//2 - 105,
                y=692,
                width=210, height=52,
                text="🎤  SAY IT!",
                font_size=24,
                color=(80, 160, 255),
                hover_color=(50, 120, 220),
                text_color=WHITE)
        else:
            self.mic_btn = None

        # Replay button — replays question instruction
        self.replay_btn = Button(
            x=SCREEN_WIDTH - 80, y=72,
            width=62, height=52,
            text="🔊",
            font_size=26,
            color=(80, 160, 255),
            hover_color=(50, 120, 220),
            text_color=WHITE)

        self._new_question()

    # ── Load image ────────────────────────────
    def _load_img(self, item, size=(240, 240)):
        key = item["word"]
        if key in self._img_cache:
            return self._img_cache[key]
        path = f"assets/images/vocabulary/{item['image']}"
        try:
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, size)
            self._img_cache[key] = img
            return img
        except Exception:
            surf = pygame.Surface(size, pygame.SRCALPHA)
            cols = [(255,200,80),(100,200,255),
                    (200,255,100),(255,150,200)]
            pygame.draw.rect(surf, random.choice(cols),
                             (0,0,*size), border_radius=24)
            es = self.f_emoji.render(
                item.get("emoji","❓"), True, BLACK)
            surf.blit(es,(size[0]//2 - es.get_width()//2,
                          size[1]//2 - es.get_height()//2))
            self._img_cache[key] = surf
            return surf

    # ── New question (brand new word) ─────────
    def _new_question(self):
        self.answered     = False
        self.ans_timer    = 0
        self.message      = ""
        self.glow_t       = 0.0
        self.celebrate    = False
        self.cel_t        = 0
        self.flash_alpha  = 0
        self.msg_scale    = 1.0
        self.shake_t      = 0
        self.shake_x      = 0
        self.speech.reset()

        diff = self.ai.get_difficulty()
        pool = VOCAB[diff]
        lang = getattr(self.manager, 'language', 'en')

        # Exclude recently failed words for 2 questions
        skip = {w for w, n in self.recent_fails.items() if n > 0}
        pool_filtered = [v for v in pool
                         if v["word"] not in skip] or pool

        # Decrement skip counters after choosing pool
        for w in list(self.recent_fails):
            self.recent_fails[w] -= 1
            if self.recent_fails[w] <= 0:
                del self.recent_fails[w]

        weak       = self.ai.get_weak_words()
        weak_items = [v for v in pool_filtered if v["word"] in weak]
        self.correct = (random.choice(weak_items)
                        if weak_items
                        else random.choice(pool_filtered))

        # Tell AI a fresh question has started
        self.ai.new_question(self.correct["word"])

        self._build_buttons(lang)
        self.q_img = self._load_img(self.correct)
        spoken = (self.correct["malay"]
                  if lang == "ms"
                  else self.correct["word"])
        self.manager.voice.say_image(spoken)

    # ── Retry SAME question (wrong answer) ────
    def _retry_question(self):
        """
        Keep same correct word/image.
        Rebuild buttons (may reduce choices on
        high hint level). Reset answered state.
        """
        self.answered    = False
        self.ans_timer   = 0
        self.message     = ""
        self.celebrate   = False
        self.cel_t       = 0
        self.flash_alpha = 0
        self.msg_scale   = 1.0
        self.shake_t     = 0
        self.shake_x     = 0
        self.speech.reset()
        # Don't reset glow_t — keep animating

        lang = getattr(self.manager, 'language', 'en')
        self._build_buttons(lang)

        # Speak encouraging feedback and pronounce the
        # target word so the child hears the correct answer
        spoken = (self.correct["malay"]
                  if lang == "ms"
                  else self.correct["word"])
        tries_left = self.ai.get_tries_left()
        if tries_left == 1:
            # Last try — give a stronger hint with the word
            if lang == "en":
                self.manager.voice.speak(
                    f"Last try! The word is "
                    f"{spoken.capitalize()}! Look carefully!")
            else:
                self.manager.voice.speak(
                    f"Peluang terakhir! "
                    f"Perkataannya ialah "
                    f"{spoken.capitalize()}! Lihat baik-baik!")
        else:
            if lang == "en":
                self.manager.voice.speak(
                    f"Try again! The word is "
                    f"{spoken.capitalize()}!")
            else:
                self.manager.voice.speak(
                    f"Cuba lagi! Perkataannya ialah "
                    f"{spoken.capitalize()}!")

    # ── Build word-choice buttons ─────────────
    def _build_buttons(self, lang):
        diff = self.ai.get_difficulty()
        pool = VOCAB[diff]
        hint = self.ai.get_hint_level()

        # Fewer choices with high hint
        n = 2 if hint >= 3 else 4

        others = [v for v in pool
                  if v["word"] != self.correct["word"]]
        random.shuffle(others)
        choices = [self.correct] + others[:n - 1]
        random.shuffle(choices)
        self.choices = choices

        btn_w = 210
        btn_h = 190
        gap   = 18
        total = len(choices) * btn_w + (len(choices)-1) * gap
        sx    = SCREEN_WIDTH  // 2 - total // 2
        by    = 490

        self.buttons = []
        for i, ch in enumerate(choices):
            bx  = sx + i * (btn_w + gap)
            lbl = ch["malay"] if lang == "ms" else ch["word"]
            btn = Button(
                x=bx, y=by,
                width=btn_w, height=btn_h,
                text=lbl,
                font_size=30,
                color=CREAM_CARD,
                hover_color=YELLOW_BTN,
                text_color=PURPLE_TEXT,
            )
            btn._vocab = ch
            self.buttons.append(btn)

    # ── Celebration ───────────────────────────
    def _start_celebration(self):
        self.celebrate   = True
        self.cel_t       = 0
        self.flash_alpha = 220
        self.msg_scale   = 0.3
        self.rainbow_t   = 0.0
        self.cel_emoji   = random.choice(self.MSG_EMOJIS)
        self.cel_emoji2  = random.choice(
            [e for e in self.MSG_EMOJIS
             if e != self.cel_emoji])
        for btn in self.buttons:
            if btn._vocab["word"] == self.correct["word"]:
                self.confetti.trigger_burst(
                    btn.rect.centerx,
                    btn.rect.centery, 50)
        self.confetti.trigger(200)

    # ── Check answer ──────────────────────────
    def _check(self, vocab):
        is_correct = (vocab["word"] == self.correct["word"])
        self.answered  = True
        self.ai.update(is_correct, self.correct["word"])

        lang = getattr(self.manager, 'language', 'en')

        if is_correct:
            msgs = [
                UI_TEXT[lang].get("great_job", "GREAT JOB!"),
                UI_TEXT[lang].get("awesome",   "AWESOME!"),
                UI_TEXT[lang].get("well_done", "WELL DONE!"),
            ]
            self.message   = random.choice(msgs)
            self.msg_color = CORRECT_GREEN
            self.manager.add_stars(STARS_PER_CORRECT)
            self.manager.play_sfx("star")
            # Queue praise first, then pronounce the word
            # so child hears both before moving on
            self.manager.voice.say_phrase("great_job")
            spoken = (self.correct["malay"]
                      if lang == "ms"
                      else self.correct["word"])
            self.manager.voice.say_word(spoken)
            self._start_celebration()
            self.ans_timer = 150
        else:
            # Pick message based on attempt number
            attempt = self.ai.get_attempts()
            bank    = WRONG_MSGS.get(lang, WRONG_MSGS["en"])
            opts    = bank.get(attempt, bank[1])
            self.message   = random.choice(opts)
            self.msg_color = WRONG_PINK
            self.manager.play_sfx("wrong")

            # Shake the wrong button
            self.shake_t = 20

            if self.ai.should_retry:
                # Repeat same question after short pause
                self.ans_timer = 90
            else:
                # Exhausted all tries — move on
                self.ans_timer = 110

    # ── Process speech result ─────────────────
    def _check_speech(self, heard: str):
        lang   = getattr(self.manager, 'language', 'en')
        target = (self.correct["malay"]
                  if lang == "ms"
                  else self.correct["word"])

        print(f"[FindWord] Speech done — "
              f"result='{self.speech.result}' "
              f"error='{self.speech.error}' "
              f"expected='{target}'")

        if self.speech.error == "unclear":
            # Could not understand — let child try again
            msg = ("Hmm, I didn't catch that! "
                   "Try saying it louder! 🎤"
                   if lang == "en"
                   else "Hmm, cuba lagi dengan lebih kuat! 🎤")
            self.manager.voice.speak(msg)
            self.mic_listen_frames = 0
            self.speech.reset()
            return

        if self.speech.error == "timeout":
            # No speech detected within the window
            msg = ("No sound heard! Tap 🎤 and "
                   "say the word out loud!"
                   if lang == "en"
                   else "Tiada suara! Ketuk 🎤 dan "
                        "sebut perkataan dengan kuat!")
            self.manager.voice.speak(msg)
            self.mic_listen_frames = 0
            self.speech.reset()
            return

        if self.speech.matches(target):
            # Treat as tapping the correct button
            self.speech.reset()
            self._check(self.correct)
        else:
            # Wrong word spoken — register wrong answer
            # and speak the correct word so child learns
            self.answered = True
            self.ai.update(False, self.correct["word"])
            attempt = self.ai.get_attempts()
            bank    = WRONG_MSGS.get(lang, WRONG_MSGS["en"])
            opts    = bank.get(attempt, bank[1])
            self.message   = random.choice(opts)
            self.msg_color = WRONG_PINK
            self.manager.play_sfx("wrong")
            self.shake_t = 20
            # Speak the correct word after wrong SFX
            if lang == "en":
                self.manager.voice.speak(
                    f"Not quite! The word is "
                    f"{target.capitalize()}!")
            else:
                self.manager.voice.speak(
                    f"Belum tepat! Perkataannya ialah "
                    f"{target.capitalize()}!")
            self.mic_listen_frames = 0
            self.speech.reset()
            self.ans_timer = (
                90 if self.ai.should_retry else 110)

    # ── Replay current question audio ─────────
    def _replay_audio(self):
        lang   = getattr(self.manager, 'language', 'en')
        spoken = (self.correct["malay"]
                  if lang == "ms"
                  else self.correct["word"])
        self.manager.voice.stop_voice()
        self.manager.voice.say_image(spoken)

    # ── Events ───────────────────────────────
    def handle_event(self, event):
        # Replay button always active
        if self.replay_btn.is_clicked(event):
            self._replay_audio()
            return
        if self.answered:
            return
        for btn in self.buttons:
            if btn.is_clicked(event):
                self._check(btn._vocab)
                break

        # Mic button
        if (self.mic_btn
                and self.speech.is_idle
                and self.mic_btn.is_clicked(event)):
            lang = getattr(self.manager, 'language', 'en')
            # 7-second window gives the child time to speak
            self.speech.start_listening(lang=lang, timeout=7)
            self.manager.play_sfx("click")

    # ── Update ───────────────────────────────
    def update(self):
        mouse = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.update(mouse)

        # Replay and mic button hover
        self.replay_btn.update(mouse)
        self.mic_t += 0.08
        if (self.mic_btn
                and not self.answered
                and self.speech.is_idle):
            self.mic_btn.update(mouse)

        # Auto-reset mic if frozen for > 8 seconds
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

        # Check speech recognition result
        if not self.answered and self.speech.is_done:
            self._check_speech(self.speech.result or "")

        self.glow_t += 0.07
        self.confetti.update()

        # Shake decay
        if self.shake_t > 0:
            self.shake_t -= 1
            self.shake_x = int(
                math.sin(self.shake_t * 1.2) * 8)
        else:
            self.shake_x = 0

        if self.celebrate:
            self.cel_t     += 1
            self.rainbow_t += 0.12
            if self.flash_alpha > 0:
                self.flash_alpha = max(
                    0, self.flash_alpha - 18)
            if self.msg_scale < 1.15:
                self.msg_scale = min(
                    1.15, self.msg_scale + 0.08)
            else:
                self.msg_scale = (
                    1.1 + 0.05
                    * math.sin(self.cel_t * 0.12))

        if self.answered:
            self.ans_timer -= 1
            if self.ans_timer <= 0:
                if self.celebrate:
                    # Correct → next question
                    if self.q_count + 1 >= QUESTIONS_PER_GAME:
                        self.is_complete = True
                    else:
                        self.q_count += 1
                        self._new_question()
                else:
                    if self.ai.should_retry:
                        # Wrong but tries remain → retry same
                        self._retry_question()
                    else:
                        # All tries used → skip this word
                        # for the next 2 questions so the
                        # child sees other words first, then
                        # revisits it with fresh eyes
                        self.recent_fails[
                            self.correct["word"]] = 2
                        if self.q_count + 1 >= QUESTIONS_PER_GAME:
                            self.is_complete = True
                        else:
                            self.q_count += 1
                            self._new_question()

    # ── Draw helpers ─────────────────────────
    def _blit_scaled(self, surface, src, cx, cy, scale):
        if scale <= 0:
            return
        w = max(1, int(src.get_width()  * scale))
        h = max(1, int(src.get_height() * scale))
        s = pygame.transform.smoothscale(src, (w, h))
        surface.blit(s, (cx - w//2, cy - h//2))

    # ── Draw hearts (tries left) ──────────────
    def _draw_tries(self, surface):
        tries_left = self.ai.get_tries_left()
        max_tries  = 3
        hearts     = ""
        for i in range(max_tries):
            hearts += "❤️" if i < tries_left else "🖤"
        hs = self.f_heart.render(hearts, True, WHITE)
        surface.blit(hs,
                     (SCREEN_WIDTH - hs.get_width() - 16,
                      75))

    # ── Draw ─────────────────────────────────
    def draw(self, surface):
        surface.fill(GREEN_BG)

        lang = getattr(self.manager, 'language', 'en')
        hint = self.ai.get_hint_level()

        # Title
        title = self.f_title.render(
            f"🔍 {UI_TEXT[lang]['find_word']}",
            True, PURPLE_TEXT)
        surface.blit(title,
                     (SCREEN_WIDTH//2
                      - title.get_width()//2, 75))

        # Q counter
        ctr = self.f_title.render(
            f"Q {self.q_count+1}/{QUESTIONS_PER_GAME}",
            True, WHITE)
        surface.blit(ctr, (16, 75))

        # Tries hearts
        self._draw_tries(surface)

        # Attempt label under hearts
        attempt = self.ai.get_attempts()
        if attempt > 0 and not self.celebrate:
            atxt = self.f_small.render(
                f"Try {attempt+1}/3",
                True, WRONG_PINK)
            surface.blit(atxt,
                         (SCREEN_WIDTH - atxt.get_width() - 16,
                          105))

        # Image card (shake on wrong)
        img_x = SCREEN_WIDTH//2 - 135 + self.shake_x
        img_y = 145
        card_expand = 0
        if self.celebrate:
            card_expand = int(
                6 * math.sin(self.cel_t * 0.15))

        pygame.draw.rect(
            surface, WHITE,
            (img_x - 18 - card_expand,
             img_y - 18 - card_expand,
             306 + card_expand*2,
             306 + card_expand*2),
            border_radius=28)

        border_col = YELLOW_BTN
        if self.celebrate:
            ri = int(self.rainbow_t * 3) % len(RAINBOW)
            border_col = RAINBOW[ri]
        elif self.shake_t > 0:
            border_col = WRONG_PINK

        pygame.draw.rect(
            surface, border_col,
            (img_x - 18 - card_expand,
             img_y - 18 - card_expand,
             306 + card_expand*2,
             306 + card_expand*2),
            6, border_radius=28)
        surface.blit(self.q_img, (img_x, img_y))

        # Hint glow on correct button
        if hint >= 1 and not self.answered:
            glow_a = int(
                (math.sin(self.glow_t)+1)/2*180+40)
            for btn in self.buttons:
                if btn._vocab["word"] == self.correct["word"]:
                    gs = pygame.Surface(
                        (btn.rect.width+24,
                         btn.rect.height+24),
                        pygame.SRCALPHA)
                    gs.fill((255,220,0,glow_a))
                    surface.blit(gs,
                                 (btn.rect.x-12,
                                  btn.rect.y-12))

        # Buttons
        for btn in self.buttons:
            if self.celebrate and \
                    btn._vocab["word"] == self.correct["word"]:
                pulse = int(
                    (math.sin(self.cel_t*0.2)+1)/2*60)
                glow = pygame.Surface(
                    (btn.rect.width+32,
                     btn.rect.height+32),
                    pygame.SRCALPHA)
                glow.fill((80,255,120,80+pulse))
                surface.blit(glow,
                             (btn.rect.x-16,
                              btn.rect.y-16))
            btn.draw(surface)

        # Hint arrow
        if hint >= 2 and not self.answered:
            for btn in self.buttons:
                if btn._vocab["word"] == self.correct["word"]:
                    arr = self.f_arr.render(
                        "👇", True, BLACK)
                    surface.blit(arr,
                                 (btn.rect.centerx
                                  - arr.get_width()//2,
                                  btn.rect.top - 58))

        # Replay button — always visible
        self.replay_btn.draw(surface)

        # ── Mic button / listening indicator ─────
        if self.mic_btn and not self.celebrate:
            cx = SCREEN_WIDTH // 2
            if self.speech.is_listening:
                # Pulsing red ring
                pulse = int(
                    (math.sin(self.mic_t * 5)+1)/2 * 55)
                pygame.draw.circle(
                    surface,
                    (255, 70 + pulse, 70),
                    (cx, 718), 30)
                pygame.draw.circle(
                    surface, WHITE,
                    (cx, 718), 30, 3)
                ls = self.f_small.render(
                    "🎤  LISTENING...",
                    True, (210, 40, 40))
                surface.blit(ls,
                    (cx - ls.get_width()//2, 703))
            elif self.speech.is_processing:
                ts = self.f_small.render(
                    "⏳  THINKING...",
                    True, PURPLE_TEXT)
                surface.blit(ts,
                    (cx - ts.get_width()//2, 703))
            elif not self.answered:
                self.mic_btn.draw(surface)

        self.confetti.draw(surface)

        # ══ CELEBRATION OVERLAY ══════════════
        if self.celebrate and self.message:
            cx = SCREEN_WIDTH  // 2
            cy = SCREEN_HEIGHT // 2

            overlay = pygame.Surface(
                (SCREEN_WIDTH, SCREEN_HEIGHT),
                pygame.SRCALPHA)
            overlay.fill((0,0,0,90))
            surface.blit(overlay, (0,0))

            card_w, card_h = 600, 280
            card_x = cx - card_w//2
            card_y = cy - card_h//2 - 30

            shadow = pygame.Surface(
                (card_w+12, card_h+12),
                pygame.SRCALPHA)
            pygame.draw.rect(shadow,(0,0,0,80),
                             (0,0,card_w+12,card_h+12),
                             border_radius=40)
            surface.blit(shadow,(card_x-4,card_y+8))

            ri0 = int(self.rainbow_t*2) % len(RAINBOW)
            ri1 = (ri0+2) % len(RAINBOW)
            pygame.draw.rect(surface, RAINBOW[ri0],
                             (card_x,card_y,card_w,card_h),
                             border_radius=36)
            inner = pygame.Surface(
                (card_w-16,card_h-16), pygame.SRCALPHA)
            inner.fill((255,255,255,230))
            surface.blit(inner,(card_x+8,card_y+8))
            pygame.draw.rect(surface, RAINBOW[ri1],
                             (card_x,card_y,card_w,card_h),
                             6, border_radius=36)

            try:
                e1 = self.f_emoji_big.render(
                    self.cel_emoji, True, WHITE)
                e2 = self.f_emoji_big.render(
                    self.cel_emoji2, True, WHITE)
                bob = int(8*math.sin(self.cel_t*0.18))
                surface.blit(e1,
                             (card_x-85,
                              card_y+card_h//2
                              -e1.get_height()//2+bob))
                surface.blit(e2,
                             (card_x+card_w+10,
                              card_y+card_h//2
                              -e2.get_height()//2-bob))
            except Exception:
                pass

            ri_m = int(self.rainbow_t*4) % len(RAINBOW)
            ms   = self.f_msg_xl.render(
                self.message, True, RAINBOW[ri_m])
            self._blit_scaled(
                surface, ms, cx, card_y+80, self.msg_scale)

            try:
                sw  = 5 * 52
                sx0 = cx - sw//2
                for i, em in enumerate(
                        ["⭐","🌟","✨","🌟","⭐"]):
                    bob_i = int(7*math.sin(
                        self.cel_t*0.22+i*0.9))
                    es = self.f_emoji_med.render(
                        em, True, WHITE)
                    surface.blit(es,
                                 (sx0+i*52,
                                  card_y+150+bob_i))
            except Exception:
                pass

            sub = self.f_title.render(
                "Keep going! 🚀", True, PURPLE_TEXT)
            surface.blit(sub,
                         (cx-sub.get_width()//2,
                          card_y+card_h-44))

        # Wrong message
        elif self.message and not self.celebrate:
            ms = self.f_msg.render(
                self.message, True, self.msg_color)
            backing = pygame.Surface(
                (ms.get_width()+36,
                 ms.get_height()+18),
                pygame.SRCALPHA)
            backing.fill((255,255,255,170))
            bx = SCREEN_WIDTH//2 - ms.get_width()//2 - 18
            by = 400
            surface.blit(backing,(bx,by))
            surface.blit(ms,
                         (SCREEN_WIDTH//2
                          -ms.get_width()//2,
                          by+9))

        # Screen flash
        if self.flash_alpha > 0:
            flash = pygame.Surface(
                (SCREEN_WIDTH,SCREEN_HEIGHT),
                pygame.SRCALPHA)
            flash.fill((255,255,255,self.flash_alpha))
            surface.blit(flash,(0,0))
