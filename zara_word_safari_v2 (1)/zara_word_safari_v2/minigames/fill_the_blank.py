# ============================================
# minigames/fill_the_blank.py
# Mini-Game 4: Fill the Blank
# Shows an image + a word with one letter
# missing. Child taps the correct letter.
# AI hints: glow → fewer choices → reveal
# ============================================
import pygame
import random
import math
from settings import *
from components.button          import Button
from components.confetti        import Confetti
from components.speech_listener import SpeechListener


# Pastel letter-tile colours
TILE_COLS = [
    (255, 220, 100),   # yellow
    (180, 230, 255),   # sky blue
    (200, 255, 180),   # mint
    (255, 190, 220),   # pink
    (210, 190, 255),   # lavender
    (255, 210, 170),   # peach
]

RAINBOW = [
    (255,  80,  80),
    (255, 160,  40),
    (255, 220,  40),
    ( 80, 210,  80),
    ( 60, 180, 255),
    (180,  80, 255),
    (255, 100, 200),
]


class FillTheBlank:
    """
    Show a picture + the word with one letter
    replaced by __.
    Child taps the correct missing letter from
    a set of letter tiles.
    """

    def __init__(self, manager):
        self.manager     = manager
        self.ai          = manager.ai
        self.is_complete = False
        self.q_count     = 0
        self.answered    = False
        self.ans_timer   = 0
        self.message     = ""
        self.msg_color   = CORRECT_GREEN
        self.confetti    = Confetti(
            SCREEN_WIDTH, SCREEN_HEIGHT)

        # Animation timers
        self.glow_t      = 0.0
        self.cel_t       = 0
        self.celebrate   = False
        self.flash_alpha = 0
        self.msg_scale   = 1.0
        self.rainbow_t   = 0.0
        self.cel_emoji   = "⭐"

        # Blank reveal animation
        self.reveal_t    = 0.0     # 0→1 when correct
        self.reveal_letter = ""

        # Fonts
        self.f_word   = pygame.font.SysFont(
            "comicsansms", 72, bold=True)
        self.f_blank  = pygame.font.SysFont(
            "comicsansms", 72, bold=True)
        self.f_letter = pygame.font.SysFont(
            "comicsansms", 46, bold=True)
        self.f_msg    = pygame.font.SysFont(
            "comicsansms", FONT_LARGE, bold=True)
        self.f_title  = pygame.font.SysFont(
            "comicsansms", FONT_SMALL, bold=True)
        self.f_emoji  = pygame.font.SysFont(
            "segoeuiemoji", 140)
        self.f_emoji_med = pygame.font.SysFont(
            "segoeuiemoji", 56)
        self.f_emoji_big = pygame.font.SysFont(
            "segoeuiemoji", 90)

        self._img_cache = {}

        # Speak game-type instruction once at load
        manager.voice.say_game_intro("fill")

        # Replay button — lets child hear the
        # instruction and word again at any time
        self.replay_btn = Button(
            x=SCREEN_WIDTH - 80, y=72,
            width=62, height=52,
            text="🔊",
            font_size=26,
            color=(80, 160, 255),
            hover_color=(50, 120, 220),
            text_color=WHITE)

        # ── Voice input (say the missing letter) ─
        self.speech = SpeechListener()
        self.mic_t  = 0.0
        self.mic_listen_frames = 0
        if self.speech.available:
            self.mic_btn = Button(
                x=SCREEN_WIDTH // 2 - 105,
                y=692,
                width=210, height=52,
                text="🎤  SAY LETTER!",
                font_size=22,
                color=(80, 160, 255),
                hover_color=(50, 120, 220),
                text_color=WHITE)
        else:
            self.mic_btn = None

        self._new_question()

    # ── Load image (same helper as FindTheWord) ─
    def _load_img(self, item, size=(200, 200)):
        key = item["word"]
        if key in self._img_cache:
            return self._img_cache[key]
        path = (f"assets/images/vocabulary/"
                f"{item['image']}")
        try:
            img = pygame.image.load(
                path).convert_alpha()
            img = pygame.transform.scale(img, size)
            self._img_cache[key] = img
            return img
        except Exception:
            surf = pygame.Surface(
                size, pygame.SRCALPHA)
            cols = [
                (255, 200,  80),
                (100, 200, 255),
                (200, 255, 100),
                (255, 150, 200),
            ]
            pygame.draw.rect(
                surf, random.choice(cols),
                (0, 0, *size), border_radius=20)
            es = self.f_emoji.render(
                item.get("emoji", "❓"),
                True, BLACK)
            surf.blit(es,
                (size[0]//2 - es.get_width()//2,
                 size[1]//2 - es.get_height()//2))
            self._img_cache[key] = surf
            return surf

    # ── Build a new question ──────────────────
    def _new_question(self):
        self.answered    = False
        self.ans_timer   = 0
        self.message     = ""
        self.glow_t      = 0.0
        self.celebrate   = False
        self.cel_t       = 0
        self.flash_alpha = 0
        self.msg_scale   = 1.0
        self.reveal_t    = 0.0
        self.speech.reset()

        diff = self.ai.get_difficulty()
        pool = VOCAB[diff]

        weak       = self.ai.get_weak_words()
        weak_items = [v for v in pool
                      if v["word"] in weak]
        self.correct_item = (
            random.choice(weak_items)
            if weak_items
            else random.choice(pool))

        # Tell AI fresh question started
        self.ai.new_question(self.correct_item["word"])

        word = self.correct_item["word"]

        # Pick which letter index to hide
        # Avoid index 0 on easy, allow any on hard
        hint = self.ai.get_hint_level()
        if diff == 1:
            # Easy: hide last letter (easier to guess)
            self.blank_idx = len(word) - 1
        elif diff == 2:
            # Medium: hide a middle letter
            self.blank_idx = random.randint(
                1, max(1, len(word) - 1))
        else:
            # Hard: hide any letter
            self.blank_idx = random.randint(
                0, len(word) - 1)

        self.correct_letter = word[self.blank_idx]
        self.reveal_letter  = self.correct_letter

        # Build letter choices
        # Always 4 choices (2 on strong hint)
        n = 2 if hint >= 3 else 4
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        wrong_letters = [
            c for c in alphabet
            if c != self.correct_letter]
        random.shuffle(wrong_letters)
        choices = ([self.correct_letter]
                   + wrong_letters[:n - 1])
        random.shuffle(choices)
        self.letter_choices = choices

        # Layout letter tiles
        tile_w = 110
        tile_h = 110
        gap    = 20
        total  = len(choices) * tile_w \
                 + (len(choices)-1) * gap
        sx     = SCREEN_WIDTH // 2 - total // 2
        ty     = 530

        self.tile_colors = {
            c: random.choice(TILE_COLS)
            for c in choices}

        self.buttons = []
        for i, ch in enumerate(choices):
            bx = sx + i * (tile_w + gap)
            btn = Button(
                x=bx, y=ty,
                width=tile_w, height=tile_h,
                text=ch,
                font_size=42,
                color=self.tile_colors[ch],
                hover_color=YELLOW_BTN,
                text_color=PURPLE_TEXT,
            )
            btn._letter = ch
            self.buttons.append(btn)

        self.q_img = self._load_img(
            self.correct_item)

        # Announce the image excitingly, then
        # follow up with spelling prompt.
        # Use Malay word when player chose Malay.
        lang = getattr(self.manager, 'language', 'en')
        spoken = (self.correct_item["malay"]
                  if lang == "ms"
                  else self.correct_item["word"])
        self.manager.voice.say_fill_image(spoken)

    # ── Start celebration ─────────────────────
    def _start_celebration(self):
        self.celebrate   = True
        self.cel_t       = 0
        self.flash_alpha = 200
        self.msg_scale   = 0.3
        self.rainbow_t   = 0.0
        self.cel_emoji   = random.choice(
            ["⭐", "🎉", "🌟", "🎊", "🏆",
             "✨", "🥳"])
        self.reveal_t    = 0.0   # start reveal
        self.confetti.trigger(180)
        self.confetti.trigger_burst(
            SCREEN_WIDTH // 2, 360, 50)

    # ── Check answer ──────────────────────────
    def _check(self, letter):
        is_correct = (
            letter == self.correct_letter)
        self.answered = True
        self.ai.update(
            is_correct,
            self.correct_item["word"])

        lang = getattr(
            self.manager, 'language', 'en')

        # Word to pronounce (Malay if in Malay mode)
        spoken = (self.correct_item["malay"]
                  if lang == "ms"
                  else self.correct_item["word"])

        if is_correct:
            msgs = [
                UI_TEXT[lang].get(
                    "great_job", "GREAT JOB!"),
                UI_TEXT[lang].get(
                    "awesome",   "AWESOME!"),
                UI_TEXT[lang].get(
                    "well_done", "WELL DONE!"),
            ]
            self.message   = random.choice(msgs)
            self.msg_color = CORRECT_GREEN
            self.manager.add_stars(
                STARS_PER_CORRECT)
            self.manager.play_sfx("star")
            # Praise then pronounce word so child
            # hears the correct answer clearly
            self.manager.voice.say_phrase("great_job")
            self.manager.voice.say_word(spoken)
            self._start_celebration()
            self.ans_timer = 150
        else:
            attempt = self.ai.get_attempts()
            wrong_opts = {
                1: ["Oops! Try again! 💪",
                    "Not quite! One more go! 🌈"],
                2: ["Almost! Check the hint! 👀",
                    "So close! Use the glow! ✨"],
                3: ["Last try! Look carefully! 🔍",
                    "Final chance! You can do it! ⭐"],
            }
            opts = wrong_opts.get(attempt,
                                   wrong_opts[1])
            self.message   = random.choice(opts)
            self.msg_color = WRONG_PINK
            self.manager.play_sfx("wrong")
            # Speak encouragement and pronounce
            # the target word so child can try again
            if lang == "en":
                self.manager.voice.speak(
                    f"Try again! "
                    f"Complete the word "
                    f"{spoken.capitalize()}!")
            else:
                self.manager.voice.speak(
                    f"Cuba lagi! "
                    f"Lengkapkan perkataan "
                    f"{spoken.capitalize()}!")

            if self.ai.should_retry:
                self.ans_timer = 90
            else:
                self.ans_timer = 110

    # ── Replay current question audio ─────────
    def _replay_audio(self):
        lang   = getattr(self.manager, 'language', 'en')
        spoken = (self.correct_item["malay"]
                  if lang == "ms"
                  else self.correct_item["word"])
        # Stop stale audio then replay instruction
        self.manager.voice.stop_voice()
        self.manager.voice.say_fill_image(spoken)

    # ── Process spoken letter ─────────────────
    def _check_speech_letter(self):
        lang = getattr(self.manager, 'language', 'en')

        print(f"[FillBlank] Speech done — "
              f"result='{self.speech.result}' "
              f"error='{self.speech.error}' "
              f"expected='{self.correct_letter}'")

        if self.speech.error == "unclear":
            msg = ("Hmm, say just the letter louder! 🎤"
                   if lang == "en"
                   else "Hmm, sebut huruf dengan lebih kuat! 🎤")
            self.manager.voice.speak(msg)
            self.mic_listen_frames = 0
            self.speech.reset()
            return

        if self.speech.error == "timeout":
            msg = ("No sound! Tap 🎤 and say the letter!"
                   if lang == "en"
                   else "Tiada suara! Ketuk 🎤 dan sebut huruf!")
            self.manager.voice.speak(msg)
            self.mic_listen_frames = 0
            self.speech.reset()
            return

        # Use matches_letter() which handles "T", "the letter T",
        # "tee", and last-character of spoken words like "see" → C
        if self.speech.matches_letter(self.correct_letter):
            self.speech.reset()
            self._check(self.correct_letter)
        else:
            lang = getattr(self.manager, 'language', 'en')
            spoken = (self.correct_item["malay"]
                      if lang == "ms"
                      else self.correct_item["word"])
            if lang == "en":
                self.manager.voice.speak(
                    f"Not quite! The missing letter is "
                    f"{self.correct_letter}! "
                    f"Complete the word "
                    f"{spoken.capitalize()}!")
            else:
                self.manager.voice.speak(
                    f"Belum tepat! Huruf yang hilang ialah "
                    f"{self.correct_letter}! "
                    f"Lengkapkan perkataan "
                    f"{spoken.capitalize()}!")
            self.mic_listen_frames = 0
            self.speech.reset()
            # Register wrong answer via AI then retry
            self.answered = True
            self.ai.update(False, self.correct_item["word"])
            self.msg_color = WRONG_PINK
            self.manager.play_sfx("wrong")
            self.ans_timer = 90 if self.ai.should_retry else 110

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
                self._check(btn._letter)
                break

        # Mic button
        if (self.mic_btn
                and self.speech.is_idle
                and self.mic_btn.is_clicked(event)):
            lang = getattr(self.manager, 'language', 'en')
            self.speech.start_listening(lang=lang, timeout=7)
            self.manager.play_sfx("click")

    # ── Update ───────────────────────────────
    def update(self):
        mouse = pygame.mouse.get_pos()
        self.replay_btn.update(mouse)
        for btn in self.buttons:
            btn.update(mouse)

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

        # Check speech result when ready
        if not self.answered and self.speech.is_done:
            self._check_speech_letter()

        self.glow_t   += 0.07
        self.confetti.update()

        if self.celebrate:
            self.cel_t    += 1
            self.rainbow_t += 0.12
            if self.flash_alpha > 0:
                self.flash_alpha = max(
                    0, self.flash_alpha - 16)
            if self.msg_scale < 1.15:
                self.msg_scale = min(
                    1.15, self.msg_scale + 0.09)
            else:
                self.msg_scale = (
                    1.1 + 0.05
                    * math.sin(self.cel_t * 0.12))
            # Reveal animation 0→1
            if self.reveal_t < 1.0:
                self.reveal_t = min(
                    1.0,
                    self.reveal_t + 0.06)

        if self.answered:
            self.ans_timer -= 1
            if self.ans_timer <= 0:
                if self.celebrate:
                    if self.q_count + 1 >= \
                            QUESTIONS_PER_GAME:
                        self.is_complete = True
                    else:
                        self.q_count += 1
                        self._new_question()
                else:
                    if self.ai.should_retry:
                        # Reset for retry — keep same word
                        self.answered    = False
                        self.ans_timer   = 0
                        self.message     = ""
                        self.celebrate   = False
                        self.flash_alpha = 0
                        self.msg_scale   = 1.0
                        self.speech.reset()
                        # Rebuild tiles (fewer on high hint)
                        hint = self.ai.get_hint_level()
                        n    = 2 if hint >= 3 else 4
                        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                        wrong_letters = [
                            c for c in alphabet
                            if c != self.correct_letter]
                        random.shuffle(wrong_letters)
                        choices = ([self.correct_letter]
                                   + wrong_letters[:n-1])
                        random.shuffle(choices)
                        tile_w = 110
                        tile_h = 110
                        gap    = 20
                        total  = (len(choices)*tile_w
                                  + (len(choices)-1)*gap)
                        sx     = SCREEN_WIDTH//2 - total//2
                        self.buttons = []
                        for i, ch in enumerate(choices):
                            bx = sx + i*(tile_w+gap)
                            btn = Button(
                                x=bx, y=530,
                                width=tile_w,
                                height=tile_h,
                                text=ch,
                                font_size=42,
                                color=self.tile_colors.get(
                                    ch, CREAM_CARD),
                                hover_color=YELLOW_BTN,
                                text_color=PURPLE_TEXT,
                            )
                            btn._letter = ch
                            self.buttons.append(btn)
                        # Speak spelling prompt on retry
                        self.manager.voice.say_fill_prompt(
                            self.correct_item["word"],
                            self.blank_idx)
                    else:
                        if self.q_count + 1 >= \
                                QUESTIONS_PER_GAME:
                            self.is_complete = True
                        else:
                            self.q_count += 1
                            self._new_question()

    # ── Draw helpers ─────────────────────────
    def _blit_scaled(self, surface, src,
                     cx, cy, scale):
        if scale <= 0:
            return
        w = max(1, int(src.get_width()  * scale))
        h = max(1, int(src.get_height() * scale))
        s = pygame.transform.smoothscale(
            src, (w, h))
        surface.blit(
            s, (cx - w // 2, cy - h // 2))

    def _draw_word_with_blank(self, surface):
        """
        Draw the word centred, with the blank
        letter replaced by a bouncing __ slot.
        When answered correctly the letter
        drops in with a scale animation.
        """
        word       = self.correct_item["word"]
        hint       = self.ai.get_hint_level()
        cx         = SCREEN_WIDTH // 2
        base_y     = 390

        # Build list of (char, is_blank)
        chars = []
        for i, c in enumerate(word):
            chars.append((c, i == self.blank_idx))

        # Measure total width
        char_surfs = []
        for c, is_blank in chars:
            if is_blank:
                surf = self.f_blank.render(
                    "_", True, PURPLE_TEXT)
            else:
                surf = self.f_word.render(
                    c, True, PURPLE_TEXT)
            char_surfs.append(
                (surf, is_blank))

        gap      = 8
        total_w  = sum(
            s.get_width() for s, _ in char_surfs
        ) + gap * (len(char_surfs) - 1)
        x_start  = cx - total_w // 2

        # Draw each character
        x = x_start
        for i, (surf, is_blank) in \
                enumerate(char_surfs):
            if is_blank:
                # Blank slot — pulsing box
                slot_w = surf.get_width() + 10
                slot_h = surf.get_height()
                bob = int(4 * math.sin(
                    self.glow_t * 1.5))

                # Draw slot background
                slot_col = (255, 240, 100) \
                    if not self.answered \
                    else (100, 220, 100)
                pygame.draw.rect(
                    surface, slot_col,
                    (x - 4,
                     base_y + bob,
                     slot_w,
                     slot_h - 8),
                    border_radius=10)
                pygame.draw.rect(
                    surface, PURPLE_TEXT,
                    (x - 4,
                     base_y + bob,
                     slot_w,
                     slot_h - 8),
                    3, border_radius=10)

                if self.celebrate and \
                        self.reveal_t > 0:
                    # Animate correct letter
                    # dropping in
                    scale = min(
                        1.0,
                        self.reveal_t * 1.4)
                    ri  = (int(self.rainbow_t * 3)
                           % len(RAINBOW))
                    ls  = self.f_blank.render(
                        self.reveal_letter,
                        True, RAINBOW[ri])
                    self._blit_scaled(
                        surface, ls,
                        x + surf.get_width() // 2,
                        base_y + slot_h // 2
                        - 4 + bob,
                        scale)
                else:
                    # Show hint: first/last letter
                    if hint >= 2:
                        hs = self.f_blank.render(
                            "?", True,
                            (180, 180, 180))
                        surface.blit(
                            hs, (x + 2,
                                 base_y + bob))
                    else:
                        # Draw underscore
                        surface.blit(
                            surf,
                            (x + 5,
                             base_y + bob))
                x += slot_w + gap
            else:
                # Outline effect for readability
                for ox, oy in [(-2,0),(2,0),
                                (0,-2),(0,2)]:
                    sh = self.f_word.render(
                        c, True, WHITE)
                    surface.blit(
                        sh, (x+ox, base_y+oy))
                surface.blit(surf, (x, base_y))
                x += surf.get_width() + gap

    # ── Draw ─────────────────────────────────
    def draw(self, surface):
        surface.fill(GREEN_BG)

        lang = getattr(
            self.manager, 'language', 'en')
        hint = self.ai.get_hint_level()

        # ── Title ─────────────────────────────
        title_txt = (
            "Fill the blank! 📝"
            if lang == "en"
            else "Isi tempat kosong! 📝")
        title = self.f_title.render(
            title_txt, True, PURPLE_TEXT)
        surface.blit(
            title,
            (SCREEN_WIDTH // 2
             - title.get_width() // 2, 75))

        # Q counter
        ctr = self.f_title.render(
            f"Q {self.q_count + 1}"
            f"/{QUESTIONS_PER_GAME}",
            True, WHITE)
        surface.blit(ctr, (16, 75))

        # Replay button — always visible
        self.replay_btn.draw(surface)

        # ── Image card ────────────────────────
        img_x = SCREEN_WIDTH // 2 - 110
        img_y = 138
        card_expand = 0
        if self.celebrate:
            card_expand = int(
                5 * math.sin(
                    self.cel_t * 0.15))
        pygame.draw.rect(
            surface, WHITE,
            (img_x - 16 - card_expand,
             img_y - 16 - card_expand,
             252 + card_expand * 2,
             252 + card_expand * 2),
            border_radius=24)
        border_col = YELLOW_BTN
        if self.celebrate:
            ri = (int(self.rainbow_t * 3)
                  % len(RAINBOW))
            border_col = RAINBOW[ri]
        pygame.draw.rect(
            surface, border_col,
            (img_x - 16 - card_expand,
             img_y - 16 - card_expand,
             252 + card_expand * 2,
             252 + card_expand * 2),
            5, border_radius=24)
        surface.blit(self.q_img,
                     (img_x, img_y))

        # ── Word with blank ───────────────────
        self._draw_word_with_blank(surface)

        # ── Hint glow on correct tile ─────────
        if hint >= 1 and not self.answered:
            glow_a = int(
                (math.sin(self.glow_t) + 1)
                / 2 * 160 + 50)
            for btn in self.buttons:
                if (btn._letter
                        == self.correct_letter):
                    gs = pygame.Surface(
                        (btn.rect.width  + 20,
                         btn.rect.height + 20),
                        pygame.SRCALPHA)
                    gs.fill((255, 220, 0,
                             glow_a))
                    surface.blit(
                        gs,
                        (btn.rect.x - 10,
                         btn.rect.y - 10))

        # ── Letter tiles ──────────────────────
        for btn in self.buttons:
            if (self.celebrate
                    and btn._letter
                    == self.correct_letter):
                # Pulse correct tile green
                pulse = int(
                    (math.sin(
                        self.cel_t * 0.2)
                     + 1) / 2 * 60)
                glow = pygame.Surface(
                    (btn.rect.width  + 28,
                     btn.rect.height + 28),
                    pygame.SRCALPHA)
                glow.fill(
                    (80, 255, 120, 80 + pulse))
                surface.blit(
                    glow,
                    (btn.rect.x - 14,
                     btn.rect.y - 14))
            btn.draw(surface)

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

        # ── Confetti ──────────────────────────
        self.confetti.draw(surface)

        # ══════════════════════════════════════
        # CELEBRATION OVERLAY
        # ══════════════════════════════════════
        if self.celebrate and self.message:
            cx = SCREEN_WIDTH  // 2
            cy = SCREEN_HEIGHT // 2

            overlay = pygame.Surface(
                (SCREEN_WIDTH, SCREEN_HEIGHT),
                pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 85))
            surface.blit(overlay, (0, 0))

            card_w, card_h = 580, 260
            card_x = cx - card_w // 2
            card_y = cy - card_h // 2 - 20

            # Shadow
            sh = pygame.Surface(
                (card_w + 12, card_h + 12),
                pygame.SRCALPHA)
            pygame.draw.rect(
                sh, (0, 0, 0, 80),
                (0, 0, card_w+12, card_h+12),
                border_radius=40)
            surface.blit(sh,
                         (card_x - 4,
                          card_y + 8))

            # Card
            ri0 = (int(self.rainbow_t * 2)
                   % len(RAINBOW))
            ri1 = (ri0 + 2) % len(RAINBOW)
            pygame.draw.rect(
                surface, RAINBOW[ri0],
                (card_x, card_y,
                 card_w, card_h),
                border_radius=36)
            inner = pygame.Surface(
                (card_w-16, card_h-16),
                pygame.SRCALPHA)
            inner.fill((255, 255, 255, 228))
            surface.blit(inner,
                         (card_x+8, card_y+8))
            pygame.draw.rect(
                surface, RAINBOW[ri1],
                (card_x, card_y,
                 card_w, card_h),
                6, border_radius=36)

            # Flanking emojis
            try:
                e1 = self.f_emoji_big.render(
                    self.cel_emoji, True, WHITE)
                bob = int(
                    8 * math.sin(
                        self.cel_t * 0.18))
                surface.blit(e1,
                    (card_x - 80,
                     card_y + card_h//2
                     - e1.get_height()//2
                     + bob))
                surface.blit(e1,
                    (card_x + card_w + 8,
                     card_y + card_h//2
                     - e1.get_height()//2
                     - bob))
            except Exception:
                pass

            # Rainbow message
            ri_m = (int(self.rainbow_t * 4)
                    % len(RAINBOW))
            ms = self.f_msg.render(
                self.message, True,
                RAINBOW[ri_m])
            self._blit_scaled(
                surface, ms,
                cx, card_y + 72,
                self.msg_scale)

            # Dancing stars row
            star_row = ["⭐","🌟","✨","🌟","⭐"]
            try:
                sw = len(star_row) * 50
                sx0 = cx - sw // 2
                for i, em in enumerate(star_row):
                    bob_i = int(
                        7 * math.sin(
                            self.cel_t * 0.22
                            + i * 0.9))
                    es = self.f_emoji_med.render(
                        em, True, WHITE)
                    surface.blit(
                        es,
                        (sx0 + i * 50,
                         card_y + 138 + bob_i))
            except Exception:
                pass

            # Sub-label
            sub = self.f_title.render(
                "Keep going! 🚀",
                True, PURPLE_TEXT)
            surface.blit(sub,
                (cx - sub.get_width()//2,
                 card_y + card_h - 40))

        # ── Wrong answer message ───────────────
        elif self.message and not self.celebrate:
            ms = self.f_msg.render(
                self.message, True,
                self.msg_color)
            backing = pygame.Surface(
                (ms.get_width()  + 36,
                 ms.get_height() + 18),
                pygame.SRCALPHA)
            backing.fill((255, 255, 255, 170))
            bx = (SCREEN_WIDTH  // 2
                  - ms.get_width()  // 2 - 18)
            by = 430
            surface.blit(backing, (bx, by))
            surface.blit(
                ms,
                (SCREEN_WIDTH // 2
                 - ms.get_width() // 2,
                 by + 9))

        # ── Screen flash ──────────────────────
        if self.flash_alpha > 0:
            flash = pygame.Surface(
                (SCREEN_WIDTH, SCREEN_HEIGHT),
                pygame.SRCALPHA)
            flash.fill(
                (255, 255, 255,
                 self.flash_alpha))
            surface.blit(flash, (0, 0))
