# The House of Amon

## Premise

A young protagonist returns to a decaying family house where their grandmother has resumed strange nightly rituals involving tea, blood, and unseen visitors. The house itself seems to amplify memory, guilt, and obedience. The player must explore the estate, understand the rituals, protect what remains of the family, and decide whether to destroy, inherit, or join the power inside the house.

This game is inspired by classic gothic horror and occult family drama. It should feel personal, claustrophobic, dreamlike, and increasingly unstable.

## Design Goals

- Build a short-to-medium parser adventure with a strong horror atmosphere.
- Use a compact map where rooms change meaning as the player learns more.
- Make the house feel like an active force rather than a passive setting.
- Let puzzles emerge from ritual logic, family relationships, and altered perception.
- Preserve a few different endings based on what the player learns and who they protect.

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
- The sibling is suspicious and frightened.
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

- The player begins to hear or glimpse the unseen guests.
- Mother weakens.
- The sibling tries to warn the player more directly.
- The player discovers that the house rewards silence, obedience, and curiosity in equal measure.

Player questions:

- What exactly does the tea do?
- Are the entities real, symbolic, or both?
- What object anchors the haunting?

Likely rooms:

- Upstairs Hallway
- Player Bedroom
- Cellar
- Garden
- Shed

Puzzle beats:

- Find the attic key or attic access method.
- Discover records, family relics, or ritual notes in the cellar.
- Gather a set of practical tools and occult objects.
- Learn that one object in the house holds or channels the ritual presence.

## Act 3: Tea Night

Goal: witness the ritual and decide how close to it the player is willing to get.

What happens:

- The player gains access to the attic.
- Grandma hosts a tea ritual with invisible presences.
- The player enters an altered state that reveals the deeper version of the house.
- The family crisis becomes immediate: Mother is being drained, and the sibling is at risk.

Player questions:

- Is the tea just bait, or is it a genuine source of power?
- Can the ritual be interrupted safely?
- Who can still be saved?

Likely rooms:

- Attic
- Alternate or trance versions of existing rooms

Puzzle beats:

- Use observation commands to identify ritual stages.
- Decide whether to participate, interrupt, or spy.
- Learn the specific weakness of the house focus object.

## Act 4: The Break

Goal: disrupt the ritual system and survive the house’s backlash.

What happens:

- The player damages or removes the focus object.
- The unseen guests become openly hostile.
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
- Fail to resist and join the invisible guests.

## Map Direction

The current room list is strong and should mostly stay:

- Front Gate
- Cemetery
- Front Door
- Foyer
- Living Room
- Kitchen
- Upstairs Hallway
- Bedroom
- Attic
- Cellar
- Garden
- Shed

Good additions:

- Dining Room or Parlor for family scenes
- Study or locked archive for family records
- Pantry or Scullery for practical ingredients and clues
- Secret passage between cellar and attic wall-space

## Command Design

Current commands are a good base. The next commands should support investigation and ritual play rather than generic adventure verbs.

High-value next commands:

- `ask <person> about <topic>`
- `show <item> to <person>`
- `open` and `close`
- `move <object>`
- `hide`
- `smell`
- `read`
- `pour <item> into/on <target>`
- `light <object>`
- `attack <target>` as a desperate, rarely useful action

Parser goals:

- Recognize multi-word items reliably.
- Let room-specific verbs unlock custom scenes.
- Give distinct responses for grounded and trance states.

## Item Design

Items should split into three categories.

Practical items:

- Brass key
- Axe
- Sharpening stone
- Candle
- Matches
- Wire cutters

Family items:

- Bandaged handkerchief
- Childhood toy
- Photo of Grandpa
- House key ring
- Phone receiver or cut phone wire

Ritual items:

- Amon teapot
- Blood-stained teacup
- Invitation card
- Grandmother's cane
- Ritual ledger
- Ash from the hearth

## Puzzle Philosophy

Puzzles should feel like uncovering a household ritual system, not solving abstract locks.

Good puzzle patterns:

- Learn a rule in one room and apply it in another.
- Use mundane objects to interrupt supernatural processes.
- Require the player to decide who or what to prioritize.
- Let altered perception reveal truths but also distort danger.

Avoid:

- Arbitrary item combinations with no story logic.
- Large dead-end mazes.
- Long trial-and-error command sequences.

## Family Roles

Grandmother:

- Charismatic, cruel, theatrical, manipulative.
- May be frailer physically than she appears.
- Uses invitation, shame, affection, and ritual authority.

Mother:

- A tragic figure caught between protection and surrender.
- Starts passive, but may still help in small, costly ways.

Sibling:

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

1. Expand the command set for investigation and item interaction.
2. Add one new family room and one document-heavy room.
3. Create a clear early-game puzzle chain for attic access.
4. Add a trance-state system that changes more room descriptions and clues.
5. Add a mid-game ritual sequence with branching outcomes.
6. Add one ending path fully before trying to build all endings.
