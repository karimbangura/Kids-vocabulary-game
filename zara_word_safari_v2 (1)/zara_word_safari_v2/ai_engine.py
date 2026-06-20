# ============================================
# ai_engine.py
# ZaraAI — Rule-based adaptive engine
# Tracks mistakes, adjusts difficulty,
# and signals when to RETRY same question
# ============================================

MAX_TRIES_PER_QUESTION = 3   # retries before moving on


class ZaraAI:
    """
    Adaptive AI engine.
    Monitors child performance in real time.
    Adjusts difficulty and hints automatically.

    NEW: tracks per-question attempt count so
    minigames can repeat the same question
    with escalating hints before moving on.
    """

    def __init__(self):
        self.reset()

    def reset(self):
        self.difficulty          = 1
        self.consecutive_wrong   = 0
        self.consecutive_correct = 0
        self.total_correct       = 0
        self.total_wrong         = 0
        self.hint_level          = 0
        self.mistake_log         = {}
        self.bonus_unlocked      = False
        self.session_log         = []

        # ── Per-question retry tracking ───────
        self.current_word        = ""
        self.attempts_this_q     = 0   # wrong tries on current question
        self.should_retry        = False  # minigame reads this

    def new_question(self, word: str):
        """
        Call when a brand-new question starts
        (not a retry). Resets attempt counter.
        """
        self.current_word    = word
        self.attempts_this_q = 0
        self.should_retry    = False

    def update(self, is_correct: bool,
               word: str = ""):
        self.session_log.append({
            "word"      : word,
            "correct"   : is_correct,
            "difficulty": self.difficulty,
        })
        if is_correct:
            self._handle_correct()
        else:
            self._handle_wrong(word)

    def _handle_correct(self):
        self.consecutive_wrong    = 0
        self.consecutive_correct += 1
        self.total_correct       += 1
        self.attempts_this_q     = 0
        self.should_retry        = False

        # Level up after 3 correct in a row
        if self.consecutive_correct >= 3:
            if self.difficulty < 3:
                self.difficulty += 1
            self.consecutive_correct = 0
            self.hint_level          = 0

        # Unlock bonus every 5 total correct answers
        if self.total_correct > 0 and self.total_correct % 5 == 0:
            self.bonus_unlocked = True

    def _handle_wrong(self, word: str):
        self.consecutive_correct  = 0
        self.consecutive_wrong   += 1
        self.total_wrong         += 1
        self.attempts_this_q     += 1

        # Log mistake
        if word:
            self.mistake_log[word] = (
                self.mistake_log.get(word, 0) + 1)

        # ── Decide: retry or move on ──────────
        if self.attempts_this_q < MAX_TRIES_PER_QUESTION:
            # Still has tries left — repeat question
            self.should_retry = True
        else:
            # Used all tries — move to next question
            self.should_retry        = False
            self.attempts_this_q     = 0

        # ── Escalate hints per wrong attempt ──
        # Attempt 1 wrong → hint level 1 (glow)
        # Attempt 2 wrong → hint level 2 (arrow)
        # Attempt 3 wrong → hint level 3 (fewer choices)
        if self.attempts_this_q == 1:
            self.hint_level = max(self.hint_level, 1)
        elif self.attempts_this_q == 2:
            self.hint_level = max(self.hint_level, 2)
        elif self.attempts_this_q >= 3:
            self.hint_level = max(self.hint_level, 3)

        # Drop difficulty after too many consecutive
        # wrong across questions
        if self.consecutive_wrong >= 4:
            self.difficulty        = max(1, self.difficulty - 1)
            self.consecutive_wrong = 0

    # ── Getters ──────────────────────────────
    def get_hint_level(self)      -> int:
        return self.hint_level

    def get_difficulty(self)      -> int:
        return self.difficulty

    def get_attempts(self)        -> int:
        """How many wrong tries on current question."""
        return self.attempts_this_q

    def get_tries_left(self)      -> int:
        return max(0,
                   MAX_TRIES_PER_QUESTION
                   - self.attempts_this_q)

    def get_weak_words(self)      -> list:
        return [w for w, c
                in self.mistake_log.items()
                if c >= 2]

    def should_unlock_bonus(self) -> bool:
        return self.bonus_unlocked

    def get_summary(self)         -> dict:
        return {
            "total_correct": self.total_correct,
            "total_wrong"  : self.total_wrong,
            "difficulty"   : self.difficulty,
            "weak_words"   : self.get_weak_words(),
        }
