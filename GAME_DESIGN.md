# The House of Amon

## Design Intent

The House of Amon is a short-to-medium gothic parser adventure about returning to a decaying family estate where household etiquette, memory, blood, and invitation have become supernatural rules.

The horror should feel intimate rather than epic. Rooms are ordinary family spaces first: a foyer, a living room, a dining room, a bedroom, a kitchen, a cellar, a garden, and an attic. The house becomes frightening because those familiar spaces begin to behave as if they remember roles the family has tried to forget.

## Current Build Summary

The current build is playable in Python and in the browser through a generated PyScript wrapper.

The game currently includes:

- A 15-room map.
- A broad parser command set.
- Discovery-gated clues and state-aware room text.
- A layered attic encounter with Grandma, tea, a teapot, and a china teacup.
- Grounded, full-trance, weakened-trance, and spell-broken states.
- Missy as an internal voice rather than a visible character.
- Mother as a vulnerable family figure who can become awake and healed after the spell breaks.
- Branch-aware bad endings for violent choices.
- A browser interface with CRT-inspired styling, typed output, move counter, state-preserving transcript colors, and favicon support.

## Source Of Truth

The Python game is the source of truth.

- `main.py`: session loop, command handling, state transitions, endings, special room text, and browser-compatible game session behavior.
- `engine.py`: parser, room model, and `GameState`.
- `world.py`: room graph, room descriptions, exits, scenery, and starting items.
- `build_pyscript_bundle.py`: generates `index.html` by embedding the Python sources and browser runtime code.
- `web.css`: browser presentation.
- `index.html`: generated browser artifact.
- `favicon.svg` and `favicon.ico`: browser tab icons.

When Python or wrapper behavior changes, rebuild:

```bash
python3 build_pyscript_bundle.py
```

## Core Pillars

### Family Horror

The danger is personal. The house uses family roles, rooms, keepsakes, manners, and guilt as pressure points.

### Ritual Logic

The supernatural should follow rules that feel symbolic but consistent. Objects matter because of what they prove, remember, or invite.

### Shifting Perception

The house is not described the same way in every state. Player perception changes as the ritual gains or loses authority.

### Discovery Before Guidance

The game should not mention a solution object, clue, or relationship before the player has found the source that makes it knowable.

### Consequences Over Combat

Violence is supported by the parser, but it is not framed as the clean heroic solution. The game should respond to violent player intent without rewarding it as the default best path.

## Map

Current room graph:

- Front Gate: north to Front Door, south to Cemetery.
- Cemetery: north to Front Gate.
- Front Door: south to Front Gate, north to Foyer once opened.
- Foyer: south to Front Door, north to Kitchen, west to Living Room, east to Dining Room, up to Upstairs Hallway.
- Living Room: east to Foyer, north to Study.
- Dining Room: west to Foyer.
- Study: south to Living Room.
- Kitchen: south to Foyer, east to Garden, down to Cellar.
- Cellar: up to Kitchen.
- Garden: west to Kitchen, north to Shed.
- Shed: south to Garden.
- Upstairs Hallway: down to Foyer, west to Your Bedroom, up to Attic Landing.
- Your Bedroom: east to Upstairs Hallway.
- Attic Landing: down to Upstairs Hallway, north to Attic once access is granted.
- Attic: south or down to Attic Landing.

Important map rules:

- The attic is reached through a narrow stair and landing, not by a ladder.
- The Study is reached through the Living Room.
- The teapot and china teacup belong to the attic; if carried away, they return to the attic and are removed from inventory with a notification.

## Player-Facing Hint Policy

The game can include layered clues, but documentation should avoid spoiling the puzzle chain.

The README contains the single allowed public puzzle hint. Avoid adding additional puzzle hints to project documentation unless the user explicitly asks for a spoiler version.

## Command Design

The parser supports:

- Movement: compass words, short directions, `go`, `enter`, and `exit`.
- Investigation: `look`, `inspect`, `examine`, `peek`, `search`, `read`, `listen`, and `smell`.
- Inventory: `take`, `get`, `get all`, `drop`, `inventory`, and `i`.
- Social interaction: `talk`, `ask <person> about <topic>`, and `show <item> to <person>`.
- Object interaction: `open`, `close`, `move`, `turn`, `push`, `pull`, `knock`, `unlock`, and `use <item> on <target>`.
- Ritual and action verbs: `drink`, `pour`, `spill`, `light`, `sharpen`, and combat verbs.
- Global commands: `help`, `restart`, and `quit`.

Design standards:

- Support likely natural phrasings instead of requiring one exact command.
- Give specific responses for visible scenery, even when it cannot be taken.
- Do not say a visible important object is absent just because it is scenery instead of inventory.
- Treat repeated parser-equivalent commands as the same move for browser move counting.
- Keep `help` practical without giving away puzzle solutions.

## State Model

### Grounded

The default state. The house is disturbing, but the descriptions are still mostly physical and literal.

### Full Trance

Begins after the attic tea is accepted. The house becomes more openly supernatural, room descriptions shift, sensory verbs reveal more, and some clues become mechanically available.

### Weakened Trance

Begins after the teapot's steam is interrupted with the correct ritual countermeasure while already in trance. The house remains strange, but its control has loosened.

### Spell Broken

Begins after the ash branch is completed and the player reaches a release point outside the attic's immediate pressure. The state:

- Turns off trance and weakened-trance text coloring.
- Replaces room descriptions across the map with calmer post-spell descriptions.
- Removes Grandma from the attic.
- Shows Mother awake in the Living Room.
- Stops Missy's internal voice events.
- Makes listening and social interactions reflect quiet rather than active haunting.

The spell-broken state currently lets the player continue walking the map so the changed house can be inspected.

## Attic And Tea Sequence

The attic is the game's central pressure chamber.

Implemented elements:

- Grandma sits in the rocking chair.
- A small table holds the teapot and china teacup.
- The teacup can be taken.
- The teapot can pour into the teacup as part of the drinking interaction.
- The teacup can hold dark tea, and inventory text reflects that when carried.
- The first attic encounter supports compliance, questioning, and disruption as different attitudes.
- Grandma can answer questions about several topics, with branch-aware responses.
- The attic text changes when the teapot or teacup has been taken, filled, returned, or disturbed.

The goal is for the player to feel that drinking tea is not just a command, but a choice about consent, curiosity, and participation.

## Witness, Ash, And Release

The mid-game ritual branch is built around discovering what the house is using and how to interrupt it.

Current design behavior:

- The sealed jar cannot be broken.
- The jar can become a witness when approached with the correct kind of proof.
- The ash branch depends on trance perception.
- Hearth ash is ordinary before the player has the right perception state.
- Once used successfully, ash weakens the trance rather than immediately ending all danger.
- The final release happens after the player reaches a calmer threshold away from the attic's immediate pressure.

This branch now has a hopeful aftermath: Mother is awake, Grandma is gone from the attic, Missy's voice no longer needs to guide the player from inside the mind, and the house is described as lighter and calmer.

## Characters

### Grandma

Grandma is manipulative, theatrical, intimate, and dangerous. She uses etiquette, affection, shame, and ritual language to make obedience feel like belonging.

After the spell breaks, she is no longer present in the attic.

### Mother

Mother begins weak and nearly unreachable in the Living Room. She is tied to family evidence, warning, and survival rather than combat.

After the spell breaks, she sits awake on the sofa. Her post-spell dialogue should feel tired, clear, and relieved without becoming artificially cheerful.

### Missy

Missy is a voice in the player's mind, not a visible body. She warns, nudges, and grieves. She cannot be attacked or inspected as a physical entity.

After the spell breaks, she stops speaking in the player's mind. The silence should read as rest rather than abandonment.

### The Player

The player is vulnerable but active. Supported attitudes include curiosity, obedience, doubt, disruption, refusal, and violence. The game should notice those choices.

### Amon

Amon is deliberately unresolved: a name, a household identity, a ritual opening, and something older than the visible building. The design should avoid overexplaining it.

## Combat And Endings

Combat verbs exist so players can express violent intent, but violent choices generally create bad outcomes.

Current bad ending families:

- Attacking Mother.
- Attacking Grandma before understanding what protects her.
- Killing Grandma after weakening the ritual, which removes the visible authority but leaves a deeper problem.

Current hopeful outcome:

- The ash branch can break the spell and shift the entire house into a calmer aftermath.

Design rule: endings should reflect what the player actually did, including whether they complied, questioned, discovered the witness, carried ash, attacked, or protected someone.

## Browser Experience

The browser version should feel like a playable retro terminal, not a separate game.

Current behavior:

- PyScript loads the embedded Python game.
- A spinner displays while the runtime loads.
- The game starts automatically.
- The command input is labeled `What do you do?`
- Enter/Return and the Send button submit the same command.
- A move counter appears above the Send button.
- Text appears with a fast typed effect.
- The transcript preserves the color state of each output block, so text printed before trance does not change color when trance begins.
- The current-location bar is preserved in code but hidden for now.
- The page includes SVG and ICO favicon links.

Current visual direction:

- Warm dark gray page background.
- CRT-inspired output frame.
- Monospaced game text.
- Gothic title styling.
- Yellow-orange title and accent color.
- Player command lines use a distinct green before trance and gold during trance.
- Missy's spoken lines use purple and italicized speech.
- Grandma and Mother speech have distinct colors, with Grandma shifting red in trance.

## Item And Object Notes

Important implemented items:

- Brass key.
- Heavy axe.
- Sharp axe.
- Sharpening stone.
- Silver spoon.
- Family photograph.
- Bloodied bandage.
- Grave dirt.
- Ritual ledger.
- Invitation card.
- Teapot.
- China teacup.
- Hearth ash.
- Sealed jar.

State-aware object rules:

- Taken objects should no longer appear in room search text as if still present.
- The bandage should disappear from Mother descriptions once taken.
- The Study should stop mentioning documents that have already been picked up.
- The bedroom key is hidden until the relevant room feature is moved.
- The teapot and teacup return to the attic if carried away.
- The teacup can contain tea, and inventory text should say so.

Currently low-use or future-use items:

- Silver spoon.
- Grave dirt.

These can remain as atmosphere for now, but future versions should either give them clear roles or document them intentionally as optional flavor.

## Originality Direction

The current build still uses Amon, Grandma, Mother, Missy, tea, and attic terminology. The project should continue moving toward its own mythology before any broad public release.

Recommended originality work:

- Change names and relationship details on a dedicated branch first.
- Keep the house mythology centered on original symbols, documents, and family history.
- Avoid reproducing exact album scene order or causality.
- Preserve the emotional structure of occult family horror while changing plot mechanisms.
- Maintain `greywake-alternate-story` as the branch for alternate naming and story experiments.

## Completed Work

- Expanded parser commands.
- Added family and document rooms.
- Built the attic landing and attic access sequence.
- Added the trance system.
- Added the teapot, teacup, tea-pouring, and attic-return behavior.
- Added witness, ash, weakened trance, and spell-broken states.
- Added combat verbs and branch-aware bad endings.
- Added a browser wrapper through PyScript.
- Added CRT-inspired browser UI styling.
- Added move counting and repeated-command handling.
- Added transcript colors that preserve the state of older text.
- Added favicon support.
- Reworked post-spell descriptions across the whole map.

## Recommended Next Work

1. Add lightweight automated playthrough tests for core routes and state transitions.
2. Decide whether the spell-broken state should eventually end the game automatically or remain explorable.
3. Give the silver spoon and grave dirt a clear purpose, or mark them as flavor.
4. Continue originality work on a separate branch.
5. Add save/load only after the main structure stabilizes.
