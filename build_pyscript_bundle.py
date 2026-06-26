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


def transcript_state():
    if session.gs.trance and not session.gs.weakened_trance:
        return "trance"
    if session.gs.trance and session.gs.weakened_trance:
        return "weakened"
    return "early"


def capture_output(action, *args):
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        action(*args)
    return stream.getvalue().rstrip()


def append_output(text):
    if not text:
        return
    window.typeGameText(text, transcript_state())


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
    document.body.dataset.tranceActive = "true" if session.gs.trance else "false"
    document.body.dataset.weakenedTranceActive = "true" if session.gs.weakened_trance else "false"
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
    <link rel="icon" href="./favicon.svg" type="image/svg+xml" />
    <link rel="alternate icon" href="./favicon.ico" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=IM+Fell+DW+Pica&display=swap" rel="stylesheet" />
    <link rel="stylesheet" href="https://pyscript.net/releases/2026.3.1/core.css" />
    <link rel="stylesheet" href="./web.css?v=20260625-transcript-state" />
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
        const transcriptBlocks = [];
        const typeDelayMs = 2;
        const charsPerTick = 2;
        let typing = false;

        function normalizeTranscriptState(state) {{
          if (state === "trance" || state === "weakened") {{
            return state;
          }}
          return "early";
        }}

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

        function hasDialogueQuote(line) {{
          let quoteCount = 0;
          for (let i = 0; i < line.length; i += 1) {{
            if (line[i] === "'" && !isWordApostrophe(line, i) && !isLiteralNameQuote(line, i)) {{
              quoteCount += 1;
            }}
          }}
          return quoteCount >= 2;
        }}

        function isGrandmaLine(line) {{
          const speechVerb = "(?:says|asks|whispers|murmurs|laughs|chuckles|answers|tells)";
          const grandmaAttribution = new RegExp("\\\\bGrandma\\\\s+" + speechVerb + "\\\\b");
          const sheAttribution = new RegExp("\\\\bshe\\\\s+" + speechVerb + "\\\\b");
          if (/Grandma:/.test(line)) {{
            return true;
          }}
          if (/^'/.test(line) && sheAttribution.test(line)) {{
            return true;
          }}
          if (!hasDialogueQuote(line)) {{
            return false;
          }}
          return grandmaAttribution.test(line) ||
            (/\\bGrandma(?:'s)?\\b/.test(line) && sheAttribution.test(line)) ||
            /^Grandma(?:'s)?\\b/.test(line);
        }}

        function isMotherLine(line) {{
          return /Mother(?:'s)? (?:barely|warning|lips|answer|eyes).*'|Mother stirs|Mother is too weak to answer|'.*Mother\s+(?:says|asks|whispers|answers|murmurs)/.test(line);
        }}

        function isSpokenLine(line) {{
          return /(?:voice|whisper|whispers|murmur|murmurs|says|asks|answers|tells|insists|calls|cries|shouts).*'|^'[^']*'[, ]+[^.]*\\b(?:says|asks|whispers|murmurs|answers|tells|insists|calls|cries|shouts)\\b/.test(line);
        }}

        const interactiveTerms = [
          "attic key",
          "big axe",
          "brass key",
          "bloodied bandage",
          "bloodied cloth",
          "cemetery dirt",
          "china tea cup",
          "china cup",
          "china teacup",
          "cold ash",
          "cold brass key",
          "disturbed soil",
          "family photograph",
          "family photo",
          "face down photograph",
          "face down photo",
          "face-down photograph",
          "face-down photo",
          "flat stone",
          "formal invitation",
          "glass jar",
          "grave dirt",
          "grave soil",
          "heavy axe",
          "hearth ash",
          "hearth cinders",
          "household ledger",
          "invitation card",
          "kitchen axe",
          "lidded teapot",
          "loose grave dirt",
          "loose soil",
          "mother's bandage",
          "mothers bandage",
          "old brass key",
          "old invitation",
          "old key",
          "old ledger",
          "old photograph",
          "old photo",
          "oily stone",
          "pale ash",
          "pale cinders",
          "pale hearth ash",
          "photograph",
          "porcelain cup",
          "porcelain teacup",
          "ritual book",
          "ritual ledger",
          "ritual teapot",
          "sealed glass jar",
          "sealed jar",
          "sharp axe",
          "sharp heavy axe",
          "sharpened axe",
          "sharpened heavy axe",
          "sharpening stone",
          "silver spoon",
          "silver teapot",
          "silver teaspoon",
          "single china teacup",
          "single teacup",
          "small brass key",
          "tea cup",
          "tea spoon",
          "thick glass jar",
          "unlabelled jar",
          "unlabeled jar",
          "wet dirt",
          "wet soil",
          "whet stone",
          "whetstone",
          "white bandage",
          "white card",
          "white cloth",
          "white teacup",
          "witness jar",
          "bandage",
          "card",
          "ledger",
          "photo",
          "teacup",
          "teapot"
        ].sort((a, b) => b.length - a.length);

        const interactiveTermPattern = new RegExp(
          "(^|[^A-Za-z0-9_])(" +
            interactiveTerms.map((term) => term.split(" ").join("\\\\s+")).join("|") +
            ")(?=$|[^A-Za-z0-9_])",
          "gi"
        );

        function emphasizeInteractiveObjects(safeLine) {{
          return safeLine.replace(interactiveTermPattern, (match, prefix, term) => {{
            return prefix + '<span class="interactive-object">' + term + '</span>';
          }});
        }}

        function isWordApostrophe(text, index) {{
          return /[A-Za-z]/.test(text[index - 1] || "") && /[A-Za-z]/.test(text[index + 1] || "");
        }}

        function isLiteralNameQuote(text, index) {{
          return text.slice(index, index + 6) === "'THEM'" || text.slice(index - 5, index + 1) === "'THEM'";
        }}

        function formatPlainLine(line) {{
          return emphasizeInteractiveObjects(escapeHtml(line));
        }}

        function formatSpokenLine(line) {{
          let html = "";
          let index = 0;
          let inQuote = false;

          for (let i = 0; i < line.length; i += 1) {{
            if (line[i] !== "'" || isWordApostrophe(line, i) || isLiteralNameQuote(line, i)) {{
              continue;
            }}

            const chunk = line.slice(index, i);
            html += inQuote
              ? '<span class="spoken-quote">' + formatPlainLine(chunk) + '</span>'
              : formatPlainLine(chunk);
            html += escapeHtml("'");
            inQuote = !inQuote;
            index = i + 1;
          }}

          const rest = line.slice(index);
          html += inQuote
            ? '<span class="spoken-quote">' + formatPlainLine(rest) + '</span>'
            : formatPlainLine(rest);
          return html;
        }}

        function formatGameText(text, state) {{
          const blockState = normalizeTranscriptState(state);
          const html = text
            .split("\\n")
            .map((line) => {{
              const safeLine = escapeHtml(line);
              if (/^--- .+ ---$/.test(line)) {{
                return '<span class="room-title">' + safeLine + '</span>';
              }}
              if (/^> /.test(line)) {{
                return '<span class="player-input-line">' + safeLine + '</span>';
              }}
              if (isMissyLine(line)) {{
                return '<span class="missy-line">' + formatSpokenLine(line) + '</span>';
              }}
              if (isMotherLine(line)) {{
                return '<span class="mother-line">' + formatSpokenLine(line) + '</span>';
              }}
              if (isGrandmaLine(line)) {{
                return '<span class="grandma-line">' + formatSpokenLine(line) + '</span>';
              }}
              if (isSpokenLine(line)) {{
                return formatSpokenLine(line);
              }}
              return formatPlainLine(line);
            }})
            .join("\\n");
          return '<span class="transcript-block transcript-block--' + blockState + '">' + html + '</span>';
        }}

        function renderTranscript() {{
          output.innerHTML = transcriptBlocks
            .map((block) => formatGameText(block.text, block.state))
            .join("\\n\\n");
        }}

        function scrollOutput() {{
          outputFrame.scrollTop = outputFrame.scrollHeight;
        }}

        function typeNextChunk(block, text, index) {{
          const nextIndex = Math.min(index + charsPerTick, text.length);
          block.text += text.slice(index, nextIndex);
          renderTranscript();
          scrollOutput();

          if (nextIndex < text.length) {{
            window.setTimeout(() => typeNextChunk(block, text, nextIndex), typeDelayMs);
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
          const nextItem = textQueue.shift();
          const block = {{
            text: "",
            state: normalizeTranscriptState(nextItem.state)
          }};
          transcriptBlocks.push(block);
          typeNextChunk(block, nextItem.text, 0);
        }}

        window.typeGameText = (text, state = "early") => {{
          if (!text) {{
            return;
          }}

          textQueue.push({{
            text: String(text),
            state: normalizeTranscriptState(state)
          }});
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
