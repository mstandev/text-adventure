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

from js import document, window
from pyodide.ffi import create_proxy

{assignments}

Path("engine.py").write_text(ENGINE_SOURCE)
Path("world.py").write_text(WORLD_SOURCE)
Path("main.py").write_text(MAIN_SOURCE)
sys.path.insert(0, ".")

import main

runtime_status = document.getElementById("runtime-status")
current_location = document.getElementById("current-location")
move_count = document.getElementById("move-count")
command_move_count = document.getElementById("command-move-count")
spinner = document.getElementById("runtime-spinner")
command_form = document.getElementById("command-form")
command_input = document.getElementById("command-input")
send_command = document.getElementById("send-command")
session = main.GameSession(interactive_prompts=False)
ONBOARDING_PLACEHOLDER = "Begin: inspect, n, s"
PRACTICED_PLACEHOLDER = "Type your next move"
PRACTICED_PLACEHOLDER_AFTER = 6
DANGER_WEAPONS = ("sharp axe", "heavy axe")


def capture_output(action, *args):
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        action(*args)
    return stream.getvalue().rstrip()


def append_output(text):
    if not text:
        return
    window.typeGameText(text)


def nearing_bad_ending():
    gs = session.gs
    has_danger_weapon = any(item in gs.inventory for item in DANGER_WEAPONS)
    if gs.game_over or gs.dead_characters:
        return True
    if gs.current_room == "Attic" and has_danger_weapon:
        return True
    if gs.current_room == "Attic" and gs.attic_choice == "disrupt":
        return True
    if gs.ritual_branch == "ash" and has_danger_weapon:
        return True
    return False


def update_interactive_visual_state():
    if nearing_bad_ending():
        document.body.dataset.interactiveState = "danger"
    elif session.gs.trance:
        document.body.dataset.interactiveState = "trance"
    else:
        document.body.dataset.interactiveState = "early"


def update_state_bar(message=None):
    update_interactive_visual_state()
    current_location.textContent = session.current_location()
    move_count.textContent = str(session.move_count)
    move_label = "move" if session.move_count == 1 else "moves"
    command_move_count.textContent = f"{{session.move_count}} {{move_label}}"
    runtime_status.textContent = message or ""


def update_command_placeholder():
    if session.move_count >= PRACTICED_PLACEHOLDER_AFTER:
        command_input.placeholder = PRACTICED_PLACEHOLDER
    else:
        command_input.placeholder = ONBOARDING_PLACEHOLDER


def enable_input():
    spinner.hidden = True
    update_state_bar()
    update_command_placeholder()
    command_input.disabled = False
    send_command.disabled = False
    command_input.focus()


def disable_input(message):
    update_state_bar(message)
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
    update_state_bar()
    update_command_placeholder()

    if session.finished:
        disable_input("Game session ended. Refresh the page to begin again.")
    else:
        command_input.focus()


try:
    update_interactive_visual_state()
    append_output(capture_output(session.start))
    submit_proxy = create_proxy(handle_submit)
    command_form.addEventListener("submit", submit_proxy)
    enable_input()
except Exception as error:
    spinner.hidden = True
    runtime_status.textContent = f"Unable to start PyScript: {{error}}"
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
        <h1>House of Amon</h1>
      </header>

      <section class="location-bar" aria-label="Current game state" hidden>
        <div class="location-group">
          <span class="bar-label">Current Location</span>
          <strong id="current-location">Loading Python...</strong>
        </div>
        <div class="move-group">
          <span class="bar-label">Moves</span>
          <strong id="move-count">0</strong>
        </div>
        <div class="runtime-group" aria-live="polite">
          <span id="runtime-spinner" class="spinner" aria-hidden="true"></span>
          <span id="runtime-status">Loading Python runtime...</span>
        </div>
      </section>

      <section class="output-frame" aria-label="Game output">
        <pre id="game-output"></pre>
      </section>

      <form id="command-form" class="command-panel" aria-label="Game command">
        <div class="command-heading">
          <label for="command-input">What do you do?</label>
          <span id="command-move-count" class="command-move-count">0 moves</span>
        </div>
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
    <script>
      (() => {{
        const output = document.getElementById("game-output");
        const outputFrame = document.querySelector(".output-frame");
        const textQueue = [];
        const typeDelayMs = 2;
        const charsPerTick = 2;
        let outputText = "";
        let typing = false;

        function escapeHtml(text) {{
          return text
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
        }}

        function isMissyLine(line) {{
          return /Missy's (voice|thought)|Missy (whispers|says)|her voice says.*inside your mind/.test(line);
        }}

        // Keep these callouts deliberate: only objects the parser meaningfully handles.
        const interactiveTerms = [
          "AMON nameplate",
          "Amon ancestors",
          "ancestor paintings",
          "ancestor portraits",
          "attic door",
          "back door",
          "barred door",
          "blackened silver candelabrum",
          "blue fire",
          "blue flame",
          "brass gargoyle",
          "brass key",
          "brass knocker",
          "brass lock",
          "brass nameplate",
          "bloodied bandage",
          "bloodied cloth",
          "carved initials",
          "carved message",
          "china cup",
          "china tea cup",
          "china teacup",
          "cold blue flame",
          "cold blue fire",
          "cold fire",
          "cracked window",
          "crooked drawer",
          "crooked headstone",
          "crooked headstones",
          "dark archway",
          "disturbed soil",
          "dull brass lock",
          "empty head chair",
          "family photograph",
          "family photo",
          "floor carving",
          "floor initials",
          "formal invitation",
          "front door",
          "garden door",
          "gargoyle jaw",
          "gargoyle knocker",
          "grave marker",
          "grave dirt",
          "half-open door",
          "hanging tools",
          "hanging utensils",
          "head chair",
          "heavy brass knocker",
          "hearth ash",
          "hearth fire",
          "heavy axe",
          "heavy oak door",
          "hidden carving",
          "invitation card",
          "iron gate",
          "iron gates",
          "keyhole",
          "large ornate keyhole",
          "lidded teapot",
          "long walnut table",
          "loose papers",
          "loose grave dirt",
          "loose soil",
          "narrow nameplate",
          "narrow brass nameplate",
          "oak door",
          "old grave",
          "old headstone",
          "old ledger",
          "old photograph",
          "old writing desk",
          "oil painting",
          "oil paintings",
          "oil portrait",
          "oil portraits",
          "ornate keyhole",
          "pale ash",
          "pale hearth ash",
          "pale scrapes",
          "painted ancestors",
          "painted faces",
          "place settings",
          "porcelain cup",
          "porcelain teacup",
          "rocking chair",
          "ritual book",
          "ritual ledger",
          "ritual teapot",
          "rusted gate",
          "rusted gates",
          "rusted garden blades",
          "rusted iron gate",
          "rusted iron gates",
          "scarred worktable",
          "sealed jar",
          "sealed glass jar",
          "sharp axe",
          "sharp tools",
          "sharpening stone",
          "silver spoon",
          "silver teapot",
          "silver teaspoon",
          "single china teacup",
          "single teacup",
          "small table",
          "small brass key",
          "stone hearth",
          "sunken grave",
          "swollen sideboard",
          "tea cup",
          "thick glass jar",
          "tiny initials",
          "tools on wall",
          "unlabelled jar",
          "unlabelled jars",
          "unlabeled jar",
          "unlabeled jars",
          "violet steam",
          "watching faces",
          "warped wardrobe",
          "warped door",
          "warped shed door",
          "white cloth",
          "white bandage",
          "white teacup",
          "witness jar",
          "writing desk",
          "bandage",
          "candelabrum",
          "carving",
          "drawer",
          "floorboards",
          "gargoyle",
          "hearth",
          "headstones",
          "initials",
          "knocker",
          "lock",
          "marker",
          "nameplate",
          "photograph",
          "portraits",
          "sideboard",
          "steam",
          "teapot",
          "teacup",
          "teacups",
          "workbench"
        ].sort((a, b) => b.length - a.length);

        const interactiveTermPattern = new RegExp(
          "(^|[^A-Za-z0-9_])(" +
            interactiveTerms.map((term) => term.split(" ").join("\\\\s+")).join("|") +
            ")(?=$|[^A-Za-z0-9_])",
          "gi"
        );

        function highlightInteractiveTerms(safeLine) {{
          return safeLine.replace(interactiveTermPattern, (match, prefix, term) => {{
            return prefix + '<span class="interactive-item">' + term + '</span>';
          }});
        }}

        function isWordApostrophe(text, index) {{
          return /[A-Za-z]/.test(text[index - 1] || "") && /[A-Za-z]/.test(text[index + 1] || "");
        }}

        function formatLineWithHighlights(line) {{
          return highlightInteractiveTerms(escapeHtml(line));
        }}

        function formatMissyLine(line) {{
          let html = "";
          let index = 0;
          let inQuote = false;

          for (let i = 0; i < line.length; i += 1) {{
            if (line[i] !== "'" || isWordApostrophe(line, i)) {{
              continue;
            }}

            const chunk = line.slice(index, i);
            html += inQuote
              ? '<span class="missy-quote">' + formatLineWithHighlights(chunk) + '</span>'
              : formatLineWithHighlights(chunk);
            html += escapeHtml("'");
            inQuote = !inQuote;
            index = i + 1;
          }}

          const rest = line.slice(index);
          html += inQuote
            ? '<span class="missy-quote">' + formatLineWithHighlights(rest) + '</span>'
            : formatLineWithHighlights(rest);
          return html;
        }}

        function formatItemsLine(line) {{
          const match = line.match(/^(Items here: )(.+)$/);
          if (!match) {{
            return null;
          }}

          const items = match[2]
            .split(", ")
            .map((item) => '<span class="item-name">' + escapeHtml(item) + '</span>')
            .join(", ");
          return escapeHtml(match[1]) + items;
        }}

        function formatGameText(text) {{
          return text
            .split("\\n")
            .map((line) => {{
              const safeLine = escapeHtml(line);
              if (/^--- .+ ---$/.test(line)) {{
                return '<span class="room-title">' + safeLine + '</span>';
              }}
              if (isMissyLine(line)) {{
                return formatMissyLine(line);
              }}
              const itemsLine = formatItemsLine(line);
              if (itemsLine) {{
                return itemsLine;
              }}
              return formatLineWithHighlights(line);
            }})
            .join("\\n");
        }}

        function scrollOutput() {{
          outputFrame.scrollTop = outputFrame.scrollHeight;
        }}

        function typeNextChunk(text, index) {{
          const nextIndex = Math.min(index + charsPerTick, text.length);
          outputText += text.slice(index, nextIndex);
          output.innerHTML = formatGameText(outputText);
          scrollOutput();

          if (nextIndex < text.length) {{
            window.setTimeout(() => typeNextChunk(text, nextIndex), typeDelayMs);
            return;
          }}

          window.setTimeout(typeNextQueuedText, typeDelayMs);
        }}

        function typeNextQueuedText() {{
          if (!textQueue.length) {{
            typing = false;
            output.classList.remove("is-typing");
            return;
          }}

          typing = true;
          output.classList.add("is-typing");
          const nextText = textQueue.shift();
          const prefix = outputText ? "\\n\\n" : "";
          typeNextChunk(prefix + nextText, 0);
        }}

        window.typeGameText = (text) => {{
          if (!text) {{
            return;
          }}

          textQueue.push(String(text));
          if (!typing) {{
            typeNextQueuedText();
          }}
        }};
      }})();
    </script>
    <script type="py">
{bootstrap}
    </script>
  </body>
</html>
"""


if __name__ == "__main__":
    (ROOT / "index.html").write_text(build_html())
    print("Rebuilt index.html with browser command interface.")
