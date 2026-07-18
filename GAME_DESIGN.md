# The House of Amon

## Premise

A young protagonist returns to a decaying family house where Grandma has resumed strange nightly rituals involving tea, blood, and 'THEM'. The house amplifies memory, guilt, obedience, and invitation. The player explores the estate, learns the rules of the ritual, chooses how closely to obey Grandma, and discovers that violence alone does not solve what the house has become.

The tone should remain gothic, intimate, claustrophobic, and dreamlike. The horror comes from household spaces turning ceremonial: doors that prefer manners, rooms that remember family roles, and ordinary objects that become proof, invitation, or warning.

## Design Goals

- Build a short-to-medium parser adventure with strong horror atmosphere.
- Keep the Python parser game as the source of truth.
- Provide a browser presentation layer that lets the same Python game play through PyScript.
- Use a compact, readable map where rooms change meaning as the player learns more.
- Make the house feel like an active force rather than a passive setting.
- Let puzzles emerge from ritual logic, family relationships, and altered perception.
- Avoid dead ends caused by hidden exact wording, missing optional clues, or early player mistakes.
- Keep future originality work available without losing the current Amon build.

## Development Note

The current build was developed and iterated with assistance from Codex and GPT-5.6. That assistance has included Python implementation, parser expansion, puzzle design review, documentation updates, browser UI refinement, and playthrough-based testing.

## Current Build Snapshot

The current build is a playable Python parser adventure with a PyScript browser wrapper.

Core files:

- `main.py`: game session, command handling, branching scenes, puzzle logic, state-aware room text, combat endings, restart confirmation, and browser-friendly move counting.
- `engine.py`: parser, `Room`, and `GameState`.
- `world.py`: room graph, base descriptions, trance descriptions, scenery, exits, and starting items.
- `build_pyscript_bundle.py`: generates `index.html` by embedding the Python sources into the browser page.
- `web.css`: browser UI styling.
- `index.html`: generated browser page. Do not hand-edit when changing Python or wrapper behavior; rebuild it with `build_pyscript_bundle.py`.

Branch notes:

- `pyscript-wrapper` is the active browser-playable branch.
- `greywake-alternate-story` preserves an alternate renamed story experiment.
- The active build currently uses the Amon, Grandma, Mother, Missy, tea, teapot, and attic terminology.

The current build supports:

- A broad parser command set for movement, investigation, social interaction, item use, combat, restart, and help.
- A map that includes the Dining Room, Study, Attic Landing, Garden, Shed, Cellar, Your Bedroom, and Attic.
- A clear attic access puzzle chain that works even if the player never finds the invitation card.
- Grounded, full-trance, and weakened-trance perception states.
- A ritual branch where obedient tea drinking differs from ash-smothering the teapot.
- A witness-jar clue chain for the ash branch.
- A china teacup beside the teapot, with both ritual objects returning to the attic if carried away.
- Combat verbs with negative, path-aware outcomes.
- Missy as an internal voice or spiritual presence, not an attackable body.
- Discovery-gated clueing, so the game avoids mentioning puzzle clues before the player has found the relevant object, room feature, witness, or conversation source.
- Browser UI callouts for specific interactive nouns and clues.

## Browser Experience

The browser version runs the Python game through PyScript. The page starts the game after the Python runtime loads and shows a spinner while loading.

Current interface:

- Title: `House of Amon`.
- Output area: fast type-on text effect for new game output.
- Input label: `What do you do?`
- Placeholder starts as `Begin: inspect, n, s`, then changes after early moves to `Type your next move`.
- Send button and Enter/Return submission use the same form behavior.
- A move counter appears above the Send button, aligned with the input label.
- The hidden current-location bar remains preserved in the generated page for possible later reuse.

Move counter rules:

- Count meaningful parser moves, not repeated mistakes.
- Consecutive parser-equivalent repeats do not increment the counter. For example, repeating `n`, `north`, or `N` should count as the same attempted move.
- Equivalent phrasing such as `knock door` and `knock on door` should also avoid duplicate counting when repeated consecutively.

Browser styling rules:

- The UI uses a warm dark gray background, yellowed text, and a clean modern wrapper.
- Room titles are bold and slightly larger than body text.
- The game title uses the same warm interactive color family as puzzle clues and collectible items.
- Items listed under `Items here:` use the interactive item color.
- Specific interactive nouns and clues are highlighted, not every possible noun.
- Default interactive color is warm orange-yellow.
- Trance interactive color shifts slightly redder.
- Near bad-ending states animate interactive text with an RGB/rainbow scan, limited to font color treatment.
- Missy lines remain normal narrative text except for Missy's quoted words, which are italicized.

## Core Pillars

### 1. Family Horror

The danger is intimate. The most disturbing events happen between relatives, in bedrooms, kitchens, dining rooms, and hallways.

### 2. Ritual Logic

The supernatural follows rules. Blood, objects, rooms, names, invitation, etiquette, and perception matter.

### 3. Shifting Perception

The player sees one version of the house while grounded, another while in full trance, and a third weakened version after the ash interrupts the ritual.

### 4. Player Complicity

The player should feel tempted by forbidden knowledge and comfort, not only threatened by it.

### 5. Discovery Before Guidance

The game should not guide the player toward an object, clue, or solution until the player has discovered the relevant source. Clues can be layered, but they must be earned.

## Narrative Shape

### Act 1: Arrival

Goal: enter the house and learn that the house responds to etiquette.

What happens:

- The player arrives at the estate at night.
- The Front Gate subtly teaches basic parser interaction and directions.
- The front door is barred from inside.
- The knocker and AMON nameplate establish that the door expects ritualized entry.
- Missy can begin to exist as a voice inside thought rather than a visible person.

Player questions:

- Why is the house named Amon?
- Why does the front door behave like a listener?
- Why does force seem less useful than manners?

Puzzle beats:

- Move from Front Gate to Front Door.
- Inspect the door, knocker, gargoyle, or nameplate if needed.
- Knock on or use the knocker to open the house.
- Enter the house through the opened front door.

### Act 2: The House Teaches You

Goal: explore family spaces and learn the hidden rules.

What happens:

- Mother is weak in the Living Room.
- The Study contains documents that clarify invitation, blood, and the house's record-keeping.
- The Dining Room contains family evidence and floor clues.
- The Upstairs Hallway portraits point toward the attic stair and conceal a hidden carving.
- Your Bedroom contains the brass key.
- The Cellar contains the sealed jar, which cannot be broken.
- The Kitchen, Garden, and Shed provide practical items and later trance clues.

Player questions:

- What exactly does the tea do?
- Are 'THEM' guests, memories, spirits, witnesses, or all of those?
- What object anchors the ritual?
- What does Mother still know?

Puzzle beats:

- Find the brass key.
- Move or search the upstairs paintings to reveal the hidden carving.
- Learn that the attic wants both a key and a ritualized knock.
- Optionally find the invitation card and ritual ledger for extra context.
- Optionally collect the photograph and show it to Mother for additional clueing.

### Act 3: The Attic Ritual

Goal: enter the attic and choose how to meet Grandma's ceremony.

What happens:

- Grandma sits in the rocking chair.
- The table holds the teapot and china teacup.
- The teacup turns itself toward the player and the teapot pours into it when the player drinks.
- The first encounter supports comply, question, and disrupt attitudes.
- Drinking tea creates full trance and reveals the house's deeper structure.

Player questions:

- Is drinking tea obedience, entry, contamination, or knowledge?
- Can questions change Grandma's control of the room?
- Can the ritual be interrupted without making things worse?

Puzzle beats:

- `drink tea`, `drink from cup`, or similar tea/cup commands begin the obedient path.
- Asking Grandma about Mother, Missy, tea, Amon, the house, ancestors, company, guests, or 'THEM' sets or reinforces the question path.
- Pouring or spilling the tea, attacking, or using hearth ash can move the scene into disruption.

### Act 4: The Ash Branch

Goal: learn the ritual weakness and interrupt the teapot's steam.

What happens:

- The witness jar explains that feeding the teapot opens Amon.
- Hearth ash only becomes meaningful while the player is in full trance.
- Searching the Kitchen in full trance reveals the ash.
- Casting the ash across the teapot's steam in the Attic smothers the ritual breath.
- The trance weakens, but the house is not defeated.

Player questions:

- What is Amon: the house, the name, the ritual, or something behind all three?
- Does smothering the steam save anyone, or only change who is in control?
- What remains after Grandma's authority is weakened?

Puzzle beats:

- Take Mother's bloodied bandage.
- Use the bloodied bandage on the sealed jar in the Cellar.
- Receive the witness clue.
- Drink tea to enter full trance.
- Search the Kitchen to reveal hearth ash.
- Take hearth ash.
- Return to the Attic.
- Use, cast, scatter, or put hearth ash on/across the teapot, tea, steam, or violet steam.

### Act 5: Reckoning

Goal: decide what to do after the ritual is changed.

Current status:

- The build currently has strong bad endings and branch-aware consequences.
- The ash branch weakens the ritual but does not yet provide a complete satisfying non-bad ending.
- Killing Grandma after ash is possible, but it is still a bad ending because 'THEM' remain.
- Violence is framed as understandable but insufficient.

Future endings to design:

- A non-bad ash ending that preserves evidence, protects Mother or Missy, and escapes the house's immediate claim.
- A refusal ending where the player leaves after learning enough, haunted but alive.
- A containment ending involving the witness jar, ledger, ash, or cemetery.
- A darker inheritance ending where the player knowingly takes Grandma's role.

## Current Map

The implemented room graph is:

- Front Gate: north to Front Door, south to Cemetery.
- Cemetery: north to Front Gate.
- Front Door: south to Front Gate, north to Foyer after the door is opened.
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
- Attic Landing: down to Upstairs Hallway, north to Attic after the attic sequence is completed.
- Attic: south or down to Attic Landing.

Important map rules:

- The attic is reached by a narrow stair to the Attic Landing, not by a ladder.
- The attic door is on the landing and opens north into the attic.
- The Study is reached from the Living Room.
- The invitation card is useful clue material, but is not required for attic access.
- The teapot and china teacup belong to the attic. If the player carries either out, the object returns to Grandma's table and the inventory reports feeling lighter.

## Current Command Design

The parser recognizes:

- Movement: `go`, compass directions, `n`, `s`, `e`, `w`, `u`, `d`, `enter`, `exit`.
- Investigation: `look`, `examine`, `inspect`, `peek`, `search`, `read`, `listen`, `smell`.
- Inventory: `take`, `get`, `drop`, `inventory`.
- Social commands: `talk`, `ask <person> about <topic>`, `show <item> to <person>`.
- Object interaction: `open`, `close`, `move`, `turn`, `push`, `pull`, `knock`, `unlock`, `use <item> on <target>`.
- Ritual and action verbs: `drink`, `pour`, `spill`, `light`, `sharpen`, `attack`.
- Global commands: `help`, `restart`, `quit`.

Useful supported variations:

- `knock door`, `knock on door`, `knock at door`, `use knocker`.
- `enter house`, `enter attic`, `go north` from the Attic Landing after the door opens.
- `show photo to mother`, `show mother photo`, `show photograph mother`.
- `inspect photo` and `read photo`.
- `sharpen axe`, `hone axe`, `whet axe`, `use stone on axe`, `use axe on stone`.
- `look behind paintings`, `search behind portraits`, `move paintings`, `turn painting`, `straighten portraits`.
- `inspect hearth`, `inspect fire`, `inspect blue flame`, `search hearth`, `search fire`.
- `exit` in the Shed sends the player south to the Garden.

Design rule for responses:

- If the player names visible scenery, give a specific response even when the object cannot be taken.
- Avoid saying "There is no X here" for important visible room features like the candelabrum, hearth, tools, workbench, paintings, doors, keyhole, floor runes, flame, grave, or nameplate.
- If the player attacks a recognized noun that is not a meaningful combat target, answer with `You can't attack the [noun].`
- Do not reveal an undiscovered clue, object, or puzzle solution before the player has encountered the relevant source.

## Current Item Design

Practical items:

- Brass key: found in Your Bedroom; required for the attic door.
- Heavy axe: found in Kitchen.
- Sharpening stone: found in Shed.
- Sharp axe: created by sharpening the heavy axe with the sharpening stone.
- Silver spoon: found in Kitchen; currently mostly flavor and potential future puzzle material.

Family items:

- Family photograph: found face-down in the Dining Room until taken.
- Bloodied bandage: taken from Mother's hand in the Living Room.
- Grave dirt: found in the Cemetery.

Ritual and document items:

- Teapot: found in the Attic; can be taken, but returns to the attic if carried away.
- China teacup: found in the Attic; can be taken, but returns to the attic if carried away.
- Ritual ledger: found in the Study.
- Invitation card: found in the Study.
- Hearth ash: found by searching the Kitchen while in full trance.
- Sealed jar: found in the Cellar; cannot be broken.

State-aware item notes:

- Once the family photograph is taken, Dining Room search and sideboard descriptions no longer show it as present.
- Once the bandage is taken, Living Room descriptions mention Mother's exposed hand instead of the bandage.
- Once the ledger and invitation card are taken, Study descriptions stop presenting them as still waiting in the room.
- Once the teacup is taken, Attic descriptions show the missing cup-ring.
- Once the teapot is taken, Attic descriptions show the missing teapot or a bare table.
- If the teapot or teacup leaves the Attic, it returns to the Attic and is removed from inventory with an explicit message.

## Current Attic Access Puzzle

The intended sequence is:

1. At the Front Door, knock on the gargoyle knocker to open the house.
2. Enter the house and explore the family rooms.
3. Find the brass key in Your Bedroom.
4. In the Upstairs Hallway, look behind, search behind, move, or turn the paintings.
5. Find the hidden carving: "Let invited blood knock, and the listening room shall answer."
6. Go up the narrow stair to the Attic Landing.
7. Unlock the attic door with the brass key.
8. Knock on the attic door.
9. Go north or enter attic.

Current clue sources:

- The Front Door teaches that knocking matters.
- The AMON nameplate implies the house has a name and expects address.
- The Upstairs Hallway paintings subtly point toward the attic stair.
- Moving the paintings reveals the hidden carving.
- The Attic Landing keyhole shows flickering light, the edge of a rocking chair, and a small table with something pale on top.
- The invitation card reinforces etiquette, but the sequence still works without it.

## Current Trance System

There are three perception states:

- Grounded: the house is unsettling but mostly physical and literal.
- Full trance: begins after the player drinks tea in the Attic. Rooms reveal supernatural structure, stronger sensory clues, ritual meanings, and the hearth ash.
- Weakened trance: begins when the player smothers the teapot's steam with hearth ash while already in trance. The supernatural remains visible, but the house has less authority over perception.

Trance affects:

- Room descriptions.
- Inventory descriptions.
- Movement text.
- Search, listen, smell, read, examine, talk, ask, use, drink, and error responses.
- Browser interactive word color.
- Clue availability, especially hearth ash and deeper cellar/study meanings.

Mechanically actionable trance clues:

- Searching Kitchen in full trance reveals hearth ash as a takeable item.
- Inspecting, smelling, or listening around the hearth in trance makes the ash feel ritually different from ordinary ash.
- Reading or searching the Cellar in trance points toward the witness jar.
- Asking Mother about the bandage or Missy can suggest that blood still answers where speech cannot.
- Showing hearth ash to Grandma while in trance makes the steam visibly recoil.
- Listening in the Attic after learning the witness clue can reinforce that the steam, not the metal teapot, is the vulnerable part.

Important trance rule:

- Hearth ash is not useful before drinking tea. If the player tries to use ash on the teapot before full trance, Grandma tells them: "Tea first, dear. Then symbols learn to bite."

## Current Ritual Branching

The first Attic encounter presents three meaningful attitudes:

- Comply: drink the tea and enter the obedient path.
- Question too far: ask Grandma about Mother, Missy, the tea, Amon, the house, ancestors, company, guests, or 'THEM'.
- Disrupt: pour or spill the tea, attack, or use hearth ash against the steam.

Obedient tea path:

- `drink tea`, `drink cup`, or related cup/tea commands in the Attic set the player into full trance.
- The teapot pours into the china teacup as part of the drinking description.
- The room becomes more welcoming and dangerous.
- 'THEM' accept the player as a participant.

Ash-smothering path:

- The player must learn about the witness jar and hearth ash.
- Use Mother's bloodied bandage on the sealed jar in the Cellar to awaken the witness.
- The witness explains that the teapot feeds Amon through steam and that hearth ash can interrupt the ritual.
- Search the Kitchen while in full trance to find hearth ash.
- Use or cast hearth ash on the teapot, tea, steam, or violet steam in the Attic.
- The teapot is not destroyed outright; its steam is smothered and the ritual branch changes to ash.
- If the player was in full trance, this changes the state to weakened trance.

Witness jar rule:

- The jar cannot be smashed, cracked, or broken, even with the axe.
- The jar responds to bloodline evidence, specifically Mother's bloodied bandage.
- The witness clue currently says: "When the teapot is fed, Amon opens. When the teapot is choked, cast hearth ash across the steam or 'THEM' will keep drinking from the air."

Teapot and teacup rule:

- The teapot and china teacup can be taken, but the attic reclaims them.
- Leaving the Attic with the teacup prints a message that the inventory feels lighter and the teacup has returned to the attic.
- Leaving the Attic with the teapot prints a similar message and restores the teapot to Grandma's table.
- Because the ritual is anchored in the attic, using ash on the teapot outside the Attic tells the player the steam is anchored upstairs.

## Grandma And Social Topics

Grandma can currently be asked about:

- Mother.
- Missy.
- Tea.
- Amon.
- The house.
- 'THEM'.
- Ancestors.
- Company.
- Guests.

Responses change based on:

- Whether the player has complied, questioned, disrupted, or entered the ash branch.
- Whether the player is in full trance or weakened trance.
- Whether the player has awakened the witness.
- Whether the player is showing a relevant item such as the key, axe, photograph, or hearth ash.

Mother can currently be asked or shown:

- The family photograph, if the player has obtained it.
- Questions about Grandma, Missy, the bandage, and the house's control.
- Mother should not reveal the photo before the player discovers it.

Missy:

- Appears as a voice heard inside the mind, not as a visible entity.
- Can warn the player at multiple points across the map.
- In the Attic, she warns that the tea is not merely tea and later comments on the ash branch.
- Can be asked about in a few locations, but cannot be inspected as a physical body or attacked.

## Current Combat Design

Combat verbs exist, but violence is not heroic by default.

Supported combat targets:

- Mother: attacking her causes `BAD END: THE KINDNESS YOU SPENT`.
- Grandma without the right conditions: attacking with the wrong weapon fails or pushes toward danger.
- Grandma with the sharp axe before the teapot's steam is smothered causes `BAD END: THE WRONG FIRST BLOW`.
- Grandma with the sharp axe after ash smothers the teapot causes `BAD END: GRANDMA'S EMPTY CHAIR`.
- Sealed jar: can be struck or attacked, but does not break.
- Missy: cannot be attacked, because she is a spirit or presence rather than a body.
- Teapot: direct attack text redirects the player toward the importance of the steam.

Combat verbs include:

- `attack`
- `kill`
- `hit`
- `strike`
- `swing`
- `slash`
- `murder`
- `stab`
- `chop`
- `break`
- `smash`
- `damage`
- `crack`

Path-aware ending design:

- Mother ending text reacts to the weapon, whether the bandage was taken, whether Mother had spoken, and whether the player was in trance.
- Wrong-first-blow text reacts to compliance, questions, disruption, witness discovery, and whether ash was carried but not used.
- Empty-chair text reacts to witness and Missy states, emphasizing that Grandma's death does not end 'THEM'.

## Puzzle Philosophy

Puzzles should feel like uncovering a household ritual system, not solving abstract locks.

Good puzzle patterns:

- Learn a rule in one room and apply it in another.
- Use mundane objects to interrupt supernatural processes.
- Require the player to decide who or what to prioritize.
- Let altered perception reveal truths but also distort danger.
- Give layered clues through rooms, objects, senses, and character responses.
- Let the player miss optional clues without making the main path impossible.
- Support natural verb variations around likely parser guesses.

Avoid:

- Arbitrary item combinations with no story logic.
- Large dead-end mazes.
- Long trial-and-error command sequences.
- Revealing a solution before the player has found the clue source.
- Hard-locking progress behind one exact wording when several natural phrases should work.
- Making violence appear like the default correct solution.

## Family Roles

Grandma:

- Charismatic, cruel, theatrical, manipulative.
- May be frailer physically than she appears.
- Uses invitation, shame, affection, etiquette, and ritual authority.
- Knows more than she says, but also may be serving forces she cannot fully command.

Mother:

- A tragic figure caught between protection and surrender.
- Starts passive and weak, but can still help in small, costly ways.
- The bandage makes her blood a key to testimony rather than a simple item.

Missy:

- Sees danger earlier than the player.
- Acts as emotional conscience and practical warning system.
- Exists in the current build as a voice inside thought.
- Should remain non-attackable and non-collectible.

Player:

- Young enough to be vulnerable, old enough to act.
- Susceptible to fascination as much as fear.
- Should be able to act through curiosity, obedience, refusal, disruption, or violence, with different consequences.

Amon:

- Not just the front-door nameplate and not simply the physical house.
- Currently described through Grandma and the witness as a name, invitation, hunger, memory, and ritual opening.
- The design should keep Amon uncanny and partly unresolved.

## Originalizing The Material

To keep the game inspired rather than derivative:

- Change scene order and causality.
- Create original room events and puzzle chains.
- Let the house mythology go beyond the album material.
- Introduce new documents, symbols, family names, witness lore, and house history.
- Keep Missy as an internal voice rather than recreating specific plot beats.
- Use the emotional structure of occult family horror rather than reproducing exact scenes.
- Maintain the `greywake-alternate-story` branch as a safe place for alternate names and story reshaping.

## Recommended Build Order

Completed:

1. Expand the command set for investigation and item interaction.
2. Add one family room and one document-heavy room.
3. Create a clear early-game puzzle chain for attic access.
4. Add a trance-state system that changes room descriptions, clues, command responses, and browser highlight color.
5. Add a mid-game ritual sequence with branching outcomes.
6. Add combat verbs with negative outcomes.
7. Improve room descriptions so they naturally mention visible exits and points of interest.
8. Add a browser wrapper that runs the Python game through PyScript.
9. Add the teacup, teapot pouring description, and attic-return behavior for attic ritual objects.
10. Add browser move counter, curated interactive term highlighting, Missy quote italics, and danger-state interactive color animation.

Recommended next:

1. Add one complete non-bad ending path so the ash branch can reach a satisfying resolution.
2. Add stronger post-ash objectives that are not solved by killing Grandma.
3. Decide what the silver spoon and grave dirt should do, or document them as flavor until used.
4. Add automated playthrough tests for attic access, obedient tea path, ash path, restart, browser move counting, and dead-end checks.
5. Continue originality work by reshaping the most direct concept-album references on a separate branch before merging any replacements into the main playable branch.
