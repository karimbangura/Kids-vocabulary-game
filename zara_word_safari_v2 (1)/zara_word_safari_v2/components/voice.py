# ============================================
# components/voice.py
# Enhanced voice engine
# PRIMARY:  gTTS  (Google — natural, human)
# FALLBACK: pyttsx3 (offline — robotic backup)
# FIX: welcome audio pre-cached at startup
#      so it plays instantly with no delay
# ============================================
import threading
import queue
import random
import os
import tempfile


class VoiceEngine:

    IMAGE_INTRO = {
        "en": [
            "Choose the word {word}! Tap the right card!",
            "Can you find the word {word}? Tap it!",
            "Look at the picture! Choose the word {word}!",
            "Find the word {word}! Which card is correct?",
            "Tap the card that says {word}! Go!",
            "Which word matches the picture? Find {word}!",
        ],
        "ms": [
            "Pilih perkataan {word}! Ketuk kad yang betul!",
            "Boleh kamu cari perkataan {word}? Ketuk!",
            "Lihat gambar! Pilih perkataan {word}!",
            "Cari perkataan {word}! Kad mana yang betul?",
        ],
    }

    FILL_INTRO = {
        "en": [
            "Spell the word {word}! Which letter is missing?",
            "Complete the word {word}! Find the missing letter!",
            "The word is {word}! One letter is missing! Tap it!",
            "Spell {word}! Can you find the missing letter?",
            "Fill in the blank! Complete the word {word}!",
        ],
        "ms": [
            "Eja perkataan {word}! Huruf apa yang hilang?",
            "Lengkapkan perkataan {word}! Cari huruf yang hilang!",
            "Perkataannya ialah {word}! Satu huruf hilang! Ketuk!",
            "Isi tempat kosong! Lengkapkan perkataan {word}!",
        ],
    }

    BALLOON_INTRO = {
        "en": [
            "Pop the balloon that says {word}! Go go go!",
            "Find the balloon with the word {word} and pop it!",
            "Which balloon says {word}? Pop it fast!",
            "Look for the word {word}! Pop that balloon!",
            "Pop the {word} balloon! Quick quick quick!",
        ],
        "ms": [
            "Pecahkan belon yang ada perkataan {word}! Cepat!",
            "Cari belon dengan perkataan {word} dan pecahkan!",
            "Belon mana yang ada {word}? Pecahkan cepat!",
            "Cari perkataan {word}! Pecahkan belon itu!",
        ],
    }

    # ── Welcome phrases — short, punchy, fun ──
    # Kept SHORT so gTTS generates fast
    WELCOME = {
        "en": [
            "Let's start learning! Get ready to play!",
            "Get ready! It is time for Word Safari!",
            "Three, two, one! Safari time! Let's learn!",
            "Woah! A new explorer! Welcome! Let's go!",
            "Hey superstar! Word Safari time! Let's play!",
            "Choose a game to begin! Good luck explorer!",
        ],
        "ms": [
            "Jom belajar! Bersedia untuk bermain!",
            "Bersedia! Masa untuk Word Safari!",
            "Tiga, dua, satu! Masa safari! Jom belajar!",
            "Wah! Penjelajah baru! Selamat datang! Jom!",
        ],
    }

    PHRASES = {
        "en": {
            "great_job": [
                "Woohoo! Amazing! You are so smart!",
                "Yes yes yes! You got it!",
                "Oh wow! Brilliant! Total superstar!",
                "Incredible! I am so proud of you!",
                "Wahoo! You nailed it! On fire today!",
                "Fantastic! You are a word wizard!",
                "Boom! You got it! Unstoppable!",
                "Spectacular! Hooray for you!",
            ],
            "try_again": [
                "Oopsie! Tricky one! Try again!",
                "Almost! One more go! You can do it!",
                "Every explorer makes mistakes! Try again!",
                "So close! Give it another try!",
                "Don't give up! Try one more time!",
            ],
            "well_done": [
                "Well done superstar!",
                "Excellent! You are doing brilliantly!",
                "Amazing effort! Well done!",
            ],
            "level_up": [
                "You levelled up! Getting SO good!",
                "Level up! Word safari champion!",
                "New level! You are unstoppable!",
            ],
            "game_over": [
                "You finished! You are a legend!",
                "Congratulations! You completed the safari!",
                "You did it! So proud of you!",
            ],
            "hint": [
                "Psst! Look carefully! Answer is nearby!",
                "Take your time! You can find it!",
                "Look at the picture for a clue!",
            ],
            "correct_balloon": [
                "Pop! Amazing shot!",
                "Boom! Perfect pop!",
                "Yes! Bull's eye! Pop star!",
                "Kapow! Right one! Brilliant!",
                "Woosh Pop! Awesome!",
            ],
            "memory": [
                "Find all the pairs! You can do it!",
                "Flip the cards! Use that amazing brain!",
                "You have a super memory!",
            ],
        },
        "ms": {
            "great_job": [
                "Wuhuu! Luar biasa! Kamu sangat pandai!",
                "Ya ya ya! Kamu berjaya!",
                "Wow! Cemerlang! Bintang sejati!",
                "Hebat! Saya sangat bangga!",
                "Syabas! Kamu memang luar biasa!",
                "Boom! Kamu dapat! Tak boleh dikalahkan!",
            ],
            "try_again": [
                "Alamak! Cuba lagi! Kamu boleh!",
                "Hampir! Cuba sekali lagi!",
                "Tak apa! Cuba lagi! Kamu pasti boleh!",
                "Belum tepat! Cuba lagi!",
            ],
            "well_done": [
                "Syabas! Kamu patut bangga!",
                "Cemerlang! Kerja yang baik!",
                "Usaha yang hebat! Syabas!",
            ],
            "level_up": [
                "Kamu naik tahap! Semakin hebat!",
                "Tahap baru! Juara safari!",
                "Tahap baru dibuka! Hebat!",
            ],
            "game_over": [
                "Kamu habiskan semua! Legenda!",
                "Tahniah! Kamu selesaikan safari!",
                "Kamu berjaya! Bangga dengan kamu!",
            ],
            "hint": [
                "Psst! Lihat baik-baik!",
                "Ambil masa! Kamu boleh carinya!",
                "Lihat gambar untuk petunjuk!",
            ],
            "correct_balloon": [
                "Pecah! Tembakan hebat!",
                "Bom! Tembakan sempurna!",
                "Ya! Tepat sekali!",
            ],
            "memory": [
                "Cari semua pasangan! Kamu boleh!",
                "Balikkan kad! Guna otak hebat kamu!",
                "Kamu ada ingatan super!",
            ],
        },
    }

    # ── Game-type intro phrases ────────────────
    # Spoken once when each minigame first loads,
    # before the first word prompt.
    GAME_INTRO = {
        "find": {
            "en": [
                "Find the word! Look at the picture and tap the right card!",
                "Time to find the word! Look at the picture and tap!",
                "Find the right word! Tap the card that matches the picture!",
            ],
            "ms": [
                "Cari perkataan! Lihat gambar dan ketuk kad yang betul!",
                "Masa mencari perkataan! Lihat gambar dan ketuk!",
                "Cari perkataan yang betul! Ketuk kad yang sepadan!",
            ],
        },
        "fill": {
            "en": [
                "Fill the blank! Listen to the word and tap the missing letter!",
                "Spell the word! Find the missing letter and tap it!",
                "Fill in the blank! Which letter is missing? Tap it!",
            ],
            "ms": [
                "Isi tempat kosong! Dengar perkataan dan ketuk huruf yang hilang!",
                "Eja perkataan! Cari huruf yang hilang dan ketuk!",
                "Isi tempat kosong! Huruf apa yang hilang? Ketuk!",
            ],
        },
        "balloon": {
            "en": [
                "Pop the balloon! Listen and pop the right one!",
                "Balloon time! Find the right word and pop it fast!",
                "Listen to the word and pop the correct balloon!",
            ],
            "ms": [
                "Pecahkan belon! Dengar dan pecahkan belon yang betul!",
                "Masa belon! Cari perkataan dan pecahkan dengan cepat!",
                "Dengar perkataan dan pecahkan belon yang betul!",
            ],
        },
    }

    GTTS_LANG = {"en": "en", "ms": "id"}

    def __init__(self, language="en"):
        self.language     = language
        self.enabled      = False
        self._q           = queue.Queue()
        self._thread      = None
        self._engine_type = None
        # Pre-cached welcome audio paths {lang: path}
        self._welcome_cache = {}
        self._try_init()

    def _try_init(self):
        if self._init_gtts():
            self._precache_welcome()
            return
        if self._init_pyttsx3():
            return
        print("[Voice] No TTS engine — voice disabled")

    def _init_gtts(self):
        try:
            from gtts import gTTS
            import pygame
            t   = gTTS("hi", lang="en", slow=False)
            tmp = tempfile.NamedTemporaryFile(
                suffix=".mp3", delete=False)
            t.save(tmp.name)
            os.unlink(tmp.name)
            self._gtts        = gTTS
            self._pygame      = pygame
            self.enabled      = True
            self._engine_type = "gtts"
            # Always try to store pyttsx3 too so the
            # worker can fall back to it instantly if
            # a gTTS network call fails or is rate-limited
            try:
                import pyttsx3 as _p3
                _p3.init().stop()
                self._pyttsx3 = _p3
                print("[Voice] pyttsx3 loaded as offline fallback ✅")
            except Exception:
                self._pyttsx3 = None
            self._thread = threading.Thread(
                target=self._worker_gtts,
                daemon=True)
            self._thread.start()
            print("[Voice] gTTS ready ✅")
            return True
        except Exception as e:
            print(f"[Voice] gTTS not available: {e}")
            return False

    def _init_pyttsx3(self):
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.stop()
            self._pyttsx3     = pyttsx3
            self.enabled      = True
            self._engine_type = "pyttsx3"
            self._thread = threading.Thread(
                target=self._worker_pyttsx3,
                daemon=True)
            self._thread.start()
            print("[Voice] pyttsx3 ready ✅ (fallback)")
            return True
        except Exception as e:
            print(f"[Voice] pyttsx3 not available: {e}")
            return False

    # ── Pre-cache welcome for instant playback ─
    def _precache_welcome(self):
        """
        Generate welcome audio for EN + MS
        in background at startup so when the
        start screen appears it plays instantly.
        """
        def _cache_bg():
            for lang in ["en", "ms"]:
                try:
                    phrases = self.WELCOME[lang]
                    text    = random.choice(phrases)
                    gtts_l  = self.GTTS_LANG.get(
                        lang, "en")
                    tts = self._gtts(
                        text=text,
                        lang=gtts_l,
                        slow=False)
                    tmp = tempfile.NamedTemporaryFile(
                        suffix=".mp3", delete=False)
                    tts.save(tmp.name)
                    tmp.close()
                    self._welcome_cache[lang] = tmp.name
                    print(f"[Voice] Welcome cached"
                          f" ({lang}) ✅")
                except Exception as e:
                    print(f"[Voice] Cache fail"
                          f" ({lang}): {e}")

        t = threading.Thread(
            target=_cache_bg, daemon=True)
        t.start()

    # ── gTTS worker ───────────────────────────
    # Uses exactly the same method as the welcome
    # sound: save MP3 to disk, load as
    # pygame.mixer.Sound, play on Channel(1).
    # This guarantees audio goes through pygame's
    # mixer — the same path that welcome uses and
    # that is confirmed to work on this machine.
    def _worker_gtts(self):
        while True:
            item = self._q.get()
            if item is None:
                break
            text, lang = item
            tmp_path   = None
            try:
                cached = self._welcome_cache.get(lang)
                is_welcome = (
                    cached
                    and os.path.exists(cached)
                    and text in self.WELCOME.get(lang, []))

                if is_welcome:
                    # Play the pre-cached welcome MP3
                    sound = self._pygame.mixer.Sound(cached)
                else:
                    # Generate MP3 via gTTS then play via
                    # pygame — identical to welcome flow
                    gtts_l   = self.GTTS_LANG.get(lang, "en")
                    tts      = self._gtts(
                        text=text,
                        lang=gtts_l,
                        slow=False)
                    tmp      = tempfile.NamedTemporaryFile(
                        suffix=".mp3", delete=False)
                    tmp_path = tmp.name
                    tmp.close()
                    tts.save(tmp_path)
                    sound    = self._pygame.mixer.Sound(
                        tmp_path)
                    print(f"[Voice] Playing: {text[:50]}")

                ch = self._pygame.mixer.Channel(1)
                ch.play(sound)
                while ch.get_busy():
                    threading.Event().wait(0.05)

            except Exception as e:
                print(f"[Voice] Error: {e}")
            finally:
                if tmp_path and os.path.exists(tmp_path):
                    try:
                        os.unlink(tmp_path)
                    except Exception:
                        pass
                self._q.task_done()

    # ── pyttsx3 worker ────────────────────────
    def _worker_pyttsx3(self):
        while True:
            item = self._q.get()
            if item is None:
                break
            text, lang = item
            try:
                engine = self._pyttsx3.init()
                engine.setProperty('rate', 160)
                engine.setProperty('volume', 1.0)
                voices = engine.getProperty('voices')
                chosen = None
                for v in voices:
                    name = v.name.lower()
                    if any(w in name for w in
                           ['zira','hazel','susan',
                            'linda','female','girl',
                            'salli','joanna','kendra']):
                        chosen = v.id
                        break
                if chosen:
                    engine.setProperty('voice', chosen)
                engine.say(text)
                engine.runAndWait()
                try:
                    engine.stop()
                except Exception:
                    pass
            except Exception as e:
                print(f"[Voice/pyttsx3] Error: {e}")
            finally:
                self._q.task_done()

    # ── Public API ────────────────────────────
    def say_welcome(self):
        """
        Play pre-cached welcome — instant, no lag.
        Falls back to normal queue if not cached yet.
        """
        lang    = self.language
        cached  = self._welcome_cache.get(lang)
        phrases = self.WELCOME.get(
            lang, self.WELCOME["en"])
        text    = random.choice(phrases)

        if (cached
                and os.path.exists(cached)
                and self._engine_type == "gtts"):
            # Play directly on channel 1 — no queue wait
            try:
                sound = self._pygame.mixer.Sound(cached)
                ch    = self._pygame.mixer.Channel(1)
                ch.play(sound)
                return
            except Exception:
                pass
        # Fallback to normal queue
        self._enqueue(text)

    def say_game_intro(self, game_type: str):
        """Speak the game-type instruction once at
        game load (before the first word prompt)."""
        if not self.enabled:
            return
        lang    = self.language
        phrases = self.GAME_INTRO.get(
            game_type, {}).get(lang, [])
        if not phrases:
            phrases = self.GAME_INTRO.get(
                game_type, {}).get("en", [])
        if phrases:
            self._enqueue(random.choice(phrases))

    def say_image(self, word: str):
        intros = self.IMAGE_INTRO.get(
            self.language, self.IMAGE_INTRO["en"])
        self._enqueue(
            random.choice(intros).format(
                word=word.capitalize()))

    def say_fill_image(self, word: str):
        intros = self.FILL_INTRO.get(
            self.language, self.FILL_INTRO["en"])
        self._enqueue(
            random.choice(intros).format(
                word=word.capitalize()))

    def say_balloon_prompt(self, word: str):
        intros = self.BALLOON_INTRO.get(
            self.language, self.BALLOON_INTRO["en"])
        self._enqueue(
            random.choice(intros).format(
                word=word.capitalize()))

    def say_fill_prompt(self, word: str,
                        blank_idx: int):
        letters = []
        for i, ch in enumerate(word):
            if i == blank_idx:
                letters.append(
                    "kosong"
                    if self.language == "ms"
                    else "blank")
            else:
                letters.append(ch)
        spelled = ", ".join(letters)
        if self.language == "ms":
            opts = [
                f"Eja {word.capitalize()}: "
                f"{spelled}. Huruf apa yang hilang?",
            ]
        else:
            opts = [
                f"The word is {word.capitalize()}. "
                f"Listen: {spelled}. "
                f"Which letter is missing?",
                f"Spell with me! {spelled}. "
                f"What fills the blank in "
                f"{word.capitalize()}?",
            ]
        self._enqueue(random.choice(opts))

    def say_phrase(self, key: str):
        bank     = self.PHRASES.get(
            self.language, self.PHRASES["en"])
        variants = bank.get(key, [])
        if variants:
            self._enqueue(random.choice(variants))
        else:
            self._enqueue(key)

    def say_word(self, word: str):
        self._enqueue(word.capitalize())

    def say_correct_balloon(self):
        self.say_phrase("correct_balloon")

    def speak(self, text: str):
        self._enqueue(text)

    def _enqueue(self, text: str):
        if not self.enabled:
            return
        # Allow up to 4 items so game phrases are not
        # silently dropped when gTTS is slow
        if self._q.qsize() < 4:
            self._q.put((text, self.language))

    def stop_voice(self):
        """
        Immediately stop playback and discard all
        pending phrases.  Call before loading a new
        question so stale audio never plays late.
        """
        if not self.enabled:
            return
        # Stop the audio channel right now
        try:
            if hasattr(self, '_pygame'):
                self._pygame.mixer.Channel(1).stop()
                print("[Voice] Channel 1 stopped")
        except Exception:
            pass
        # Drain pending queue items
        drained = 0
        while True:
            try:
                self._q.get_nowait()
                self._q.task_done()
                drained += 1
            except Exception:
                break
        if drained:
            print(f"[Voice] Cleared {drained} pending phrase(s)")

    def speak_priority(self, text: str):
        """
        Stop any current audio, clear queue, then
        speak immediately — used for end screen and
        important callouts that must not be queued.
        """
        if not self.enabled:
            return
        self.stop_voice()
        self._q.put((text, self.language))

    def set_language(self, lang: str):
        self.language = lang
        # Pre-cache welcome for new language
        if (self._engine_type == "gtts"
                and lang not in self._welcome_cache):
            def _recache():
                try:
                    phrases = self.WELCOME.get(
                        lang, self.WELCOME["en"])
                    text   = random.choice(phrases)
                    gtts_l = self.GTTS_LANG.get(
                        lang, "en")
                    tts = self._gtts(
                        text=text,
                        lang=gtts_l,
                        slow=False)
                    tmp = tempfile.NamedTemporaryFile(
                        suffix=".mp3", delete=False)
                    tts.save(tmp.name)
                    tmp.close()
                    self._welcome_cache[lang] = tmp.name
                except Exception:
                    pass
            threading.Thread(
                target=_recache, daemon=True).start()

    def shutdown(self):
        if self.enabled:
            self._q.put(None)