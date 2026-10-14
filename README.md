# Zara's Word Safari

Zara's Word Safari is an educational vocabulary game for children aged 4–6. We built it as a group project for our Artificial Intelligence subject, using Python and Pygame.

The game is made for very young players, so it keeps things simple: easy interaction, colorful visuals and beginner-friendly words. The "AI" part is Zara, an adaptive engine that watches how the child is doing and changes the difficulty, the hints and the retries to match.

<!-- Add a screenshot: save it as screenshot.png in this folder, then remove these comment marks -->
<!-- ![Game screenshot](screenshot.png) -->

## What it does

- Teaches beginner vocabulary through short minigames.
- Adapts to the child with Zara, a rule based AI: it raises or lowers the difficulty, repeats a question with stronger hints, and remembers which words the child finds hard
- Talks to the child and can listen to them, using a voice engine and microphone input
- Gives feedback with sound effects for correct answers, wrong answers, stars, levelling up, popping balloons and clicking, plus quiet looping background music
- Keeps score as the child plays: stars, correct answers, wrong answers, accuracy and streak
- Four screens: start, instructions, the game itself and an end screen
- Starts in English or Malay

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

## Team

Group project for the Artificial Intelligence subject.

**[TODO: add the team members' names and roles.]**