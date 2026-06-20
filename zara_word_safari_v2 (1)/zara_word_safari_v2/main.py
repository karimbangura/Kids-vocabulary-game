# ============================================
# main.py
# Entry point for Zara's Word Safari
# ============================================
import pygame
import sys
import os

# Always run from the folder that contains main.py
# so asset paths work regardless of PyCharm's
# working-directory setting.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from settings import *
from ai_engine import ZaraAI


def _get_start():
    from screens.start_screen import StartScreen
    return StartScreen

def _get_instructions():
    from screens.instruction_screen import InstructionScreen
    return InstructionScreen

def _get_game():
    from screens.game_screen import GameScreen
    return GameScreen

def _get_end():
    from screens.end_screen import EndScreen
    return EndScreen


class GameManager:
    """
    Central game controller.
    Owns window, AI, score, voice, screens.
    """

    def __init__(self):
        pygame.init()

        # More channels:
        # 0 = sfx, 1 = voice, 2-7 = spare
        pygame.mixer.pre_init(
            frequency=44100,
            size=-16,
            channels=2,
            buffer=1024)
        pygame.mixer.init()
        pygame.mixer.set_num_channels(8)

        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)

        self.clock    = pygame.time.Clock()
        self.ai       = ZaraAI()
        self.stars    = 0
        self.running  = True
        self.language = "en"

        # Score fields (populated by game_screen)
        self.score_correct  = 0
        self.score_wrong    = 0
        self.score_accuracy = 0
        self.score_streak   = 0

        # Voice engine — init first so welcome
        # pre-caching starts immediately
        from components.voice import VoiceEngine
        self.voice = VoiceEngine(language="en")

        # Load sounds after voice init
        self._sounds = {}
        self._load_sounds()

        self.current = None
        self.switch_screen("start")

    # ── Sound loading ─────────────────────────
    def _load_sounds(self):
        sfx = {
            "correct"    : "assets/sounds/sfx/correct.wav",
            "wrong"      : "assets/sounds/sfx/wrong.wav",
            "star"       : "assets/sounds/sfx/star.wav",
            "level_up"   : "assets/sounds/sfx/level_up.wav",
            "balloon_pop": "assets/sounds/sfx/balloon_pop.wav",
            "click"      : "assets/sounds/sfx/click.wav",
        }
        for key, path in sfx.items():
            if os.path.exists(path):
                try:
                    self._sounds[key] = \
                        pygame.mixer.Sound(path)
                except Exception as e:
                    print(f"[Sound] {key}: {e}")
            else:
                print(f"[Sound] Missing: {path}"
                      f" — run generate_music.py")

        # Background music on channel 0 (music stream)
        for bg in [
            "assets/sounds/music/background.wav",
            "assets/sounds/music/background.mp3",
        ]:
            if os.path.exists(bg):
                try:
                    pygame.mixer.music.load(bg)
                    pygame.mixer.music.set_volume(0.25)
                    pygame.mixer.music.play(-1)
                    print(f"[Music] Playing: {bg}")
                    break
                except Exception as e:
                    print(f"[Music] {e}")

    def play_sfx(self, key: str):
        if key in self._sounds:
            try:
                # SFX on channel 0, voice on channel 1
                ch = pygame.mixer.Channel(0)
                ch.play(self._sounds[key])
            except Exception:
                pass

    # ── Screen switching ──────────────────────
    def switch_screen(self, name: str):
        if name == "start":
            self.current = _get_start()(self)
        elif name == "instructions":
            self.current = _get_instructions()(self)
        elif name == "game":
            self.current = _get_game()(self)
        elif name == "end":
            self.current = _get_end()(self)

    def add_stars(self, n: int):
        self.stars += n

    # ── Main loop ─────────────────────────────
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.current.handle_event(event)

            self.current.update()
            self.screen.fill(GREEN_BG)
            self.current.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(FPS)

        self.voice.shutdown()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    try:
        game = GameManager()
        game.run()
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to close...")
