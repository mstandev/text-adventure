from pathlib import Path


ROOT = Path(__file__).parent
SOURCES = {
    "ENGINE_SOURCE": ROOT / "engine.py",
    "WORLD_SOURCE": ROOT / "world.py",
    "MAIN_SOURCE": ROOT / "main.py",
}


def build_bootstrap():
    assignments = "\n".join(
        f"{name} = {path.read_text()!r}"
        for name, path in SOURCES.items()
    )
    return f"""import contextlib
import io
import sys
from pathlib import Path

from js import document
from pyodide.ffi import create_proxy

{assignments}

Path("engine.py").write_text(ENGINE_SOURCE)
Path("world.py").write_text(WORLD_SOURCE)
Path("main.py").write_text(MAIN_SOURCE)
sys.path.insert(0, ".")

import main

output = document.getElementById("game-output")
status = document.getElementById("start-status")
spinner = document.getElementById("runtime-spinner")
command_form = document.getElementById("command-form")
command_input = document.getElementById("command-input")
send_command = document.getElementById("send-command")
session = main.GameSession(interactive_prompts=False)


def capture_output(action, *args):
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        action(*args)
    return stream.getvalue().rstrip()


def append_output(text):
    if not text:
        return
    if output.textContent:
        output.textContent += "\\n\\n"
    output.textContent += text
    output.parentElement.scrollTop = output.parentElement.scrollHeight


def enable_input():
    spinner.hidden = True
    status.textContent = "Game running. Type a command below."
    command_input.disabled = False
    send_command.disabled = False
    command_input.placeholder = "Type a command, for example: north"
    command_input.focus()


def disable_input(message):
    status.textContent = message
    command_input.disabled = True
    send_command.disabled = True


def handle_submit(event):
    event.preventDefault()
    command = command_input.value.strip()
    if not command:
        command_input.focus()
        return

    append_output(f"> {{command}}")
    command_input.value = ""
    append_output(capture_output(session.handle_command, command))

    if session.finished:
        disable_input("Game session ended. Refresh the page to begin again.")
    else:
        command_input.focus()


try:
    append_output(capture_output(session.start))
    submit_proxy = create_proxy(handle_submit)
    command_form.addEventListener("submit", submit_proxy)
    enable_input()
except Exception as error:
    spinner.hidden = True
    status.textContent = f"Unable to start PyScript: {{error}}"
    append_output(f"Unable to start the game: {{error}}")
"""


def build_html():
    bootstrap = build_bootstrap()
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>House of Amon - PyScript</title>
    <link rel="stylesheet" href="https://pyscript.net/releases/2026.3.1/core.css" />
    <link rel="stylesheet" href="./web.css" />
    <script type="module" src="https://pyscript.net/releases/2026.3.1/core.js"></script>
  </head>
  <body>
    <main class="shell">
      <header class="masthead">
        <p class="eyebrow">PyScript branch</p>
        <h1>House of Amon</h1>
        <p class="summary">
          The Python game logic, bundled for the browser.
        </p>
      </header>

      <section class="runtime-note" aria-label="Runtime note">
        This page is self-contained, so it can run from <code>file://</code> or from a local web server.
      </section>

      <section class="start-panel" aria-label="Game status">
        <span id="runtime-spinner" class="spinner" aria-hidden="true"></span>
        <p id="start-status" aria-live="polite">Loading Python runtime...</p>
      </section>

      <section class="output-frame" aria-label="Game output">
        <pre id="game-output"></pre>
      </section>

      <form id="command-form" class="command-panel" aria-label="Game command">
        <label for="command-input">Command</label>
        <div class="command-row">
          <input
            id="command-input"
            type="text"
            autocomplete="off"
            autocapitalize="off"
            spellcheck="false"
            placeholder="Loading Python..."
            disabled
          />
          <button id="send-command" type="submit" disabled>Send</button>
        </div>
      </form>
    </main>
    <script type="py">
{bootstrap}
    </script>
  </body>
</html>
"""


if __name__ == "__main__":
    (ROOT / "index.html").write_text(build_html())
    print("Rebuilt index.html with browser command interface.")
