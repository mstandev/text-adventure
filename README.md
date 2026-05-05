# The House of Amon

A command-line text adventure inspired by classic interactive fiction like Zork.

You explore the Amon estate, collect items, inspect strange scenery, unlock rooms, and uncover what Grandma has been brewing.

## How to play

From this folder, run:

```bash
python3 main.py
```

Type commands such as:

```text
look
north
knock door
take brass key
inventory
unlock attic
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

This is an early playable prototype. The core loop works, including movement, examining scenery, taking items, unlocking the attic, inventory, and the trance state.
