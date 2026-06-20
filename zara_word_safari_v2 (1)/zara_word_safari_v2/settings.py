# ============================================
# settings.py
# All constants, colours, vocab data
# VOCAB has BOTH English and Malay pools
# so when Malay is selected, kids see and
# learn Malay words with Malay images
# ============================================
import pygame

SCREEN_WIDTH  = 1024
SCREEN_HEIGHT = 768
TITLE         = "Word Safari 🦁"
FPS           = 60

GREEN_BG      = (123, 198, 126)
DARK_GREEN    = (60,  140,  60)
YELLOW_BTN    = (255, 217,  61)
YELLOW_HOVER  = (255, 200,  20)
YELLOW_DARK   = (220, 170,   0)
CORRECT_GREEN = (107, 203, 119)
WRONG_PINK    = (255, 179, 179)
PURPLE_TEXT   = (74,   14, 143)
PURPLE_LIGHT  = (150,  80, 220)
ORANGE_STAR   = (255, 154,  60)
CREAM_CARD    = (255, 253, 231)
SKY_BLUE      = (116, 192, 252)
SKY_DARK      = (60,  140, 220)
WHITE         = (255, 255, 255)
BLACK         = (0,     0,   0)
PINK          = (255, 150, 180)
LIGHT_ORANGE  = (255, 200, 100)
TEAL          = (0,   180, 160)

CONFETTI_COLS = [
    (255,  99,  99), (99,  200, 255),
    (255, 220,  50), (120, 255, 120),
    (220, 100, 255), (255, 165,  50),
    (255, 150, 180), (100, 255, 200),
]

FONT_HUGE   = 80
FONT_LARGE  = 56
FONT_MEDIUM = 40
FONT_SMALL  = 30
FONT_TINY   = 22

STARS_PER_CORRECT    = 1
STARS_MINIGAME_BONUS = 2
STARS_BONUS_ROUND    = 5
QUESTIONS_PER_GAME   = 5

# ── Vocabulary ────────────────────────────────
# Each entry has BOTH English and Malay so:
#  - In English mode → show English word
#  - In Malay mode   → show Malay word
#    (the Malay word IS the answer the child taps)
#
# "word"  = English (used as unique key & fill blank)
# "malay" = Malay   (shown as the answer in MS mode)
# "malay_word" = the Malay word treated as vocabulary
#                in fill_the_blank when in MS mode
# ─────────────────────────────────────────────────
VOCAB = {
    # ══ LEVEL 1 — Easy (15 words) ═══════════
    1: [
        {"word": "CAT",   "malay": "KUCING",
         "image": "cat.png",   "emoji": "🐱"},
        {"word": "DOG",   "malay": "ANJING",
         "image": "dog.png",   "emoji": "🐶"},
        {"word": "COW",   "malay": "LEMBU",
         "image": "cow.png",   "emoji": "🐮"},
        {"word": "PIG",   "malay": "BABI",
         "image": "pig.png",   "emoji": "🐷"},
        {"word": "HEN",   "malay": "AYAM",
         "image": "hen.png",   "emoji": "🐔"},
        {"word": "FISH",  "malay": "IKAN",
         "image": "fish.png",  "emoji": "🐟"},
        {"word": "BIRD",  "malay": "BURUNG",
         "image": "bird.png",  "emoji": "🐦"},
        {"word": "FROG",  "malay": "KATAK",
         "image": "frog.png",  "emoji": "🐸"},
        {"word": "DUCK",  "malay": "ITIK",
         "image": "duck.png",  "emoji": "🦆"},
        {"word": "BEE",   "malay": "LEBAH",
         "image": "bee.png",   "emoji": "🐝"},
        {"word": "SUN",   "malay": "MATAHARI",
         "image": "sun.png",   "emoji": "☀️"},
        {"word": "MOON",  "malay": "BULAN",
         "image": "moon.png",  "emoji": "🌙"},
        {"word": "STAR",  "malay": "BINTANG",
         "image": "star.png",  "emoji": "⭐"},
        {"word": "BALL",  "malay": "BOLA",
         "image": "ball.png",  "emoji": "⚽"},
        {"word": "BOOK",  "malay": "BUKU",
         "image": "book.png",  "emoji": "📚"},
    ],
    # ══ LEVEL 2 — Medium (15 words) ══════════
    2: [
        {"word": "APPLE",  "malay": "EPAL",
         "image": "apple.png",  "emoji": "🍎"},
        {"word": "BANANA", "malay": "PISANG",
         "image": "banana.png", "emoji": "🍌"},
        {"word": "MANGO",  "malay": "MANGGA",
         "image": "mango.png",  "emoji": "🥭"},
        {"word": "GRAPE",  "malay": "ANGGUR",
         "image": "grape.png",  "emoji": "🍇"},
        {"word": "LEMON",  "malay": "LEMON",
         "image": "lemon.png",  "emoji": "🍋"},
        {"word": "CAKE",   "malay": "KEK",
         "image": "cake.png",   "emoji": "🎂"},
        {"word": "CAR",    "malay": "KERETA",
         "image": "car.png",    "emoji": "🚗"},
        {"word": "BOAT",   "malay": "BOT",
         "image": "boat.png",   "emoji": "⛵"},
        {"word": "TRAIN",  "malay": "TREN",
         "image": "train.png",  "emoji": "🚂"},
        {"word": "PLANE",  "malay": "KAPAL TERBANG",
         "image": "plane.png",  "emoji": "✈️"},
        {"word": "TREE",   "malay": "POKOK",
         "image": "tree.png",   "emoji": "🌳"},
        {"word": "FLOWER", "malay": "BUNGA",
         "image": "flower.png", "emoji": "🌸"},
        {"word": "HOUSE",  "malay": "RUMAH",
         "image": "house.png",  "emoji": "🏠"},
        {"word": "CHAIR",  "malay": "KERUSI",
         "image": "chair.png",  "emoji": "🪑"},
        {"word": "CLOCK",  "malay": "JAM",
         "image": "clock.png",  "emoji": "🕐"},
    ],
    # ══ LEVEL 3 — Hard (15 words) ═════════════
    3: [
        {"word": "ELEPHANT",   "malay": "GAJAH",
         "image": "elephant.png",   "emoji": "🐘"},
        {"word": "GIRAFFE",    "malay": "ZIRAFAH",
         "image": "giraffe.png",    "emoji": "🦒"},
        {"word": "PENGUIN",    "malay": "PENGUIN",
         "image": "penguin.png",    "emoji": "🐧"},
        {"word": "DOLPHIN",    "malay": "LUMBA-LUMBA",
         "image": "dolphin.png",    "emoji": "🐬"},
        {"word": "CROCODILE",  "malay": "BUAYA",
         "image": "crocodile.png",  "emoji": "🐊"},
        {"word": "RAINBOW",    "malay": "PELANGI",
         "image": "rainbow.png",    "emoji": "🌈"},
        {"word": "VOLCANO",    "malay": "GUNUNG BERAPI",
         "image": "volcano.png",    "emoji": "🌋"},
        {"word": "BUTTERFLY",  "malay": "KUPU-KUPU",
         "image": "butterfly.png",  "emoji": "🦋"},
        {"word": "UMBRELLA",   "malay": "PAYUNG",
         "image": "umbrella.png",   "emoji": "☂️"},
        {"word": "PINEAPPLE",  "malay": "NANAS",
         "image": "pineapple.png",  "emoji": "🍍"},
        {"word": "STRAWBERRY", "malay": "STRAWBERI",
         "image": "strawberry.png", "emoji": "🍓"},
        {"word": "WATERMELON", "malay": "TEMBIKAI",
         "image": "watermelon.png", "emoji": "🍉"},
        {"word": "HOSPITAL",   "malay": "HOSPITAL",
         "image": "hospital.png",   "emoji": "🏥"},
        {"word": "TELESCOPE",  "malay": "TELESKOP",
         "image": "telescope.png",  "emoji": "🔭"},
        {"word": "FIREWORKS",  "malay": "BUNGA API",
         "image": "fireworks.png",  "emoji": "🎆"},
    ],
}

# ── Helper: get display word based on language ──
# Use this in all minigames instead of
# hardcoding ch["word"] or ch["malay"]
def get_word(item: dict, lang: str) -> str:
    """Return the word to display & learn."""
    if lang == "ms":
        return item["malay"]
    return item["word"]

def get_answer_key(item: dict, lang: str) -> str:
    """
    Return the unique key to match answers.
    Always use the Malay word in MS mode,
    English word in EN mode.
    """
    if lang == "ms":
        return item["malay"]
    return item["word"]

# ── Bilingual UI text ────────────────────────
UI_TEXT = {
    "en": {
        "play"        : "PLAY!",
        "lets_go"     : "LET'S GO!",
        "great_job"   : "GREAT JOB!",
        "try_again"   : "TRY AGAIN!",
        "awesome"     : "AWESOME!",
        "well_done"   : "WELL DONE!",
        "you_did_it"  : "YOU DID IT!",
        "find_word"   : "Find the word!",
        "fill_blank"  : "Fill the blank!",
        "pop_balloon" : "Pop the balloon!",
        "memory"      : "Memory Match!",
        "feed"        : "Feed Zara!",
        "stars"       : "Stars",
        "easy"        : "EASY",
        "medium"      : "MEDIUM",
        "hard"        : "HARD",
        "play_again"  : "PLAY AGAIN",
        "quit"        : "QUIT",
        "practice"    : "Practice more:",
    },
    "ms": {
        "play"        : "MAIN!",
        "lets_go"     : "JOMLAH!",
        "great_job"   : "BAGUS SEKALI!",
        "try_again"   : "CUBA LAGI!",
        "awesome"     : "HEBAT!",
        "well_done"   : "SYABAS!",
        "you_did_it"  : "KAMU BERJAYA!",
        "find_word"   : "Cari perkataan!",
        "fill_blank"  : "Isi tempat kosong!",
        "pop_balloon" : "Pecahkan belon!",
        "memory"      : "Padankan kad!",
        "feed"        : "Beri makan Zara!",
        "stars"       : "Bintang",
        "easy"        : "MUDAH",
        "medium"      : "SEDERHANA",
        "hard"        : "SUSAH",
        "play_again"  : "MAIN SEMULA",
        "quit"        : "KELUAR",
        "practice"    : "Cuba lagi:",
    },
}

MINIGAME_ORDER = [
    "find_the_word",
    "fill_the_blank",
    "balloon_pop",
    "memory_match",
]
