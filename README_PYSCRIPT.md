# PyScript Browser Wrapper

This branch keeps the Python game intact and runs it inside a browser terminal with PyScript.

## Run Locally

Start a local web server from this repository:

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
- `engine.py` and `world.py` are loaded into PyScript's virtual filesystem through `pyscript.json`.
- `index.html` embeds the game in a PyScript terminal using the `terminal worker` mode, so `input()` works in the browser without freezing the page.
