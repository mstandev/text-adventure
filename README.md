# The House of Amon

A gothic parser-based text adventure about a family estate, a locked attic, a ritual teapot, and the voices the house calls guests.

## Development Note

This project was developed and iterated with assistance from Codex and GPT-5.6, including support for Python implementation, parser behavior, documentation, playtesting, and browser UI refinement.

The current build can be played two ways:

- In a terminal with Python.
- In a browser through the generated PyScript wrapper.

## Play In Python

From this folder, run:

```bash
python3 main.py
```

## Play In The Browser

Play the public browser version here:

[https://mstandev.github.io/text-adventure/](https://mstandev.github.io/text-adventure/)

For local development, open `index.html` in a browser. The page loads the Python runtime, starts the game automatically, and shows a command input labeled `What do you do?`

If your browser blocks the local file, serve the folder locally:

```bash
python3 -m http.server 8000
```

Then open:

```text
http://localhost:8000
```

## Current Game

The playable build includes:

- A compact estate map with the Front Gate, Front Door, Foyer, Living Room, Dining Room, Study, Kitchen, Cellar, Garden, Shed, Upstairs Hallway, Your Bedroom, Attic Landing, and Attic.
- A clear attic access puzzle involving the front-door knocker, brass key, upstairs paintings, hidden carving, attic lock, and attic knock.
- Investigation verbs for inspecting, searching, reading, listening, smelling, and peeking.
- Social commands for talking, asking Grandma or Mother about topics, and showing discovered items.
- Item interaction with taking, dropping, unlocking, moving, turning, using, sharpening, pouring, drinking, and attacking.
- Grounded, full-trance, and weakened-trance perception states.
- A ritual branch where drinking tea differs from using hearth ash against the teapot's steam.
- A witness-jar clue chain involving Mother's bloodied bandage.
- A china teacup and teapot that return to the attic if carried away.
- Missy as an internal voice rather than a visible character.
- Branch-aware bad endings for violent choices.
- A restart command with confirmation.

## Example Commands

```text
help
inspect
n
s
knock door
enter house
search room
read ledger
show photo to mother
move paintings
take brass key
unlock attic door
knock on door
enter attic
drink tea
use bandage on jar
search hearth
use ash on teapot
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

## Project Files

- `main.py`: game session, command handling, puzzle logic, branching states, endings, and move counting.
- `engine.py`: parser, room model, and game state.
- `world.py`: room graph, exits, items, scenery, and room descriptions.
- `build_pyscript_bundle.py`: rebuilds the browser wrapper by embedding the Python sources into `index.html`.
- `web.css`: browser UI styling.
- `index.html`: generated browser version of the game.
- `GAME_DESIGN.md`: current design reference for the implemented build.

When changing Python game logic that should appear in the browser version, rebuild `index.html`:

```bash
python3 build_pyscript_bundle.py
```
