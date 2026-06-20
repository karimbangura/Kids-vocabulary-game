# ============================================
# minigames/memory_match.py
# Mini-Game 3: Memory Match
# Flip cards to match picture with word
# FIXED: No stuck cards ever
# ============================================
import pygame
import random
import math
from settings import *
from components.confetti import Confetti


class Card:
    """
    Single memory card.
    Smooth flip animation using scale_x.
    """

    def __init__(self, x, y, w, h,
                 word, image, card_type):
        self.rect      = pygame.Rect(x, y, w, h)
        self.word      = word
        self.image     = image
        self.card_type = card_type  # "image" or "word"
        self.matched   = False
        self.face_up   = False

        # Flip state
        # "idle", "flipping_up", "flipping_down"
        self.flip_state = "idle"
        self.flip_prog  = 0.0   # 0.0=back, 1.0=front
        self.flip_speed = 0.07

        self.font = pygame.font.SysFont(
            "comicsansms", 28, bold=True)
        self.f_emoji = pygame.font.SysFont(
            "segoeuiemoji", 60)

    # ── Start flip ────────────────────────────
    def flip_up(self):
        if (self.flip_state == "idle"
                and not self.face_up
                and not self.matched):
            self.flip_state = "flipping_up"

    def flip_down(self):
        if (self.flip_state == "idle"
                and self.face_up
                and not self.matched):
            self.flip_state = "flipping_down"

    @property
    def is_animating(self):
        return self.flip_state != "idle"

    # ── Update flip ───────────────────────────
    def update(self):
        if self.flip_state == "flipping_up":
            self.flip_prog = min(
                1.0,
                self.flip_prog + self.flip_speed)
            if self.flip_prog >= 1.0:
                self.flip_prog  = 1.0
                self.flip_state = "idle"
                self.face_up    = True

        elif self.flip_state == "flipping_down":
            self.flip_prog = max(
                0.0,
                self.flip_prog - self.flip_speed)
            if self.flip_prog <= 0.0:
                self.flip_prog  = 0.0
                self.flip_state = "idle"
                self.face_up    = False

    # ── Draw ─────────────────────────────────
    def draw(self, surface):
        # Scale X creates flip illusion
        t       = self.flip_prog
        scale_x = abs(2 * t - 1)
        scale_x = max(0.04, scale_x)

        w  = max(2, int(self.rect.width * scale_x))
        cx = self.rect.centerx
        x  = cx - w // 2
        y  = self.rect.y
        h  = self.rect.height

        dr = pygame.Rect(x, y, w, h)

        # Matched glow
        if self.matched:
            gs = pygame.Surface(
                (w + 20, h + 20),
                pygame.SRCALPHA)
            pygame.draw.rect(
                gs, (255, 220, 0, 110),
                (0, 0, w + 20, h + 20),
                border_radius=16)
            surface.blit(gs,
                         (x - 10, y - 10))

        # Show back or front
        if t < 0.5:
            self._draw_back(surface, dr)
        else:
            self._draw_front(surface, dr)

    def _draw_back(self, surface, dr):
        # Card back — blue with pattern
        pygame.draw.rect(
            surface, SKY_BLUE,
            dr, border_radius=12)
        pygame.draw.rect(
            surface, SKY_DARK,
            dr, 3, border_radius=12)
        # Question mark
        f = pygame.font.SysFont(
            "comicsansms", 42, bold=True)
        q = f.render("?", True, WHITE)
        surface.blit(q,
                     (dr.centerx - q.get_width() // 2,
                      dr.centery - q.get_height() // 2))
        # Dot pattern
        for dx2, dy2 in [
                (-20,-20),(20,-20),
                (-20, 20),(20, 20),(0,0)]:
            cx2 = dr.centerx + dx2
            cy2 = dr.centery + dy2
            if dr.collidepoint(cx2, cy2):
                pygame.draw.circle(
                    surface,
                    (100, 170, 230),
                    (cx2, cy2), 4)

    def _draw_front(self, surface, dr):
        bg = (CORRECT_GREEN
              if self.matched
              else CREAM_CARD)
        pygame.draw.rect(
            surface, bg,
            dr, border_radius=12)
        pygame.draw.rect(
            surface, YELLOW_BTN,
            dr, 3, border_radius=12)

        if self.card_type == "image":
            if self.image:
                # Scale image to fit card
                iw = max(2, dr.width  - 12)
                ih = max(2, dr.height - 12)
                try:
                    img = pygame.transform.scale(
                        self.image, (iw, ih))
                    surface.blit(
                        img,
                        (dr.x + 6, dr.y + 6))
                except Exception:
                    pass
            else:
                # Emoji fallback
                es = self.f_emoji.render(
                    "❓", True, PURPLE_TEXT)
                surface.blit(
                    es,
                    (dr.centerx
                     - es.get_width()  // 2,
                     dr.centery
                     - es.get_height() // 2))
        else:
            # Word card
            # Break long words
            word = self.word
            lbl  = self.font.render(
                word, True, PURPLE_TEXT)
            if lbl.get_width() > dr.width - 10:
                # Smaller font
                sf  = pygame.font.SysFont(
                    "comicsansms", 22, bold=True)
                lbl = sf.render(
                    word, True, PURPLE_TEXT)
            surface.blit(
                lbl,
                (dr.centerx - lbl.get_width()  // 2,
                 dr.centery - lbl.get_height() // 2))

    def can_click(self):
        return (not self.face_up
                and not self.matched
                and not self.is_animating)


# ── MemoryMatch game ─────────────────────────

class MemoryMatch:
    """
    Mini-Game 3: Memory Match.
    Flip cards to match picture + word pairs.
    """

    def __init__(self, manager):
        self.manager     = manager
        self.ai          = manager.ai
        self.is_complete = False

        # Game state machine
        # "playing" | "wait_check" |
        # "wait_flip_back" | "hint_reveal" |
        # "done"
        self.state       = "playing"
        self.state_timer = 0

        self.flipped     = []
        self.pairs_found = 0
        self.total_pairs = 0

        self.message     = ""
        self.msg_color   = CORRECT_GREEN
        self.msg_timer   = 0

        self.confetti    = Confetti(
            SCREEN_WIDTH, SCREEN_HEIGHT)

        self.f_msg   = pygame.font.SysFont(
            "comicsansms", FONT_LARGE,  bold=True)
        self.f_title = pygame.font.SysFont(
            "comicsansms", FONT_SMALL,  bold=True)
        self.f_hint  = pygame.font.SysFont(
            "comicsansms", FONT_MEDIUM, bold=True)

        self._img_cache = {}
        self._build_board()

        # Speak instruction
        manager.voice.say_phrase("memory")

    # ── Load image ────────────────────────────
    def _load_img(self, item,
                  size=(110, 110)):
        key = item["word"]
        if key in self._img_cache:
            return self._img_cache[key]
        path = (f"assets/images/vocabulary/"
                f"{item['image']}")
        try:
            img = pygame.image.load(
                path).convert_alpha()
            img = pygame.transform.scale(
                img, size)
        except Exception:
            img = pygame.Surface(
                size, pygame.SRCALPHA)
            cols = [
                (255,200,80),(100,200,255),
                (200,255,100),(255,150,200)]
            pygame.draw.rect(
                img,
                random.choice(cols),
                (0, 0, *size),
                border_radius=14)
            f = pygame.font.SysFont(
                "segoeuiemoji", 55)
            es = f.render(
                item.get("emoji", "❓"),
                True, BLACK)
            img.blit(es,
                     (size[0]//2 - es.get_width()//2,
                      size[1]//2 - es.get_height()//2))
        self._img_cache[key] = img
        return img

    # ── Build board ───────────────────────────
    def _build_board(self):
        diff    = self.ai.get_difficulty()
        pool    = VOCAB[diff]
        hint    = self.ai.get_hint_level()
        n_pairs = 3 if hint >= 2 else 4
        n_pairs = min(n_pairs, len(pool))
        chosen  = random.sample(pool, n_pairs)
        self.total_pairs = n_pairs

        lang = getattr(
            self.manager, 'language', 'en')

        cards_data = []
        for item in chosen:
            img  = self._load_img(item)
            word = (item["malay"]
                    if lang == "ms"
                    else item["word"])
            cards_data.append(
                ("image", item["word"],
                 word, img))
            cards_data.append(
                ("word",  item["word"],
                 word, None))

        random.shuffle(cards_data)

        # Layout 4 cols × 2 rows
        card_w = 185
        card_h = 155
        cols   = 4
        gap_x  = 22
        gap_y  = 22
        tw     = cols * card_w + (cols-1) * gap_x
        th     = 2    * card_h + gap_y
        sx     = SCREEN_WIDTH  // 2 - tw // 2
        sy     = SCREEN_HEIGHT // 2 - th // 2 + 28

        self.cards = []
        for idx, (ctype, key,
                  word, img) in enumerate(
                cards_data):
            col = idx % cols
            row = idx // cols
            cx  = sx + col * (card_w + gap_x)
            cy  = sy + row * (card_h + gap_y)
            self.cards.append(
                Card(cx, cy, card_w, card_h,
                     word, img, ctype))

    # ── Events ───────────────────────────────
    def handle_event(self, event):
        if self.state != "playing":
            return
        if event.type != pygame.MOUSEBUTTONDOWN:
            return
        if len(self.flipped) >= 2:
            return

        for card in self.cards:
            if card.can_click():
                if card.rect.collidepoint(
                        event.pos):
                    card.flip_up()
                    self.flipped.append(card)
                    self.manager.play_sfx(
                        "click")

                    if len(self.flipped) == 2:
                        # Wait for flip anim
                        # before checking
                        self.state       = (
                            "wait_check")
                        self.state_timer = 45
                    break

    # ── Check pair ────────────────────────────
    def _check_pair(self):
        a, b = self.flipped
        # Match = same word key,
        # one image + one word card
        if (a.word == b.word
                and a.card_type
                != b.card_type):
            # ✅ Match
            a.matched    = b.matched = True
            self.pairs_found += 1
            lang = getattr(
                self.manager,'language','en')
            self.message   = (
                UI_TEXT[lang].get(
                    "great_job","GREAT JOB!")
                + " ⭐")
            self.msg_color = CORRECT_GREEN
            self.msg_timer = 80
            self.manager.add_stars(
                STARS_PER_CORRECT)
            self.manager.play_sfx("star")
            self.confetti.trigger(60)
            self.ai.update(True, a.word)
            self.flipped = []

            if self.pairs_found >= (
                    self.total_pairs):
                self.state       = "done"
                self.state_timer = 100
                self.manager.voice.say_phrase(
                    "great_job")
            else:
                self.state = "playing"
        else:
            # ❌ No match
            lang = getattr(
                self.manager,'language','en')
            self.message   = (
                UI_TEXT[lang].get(
                    "try_again","TRY AGAIN!")
                + " 💪")
            self.msg_color = WRONG_PINK
            self.msg_timer = 70
            self.manager.play_sfx("wrong")
            self.ai.update(False, a.word)

            # Hint: reveal all briefly
            if self.ai.get_hint_level() >= 2:
                self.state       = "hint_reveal"
                self.state_timer = 130
                for card in self.cards:
                    if not card.matched:
                        card.face_up = True
                        card.flip_prog = 1.0
                        card.flip_state = "idle"
                self.flipped = []
            else:
                self.state       = (
                    "wait_flip_back")
                self.state_timer = 75

    # ── Update ───────────────────────────────
    def update(self):
        # Update all card animations
        for card in self.cards:
            card.update()

        self.confetti.update()
        if self.msg_timer > 0:
            self.msg_timer -= 1

        # ── State machine ─────────────────────
        if self.state == "playing":
            pass

        elif self.state == "wait_check":
            # Wait for both cards to
            # finish flipping
            both_done = all(
                not c.is_animating
                for c in self.flipped)
            if both_done:
                self._check_pair()

        elif self.state == "wait_flip_back":
            self.state_timer -= 1
            if self.state_timer <= 0:
                for card in self.flipped:
                    card.flip_down()
                self.flipped = []
                self.state   = "playing"

        elif self.state == "hint_reveal":
            self.state_timer -= 1
            if self.state_timer <= 0:
                # Flip unmatched back down
                for card in self.cards:
                    if (card.face_up
                            and not card.matched):
                        card.face_up    = False
                        card.flip_prog  = 0.0
                self.state = "playing"

        elif self.state == "done":
            self.state_timer -= 1
            if self.state_timer <= 0:
                self.is_complete = True

    # ── Draw ─────────────────────────────────
    def draw(self, surface):
        surface.fill(GREEN_BG)

        # Title
        lang  = getattr(
            self.manager, 'language', 'en')
        title = self.f_title.render(
            "🃏 " + UI_TEXT[lang]["memory"]
            + "  Find the pairs!",
            True, PURPLE_TEXT)
        surface.blit(title,
                     (SCREEN_WIDTH  // 2
                      - title.get_width()  // 2,
                      74))

        # Pairs counter
        pairs = self.f_title.render(
            f"Pairs: {self.pairs_found}"
            f"/{self.total_pairs}",
            True, WHITE)
        surface.blit(pairs, (16, 74))

        # Hint reveal banner
        if self.state == "hint_reveal":
            hint_s = self.f_hint.render(
                "👀 Look carefully!",
                True, YELLOW_BTN)
            pygame.draw.rect(
                surface,
                (50, 50, 50, 150),
                (SCREEN_WIDTH  // 2
                 - hint_s.get_width()  // 2 - 14,
                 112,
                 hint_s.get_width() + 28,
                 hint_s.get_height() + 10),
                border_radius=10)
            surface.blit(hint_s,
                         (SCREEN_WIDTH  // 2
                          - hint_s.get_width() // 2,
                          116))

        # Cards
        for card in self.cards:
            card.draw(surface)

        # Message
        if self.msg_timer > 0:
            ms = self.f_msg.render(
                self.message,
                True, self.msg_color)
            backing = pygame.Surface(
                (ms.get_width()  + 36,
                 ms.get_height() + 18),
                pygame.SRCALPHA)
            backing.fill((255,255,255,175))
            bx = (SCREEN_WIDTH  // 2
                  - ms.get_width()  // 2 - 18)
            by = SCREEN_HEIGHT - 105
            surface.blit(backing, (bx, by))
            surface.blit(ms,
                         (SCREEN_WIDTH  // 2
                          - ms.get_width()  // 2,
                          by + 9))

        self.confetti.draw(surface)