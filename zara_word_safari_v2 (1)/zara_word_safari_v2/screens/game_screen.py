# ============================================
# screens/game_screen.py
# Wrapper that runs mini-games in sequence
# FIX: _filter_available now tests IMPORTS
#      only — never instantiates minigames
#      during the availability check, which
#      was silently crashing find_the_word
#      and skipping it entirely.
# ============================================
import pygame
from settings import *
from components.confetti import Confetti
from components.animator import StarCollect


# Correct sequence — do NOT change order
GAME_SEQUENCE = [
    "find_the_word",   # 1. Match image to word
    "fill_the_blank",  # 2. Complete the spelling
    "balloon_pop",     # 3. Pop the right balloon
    "memory_match",    # 4. Match the pairs
]

# Maps name → (module path, class name)
GAME_REGISTRY = {
    "find_the_word": ("minigames.find_the_word",  "FindTheWord"),
    "fill_the_blank": ("minigames.fill_the_blank", "FillTheBlank"),
    "balloon_pop":   ("minigames.balloon_pop",    "BalloonPop"),
    "memory_match":  ("minigames.memory_match",   "MemoryMatch"),
    "feed_zara":     ("minigames.feed_zara",      "FeedZara"),
}


class GameScreen:

    def __init__(self, manager):
        self.manager  = manager
        self.ai       = manager.ai

        # Test imports only — no instantiation
        self.queue    = self._filter_available(
            list(GAME_SEQUENCE))
        self.mg_index = 0
        self.current_mg = None
        self.confetti = Confetti(
            SCREEN_WIDTH, SCREEN_HEIGHT)

        self.f_hud   = pygame.font.SysFont(
            "comicsansms", FONT_TINY, bold=True)
        self.f_diff  = pygame.font.SysFont(
            "comicsansms", FONT_TINY, bold=True)
        self.f_score = pygame.font.SysFont(
            "comicsansms", FONT_TINY, bold=True)

        self.feedback_text  = ""
        self.feedback_color = CORRECT_GREEN
        self.feedback_timer = 0
        self.flying_stars   = []

        self.score_correct = 0
        self.score_wrong   = 0
        self.score_streak  = 0
        self.score_best    = 0

        self._orig_add_stars = manager.add_stars
        manager.add_stars    = self._tracked_add_stars

        print(f"[GameScreen] Queue: {self.queue}")

        lang = getattr(manager, 'language', 'en')
        manager.voice.speak(
            "Ready? Let's find some words!"
            if lang == 'en'
            else "Sedia? Jom cari perkataan!")

        self._load_next()

    # ── Safe import test (NO instantiation) ──
    def _can_import(self, name):
        """
        Only tests whether the module and class
        can be imported. Never creates an object.
        This prevents voice/AI side-effects from
        crashing the availability check.
        """
        if name not in GAME_REGISTRY:
            return False
        module_path, class_name = GAME_REGISTRY[name]
        try:
            import importlib
            mod = importlib.import_module(module_path)
            getattr(mod, class_name)   # just check it exists
            return True
        except Exception as e:
            print(f"[GameScreen] Cannot import "
                  f"'{name}': {e}")
            return False

    def _filter_available(self, names):
        available = []
        for name in names:
            if self._can_import(name):
                available.append(name)
                print(f"[GameScreen] ✅ Available: {name}")
            else:
                print(f"[GameScreen] ⚠️  Missing:   {name}")
        if not available:
            print("[GameScreen] No games found — "
                  "defaulting to find_the_word")
            available = ["find_the_word"]
        return available

    # ── Build (instantiate) a minigame ────────
    def _build(self, name):
        if name not in GAME_REGISTRY:
            raise ImportError(
                f"Unknown game: {name}")
        module_path, class_name = GAME_REGISTRY[name]
        import importlib
        mod = importlib.import_module(module_path)
        cls = getattr(mod, class_name)
        return cls(self.manager)

    def _load_next(self):
        if self.mg_index >= len(self.queue):
            self._finalise_score()
            # Restore original add_stars
            # before leaving game screen
            self.manager.add_stars = \
                self._orig_add_stars
            self.manager.switch_screen("end")
            return
        name = self.queue[self.mg_index]
        self.mg_index += 1
        print(f"[GameScreen] ▶ Starting: {name} "
              f"({self.mg_index}/{len(self.queue)})")
        try:
            self.current_mg = self._build(name)
        except Exception as e:
            print(f"[GameScreen] ❌ Failed to start "
                  f"'{name}': {e}")
            import traceback
            traceback.print_exc()
            self._load_next()   # skip and try next

    # ── Score ─────────────────────────────────
    def _finalise_score(self):
        self.manager.score_correct  = self.score_correct
        self.manager.score_wrong    = self.score_wrong
        self.manager.score_streak   = self.score_best
        total = self.score_correct + self.score_wrong
        self.manager.score_accuracy = (
            int(self.score_correct / total * 100)
            if total > 0 else 0)

    def _tracked_add_stars(self, amount):
        if amount == STARS_PER_CORRECT:
            self.score_correct += 1
            self.score_streak  += 1
            self.score_best     = max(
                self.score_best,
                self.score_streak)
        self._orig_add_stars(amount)

    def record_wrong(self):
        self.score_wrong  += 1
        self.score_streak  = 0

    def show_feedback(self, text,
                      correct=True, origin=None):
        self.feedback_text  = text
        self.feedback_color = (CORRECT_GREEN
                               if correct
                               else WRONG_PINK)
        self.feedback_timer = 85
        if correct:
            self.confetti.trigger(70)
            self.manager.play_sfx("correct")
            if origin:
                self.flying_stars.append(
                    StarCollect(
                        origin[0], origin[1],
                        80, 30))
        else:
            self.manager.play_sfx("wrong")

    # ── HUD ──────────────────────────────────
    def _draw_hud(self, surface):
        pygame.draw.rect(
            surface, (40, 120, 40),
            (0, 0, SCREEN_WIDTH, 58))
        pygame.draw.rect(
            surface, DARK_GREEN,
            (0, 55, SCREEN_WIDTH, 3))

        lang = getattr(
            self.manager, 'language', 'en')

        s_txt = self.f_hud.render(
            f"⭐ {UI_TEXT[lang]['stars']}: "
            f"{self.manager.stars}",
            True, YELLOW_BTN)
        surface.blit(s_txt, (14, 8))

        # Player nickname in centre of HUD
        name = getattr(
            self.manager, 'player_name', '')
        if name:
            n_txt = self.f_hud.render(
                f"🦁 {name}", True, WHITE)
            surface.blit(n_txt,
                (SCREEN_WIDTH//2
                 - n_txt.get_width()//2, 8))

        score_txt = self.f_score.render(
            f"✅ {self.score_correct}"
            f"  ❌ {self.score_wrong}",
            True, WHITE)
        surface.blit(score_txt, (14, 30))

        if self.score_streak >= 2:
            streak_txt = self.f_score.render(
                f"🔥 x{self.score_streak}",
                True, YELLOW_BTN)
            surface.blit(streak_txt,
                         (14 + score_txt.get_width()
                          + 12, 30))

        diff_map = {
            1: ("🟢", UI_TEXT[lang]["easy"],
                CORRECT_GREEN),
            2: ("🟡", UI_TEXT[lang]["medium"],
                YELLOW_BTN),
            3: ("🔴", UI_TEXT[lang]["hard"],
                WRONG_PINK),
        }
        icon, label, col = \
            diff_map[self.ai.get_difficulty()]
        d_s = self.f_diff.render(
            f"{icon} {label}", True, col)
        surface.blit(d_s,
                     (SCREEN_WIDTH
                      - d_s.get_width() - 14, 8))

        # Progress dots — one per game
        total = len(self.queue)
        gap   = 22
        start = (SCREEN_WIDTH // 2
                 - (total * gap) // 2)
        for i in range(total):
            c = (CORRECT_GREEN
                 if i < self.mg_index
                 else (100, 100, 100))
            pygame.draw.circle(
                surface, c,
                (start + i * gap, 29), 7)
            pygame.draw.circle(
                surface, WHITE,
                (start + i * gap, 29), 7, 2)

        # Progress bar
        bar_w    = 180
        bar_x    = SCREEN_WIDTH - bar_w - 14
        bar_y    = 32
        filled_w = int(
            bar_w * self.mg_index
            / max(1, len(self.queue)))
        pygame.draw.rect(
            surface, (80, 80, 80),
            (bar_x, bar_y, bar_w, 8),
            border_radius=4)
        if filled_w > 0:
            pygame.draw.rect(
                surface, CORRECT_GREEN,
                (bar_x, bar_y, filled_w, 8),
                border_radius=4)

    # ── Events ───────────────────────────────
    def handle_event(self, event):
        if self.current_mg:
            self.current_mg.handle_event(event)

    # ── Update ───────────────────────────────
    def update(self):
        if self.current_mg:
            self.current_mg.update()
            if self.current_mg.is_complete:
                self.manager.add_stars(
                    STARS_MINIGAME_BONUS)
                self.manager.play_sfx("level_up")
                self._load_next()

        if self.feedback_timer > 0:
            self.feedback_timer -= 1

        for fs in self.flying_stars:
            fs.update()
        self.flying_stars = [
            fs for fs in self.flying_stars
            if not fs.done]

        self.confetti.update()

    # ── Draw ─────────────────────────────────
    def draw(self, surface):
        surface.fill(GREEN_BG)

        if self.current_mg:
            self.current_mg.draw(surface)

        self._draw_hud(surface)

        if self.feedback_timer > 0:
            f   = pygame.font.SysFont(
                "comicsansms",
                FONT_LARGE, bold=True)
            msg = f.render(
                self.feedback_text,
                True, self.feedback_color)
            backing = pygame.Surface(
                (msg.get_width()  + 44,
                 msg.get_height() + 22),
                pygame.SRCALPHA)
            backing.fill((255, 255, 255, 180))
            bx = (SCREEN_WIDTH  // 2
                  - backing.get_width()  // 2)
            by = (SCREEN_HEIGHT // 2
                  - backing.get_height() // 2)
            surface.blit(backing, (bx, by))
            surface.blit(
                msg,
                (SCREEN_WIDTH  // 2
                 - msg.get_width()  // 2,
                 SCREEN_HEIGHT // 2
                 - msg.get_height() // 2))

        for fs in self.flying_stars:
            fs.draw(surface)

        self.confetti.draw(surface)