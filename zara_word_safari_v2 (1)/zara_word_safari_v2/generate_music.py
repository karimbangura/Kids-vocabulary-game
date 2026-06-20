# ============================================
# generate_music.py
# Run this ONCE to generate all game music
# and sound effects into assets/sounds/
# No downloads needed — pure Python!
# ============================================
import numpy as np
import wave
import struct
import os
import math

RATE = 44100

def save_wav(filename, data, rate=RATE):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    data = np.clip(data, -32767, 32767).astype(np.int16)
    with wave.open(filename, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(rate)
        f.writeframes(data.tobytes())
    print(f"  ✅ {filename}")

def tone(freq, duration, vol=0.5, wave_type="sine",
         rate=RATE, attack=0.01, decay=0.05):
    t   = np.linspace(0, duration, int(rate * duration), False)
    if wave_type == "sine":
        w = np.sin(2 * np.pi * freq * t)
    elif wave_type == "square":
        w = np.sign(np.sin(2 * np.pi * freq * t))
    elif wave_type == "triangle":
        w = 2 * np.abs(2 * (t * freq - np.floor(t * freq + 0.5))) - 1
    elif wave_type == "sawtooth":
        w = 2 * (t * freq - np.floor(t * freq + 0.5))
    else:
        w = np.sin(2 * np.pi * freq * t)

    # Envelope
    env = np.ones_like(t)
    att = int(attack * rate)
    dec = int(decay * rate)
    if att > 0:
        env[:att] = np.linspace(0, 1, att)
    if dec > 0 and dec < len(env):
        env[-dec:] = np.linspace(1, 0, dec)

    return (w * env * vol * 32767).astype(np.float64)

def silence(duration, rate=RATE):
    return np.zeros(int(rate * duration))

def concat(*parts):
    return np.concatenate(parts)

# ── Notes helper ─────────────────────────────
NOTE = {
    'C4':261.63,'D4':293.66,'E4':329.63,
    'F4':349.23,'G4':392.00,'A4':440.00,
    'B4':493.88,'C5':523.25,'D5':587.33,
    'E5':659.25,'F5':698.46,'G5':783.99,
    'A5':880.00,'B5':987.77,'C6':1046.50,
    'G3':196.00,'A3':220.00,'B3':246.94,
    'REST':0,
}

def melody_note(name, dur, vol=0.45,
                wave_type="sine"):
    if name == 'REST' or NOTE.get(name,0) == 0:
        return silence(dur)
    return tone(NOTE[name], dur, vol=vol,
                wave_type=wave_type,
                attack=0.02, decay=0.08)

# ════════════════════════════════════════════
# 1. BACKGROUND MUSIC
#    Bouncy, cheerful children's game tune
#    ~60 seconds, loops seamlessly
# ════════════════════════════════════════════
print("\n🎵 Generating background music...")

def make_background():
    bpm   = 132
    beat  = 60 / bpm
    half  = beat / 2
    qtr   = beat / 4

    # Main melody — bright and bouncy
    melody_seq = [
        ('C5', beat), ('E5', beat), ('G5', beat), ('E5', beat),
        ('D5', beat), ('F5', beat), ('A5', beat), ('F5', beat),
        ('C5', beat), ('E5', beat), ('G5', beat), ('A5', beat),
        ('G5', half), ('F5', half), ('E5', beat), ('D5', beat),
        ('E5', beat), ('G5', beat), ('B4', beat), ('C5', beat),
        ('D5', beat), ('G4', beat), ('A4', beat), ('B4', beat),
        ('C5', beat*2), ('REST', beat), ('C5', beat),
        ('E5', beat), ('D5', beat), ('C5', beat), ('B4', beat),
    ]

    # Counter melody (harmony layer)
    harmony_seq = [
        ('G4', beat), ('G4', beat), ('B4', beat), ('G4', beat),
        ('A4', beat), ('A4', beat), ('C5', beat), ('A4', beat),
        ('G4', beat), ('G4', beat), ('B4', beat), ('C5', beat),
        ('B4', half), ('A4', half), ('G4', beat), ('F4', beat),
        ('G4', beat), ('B4', beat), ('G3', beat), ('G4', beat),
        ('F4', beat), ('E4', beat), ('F4', beat), ('G4', beat),
        ('E4', beat*2), ('REST', beat), ('E4', beat),
        ('G4', beat), ('F4', beat), ('E4', beat), ('D4', beat),
    ]

    # Bass line — punchy
    bass_seq = [
        ('C4', half), ('REST', half),
        ('E4', half), ('REST', half),
        ('D4', half), ('REST', half),
        ('F4', half), ('REST', half),
    ] * 4

    mel  = concat(*[melody_note(n, d, 0.40, "sine")
                    for n, d in melody_seq])
    har  = concat(*[melody_note(n, d, 0.25, "triangle")
                    for n, d in harmony_seq])
    bas  = concat(*[melody_note(n, d, 0.30, "square")
                    for n, d in bass_seq])

    # Pad to same length
    max_len = max(len(mel), len(har), len(bas))
    mel  = np.pad(mel,  (0, max_len - len(mel)))
    har  = np.pad(har,  (0, max_len - len(har)))
    bas  = np.pad(bas,  (0, max_len - len(bas)))

    # Repeat 3x for a longer loop
    track = (mel + har + bas) * 3
    track = np.tile(track, 1)

    # Gentle fade in/out for seamless loop
    fade = int(0.3 * RATE)
    track[:fade] *= np.linspace(0, 1, fade)
    track[-fade:] *= np.linspace(1, 0, fade)

    return track

bg = make_background()
save_wav("assets/sounds/music/background.wav", bg)

# ════════════════════════════════════════════
# 2. CELEBRATION MUSIC (end screen)
#    Big fanfare — triumphant and fun
# ════════════════════════════════════════════
print("🎺 Generating celebration music...")

def make_celebration():
    fanfare = [
        ('C5', 0.12), ('E5', 0.12), ('G5', 0.12),
        ('C6', 0.40), ('REST', 0.08),
        ('C6', 0.15), ('B5', 0.15), ('A5', 0.15),
        ('G5', 0.35), ('REST', 0.08),
        ('E5', 0.12), ('G5', 0.12), ('B5', 0.12),
        ('C6', 0.50), ('REST', 0.15),
        ('G5', 0.12), ('A5', 0.12), ('B5', 0.12),
        ('C6', 0.12), ('B5', 0.12), ('A5', 0.12),
        ('G5', 0.50), ('REST', 0.15),
        ('C5', 0.10), ('E5', 0.10), ('G5', 0.10),
        ('C6', 0.10), ('E6', 0.10),
        ('C6', 0.60),
    ]
    mel = concat(*[melody_note(n, d, 0.55, "sine")
                   for n, d in fanfare])
    har = concat(*[melody_note(n, d, 0.30, "triangle")
                   for n, d in [
                       ('E4',0.12),('G4',0.12),('B4',0.12),
                       ('E5',0.40),('REST',0.08),
                       ('E5',0.15),('D5',0.15),('C5',0.15),
                       ('B4',0.35),('REST',0.08),
                       ('G4',0.12),('B4',0.12),('D5',0.12),
                       ('E5',0.50),('REST',0.15),
                       ('B4',0.12),('C5',0.12),('D5',0.12),
                       ('E5',0.12),('D5',0.12),('C5',0.12),
                       ('B4',0.50),('REST',0.15),
                       ('E4',0.10),('G4',0.10),('B4',0.10),
                       ('E5',0.10),('G5',0.10),
                       ('E5',0.60),
                   ]])
    max_l = max(len(mel), len(har))
    mel = np.pad(mel, (0, max_l - len(mel)))
    har = np.pad(har, (0, max_l - len(har)))
    track = np.tile(mel + har, 4)
    fade  = int(0.2 * RATE)
    track[-fade:] *= np.linspace(1, 0, fade)
    return track

cel = make_celebration()
save_wav("assets/sounds/music/celebration.wav", cel)

# ════════════════════════════════════════════
# 3. SOUND EFFECTS
# ════════════════════════════════════════════
print("🔊 Generating sound effects...")

os.makedirs("assets/sounds/sfx", exist_ok=True)

# ── Correct answer — happy ascending chime ──
correct = concat(
    tone(523, 0.10, 0.6, "sine"),
    tone(659, 0.10, 0.6, "sine"),
    tone(784, 0.18, 0.7, "sine"),
)
save_wav("assets/sounds/sfx/correct.wav", correct)

# ── Star collected — sparkle ─────────────────
star = concat(
    tone(880,  0.08, 0.5, "sine"),
    tone(1047, 0.08, 0.5, "sine"),
    tone(1319, 0.08, 0.6, "sine"),
    tone(1568, 0.15, 0.6, "sine"),
    silence(0.05),
    tone(1568, 0.08, 0.4, "sine"),
)
save_wav("assets/sounds/sfx/star.wav", star)

# ── Wrong answer — low thud ──────────────────
wrong_note = tone(150, 0.25, 0.55, "square")
wrong_note += tone(120, 0.25, 0.3, "sine")
save_wav("assets/sounds/sfx/wrong.wav", wrong_note)

# ── Click — short, crisp ──────────────────────
click = tone(800, 0.06, 0.4, "sine")
save_wav("assets/sounds/sfx/click.wav", click)

# ── Level up — ascending fanfare ─────────────
level_up = concat(
    tone(392,  0.09, 0.5, "sine"),
    tone(523,  0.09, 0.5, "sine"),
    tone(659,  0.09, 0.5, "sine"),
    tone(784,  0.09, 0.5, "sine"),
    tone(1047, 0.25, 0.65, "sine"),
    silence(0.04),
    tone(1047, 0.15, 0.5, "sine"),
)
save_wav("assets/sounds/sfx/level_up.wav", level_up)

# ── Balloon pop — satisfying burst ───────────
t_pop = np.linspace(0, 0.18, int(RATE*0.18))
noise = np.random.uniform(-1, 1, len(t_pop))
env   = np.exp(-t_pop * 22)
pop   = noise * env * 0.7 * 32767
save_wav("assets/sounds/sfx/balloon_pop.wav", pop)

print("\n✅ All audio generated successfully!")
print("📁 Files saved to assets/sounds/")
