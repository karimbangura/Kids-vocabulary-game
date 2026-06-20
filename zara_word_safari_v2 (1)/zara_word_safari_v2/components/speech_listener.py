# ============================================
# components/speech_listener.py
# Non-blocking speech recogniser for Word Safari
#
# FIX: energy threshold now calibrated from
#      ambient noise each time the mic opens
#      (adjust_for_ambient_noise, 0.3 s).
#      Without this, PyAudio on Windows returns
#      audio in a scale where speech energy never
#      exceeds the fixed threshold of 100, causing
#      WaitTimeoutError on every single listen().
#
# FIX: punctuation stripped from result so
#      "book." and "book!" both equal "BOOK".
#
# FIX: matches() uses fuzzy ratio (difflib) so
#      "books" → "book" and near-misses pass.
# ============================================
import threading
import difflib
import string


class SpeechListener:
    """
    Non-blocking speech recogniser.
    Usage:
        sl = SpeechListener()
        sl.start_listening(lang="en")
        # poll sl.is_done in the pygame game loop
        if sl.is_done:
            if sl.matches("CAT"):
                ...
    """

    def __init__(self):
        self.available = False
        self.state     = "idle"   # idle|listening|processing|done
        self.result    = None     # recognized text, UPPER, no punctuation
        self.error     = None     # "timeout"|"unclear"|<msg>
        self._lang     = "en"
        self._lock     = threading.Lock()
        self._gen      = 0        # incremented on every start/reset
                                  # to invalidate stale threads
        try:
            import speech_recognition as sr
            self._sr = sr
            self._r  = sr.Recognizer()
            # pause_threshold: seconds of silence that end a phrase
            self._r.pause_threshold          = 0.6
            # dynamic_energy_threshold: let the recognizer auto-tune
            # during a phrase (keep False so our calibration stays)
            self._r.dynamic_energy_threshold = False
            self.available = True
            print("[Speech] speech_recognition ready ✅")
        except ImportError:
            print("[Speech] speech_recognition not installed — "
                  "pip install SpeechRecognition pyaudio")

    # ── Start listening (non-blocking) ─────────────────────────────
    def start_listening(self, lang="en", timeout=7):
        if not self.available:
            return
        if self.state in ("listening", "processing"):
            return
        with self._lock:
            self._gen  += 1
            gen         = self._gen
            self._lang  = lang
            self.state  = "listening"
            self.result = None
            self.error  = None
        threading.Thread(
            target=self._listen,
            args=(timeout, gen),
            daemon=True).start()

    def reset(self):
        """Discard any in-flight thread result and return to idle."""
        with self._lock:
            self._gen  += 1        # any running thread will see mismatch
            self.state  = "idle"
            self.result = None
            self.error  = None

    # ── Match recognized text against a target word/phrase ─────────
    def matches(self, target: str) -> bool:
        """
        Return True if the recognized text is close enough to target.

        Checks (in order):
        1. Exact match after normalization
        2. Target is a substring of heard  (e.g. "BOOK" in "THE BOOK")
        3. Heard is a substring of target  (partial capture)
        4. Any single word in heard matches target exactly
        5. Multi-word target: all target words appear in heard
        6. Fuzzy ratio ≥ 80 % (difflib.SequenceMatcher)
        7. Any single word in heard has fuzzy ratio ≥ 85 % vs target
        """
        if not self.result:
            return False

        heard  = self.result.upper().strip()
        tgt    = target.upper().strip()

        # 1. Exact
        if heard == tgt:
            print(f"[Speech] ✅ MATCH (exact): '{heard}' == '{tgt}'")
            return True

        # 2. Target inside heard  ("BOOK" in "THE BOOK")
        if tgt in heard:
            print(f"[Speech] ✅ MATCH (target⊂heard): '{tgt}' in '{heard}'")
            return True

        # 3. Heard inside target  ("BOO" in "BOOK" — partial capture)
        if heard in tgt and len(heard) >= max(2, len(tgt) - 2):
            print(f"[Speech] ✅ MATCH (heard⊂target): '{heard}' in '{tgt}'")
            return True

        heard_words = heard.split()

        # 4. Any single word in heard equals target exactly
        if tgt in heard_words:
            print(f"[Speech] ✅ MATCH (word exact): '{tgt}' in words {heard_words}")
            return True

        # 5. Multi-word target (e.g. KAPAL TERBANG)
        tgt_words = tgt.split()
        if len(tgt_words) > 1 and all(w in heard for w in tgt_words):
            print(f"[Speech] ✅ MATCH (multi-word): all {tgt_words} in '{heard}'")
            return True

        # 6. Full-string fuzzy
        ratio = difflib.SequenceMatcher(None, heard, tgt).ratio()
        print(f"[Speech] Fuzzy (full): '{heard}' vs '{tgt}' → {ratio:.0%}")
        if ratio >= 0.80:
            print(f"[Speech] ✅ MATCH (fuzzy full {ratio:.0%})")
            return True

        # 7. Per-word fuzzy  (handles "BOOKS" vs "BOOK", "BUKU" vs "BUKU.")
        for w in heard_words:
            wr = difflib.SequenceMatcher(None, w, tgt).ratio()
            if wr >= 0.85:
                print(f"[Speech] ✅ MATCH (fuzzy word '{w}' {wr:.0%} vs '{tgt}')")
                return True

        print(f"[Speech] ❌ NO MATCH: heard='{heard}' expected='{tgt}'")
        return False

    # ── Convenience: compare a single character ─────────────────────
    def matches_letter(self, letter: str) -> bool:
        """
        True if the recognized text contains the target letter.
        Handles:
          "T" → "T"   (exact single char)
          "THE LETTER T" → last/any single-char word == letter
          "TEE" / "SEE" etc. → first char of first word
        """
        if not self.result:
            return False
        letter = letter.upper().strip()
        heard  = self.result.upper().strip()

        # Single-character result
        if heard == letter:
            print(f"[Speech] ✅ LETTER MATCH (exact): '{heard}'")
            return True

        # Any word that is exactly the target letter
        for w in heard.split():
            if w == letter:
                print(f"[Speech] ✅ LETTER MATCH (word): '{w}' in '{heard}'")
                return True

        # First character of first recognized word
        first_char = heard.split()[0][0] if heard else ""
        if first_char == letter:
            print(f"[Speech] ✅ LETTER MATCH (first char): '{first_char}' in '{heard}'")
            return True

        # Last character of last word (catches "tee" → "T")
        last_word = heard.split()[-1] if heard else ""
        if last_word and last_word[-1] == letter:
            print(f"[Speech] ✅ LETTER MATCH (last char): '{last_word}[-1]' in '{heard}'")
            return True

        print(f"[Speech] ❌ NO LETTER MATCH: heard='{heard}' expected='{letter}'")
        return False

    # ── State properties ─────────────────────────────────────────────
    @property
    def is_idle(self):
        return self.state == "idle"

    @property
    def is_listening(self):
        return self.state == "listening"

    @property
    def is_processing(self):
        return self.state == "processing"

    @property
    def is_done(self):
        return self.state == "done"

    # ── Worker thread ────────────────────────────────────────────────
    def _listen(self, timeout, gen):
        """
        Run in a daemon thread.  Never touch pygame here.

        Uses direct PyAudio fixed-duration recording instead of
        sr.Recognizer.listen() to bypass the energy-threshold mechanism
        that causes WaitTimeoutError on Windows even when the mic works.
        Records exactly RECORD_SECS seconds of audio unconditionally,
        saves to a temp WAV, then sends to Google STT.
        """
        import pyaudio
        import wave
        import tempfile
        import os

        RATE        = 16000
        CHANNELS    = 1
        FORMAT      = pyaudio.paInt16
        CHUNK       = 1024
        RECORD_SECS = 4          # always record this many seconds

        def _set(state, result=None, error=None):
            with self._lock:
                if self._gen != gen:
                    print("[Speech] Thread is stale — discarding result")
                    return
                self.state  = state
                self.result = result
                self.error  = error

        tmp_path = None
        pa       = None
        stream   = None
        try:
            pa = pyaudio.PyAudio()
            stream = pa.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
            )
            print(f"[Speech] Recording {RECORD_SECS}s of audio...")
            frames = []
            num_chunks = int(RATE / CHUNK * RECORD_SECS)
            for _ in range(num_chunks):
                with self._lock:
                    if self._gen != gen:
                        print("[Speech] Thread is stale — stopping early")
                        return
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)
            print("[Speech] Recording done — saving WAV...")
        except Exception as e:
            _set("done", error=str(e))
            print(f"[Speech] ❌ PyAudio error: {e}")
            return
        finally:
            if stream:
                try:
                    stream.stop_stream()
                    stream.close()
                except Exception:
                    pass
            if pa:
                try:
                    pa.terminate()
                except Exception:
                    pass

        # Save raw frames to a temp WAV file
        try:
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            tmp_path = tmp.name
            tmp.close()
            with wave.open(tmp_path, "wb") as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(2)          # paInt16 → 2 bytes
                wf.setframerate(RATE)
                wf.writeframes(b"".join(frames))
        except Exception as e:
            _set("done", error=str(e))
            print(f"[Speech] ❌ WAV save error: {e}")
            return

        # Send to Google STT via sr.AudioFile
        try:
            _set("processing")
            with self._sr.AudioFile(tmp_path) as source:
                audio = self._r.record(source)

            lang_code = "id-ID" if self._lang == "ms" else "en-US"
            print("[Speech] Sending to Google STT...")
            raw_text = self._r.recognize_google(audio, language=lang_code)

            clean = (raw_text
                     .translate(str.maketrans('', '', string.punctuation))
                     .upper()
                     .strip())
            print(f"[Speech] Raw:        '{raw_text}'")
            print(f"[Speech] Normalized: '{clean}'")
            _set("done", result=clean)

        except self._sr.UnknownValueError:
            _set("done", error="unclear")
            print("[Speech] 🔇 Google could not understand the audio")
        except self._sr.RequestError as e:
            _set("done", error=str(e))
            print(f"[Speech] ❌ Google STT request error: {e}")
        except Exception as e:
            _set("done", error=str(e))
            print(f"[Speech] ❌ STT error: {e}")
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass
