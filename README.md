# The House of Amon

A command-line text adventure inspired by classic interactive fiction like Zork.

You explore the Amon estate, collect items, inspect strange scenery, unlock rooms, and uncover what Grandma has been preparing in the upper attic.

## How to play

From this folder, run:

```bash
python3 main.py
```

Type commands such as:

```text
help
look
north
knock door
search
smell tea
read portraits
ask grandma about tea
show key to grandma
move portraits
take brass key
inventory
drop spoon
unlock attic
use stone on axe
drink tea
quit
```

Short directions work too:

```text
n
s
e
w
u
d
```

## Files

- `main.py` runs the game loop and handles player actions.
- `engine.py` contains the parser, room model, and game state.
- `world.py` defines the rooms, exits, items, and descriptions.

## Current status

This is an early playable prototype. The core loop works, including movement, examining scenery, taking and dropping items, room searching, listening, talking, unlocking the attic, inventory, item use, and the trance state.
