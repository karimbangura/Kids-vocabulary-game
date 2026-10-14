# Zara's Word Safari

Zara's Word Safari is an educational vocabulary game for children aged 4–6. We built it as a group project for our Artificial Intelligence subject, using Python and Pygame.

The game is made for very young players, so it keeps things simple: easy interaction, colorful visuals and beginner-friendly words. The "AI" part is Zara, an adaptive engine that watches how the child is doing and changes the difficulty, the hints and the retries to match.

<!-- Add a screenshot: save it as screenshot.png in this folder, then remove these comment marks -->
<!-- ![Game screenshot](screenshot.png) -->

## What it does

- Teaches beginner vocabulary through short minigames. **[TODO: list the minigames and the word categories, for example animals, colors or fruit.]**
- Adapts to the child with Zara, a rule-based AI: it raises or lowers the difficulty, repeats a question with stronger hints, and remembers which words the child finds hard
- Talks to the child and can listen to them, using a voice engine and microphone input
- Gives feedback with sound effects for correct answers, wrong answers, stars, levelling up, popping balloons and clicking, plus quiet looping background music
- Keeps score as the child plays: stars, correct answers, wrong answers, accuracy and streak
- Four screens: start, instructions, the game itself and an end screen
- Starts in English

## How Zara (the AI) works

Zara is a **rule-based adaptive engine** (`ai_engine.py`). It doesn't use machine learning. It follows a small set of fixed rules and updates itself after every answer.

| What happens | What Zara does |
|---|---|
| The child answers wrong | Repeats the same question, up to **3 tries**. After the third wrong try it moves on to the next question |
| First wrong try on a question | Hint level 1: the right answer **glows** |
| Second wrong try on a question | Hint level 2: an **arrow** points to the right answer |
| 3 correct answers in a row | Difficulty goes **up** by 1 (the highest level is 3), and the hint level resets to 0 |
| 4 wrong answers in a row | Difficulty goes **down** by 1 (the lowest level is 1) |
| Total correct answers reach 5, 10, 15 and so on | The **bonus** is unlocked |
| The same word is wrong 2 or more times | The word is saved as a **weak word** |

Some details worth knowing:

- Difficulty starts at level 1.
- Hints stay at their highest level until the child levels up, so they carry over to the next questions instead of switching off after one right answer.
- The bonus switch stays on once it has been turned on. Only `reset()` clears it.
- Every answer is saved in a session log with the word, whether it was correct, and the difficulty at that moment.

The minigames talk to Zara through a few simple calls:

| Call | What it does |
|---|---|
| `new_question(word)` | Starts a brand-new question and resets the try counter |
| `update(is_correct, word)` | Tells Zara the child's answer, and Zara applies the rules above |
| `should_retry` | Becomes `True` when the same question should be shown again |
| `get_hint_level()` | Returns 0 to 2: no hint, glow or arrow |
| `get_difficulty()` | Returns the current difficulty, 1 to 3 |
| `get_attempts()` and `get_tries_left()` | Wrong tries so far, and tries remaining on this question |
| `get_weak_words()` | Words the child got wrong at least twice |
| `should_unlock_bonus()` | `True` once the bonus is unlocked |
| `get_summary()` | Total correct, total wrong, difficulty and weak words |
| `reset()` | Starts everything again from zero |

## How to run

1. Install Python 3. **[TODO: add the version you used, for example 3.11.]**
2. Install the libraries:
   ```
   pip install pygame SpeechRecognition pyaudio
   ```
   **[TODO: add any other package the voice engine needs to speak, if there is one. If you don't have a requirements.txt yet, `pip freeze > requirements.txt` makes one.]**
3. Plug in a microphone, and check that it works (see the next section).
4. Start the game:
   ```
   python main.py
   ```

You can run it from PyCharm or from a terminal. `main.py` switches to its own folder when it starts, so the asset paths work no matter where you launch it from.

If something goes wrong, the error and its traceback are printed and the window waits for you to press Enter, so you have time to read it.

## How to play

**[TODO: explain the controls (mouse, keyboard, voice or all three) and how a round works, step by step. The game has voice input, so say where the child speaks.]**

## Microphone test

The game can listen to the child, so the microphone has to work. We made a test script to find out why it isn't working:

```
python test_mic.py
```

It goes through five steps and tells you which one fails:

1. Checks that `SpeechRecognition` and `pyaudio` are installed
2. Lists the microphones it can find
3. Opens the default microphone and listens to the background noise for 1 second, so stay quiet
4. Waits up to 7 seconds for you to say a word
5. Sends what it heard to Google Speech Recognition and prints the words it understood

Because step 5 uses Google Speech Recognition, it needs an internet connection.

Common fixes the script suggests:

- **Windows privacy settings:** go to Settings → Privacy → Microphone and turn on access for apps and for desktop apps
- **Wrong microphone:** check the list from step 2. If the default isn't the right one, try `device_index=1` or `2`
- **Muted microphone:** check the volume icon in the system tray
- **Microphone in use:** close other apps that might be using it
- **Too noisy:** try again somewhere quieter
- **Not understood:** speak louder and more clearly

## Project structure

```
zaras-word-safari/
├── main.py                  entry point and game manager
├── settings.py              shared settings (window size, FPS, title, colors)
├── ai_engine.py             ZaraAI, the adaptive engine
├── test_mic.py              microphone diagnostic
├── generate_music.py        creates the sound files if they are missing
├── components/
│   └── voice.py             VoiceEngine, the voice part of the game
├── screens/
│   ├── start_screen.py      StartScreen
│   ├── instruction_screen.py   InstructionScreen
│   ├── game_screen.py       GameScreen
│   └── end_screen.py        EndScreen
└── assets/
    └── sounds/
        ├── sfx/             correct, wrong, star, level_up, balloon_pop, click (.wav)
        └── music/           background.wav (or background.mp3)
```

**[TODO: add any other files or folders, such as images, fonts or word lists, and check that the file names above match your project.]**

## Sounds

The game looks for these files:

| File | Sound for |
|---|---|
| `assets/sounds/sfx/correct.wav` | a correct answer |
| `assets/sounds/sfx/wrong.wav` | a wrong answer |
| `assets/sounds/sfx/star.wav` | earning a star |
| `assets/sounds/sfx/level_up.wav` | levelling up |
| `assets/sounds/sfx/balloon_pop.wav` | popping a balloon |
| `assets/sounds/sfx/click.wav` | clicking a button |
| `assets/sounds/music/background.wav` or `background.mp3` | background music |

If a sound file is missing, the game prints `[Sound] Missing: ...` and keeps running without it. It won't crash. Run `generate_music.py` to create the missing files.

The music loops at a low volume (0.25) so it doesn't cover the voice.

## How the game is built

Everything is controlled by one class, `GameManager`, in `main.py`. It owns the window, Zara, the voice engine, the stars, the score and whichever screen is showing.

- **Screens.** `switch_screen()` swaps between `"start"`, `"instructions"`, `"game"` and `"end"`. Each screen is its own class with three methods: `handle_event()`, `update()` and `draw()`. The screens are only imported when they are first needed.
- **Main loop.** Every frame it passes the events to the current screen, updates it, fills the background green, draws the screen and flips the display. Then it waits to keep the frame rate steady.
- **Score.** `GameManager` keeps `score_correct`, `score_wrong`, `score_accuracy` and `score_streak`. The game screen fills them in as the child plays, and `add_stars()` adds to the star count.
- **Audio.** The mixer runs at 44.1 kHz with 8 channels. Channel 0 plays sound effects and channel 1 plays the voice, so a sound effect never cuts off the voice. The other channels are spare.
- **Voice.** The voice engine is created before the sounds load, so it can start preparing the welcome line straight away.
- **Quitting.** When you close the window, the voice engine is shut down first and then Pygame closes.

## Settings

`settings.py` holds the shared values the game imports, such as `SCREEN_WIDTH`, `SCREEN_HEIGHT`, `TITLE`, `FPS` and `GREEN_BG`. **[TODO: list any other settings people might want to change.]**

## Customizing

- **Window size and speed:** change `SCREEN_WIDTH`, `SCREEN_HEIGHT` and `FPS` in `settings.py`.
- **Background color:** change `GREEN_BG` in `settings.py`.
- **Tries per question:** change `MAX_TRIES_PER_QUESTION` at the top of `ai_engine.py`.
- **How fast the difficulty changes:** the numbers are written directly in the code. The 3 correct answers in a row for levelling up is in `_handle_correct()`, the 4 wrong answers in a row for dropping down is in `_handle_wrong()`, and the bonus every 5 correct answers is in `_handle_correct()`.
- **Music volume:** change the number in `pygame.mixer.music.set_volume(0.25)` inside `_load_sounds()` in `main.py`.
- **Your own sounds:** replace a file in `assets/sounds` with another one that has the same name.

## Troubleshooting

- **No sound:** look in the console for `[Sound] Missing`. If you see it, run `generate_music.py`, or check that the files are in `assets/sounds/sfx` and `assets/sounds/music`.
- **The game can't hear the child:** run `python test_mic.py` and follow the fix it suggests.
- **The window closes straight away:** run the game from a terminal, or read the error that waits on screen for Enter.

## Team

Group project for the Artificial Intelligence subject.

**[TODO: add the team members' names and roles.]**