# ============================================
# test_mic.py
# Run this directly:  python test_mic.py
# It tells you exactly why voice is not working.
# ============================================
import sys

print("=" * 55)
print("  Word Safari — Microphone Diagnostic")
print("=" * 55)

# ── Step 1: check libraries ────────────────────
try:
    import speech_recognition as sr
    print("[✅] speech_recognition installed")
except ImportError:
    print("[❌] speech_recognition NOT installed")
    print("    Fix: pip install SpeechRecognition")
    input("\nPress Enter to exit...")
    sys.exit(1)

try:
    import pyaudio
    print("[✅] pyaudio installed")
except ImportError:
    print("[❌] pyaudio NOT installed")
    print("    Fix: pip install pyaudio")
    input("\nPress Enter to exit...")
    sys.exit(1)

# ── Step 2: list microphone devices ───────────
print("\n--- Microphone devices found ---")
try:
    devices = sr.Microphone.list_microphone_names()
    if not devices:
        print("[❌] No microphone devices found!")
        print("    Check that a microphone is plugged in.")
    else:
        for i, name in enumerate(devices):
            marker = " ← default" if i == 0 else ""
            print(f"  [{i}] {name}{marker}")
except Exception as e:
    print(f"[❌] Cannot list devices: {e}")
    print("    PyAudio may not be installed correctly.")
    input("\nPress Enter to exit...")
    sys.exit(1)

# ── Step 3: open default mic and calibrate ─────
print("\n--- Testing microphone ---")
r = sr.Recognizer()
r.dynamic_energy_threshold = False

try:
    with sr.Microphone() as source:
        print("[✅] Microphone opened successfully")
        print("    Calibrating ambient noise (1 second)...")
        print("    → Stay quiet during calibration")
        r.adjust_for_ambient_noise(source, duration=1)
        ambient = r.energy_threshold
        calibrated = max(150, min(ambient * 1.5, 700))
        r.energy_threshold = calibrated
        print(f"    Ambient energy : {ambient:.0f}")
        print(f"    Set threshold  : {calibrated:.0f}")

        if ambient < 10:
            print("\n[⚠️ ] Ambient energy is near zero.")
            print("    This usually means the microphone")
            print("    is returning silent/empty audio.")
            print("    → Check Windows Privacy settings:")
            print("      Settings → Privacy → Microphone")
            print("      Allow desktop apps to access microphone: ON")
        elif ambient > 500:
            print("\n[⚠️ ] Very noisy environment detected.")
            print("    Try speaking in a quieter place.")

        # ── Step 4: listen ─────────────────────
        print("\n--- Speak now! ---")
        print("    Say any word (you have 7 seconds)...")
        try:
            audio = r.listen(source, timeout=7,
                             phrase_time_limit=6)
            print("[✅] Audio captured!")
        except sr.WaitTimeoutError:
            print("[❌] TIMEOUT — no speech detected.")
            print("\n    Possible causes:")
            print("    1. Windows microphone privacy blocked:")
            print("       Settings → Privacy → Microphone")
            print("       'Allow apps to access your microphone' = ON")
            print("       'Allow desktop apps...' = ON")
            print("    2. Wrong microphone selected above.")
            print("       Try specifying device_index=1 or 2.")
            print("    3. Microphone muted in system tray.")
            input("\nPress Enter to exit...")
            sys.exit(1)

except OSError as e:
    print(f"[❌] Cannot open microphone: {e}")
    print("\n    Possible causes:")
    print("    1. No microphone plugged in")
    print("    2. Another app has exclusive mic access")
    print("    3. PyAudio cannot find an input device")
    input("\nPress Enter to exit...")
    sys.exit(1)

# ── Step 5: send to Google STT ────────────────
print("\n--- Sending to Google Speech Recognition ---")
try:
    text = r.recognize_google(audio, language="en-US")
    print(f"[✅] Google heard: '{text}'")
    print("\n✅ MICROPHONE IS WORKING CORRECTLY")
    print("   The game voice input should work.")
except sr.UnknownValueError:
    print("[❌] Google could not understand the audio.")
    print("    Try speaking more clearly or louder.")
except sr.RequestError as e:
    print(f"[❌] Google STT request failed: {e}")
    print("    Check your internet connection.")

print("\n" + "=" * 55)
input("Press Enter to exit...")
