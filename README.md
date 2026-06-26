# The House of Amon

The House of Amon is a gothic parser-based text adventure about a family estate, an attic room, a ritual tea service, and the voices the house calls guests.

The game is written in Python and can be played in either a terminal or a browser. The browser version uses PyScript, but the Python files remain the source of truth.

## Play In Python

From this folder, run:

```bash
python3 main.py
```

## Play In The Browser

Serve the folder locally:

```bash
python3 -m http.server 8000
```

Then open:

```text
http://localhost:8000/index.html
```

Opening `index.html` directly as a local file may be blocked by browser security rules, and PyScript generally behaves more reliably through `localhost`.

## Current Build

The current version includes:

- A 15-room estate map with the front grounds, family rooms, work rooms, cellar, garden, shed, upstairs hall, attic landing, and attic.
- A parser that accepts movement, investigation, inventory, social, ritual, restart, and combat commands.
- State-aware descriptions for grounded play, full trance, weakened trance, and the spell-broken aftermath.
- A layered attic sequence with Grandma, a teapot, a china teacup, and branching player attitudes.
- A witness-jar and ash branch that can weaken the house's hold.
- A spell-broken state that changes the whole map, quiets Missy's internal voice, removes Grandma from the attic, and shows Mother awake in the living room.
- Negative endings for violent choices, with text that reflects the path the player took.
- A browser wrapper with CRT-inspired styling, typed text, move counter, favicon, and state-preserving transcript colors.

## Commands

Try natural parser commands such as:

```text
help
inspect
search
read
listen
smell
talk to mother
ask grandma about tea
show photo to mother
take key
get all
drop spoon
inventory
i
use item on target
restart
quit
```

Short directions work:

```text
n
s
e
w
u
d
```

One puzzle hint: the house responds better to manners than force.

## Browser Notes

The generated browser page is `index.html`. It embeds the current Python sources so the game can run through PyScript.

When changing Python game logic or browser wrapper behavior, rebuild the page:

```bash
python3 build_pyscript_bundle.py
```

Recent browser behavior:

- The game starts automatically after the Python runtime loads.
- The command prompt is labeled `What do you do?`
- Enter/Return and the Send button submit the same command.
- Repeating the same parser-equivalent command does not increase the move counter.
- Text that appears before trance keeps its original color after trance begins.
- New text after trance begins uses the trance color, while later post-trance text can return to the normal color.

## Project Files

- `main.py`: game session, command handling, puzzle logic, branching states, endings, and move counting.
- `engine.py`: parser, room model, and game state.
- `world.py`: room graph, exits, items, scenery, and base room descriptions.
- `build_pyscript_bundle.py`: generates `index.html` by embedding the Python sources.
- `web.css`: browser UI styling.
- `index.html`: generated browser version of the game.
- `favicon.svg` and `favicon.ico`: browser tab icons.
- `GAME_DESIGN.md`: design reference for the current implemented build.
