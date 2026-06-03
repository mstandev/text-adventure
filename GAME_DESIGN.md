# The House of Amon

## Premise

A young protagonist returns to a decaying family house where Grandma has resumed strange nightly rituals involving tea, blood, and 'THEM'. The house itself seems to amplify memory, guilt, and obedience. The player must explore the estate, understand the rituals, protect what remains of the family, and decide whether to destroy, inherit, or join the power inside the house.

This game is inspired by classic gothic horror and occult family drama. It should feel personal, claustrophobic, dreamlike, and increasingly unstable.

## Design Goals

- Build a short-to-medium parser adventure with a strong horror atmosphere.
- Use a compact map where rooms change meaning as the player learns more.
- Make the house feel like an active force rather than a passive setting.
- Let puzzles emerge from ritual logic, family relationships, and altered perception.
- Preserve a few different endings based on what the player learns and who they protect.

## Current Implementation Snapshot

The game is currently a playable Python parser adventure built from three core files:

- `main.py`: game loop, command handling, branching scenes, puzzle logic, restart flow.
- `engine.py`: parser, room model, and `GameState`.
- `world.py`: room graph, room descriptions, scenery, exits, and starting items.

The current build supports:

- A larger investigation verb set.
- A richer map with Dining Room, Study, and Attic Landing added.
- A clear attic access puzzle chain.
- Grounded, full-trance, and weakened-trance perception states.
- A ritual branch where obedient tea drinking differs from ash-smothering the teapot.
- Combat verbs with negative outcomes, while Missy cannot be attacked because she is a spirit.
- A restart command with confirmation.
- More precise failure text for scenery and untakeable objects.
- Discovery-gated clueing, so the game should avoid mentioning puzzle clues before the player has found the relevant object, room feature, or witness.

## Core Pillars

### 1. Family Horror

The danger is intimate. The most disturbing events happen between relatives, in bedrooms, kitchens, and hallways.

### 2. Ritual Logic

The supernatural follows rules. Blood, objects, rooms, names, and invitation all matter.

### 3. Shifting Perception

The player sees one version of the house while grounded and another while spiritually influenced by the tea and the house.

### 4. Player Complicity

The player should feel tempted by forbidden knowledge and comfort, not just threatened by it.

## Narrative Shape

## Act 1: Arrival

Goal: enter the house and reestablish the family dynamic.

What happens:

- The player arrives at the estate at night.
- The front door is barred.
- Grandma has recently returned from an institution, sanatorium, or unexplained absence.
- Mother is strained and evasive.
- Missy is suspicious and frightened.
- The house immediately establishes that some spaces are forbidden.

Player questions:

- Why is Grandma back?
- What is in the attic?
- Why is everyone pretending things are normal?

Likely rooms:

- Front Gate
- Cemetery
- Front Door
- Foyer
- Living Room
- Kitchen

Puzzle beats:

- Gain entry by following house etiquette instead of forcing the door.
- Learn that Grandma responds to ritual behavior, not logic.
- Find the first clue that the attic is the center of the haunting.

## Act 2: The House Teaches You

Goal: explore the family spaces and learn the hidden rules.

What happens:

- The player begins to hear or glimpse 'THEM'.
- Mother weakens.
- Missy tries to warn the player more directly.
- The player discovers that the house rewards silence, obedience, and curiosity in equal measure.

Player questions:

- What exactly does the tea do?
- Are the entities real, symbolic, or both?
- What object anchors the haunting?

Likely rooms:

- Upstairs Hallway
- Your Bedroom
- Cellar
- Garden
- Shed
- Dining Room
- Study
- Attic Landing

Puzzle beats:

- Find the attic key or attic access method.
- Discover records, family relics, or ritual notes in the cellar.
- Gather a set of practical tools and occult objects.
- Learn that one object in the house holds or channels the ritual presence.

## Act 3: The Attic Ritual

Goal: witness the ritual and decide how close to it the player is willing to get.

What happens:

- The player gains access to the attic.
- Grandma hosts a tea ritual with 'THEM'.
- The player enters an altered state that reveals the deeper version of the house.
- The family crisis becomes immediate: Mother is being drained, and Missy is at risk.

Player questions:

- Is the tea just bait, or is it a genuine source of power?
- Can the ritual be interrupted safely?
- Who can still be saved?

Likely rooms:

- Attic
- Alternate or trance versions of existing rooms

Puzzle beats:

- Use observation commands to identify ritual stages.
- Decide whether to comply, question too far, or disrupt the ceremony.
- Learn the specific weakness of the house focus object.

## Act 4: The Break

Goal: disrupt the ritual system and survive the house’s backlash.

What happens:

- The player damages or removes the focus object.
- 'THEM' become openly hostile.
- Objects animate, exits shift, and the house stops pretending to be normal.
- The player must move quickly to protect at least one family member or secure proof of what happened.

Player questions:

- Can the house be cleansed, or only damaged?
- Does Grandma control the entities, or serve them?
- What must be destroyed, and what must be preserved?

Likely rooms:

- Kitchen during the fire sequence
- Cellar during manifestation
- Stair hall during collapse
- Exterior grounds during escape

Puzzle beats:

- Escape a room while animated objects attack.
- Use earlier-found tools in practical ways, not just occult ways.
- Make an irreversible choice involving the teapot, ritual book, or blood source.

## Act 5: Reckoning

Goal: confront Grandma and determine the future of Amon.

What happens:

- Grandma is separated from part of the house’s power, but still dangerous.
- The player confronts her inside or just outside the protective boundary of the house.
- The final choice depends on what the player learned and what they preserved.

Possible endings:

- Burn the house and end the bloodline power.
- Bury the focus object and leave, but remain haunted.
- Take control of the ritual and become the next keeper.
- Save a family member but leave the house active.
- Fail to resist and join 'THEM'.

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

Important map changes:

- The attic is no longer reached by a ladder. The upstairs hallway has a narrow stair leading to an Attic Landing.
- The attic door is on the landing and opens north into the attic.
- The invitation card is useful flavor and clue material, but is no longer required for attic access.

## Current Command Design

The parser now recognizes a broad command set:

- Movement: `go`, compass directions, `n`, `s`, `e`, `w`, `u`, `d`, `enter`, `exit`.
- Investigation: `look`, `examine`, `inspect`, `peek`, `search`, `read`, `listen`, `smell`.
- Inventory: `take`, `get`, `drop`, `inventory`.
- Social commands: `talk`, `ask <person> about <topic>`, `show <item> to <person>`.
- Object interaction: `open`, `close`, `move`, `knock`, `unlock`, `use <item> on <target>`.
- Ritual and action verbs: `drink`, `pour`, `light`, `sharpen`, `attack`.
- Global commands: `help`, `restart`, `quit`.

Useful supported variations include:

- `knock door`, `knock on door`, `use knocker`.
- `enter house`, `enter attic`, `go north` from the Attic Landing after the door opens.
- `show photo to mother`, `show mother photo`, `show photograph mother`.
- `sharpen axe`, `hone axe`, `whet axe`, `use stone on axe`, `use axe on stone`.
- `look behind paintings`, `search behind portraits`, `move paintings`.

Design rule for responses:

- If the player names visible scenery, give a specific response even when the object cannot be taken.
- Avoid saying "There is no X here" for important visible room features like the candelabrum, hearth, tools, workbench, paintings, doors, or initials.
- Do not reveal an undiscovered clue, object, or puzzle solution before the player has encountered the relevant source.

## Current Item Design

Practical items:

- Brass key: found in Your Bedroom; required for the attic door.
- Heavy axe: found in Kitchen.
- Sharpening stone: found in Shed.
- Sharp axe: created by sharpening the heavy axe with the sharpening stone.
- Silver spoon: found in Kitchen.

Family items:

- Family photograph: found face-down in the Dining Room until taken.
- Bloodied bandage: taken from Mother's hand in the Living Room.
- Grave dirt: found in the Cemetery.

Ritual/document items:

- Teapot: found in the Attic.
- Ritual ledger: found in the Study.
- Invitation card: found in the Study.
- Hearth ash: found by searching the Kitchen while in full trance.
- Sealed jar: found in the Cellar; cannot be broken.

State-aware item notes:

- Once the family photograph is taken, Dining Room search and sideboard descriptions should no longer show it as present.
- Once the bandage is taken, Living Room descriptions should mention Mother's exposed hand instead of the bandage.
- Once the teapot is taken, Attic descriptions should no longer say that the teapot sits on the table.

## Current Attic Access Puzzle

The intended sequence is:

1. At the Front Door, knock on the gargoyle knocker to open the house.
2. Enter the house and explore the family rooms.
3. Find the brass key in Your Bedroom.
4. In the Upstairs Hallway, look behind, search behind, or move the paintings.
5. Find the hidden carving: "Let invited blood knock, and the listening room shall answer."
6. Go up the narrow stair to the Attic Landing.
7. Unlock the attic door with the brass key.
8. Knock on the attic door.
9. Go north or enter attic.

The invitation card can reinforce the etiquette of knocking and entering, but the puzzle must still work without the player finding it.

## Current Trance System

There are three perception states:

- Grounded: the house is unsettling but still mostly physical and literal.
- Full trance: begins after the player drinks tea in the Attic. Rooms reveal supernatural structure, stronger sensory clues, and ritual meanings.
- Weakened trance: begins when the player smothers the teapot's steam with hearth ash while already in trance. The supernatural remains visible, but the house has less authority over perception.

Trance affects:

- Room descriptions.
- Inventory descriptions.
- Movement text.
- Search, listen, smell, read, examine, talk, ask, use, drink, and error responses.
- Clue availability, especially the hearth ash and deeper cellar/study meanings.

Mechanically actionable trance clues:

- Searching Kitchen in full trance reveals hearth ash as a takeable item.
- Inspecting the hearth in full trance suggests the ash only has ritual significance while the house is "dreaming through" the player.
- Listening or smelling in the Attic can reveal that the steam recoils from ash once the player has the ash and has awakened the witness.
- Reading labels or searching the Cellar in trance points toward the witness jar.

## Current Ritual Branching

The first Attic encounter presents three meaningful attitudes:

- Comply: drink the tea and enter the obedient path.
- Question too far: ask Grandma about Mother, Missy, the tea, the house, or 'THEM'.
- Disrupt: pour/spill the tea or later use hearth ash against the steam.

Obedient tea path:

- `drink tea` in the Attic sets the player into full trance.
- The room becomes more welcoming and dangerous.
- 'THEM' accept the player as a participant.

Ash-smothering path:

- The player must learn about the witness jar and hearth ash.
- Use Mother's bloodied bandage on the sealed jar in the Cellar to awaken the witness.
- The witness explains that the teapot feeds Amon through steam and that hearth ash can interrupt the ritual.
- Search the Kitchen while in full trance to find hearth ash.
- Use or cast hearth ash on the teapot, tea, steam, or violet steam in the Attic.
- The teapot is not destroyed outright; its steam is smothered and the ritual branch changes.
- If the player was in full trance, this changes the state to weakened trance.

Witness jar rule:

- The jar cannot be smashed, cracked, or broken, even with the axe.
- The jar responds to bloodline evidence, specifically Mother's bloodied bandage.
- The witness clue currently says: "When the teapot is fed, Amon opens. When the teapot is choked, cast hearth ash across the steam or 'THEM' will keep drinking from the air."

## Current Combat Design

Combat verbs exist, but violence is not heroic by default.

Supported combat targets:

- Mother: attacking her causes a bad ending.
- Grandma: attacking her without the right conditions fails or causes a bad ending.
- Grandma with the sharp axe after the teapot is smothered causes a different bad ending, because 'THEM' remain.
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

## Puzzle Philosophy

Puzzles should feel like uncovering a household ritual system, not solving abstract locks.

Good puzzle patterns:

- Learn a rule in one room and apply it in another.
- Use mundane objects to interrupt supernatural processes.
- Require the player to decide who or what to prioritize.
- Let altered perception reveal truths but also distort danger.
- Give layered clues through rooms, objects, senses, and character responses.
- Let the player miss optional clues without making the main path impossible.

Avoid:

- Arbitrary item combinations with no story logic.
- Large dead-end mazes.
- Long trial-and-error command sequences.
- Revealing a solution before the player has found the clue source.
- Hard-locking progress behind one exact wording when several natural phrases should work.

## Family Roles

Grandma:

- Charismatic, cruel, theatrical, manipulative.
- May be frailer physically than she appears.
- Uses invitation, shame, affection, and ritual authority.

Mother:

- A tragic figure caught between protection and surrender.
- Starts passive, but may still help in small, costly ways.

Missy:

- Sees danger earlier than the player.
- Acts as emotional conscience and practical warning system.
- Could survive, disappear, or be transformed depending on player action.

Player:

- Young enough to be vulnerable, old enough to act.
- Susceptible to fascination as much as fear.

## Originalizing The Material

To keep the game inspired rather than derivative:

- Change scene order and causality.
- Create original room events and puzzle chains.
- Let the house mythology go beyond the album material.
- Introduce new documents, symbols, and family history.
- Use the album's emotional structure rather than reproducing exact scenes.

## Recommended Build Order

Completed:

1. Expand the command set for investigation and item interaction.
2. Add one family room and one document-heavy room.
3. Create a clear early-game puzzle chain for attic access.
4. Add a trance-state system that changes room descriptions, clues, and command responses.
5. Add a mid-game ritual sequence with branching outcomes.
6. Add combat verbs with negative outcomes.
7. Improve room descriptions so they naturally mention visible exits and points of interest.

Recommended next:

1. Add one complete non-bad ending path so the ash branch can reach a satisfying resolution.
2. Add stronger Missy-related scenes now that she is treated as a spirit instead of a physical target.
3. Continue originality work by renaming or reshaping the most direct concept-album references.
4. Add automated playthrough tests for the attic path, obedient tea path, ash path, and main dead-end checks.
5. Consider a browser or GitHub Pages presentation layer later, but keep the Python parser version as the source of truth for now.
