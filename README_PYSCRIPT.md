# PyScript Browser Wrapper

This branch keeps the Python game intact and runs it inside a browser page with PyScript.

## Run Locally

Open `index.html` in a browser. The page bundles the current Python source into an inline
PyScript bootstrap, so it can run from a `file://` URL. The game starts automatically after
the PyScript runtime is ready.

You can also start a local web server from this repository:

```bash
python3 -m http.server 8000
```

Then open:

```text
http://localhost:8000/index.html
```

PyScript loads from `pyscript.net`, so the browser needs internet access the first time it starts.

## What This Branch Does

- `main.py` still contains the terminal game loop.
- `main.py` exposes a `GameSession` class so the CLI and browser can share the same command logic.
- `index.html` writes bundled copies of `engine.py`, `world.py`, and `main.py` into PyScript's virtual filesystem before importing the game.
- A loading spinner appears while PyScript initializes, then the game starts automatically.
- A browser command box sends each command to the Python `GameSession` and prints the captured output in the page.

When `main.py`, `engine.py`, or `world.py` change, regenerate the inline bundle before publishing this branch:

```bash
python3 build_pyscript_bundle.py
```
