# main.py
from engine import AdvancedParser, GameState
from world import setup_amon_house

def resolve_item(gs, name, context="room"):
    """
    Helper to handle Aliases and Disambiguation.
    Returns the specific item_id (e.g., 'brass key') even if the user typed 'key'.
    """
    matches = gs.get_matches(name, context)
    
    if not matches:
        return None
    
    if len(matches) == 1:
        return matches[0]
    
    # If multiple items match (e.g., player types 'key' and has two different keys)
    print(f"\nWhich {name} do you mean?")
    for i, match in enumerate(matches, 1):
        print(f"{i}. {match}")

    if not getattr(gs, "allow_interactive_prompts", True):
        print("Type the full item name so the house knows exactly what you mean.")
        return None
    
    choice = input("> ")
    if choice.isdigit() and 0 < int(choice) <= len(matches):
        return matches[int(choice)-1]
    elif choice in matches:
        return choice
    return None

def parse_show_command(gs, obj, i_obj):
    target_names = ("mother", "mom", "grandma", "grandmother")
    normalized_obj = normalize_object_name(obj)
    shown_item = resolve_item(gs, normalized_obj, "inventory") if normalized_obj else None
    target = normalize_object_name(i_obj)
    requested_item = normalized_obj

    if shown_item or target or not normalized_obj:
        return shown_item, target, requested_item

    words = normalized_obj.split()
    if words and words[0] in target_names:
        target = words[0]
        requested_item = normalize_object_name(" ".join(words[1:]))
        shown_item = resolve_item(gs, requested_item, "inventory") if requested_item else None
    elif words and words[-1] in target_names:
        target = words[-1]
        requested_item = normalize_object_name(" ".join(words[:-1]))
        shown_item = resolve_item(gs, requested_item, "inventory") if requested_item else None

    return shown_item, target, requested_item

def move_item(source, target, item_id):
    aliases = source.pop(item_id)
    target[item_id] = aliases

def resolve_any_item(gs, name):
    return resolve_item(gs, name, "room") or resolve_item(gs, name, "inventory")

def describe_inventory(gs):
    if not gs.inventory:
        if in_full_trance(gs):
            print("Your pockets are empty, but not the room around you. It keeps trying to lend you meanings instead of objects.")
        elif in_weakened_trance(gs):
            print("Your pockets are empty. Even so, the house still seems convinced you are carrying something away from it.")
        else:
            print("Your pockets are empty.")
    else:
        items = ", ".join(gs.inventory.keys())
        if in_full_trance(gs):
            print(f"Inventory: {items}. In trance, each thing feels less owned than temporarily entrusted.")
        elif in_weakened_trance(gs):
            print(f"Inventory: {items}. The objects feel ordinary in your hands again, though the house has not quite agreed.")
        else:
            print(f"Inventory: {items}")

def print_room(gs, include_entry=True):
    room = gs.rooms[gs.current_room]
    print(f"\n--- {room.name} ---")
    print(room_text(gs, room))
    if gs.current_room == "Front Gate" and not gs.front_gate_hint_seen:
        print("\nBegin: inspect, search, n, s, e, w. The house will answer what it understands.")
        gs.front_gate_hint_seen = True
    if include_entry:
        handle_room_entry(gs, room)
    if room.items:
        print(f"Items here: {', '.join(room.items)}")

def print_help():
    print("You can try commands like these:")
    print("")
    print("Movement:")
    print("  north, south, east, west, up, down")
    print("  n, s, e, w, u, d")
    print("  enter house, enter attic, exit")
    print("")
    print("Looking around:")
    print("  inspect, examine, inspect door, examine keyhole")
    print("  search room, search table, look behind paintings")
    print("  read ledger, listen, smell hearth")
    print("")
    print("Items:")
    print("  take key, get teacup, get all, drop spoon")
    print("  inventory, i")
    print("")
    print("Using things:")
    print("  knock door, unlock attic door")
    print("  use item on target")
    print("  show photo to mother")
    print("  ask grandma about tea")
    print("  sharpen axe, drink tea, pour tea")
    print("")
    print("Game:")
    print("  restart, quit")
    print("")
    print("The house understands several similar phrasings, so natural commands are worth trying.")

def in_full_trance(gs):
    return gs.trance and not gs.weakened_trance

def in_weakened_trance(gs):
    return gs.trance and gs.weakened_trance

def living_room_text(gs, room):
    if not gs.bandage_taken:
        return room.trance_desc if gs.trance else room.desc
    if in_full_trance(gs):
        return "Mother's shadow stands over her, a tall, faceless thing that turns as you enter. East, the foyer shivers with detached shadows; north, the study's papers whisper against one another. The room smells of copper and unwashed china teacups, and Mother's unwrapped hand lies exposed beneath the thing that is almost her shape."
    if in_weakened_trance(gs):
        return "Mother still lies on the sofa, with the foyer east and the study north. Her shadow has sunk back into the shape of her body. Around the floorboards, the dark cup-stains remain, half-seen and impossible to forget, and her unwrapped hand rests pale against the velvet."
    return "Mother lies on a velvet sofa, her face a mask of waxen exhaustion. The foyer waits east through a dark archway, and a narrow doorway north leads into a study crowded with books and papers. Her unwrapped hand rests limp against the sofa, marked by a dark red stain where the bandage used to be."

def attic_room_text(gs, room):
    if TEAPOT_ITEM in room.items:
        if "china teacup" not in room.items:
            return state_text(
                gs,
                "The attic is narrow and close beneath the roof beams. South, the open door back to the landing waits behind you. Grandma sits in her rocking chair with her back to you. Beside her, the small table holds the teapot beside a pale ring where the teacup should be.",
                "The attic is crowded with flickering, translucent figures, each one hollow where a face should be. South through the open door lies the landing and the hallway beyond. The small table holds the teapot, but the missing teacup has left a place in the ceremony that every guest seems to notice.",
                "Grandma remains in the rocking chair, with the open door south to the landing behind you. The small table holds the teapot beside an empty cup-ring that the room keeps trying to correct."
            )
        return room.trance_desc if gs.trance else room.desc
    if "china teacup" in room.items:
        return state_text(
            gs,
            "The attic is narrow and close beneath the roof beams. South, the open door back to the landing waits behind you. Grandma sits in her rocking chair with her back to you. The small table holds only the china teacup now, waiting beside the clean silver ring where the teapot rested.",
            "The attic is crowded with flickering, translucent figures, each one hollow where a face should be. The small table holds only the china teacup, and every faceless guest looks toward the teapot in your hands.",
            "Grandma remains in the rocking chair, with the open door south to the landing behind you. The small table holds only the china teacup, too clean and too patient."
        )
    if gs.teapot_smothered:
        if in_full_trance(gs):
            return "The attic is narrow and close beneath the roof beams. South, the open door back to the landing waits behind you. Grandma remains in the rocking chair while the guests gather around the small table, where bruised ribbons of steam hang low over an empty place."
        if in_weakened_trance(gs):
            return "Grandma remains in the rocking chair, with the open door south to the landing behind you. The small table stands bare except for a dark ring in the dust, and the room feels haunted now more than welcoming."
        return "Grandma remains in the rocking chair, with the open door south to the landing behind you. The small table stands bare except for a dark ring in the dust, and bruised ribbons of steam cling low to the air."
    if in_full_trance(gs):
        return "The attic is crowded with flickering, translucent figures, each one hollow where a face should be. South through the open door lies the landing and the hallway beyond. The small table beside Grandma is bare now, but every faceless guest turns toward the teapot in your hands."
    if in_weakened_trance(gs):
        return "Grandma remains in the rocking chair, with the open door south to the landing behind you. The small table stands bare except for a silver ring in the dust, and the teapot in your hands feels heavier than metal should."
    return "The attic is narrow and close beneath the roof beams. South, the open door back to the landing waits behind you. Grandma sits in her rocking chair with her back to you. Beside her, the small table stands bare except for a clean silver ring in the dust."

def study_room_text(gs, room):
    has_ledger = "ritual ledger" in room.items
    has_card = "invitation card" in room.items

    if has_ledger and has_card:
        if in_weakened_trance(gs):
            return "The study has stopped whispering in chorus. South, Mother's room waits beyond the doorway. The pages shift only when you look away now, and the records feel less enchanted than embarrassed to have been caught."
        return room.trance_desc if gs.trance else room.desc

    if has_ledger:
        return state_text(
            gs,
            "Tall bookcases crowd the walls, bowing beneath hymnals and family records. South, the doorway returns to Mother's room. The crooked desk drawer hangs open, with the ritual ledger still waiting among loose papers scattered across the rug.",
            "The books whisper in overlapping voices. South, Mother's room waits like a held sob. The drawer hangs open, and the ritual ledger keeps dragging the loose papers around itself whenever you blink.",
            "The study has stopped whispering in chorus. South, Mother's room waits beyond the doorway. The ritual ledger remains among papers that now seem embarrassed by their own importance."
        )

    if has_card:
        return state_text(
            gs,
            "Tall bookcases crowd the walls, bowing beneath hymnals and family records. South, the doorway returns to Mother's room. The crooked desk drawer hangs open, with the invitation card still waiting among loose papers scattered across the rug.",
            "The books whisper in overlapping voices. South, Mother's room waits like a held sob. The drawer hangs open, and the invitation card keeps catching the room's attention like a white tooth in the dark.",
            "The study has stopped whispering in chorus. South, Mother's room waits beyond the doorway. The invitation card remains among papers that no longer quite manage to hide it."
        )

    return state_text(
        gs,
        "Tall bookcases crowd the walls, bowing beneath hymnals and family records. South, the doorway returns to Mother's room. The crooked desk drawer hangs open and empty, while loose papers lie across the rug like pale leaves after a storm.",
        "The books whisper in overlapping voices. South, Mother's room waits like a held sob. The desk drawer chatters emptily against its frame, and the loose papers rearrange themselves around absences they resent.",
        "The study has stopped whispering in chorus. South, Mother's room waits beyond the doorway. The drawer hangs open and empty, and the remaining papers look less enchanted than caught."
    )

def room_text(gs, room):
    if gs.current_room == "Living Room":
        return living_room_text(gs, room)
    if gs.current_room == "Attic":
        return attic_room_text(gs, room)
    if gs.current_room == "Study":
        return study_room_text(gs, room)
    if in_weakened_trance(gs):
        return WEAKENED_ROOM_TEXTS.get(gs.current_room, room.desc + " Something of the tea remains in your senses, but the house no longer holds you quite so tightly.")
    return room.trance_desc if gs.trance else room.desc

def inspect_room_text(gs):
    room = gs.rooms[gs.current_room]

    if gs.current_room == "Front Gate":
        return state_text(
            gs,
            "You let your eyes adjust to the estate. The iron gate stands open just enough for a body to pass through, its rust bright against the wet dark. North, the leaf-choked path climbs toward the house; south, the cemetery waits beyond the low wall. Nothing blocks you here, but the place has the feeling of a threshold that expects you to notice what you are crossing.",
            "You inspect the gate and the grounds, and the shape of them changes under attention. The iron bars seem jointed now, less like metal than long fingers holding the path apart. North, the house waits like a mouth trying not to speak; south, the cemetery breathes through its stones. Every leaf on the ground seems turned in the same direction, pointing you inward.",
            "You study the gate after the trance has weakened. The bars are mostly iron again, though their curves still suggest knuckles if you look too long. North lies the house, south the cemetery, and between them the path feels less commanding than it once did, which is not the same as safe."
        )

    if gs.current_room == "Cemetery":
        dirt_note = "The loose grave dirt remains near the old grave, damp and easy to gather." if "grave dirt" in room.items else "The disturbed patch beside the old grave is darker where you took the loose dirt."
        return state_text(
            gs,
            f"You inspect the cemetery row by row. The headstones lean at different angles, their names softened by rain until they seem half-erased from the family record. North, the gate leads back toward the path and the house. One old grave has sunk lower than the rest, and its marker keeps a stubborn shadow at its base. {dirt_note}",
            "In trance, the cemetery refuses to remain still. The headstones pulse faintly, not with life but with a ledger's cold insistence, as if every buried name is still being counted. North, the gate gleams like ribs around the path. The oldest grave seems less closed than paused, its loose earth listening for instructions from the house.",
            f"You inspect the cemetery in the aftertaste of trance. The green light is gone, but the stones still look recently accused. North, the gate leads back to the estate path. {dirt_note} The quiet here feels negotiated rather than natural."
        )

    if gs.current_room == "Front Door":
        if gs.door_unlocked:
            return state_text(
                gs,
                "You inspect the open front door. The heavy oak has swung inward, revealing the dark foyer to the north, while the path back to the gate lies south. The gargoyle knocker hangs above the AMON nameplate with the pleased stillness of a thing whose duty has been performed. Scratches in the wood show where others tried force before remembering manners.",
                "You inspect the open door in trance. North, the foyer waits with shadows folded close around the threshold; south, the path thins behind you. The gargoyle's brass mouth seems damp from speaking, and the AMON nameplate gleams as if the house has just heard its name properly used.",
                "You inspect the open door after the trance has loosened. North, the foyer is only a room again at first glance, and south the path remains possible. The knocker and nameplate look ordinary until your eyes remember the moment the bolt answered."
            )
        return state_text(
            gs,
            "You inspect the front door closely. There is no handle on this side, no visible latch, and no keyhole meant for you. The oak is scarred by age and weather, but only the brass gargoyle knocker has been polished bright by repeated touch. Beneath it, the narrow AMON nameplate makes the door feel less like an entrance than a thing waiting to be addressed.",
            "In trance, the door seems to breathe through the grain of the wood. The knocker's gargoyle mouth opens a little wider each time you focus on it, and the AMON nameplate shines with the certainty of a word that expects obedience. South, the path behind you looks thin and temporary.",
            "You inspect the closed door with the trance weakened. It is still barred, still handleless, still intent on being approached correctly. The knocker remains the only part of the door that looks willing to answer."
        )

    if gs.current_room == "Foyer":
        return state_text(
            gs,
            "You inspect the foyer as a map of the house rather than a room. South, the front door waits behind you; north, the kitchen leaks a smell of cold metal and old smoke; west, the living room lies dim around Mother; east, the dining room keeps its table set; and up the staircase the upper floor gathers its dark. The chandelier gives the dust just enough light to look deliberate.",
            "In trance, the foyer becomes a crossroads of intentions. The exits still hold their places, but each one has a mood: the kitchen hungers north, the living room suffers west, the dining room remembers east, and the staircase rises like a thought the house keeps repeating. South, the front door looks too far away for comfort.",
            "You inspect the foyer in the weakened trance. The exits are plain again, but the shadows lag behind the furniture before settling where they belong. The room no longer dances around you, yet it still feels like the house's first attempt to decide what kind of guest you are."
        )

    if gs.current_room == "Living Room":
        bandage_note = "The white bandage on Mother's hand is the brightest object in the room." if not gs.bandage_taken else "Mother's hand is unwrapped now, the old stain visible against her skin."
        return state_text(
            gs,
            f"You inspect the living room carefully. Mother lies on the velvet sofa as if sleep has become a weight placed on her chest. East, the foyer remains open; north, the study doorway waits behind the stale air. Dust lies thick on the furniture, but the space around Mother has been disturbed often. {bandage_note}",
            f"In trance, the living room shows the cruelty beneath its quiet. Mother's shadow is too tall for her body, and the floor around the sofa carries dark cup-shaped stains that ordinary sight tries to ignore. East, the foyer shivers; north, the study papers whisper. {bandage_note}",
            f"You inspect the living room after the trance has thinned. Mother looks painfully human again, which makes the room worse rather than easier. East is the foyer, north the study, and around the sofa the old marks remain half-visible in the floorboards. {bandage_note}"
        )

    if gs.current_room == "Dining Room":
        photo_note = "A family photograph lies face-down on the sideboard, left there with the awkward care of something deliberately hidden." if "family photograph" in room.items else "The sideboard holds a clean rectangle in the dust where the photograph used to lie."
        floor_note = "The initials carved into the floor are visible now beneath the shifted head chair." if "initials" in room.scenery else "The floor beneath the head chair is scraped pale, though the chair still hides the worst of the marks."
        return state_text(
            gs,
            f"You inspect the dining room from the west doorway inward. The walnut table dominates everything, laid with three place settings beneath a blackened silver candelabrum, while the fourth chair at the head feels more ceremonial than useful. {photo_note} {floor_note} The room gives the impression of a family meal preserved at the instant before someone said the unforgivable thing.",
            f"In trance, the dining room extends farther than its walls allow. More places appear in the dark between blinks, and the head chair seems occupied by expectation if not by a body. {photo_note} {floor_note} The cutlery shifts softly, though no visible hand touches it.",
            f"You inspect the dining room in the weakened trance. The table is only a table until you look away, and then the fourth place threatens to become important again. {photo_note} {floor_note} West, the foyer remains plainly reachable, which feels like a mercy the room resents."
        )

    if gs.current_room == "Study":
        visible_records = [item for item in STUDY_FINDABLE_ITEMS if item in room.items]
        if visible_records:
            record_note = f"The open drawer and scattered papers still hold: {', '.join(visible_records)}."
        else:
            record_note = "The drawer has been emptied of its most useful papers, leaving only household fragments and crossed-out names."
        return state_text(
            gs,
            f"You inspect the study by following the paper trail. Bookcases lean over the room with ledgers, hymnals, medical texts, and family histories pressed shoulder to shoulder. South leads back to Mother's room. The writing desk sits under the rain-streaked window, its crooked drawer open like a mouth caught mid-sentence. {record_note}",
            f"In trance, the study is less a room than an accounting chamber. The books whisper names in overlapping columns, and the papers keep trying to arrange themselves into invitation, blood, return, and obedience. South, Mother's room waits too close. {record_note}",
            f"You inspect the study after the trance has weakened. The papers no longer rearrange themselves boldly, but they still seem embarrassed by what they know. South leads back to Mother's room, and the window shows the cemetery through rain and black branches. {record_note}"
        )

    if gs.current_room == "Kitchen":
        item_note = []
        if "heavy axe" in room.items:
            item_note.append("the heavy axe waits near the worktable")
        if "silver spoon" in room.items:
            item_note.append("the silver spoon catches a thin line of blue light")
        if "hearth ash" in room.items:
            item_note.append("pale hearth ash lies revealed beneath the blue flame")
        elif "hearth ash" in gs.inventory:
            item_note.append("the hearth looks strangely bare where the pale ash was gathered")
        detail = "You notice " + ", and ".join(item_note) + "." if item_note else "The obvious tools have already been taken or made useful elsewhere."
        return state_text(
            gs,
            f"You inspect the kitchen from hearth to threshold. South returns to the foyer, east opens toward the garden, and down a steep stair the cellar exhales damp air. The blue flame burns cold in the stone hearth, throwing the hanging utensils into sharp shadows across the scarred worktable. {detail}",
            f"In trance, the kitchen reveals the ritual hiding inside its usefulness. The blue flame screams without sound, the utensils cast hook-shaped shadows, and the cellar stairs breathe glass and old liquid from below. South, the foyer tilts; east, the garden presses at the door. {detail}",
            f"You inspect the kitchen after the trance has loosened. It is practical again at a glance, but the hearthstone still carries tiny cuts and circles that no cooking explains. South, east, and down remain clear routes out. {detail}"
        )

    if gs.current_room == "Upstairs Hallway":
        carving_note = "One portrait hangs crooked now, exposing the carved message behind it." if gs.moved_portraits else "The portraits hang in a severe family procession, each painted hand subtly angled toward the attic stair."
        return state_text(
            gs,
            f"You inspect the upstairs hallway from the stairwell to the narrow stair at the far end. Down lies the foyer; west, your bedroom waits half-open; up, the stair climbs toward the attic landing. {carving_note} The air carries the steady creak of a rocking chair from above, too regular to be comforting.",
            f"In trance, the hallway loses faith in its paintings. The frames hold emptiness, while the ancestors' attention seems to move inside the walls instead. Down, west, and up remain possible, but the attic stair feels like the direction the house has been preparing all along. {carving_note}",
            f"You inspect the upstairs hallway in the weakened trance. The portraits have returned to paint, mostly, and the routes are clear: down to the foyer, west to your bedroom, up to the attic landing. {carving_note} The rocking above continues, quieter now but not gone."
        )

    if gs.current_room == "Attic Landing":
        door_note = "The attic door is unlocked now, and north leads through it into Grandma's room." if gs.attic_unlocked else "The attic door is locked, but its keyhole offers a narrow view of rocking motion and a small table beyond."
        return state_text(
            gs,
            f"You inspect the cramped landing under the sloped roof. Down the narrow stair lies the upstairs hallway. North, the attic door fills the little space ahead, its brass lock and ornate keyhole making the threshold feel ceremonial. {door_note}",
            f"In trance, the landing tightens around you like the pause before a verdict. Down seems farther away than it should, while north the attic door listens through its keyhole. {door_note} The rocking chair beyond keeps time with something under your skin.",
            f"You inspect the attic landing after the trance has weakened. The roof presses low, the stair drops down behind you, and north remains the house's most stubborn threshold. {door_note}"
        )

    if gs.current_room == "Your Bedroom":
        key_note = "The brass key catches the candlelight as if it has been waiting to be noticed." if "brass key" in room.items else "The place where the brass key waited is empty now."
        return state_text(
            gs,
            f"You inspect your old bedroom slowly, because childhood has made the room crowded with meanings. East, the half-open door returns to the hallway. The unmade bed slumps beside the nightstand, where a weak candle gutters over old toys, a warped wardrobe, and dust disturbed beneath the bed. {key_note}",
            f"In trance, the bedroom breathes around you. The toys have turned their faces away, the window shows a purple mist instead of grounds, and the dust beneath the bed looks recently wounded. East, the hallway calls in borrowed voices. {key_note}",
            f"You inspect your bedroom after the trance has loosened. It is stale, small, and almost ordinary, but the bed, toys, wardrobe, and window all seem to remember being stranger. East leads back to the hallway. {key_note}"
        )

    if gs.current_room == "Attic":
        table_pieces = []
        held_pieces = []
        if TEAPOT_ITEM in room.items:
            table_pieces.append("the teapot")
        elif TEAPOT_ITEM in gs.inventory:
            held_pieces.append("the teapot")
        if TEACUP_ITEM in room.items:
            table_pieces.append("the china teacup")
        elif TEACUP_ITEM in gs.inventory:
            held_pieces.append("the china teacup")
        if table_pieces and held_pieces:
            table_note = "The small table holds " + " and ".join(table_pieces) + ", while you carry " + " and ".join(held_pieces) + "."
        elif table_pieces:
            table_note = "The small table holds " + " and ".join(table_pieces) + ", arranged with the precision of a ceremony waiting for permission."
        elif held_pieces:
            table_note = "The table's clean rings point accusingly toward " + " and ".join(held_pieces) + " in your hands."
        elif gs.teapot_smothered:
            table_note = "The small table is bare except for dark rings and bruised steam where the ceremony was interrupted."
        else:
            table_note = "The small table is bare now, though the dust still remembers where the service belonged."
        return state_text(
            gs,
            f"You inspect the attic without trusting its stillness. South, the door back to the landing remains open. Grandma sits in the rocking chair with her back to you, not fragile so much as rooted. Roof beams press the room low, dust gathers along the edges, and violet steam makes the air around the table look rehearsed. {table_note}",
            f"In trance, the attic is crowded beyond architecture. 'THEM' gather around Grandma, around the table, around the steam, each faceless presence leaning toward the same invitation. South remains visible, but the room would prefer you forget exits. {table_note}",
            f"You inspect the attic after the trance has weakened. Grandma remains in the rocking chair, mortal-looking but not harmless, and the door south is still open. The room's authority has frayed around the edges, yet every board remembers where the ceremony stood. {table_note}"
        )

    if gs.current_room == "Cellar":
        jar_note = "The sealed jar sits among the others, too deliberate to be simple storage." if "sealed jar" in room.items or "sealed jar" in gs.inventory else "One space on the shelf looks cleaner than the rest, where the sealed jar was disturbed."
        if gs.witness_awakened:
            jar_note += " The witness inside has awakened once; the glass still looks faintly clouded from the encounter."
        return state_text(
            gs,
            f"You inspect the cellar shelf by shelf. Up the stairs lies the kitchen and its blue light. The walls sweat, the floor shines with something that is not water, and rows of jars hold dark liquids too thick to reflect you properly. {jar_note}",
            f"In trance, the cellar becomes a choir of glass. Faces drift up through the jars, hands press from within, and the shelves seem sorted by purpose rather than size: memory, witness, hunger. Up the stairs, the kitchen feels almost impossibly far. {jar_note}",
            f"You inspect the cellar after the trance has weakened. The jars are quiet enough to pretend at being jars, but the silence feels learned. Up the stairs waits the kitchen. {jar_note}"
        )

    if gs.current_room == "Garden":
        return state_text(
            gs,
            "You inspect the garden under the cold night air. West, the kitchen door leaks a thin blue line of light; north, the tool shed leans beneath dead oak trees. The flower beds are broken and furred with frost, and the wind moves through them with a cleaner smell than anything inside the house. The garden feels like a pause, not an escape.",
            "In trance, the garden becomes a field of waiting gallows. The dead trees reach down with branch-nooses, the flower beds pulse under frost, and the soft ground gives too much beneath your feet. West, the kitchen cuts the dark with blue light; north, the shed hums with metal wanting purpose.",
            "You inspect the garden after the trance has weakened. The trees are trees again, though their branches still hang too low. West leads to the kitchen, north to the shed, and the air is cold enough to feel honest for a few breaths."
        )

    if gs.current_room == "Shed":
        stone_note = "The sharpening stone waits on the cluttered workbench." if "sharpening stone" in room.items else "The workbench is cluttered, but the sharpening stone is gone now."
        return state_text(
            gs,
            f"You inspect the shed in the thin moonlight. South, the warped door opens back to the garden. Tools hang from wall hooks in careful rows: saws, hooks, shears, and rusted blades, most too dull for honest work but still hungry-looking. Oil stains darken the bench beneath the cracked window. {stone_note}",
            f"In trance, the shed is all edge and appetite. The tools drip dark oil, their shadows longer than their handles, and the hooks on the wall seem disappointed by every empty space. South, the garden breathes against the warped door. {stone_note}",
            f"You inspect the shed after the trance has loosened. It smells of oil, rust, and wet wood again, but the tools still look arranged by someone who expected them to be needed. South leads back to the garden. {stone_note}"
        )

    return room_text(gs, room)

def print_room_inspection(gs):
    room = gs.rooms[gs.current_room]
    print(inspect_room_text(gs))
    if room.items:
        print(f"Items here: {', '.join(room.items)}")

def state_text(gs, ordinary, trance=None, weakened=None):
    if in_full_trance(gs):
        return trance or ordinary
    if in_weakened_trance(gs):
        return weakened or ordinary
    return ordinary

def decision_tone(gs, neutral, obedience=None, question=None, disrupt=None, ash=None):
    if gs.ritual_branch == "ash":
        return ash or disrupt or neutral
    if gs.attic_choice == "disrupt":
        return disrupt or neutral
    if gs.attic_choice == "question":
        return question or neutral
    if gs.ritual_branch == "obedience" or gs.attic_choice == "comply":
        return obedience or neutral
    return neutral

def is_weapon(item_id):
    return item_id in WEAPON_ITEMS

def sharpen_axe(gs):
    axe = resolve_item(gs, "axe", "inventory")
    stone = resolve_item(gs, "stone", "inventory")

    if axe == "sharp axe":
        print("The axe already has a keen edge. The stone whispers against it once, but there is nothing more to improve.")
    elif axe != "heavy axe" and stone != "sharpening stone":
        print("You need both the axe and the sharpening stone before you can do that.")
    elif axe != "heavy axe":
        print("You have the stone, but no axe to sharpen.")
    elif stone != "sharpening stone":
        print("You have the axe, but nothing suitable to sharpen it with.")
    else:
        gs.inventory.pop("heavy axe")
        gs.inventory["sharp axe"] = [
            "axe", "weapon", "sharp axe", "sharpened axe",
            "sharp heavy axe", "sharpened heavy axe"
        ]
        print("You work the axe blade against the sharpening stone until the dull edge wakes into a cold gleam.")
        print("The heavy axe is now a sharp axe.")

def is_axe_sharpening_pair(held_item, target_name):
    if not held_item or not target_name:
        return False
    return (
        held_item == "sharpening stone" and target_name in AXE_TARGETS
    ) or (
        held_item in ("heavy axe", "sharp axe") and target_name in STONE_TARGETS
    )

def visible_character(gs, target):
    if target in MOTHER_TARGETS:
        return gs.current_room == "Living Room" and "mother" not in gs.dead_characters
    if target in GRANDMA_TARGETS:
        return gs.current_room == "Attic" and "grandma" not in gs.dead_characters
    return False

def resolve_attack_weapon(gs, named_weapon=None):
    if named_weapon:
        return resolve_item(gs, named_weapon, "inventory")
    if "sharp axe" in gs.inventory:
        return "sharp axe"
    if "heavy axe" in gs.inventory:
        return "heavy axe"
    return None

def attack_target_name(target):
    if not target:
        return "that"
    if target in ("them", "'them'", "\"them\"", "it", "you", "me"):
        return target
    if target.startswith(("the ", "a ", "an ")):
        return target
    return f"the {target}"

def print_bad_end(title, *paragraphs):
    print(f"\nBAD END: {title}")
    for paragraph in paragraphs:
        print(paragraph)

def print_mother_bad_end(gs, weapon):
    if weapon:
        first_line = f"The {weapon} was supposed to make you powerful. In Mother's room it only makes you accurate."
    else:
        first_line = "Your empty hands do not make the act gentler. They only make it more intimate."

    if gs.bandage_taken:
        evidence_line = "The bloodied bandage in your pocket grows warm, a witness you carried away and then betrayed."
    else:
        evidence_line = "The white bandage on Mother's hand remains unstolen and unread, a clue left bright because you chose force before understanding."

    if in_full_trance(gs):
        path_line = "'THEM' do not recoil. In trance, you can feel their approval move through the room like tea poured into waiting cups."
    elif gs.spoke_with_mother:
        path_line = "She tried to spend her last strength on a warning, and you turned that warning into permission."
    else:
        path_line = "You never learned whether Mother was a victim, a witness, or the last door still trying to stay closed."

    print_bad_end(
        "THE KINDNESS YOU SPENT",
        first_line,
        evidence_line,
        path_line,
        "By dawn the house gives the world a simple story: a sick woman, a frightened child, a room full of proof. The harder truth remains upstairs, drinking quietly from the silence you made."
    )

def print_wrong_first_blow_bad_end(gs):
    if gs.ritual_branch == "obedience":
        path_line = "You drank from the ceremony and then tried to strike from inside it. The room knows the shape of your consent better than you do."
    elif gs.attic_choice == "question":
        path_line = "Your questions made Grandma show teeth, but questions are not a blade against the breath of the teapot."
    elif gs.attic_choice == "disrupt":
        path_line = "You offended the ritual, but you did not silence it. The spilled tea only taught the guests to hold the axe for you."
    elif gs.witness_awakened:
        path_line = "The witness had begun to tell you the rule, but you chose the visible throat before the invisible engine."
    else:
        path_line = "You brought an edge to a room whose danger was never only flesh."

    if "hearth ash" in gs.inventory and not gs.teapot_smothered:
        clue_line = "The hearth ash sits uselessly close, cold in your pocket, a lesson discovered but not carried to the steam."
    else:
        clue_line = "The teapot keeps breathing. Every ribbon of violet steam becomes another unseen hand."

    print_bad_end(
        "THE WRONG FIRST BLOW",
        path_line,
        clue_line,
        "Grandma does not need to dodge. She only smiles while 'THEM' turn your courage into obedience and your weapon into a family relic.",
        "By morning the axe is clean, the teacup is waiting, and your name has become one more whisper that warns the next visitor too late."
    )

def print_empty_chair_bad_end(gs):
    if gs.witness_awakened:
        witness_line = "Far below, the witness jar clouds from within. It remembers that it told you how to choke the steam, not how to inherit the room."
    else:
        witness_line = "No witness rises to explain what you have done. The house is very good at using silence as evidence."

    if gs.missy_heard:
        missy_line = "Missy's voice says inside your thoughts: 'You killed the mouth, not the hunger.' Then even her voice learns to hide from you."
    else:
        missy_line = "Somewhere in the walls, a childlike hush pulls away before you can know whether it was warning or grief."

    print_bad_end(
        "GRANDMA'S EMPTY CHAIR",
        "The ash broke the ceremony's rhythm, and the axe ended Grandma's body, but neither act taught the house mercy.",
        witness_line,
        missy_line,
        "The rocking chair begins moving again with no one in it. Without Grandma, 'THEM' do not leave. They spread out, curious and ownerless, and decide your fear is the nearest thing to a host.",
        "You escape the attic alive, but every quiet room afterward arranges itself around an empty chair."
    )

def handle_attack(gs, room, target, weapon_name=None):
    weapon = resolve_attack_weapon(gs, weapon_name)

    if not target:
        print("Violence needs a target, and the house waits to see whether you will name one.")
        return False

    if target in TEAPOT_ACTION_TARGETS:
        print("The teapot is not alive in any merciful sense. If you mean to break the ceremony, the steam is what matters.")
        return False

    if target in JAR_TARGETS and gs.current_room == "Cellar":
        if weapon:
            print(f"You strike the sealed jar with the {weapon}. The blow rings through the cellar like a bell struck underwater.")
            print("The glass does not crack. For a moment the liquid inside clouds white, then clears around a pale shape pressing one hand to the inside.")
        else:
            print("You try to break the sealed jar with your bare hands. The glass is cold, thick, and stubbornly whole.")
            print("Something inside taps back once, not frightened, not grateful, only awake.")
        return False

    if target in MOTHER_TARGETS:
        if not visible_character(gs, target):
            print("Mother is not here.")
            return False
        if not weapon:
            print("You raise your hands toward Mother, and for one lucid instant her eyes open with complete understanding.")
        else:
            print(f"You raise the {weapon} over Mother, and for one lucid instant her eyes open with complete understanding.")
        print("There is no struggle. That is the worst part. The house goes silent, not shocked, but satisfied that you have finally mistaken weakness for permission.")
        print("Mother's breath leaves her. Somewhere upstairs, Grandma begins to laugh without joy.")
        print_mother_bad_end(gs, weapon)
        gs.dead_characters.add("mother")
        gs.game_over = True
        return True

    if target in GRANDMA_TARGETS:
        if not visible_character(gs, target):
            print("Grandma is not within reach.")
            return False
        if weapon != "sharp axe":
            print("You move against Grandma, but the attempt has no clean edge. Her chair rocks once, and 'THEM' close ranks around her.")
            print("'No,' she says, almost kindly. 'Not with fear. Not with that.'")
            return False
        if not gs.teapot_smothered:
            print("You swing the sharp axe before the teapot's breath has been silenced. The blade stops inches from Grandma's neck, caught in a crowd of hands you cannot see.")
            print("'THEM' turn the edge back toward you with patient ceremonial strength.")
            print_wrong_first_blow_bad_end(gs)
            gs.game_over = True
            return True
        print("You swing the sharp axe after the ash has choked the teapot's breath. This time no hidden hand arrives in time.")
        print("Grandma turns just enough to look offended rather than afraid. Then the chair stops rocking.")
        print("For one impossible second the house is free of her voice. Then every other voice rushes to fill the vacancy.")
        print_empty_chair_bad_end(gs)
        gs.dead_characters.add("grandma")
        gs.game_over = True
        return True

    if target in MISSY_TARGETS:
        if gs.missy_heard:
            print("You lash out at the place where Missy's presence seems nearest, but there is no body there to harm.")
            print("The air chills with a child's hurt silence. Whatever Missy is now, she is beyond your reach, and the house seems ashamed of you for trying.")
        else:
            print("Missy is not here in any way your hands can reach.")
        return False

    print(f"You can't attack {attack_target_name(target)}.")
    return False

def unlock_front_door(gs, room):
    if gs.door_unlocked:
        print("The door is already open.")
        return
    print("\n*CLANG... CLANG... CLANG*")
    print("Grandma: 'The latch heard you before I did.'")
    print("You hear the heavy bolt slide back. The door is now open.")
    gs.door_unlocked = True
    room.exits["north"] = "Foyer"
    room.desc = OPEN_FRONT_DOOR_DESC
    room.scenery["door"] = "The door is now unlocked and slightly ajar."

def enter_front_door(gs):
    gs.current_room = "Foyer"
    print(state_text(
        gs,
        "You step through the open front door into the foyer.",
        "You step through the open front door, and the house folds its shadows around your arrival.",
        "You step through the open front door. The house lets you in, though less eagerly than before."
    ))

def room_name_aliases(room_id, room):
    names = {room_id.lower(), room.name.lower()}
    for name in tuple(names):
        if name.startswith("the "):
            names.add(name[4:])
        if name.startswith("your "):
            names.add(name[5:])
        if name.endswith(" hallway"):
            names.add("hallway")
        if name.endswith(" bedroom"):
            names.add("bedroom")
        if name.endswith(" landing"):
            names.add("landing")
    return {name.replace("'s", "s") for name in names}

def is_current_room_reference(gs, room, target):
    if not target:
        return False
    return target in room_name_aliases(gs.current_room, room)

def resolve_movement_direction(gs, room, target):
    if not target:
        return None
    if target in STAIR_TARGETS:
        if "up" in room.exits:
            return "up"
        if "down" in room.exits:
            return "down"
    if target in OUT_TARGETS:
        preferred_destinations = (
            "Garden", "Front Door", "Front Gate", "Upstairs Hallway",
            "Attic Landing", "Foyer", "Kitchen"
        )
        for preferred_destination in preferred_destinations:
            for direction, destination in room.exits.items():
                if destination == preferred_destination:
                    return direction
        if len(room.exits) == 1:
            return next(iter(room.exits))
    for direction, destination in room.exits.items():
        destination_room = gs.rooms[destination]
        if target == direction or target in room_name_aliases(destination, destination_room):
            return direction
    return None

def known_room_name(gs, target):
    if not target:
        return False
    return any(target in room_name_aliases(room_id, room) for room_id, room in gs.rooms.items())

def room_display_for_target(gs, target):
    for room_id, room in gs.rooms.items():
        if target in room_name_aliases(room_id, room):
            return room.name
    return "That room"

def move_player(gs, room, direction):
    destination = room.exits[direction]
    reclaim_attic_items_if_leaving(gs, room, destination)
    gs.current_room = destination
    print(state_text(
        gs,
        f"You head {direction}...",
        f"You head {direction}, and the house seems to adjust around your choice before you arrive.",
        f"You head {direction}. The house yields the path, though reluctantly."
    ))

def take_mother_bandage(gs, room):
    if gs.bandage_taken:
        print("The bandage is already gone from Mother's hand.")
        return False
    gs.bandage_taken = True
    gs.inventory["bloodied bandage"] = [
        "bandage", "white bandage", "bloodied bandage",
        "cloth", "white cloth", "bloodied cloth",
        "mother's bandage", "mothers bandage"
    ]
    room.scenery["bandage"] = "The bandage is gone from Mother's hand. A dark red stain remains on the exposed skin beneath."
    print(state_text(
        gs,
        "You carefully loosen the bandage from Mother's hand. It comes away warm and spotted through with old blood.",
        "You carefully loosen the bandage from Mother's hand. In trance it feels less like cloth than a kept promise, still warm with the ritual that wanted to claim it.",
        "You carefully loosen the bandage from Mother's hand. It feels lighter than before, but more accusing, as if now it belongs to a choice instead of a spell."
    ))
    return True

def unlock_attic_door(gs, room):
    item_id = resolve_item(gs, "key", "inventory")
    if item_id == "brass key":
        if gs.attic_unlocked:
            print("It's already unlocked.")
        elif not gs.moved_portraits:
            print("The key yields a little, then binds as though another hand has taken hold of it from within.")
            print("Somewhere along the hallway wall, wood taps once against plaster. The watching faces seem to know why you are being refused.")
        elif not gs.attic_primed:
            print("\nThe key turns with a grudging click, then stops at a second catch.")
            print("A breath escapes the seam of the door, carrying a whisper soft as dust across a coffin lid: 'Knock, and be named.'")
            gs.attic_primed = True
            room.scenery["door"] = "The lock has given way once, but the room beyond still insists on being asked, as if a key can open the metal but not the will behind it."
            room.scenery["attic door"] = room.scenery["door"]
        else:
            print("The key has done all it can. What remains is older than locksmithing: the room is waiting to hear you ask entry in the language it prefers.")
    else:
        print("You need a specific key for this door.")

def awaken_witness_jar(gs):
    gs.witness_awakened = True
    gs.discovered_witness = True
    print(state_text(
        gs,
        "You press the bloodied bandage to the glass. The jar clouds instantly, then clears from within.",
        "You press the bloodied bandage to the glass. The jar answers as if it has been waiting for exactly this proof.",
        "You press the bloodied bandage to the glass. The response is weaker than it would once have been, but still immediate enough to make your stomach turn."
    ))
    print("A pale face forms just beneath the surface and mouths words directly into your thoughts:")
    print("'When the teapot is fed, Amon opens. When the teapot is choked, cast hearth ash across the steam or 'THEM' will keep drinking from the air.'")

def smother_teapot_with_ash(gs, room):
    if not gs.trance:
        print("The ash scatters across the steam and falls dull through it. Nothing in the room has opened enough for the gesture to matter yet.")
        print("Grandma watches the failed attempt with mild disappointment. 'Tea first, dear,' she says. 'Then symbols learn to bite.'")
        return
    gs.teapot_smothered = True
    gs.ritual_branch = "ash"
    gs.branch_scene_seen = False
    gs.weakened_trance = True
    room.desc = "Grandma remains in the rocking chair, with the open door south to the landing behind you. The violet steam now hangs in bruised, broken ribbons above the teapot, and the room feels offended rather than welcoming."
    room.trance_desc = "'THEM' no longer wait in reverence. The open door south to the landing remains visible but distant, while their shapes pull at the dim air in restless, wounded knots around the teapot's darkened mouth."
    if gs.attic_choice is None:
        gs.attic_choice = "disrupt"
    print("You cast the hearth ash across the teapot. The violet steam stutters, darkens, and sinks low.")
    print("For the first time, Grandma sounds uncertain. 'Who taught you that?' she whispers.")
    print("Something inside your head unlatches. The house does not disappear, but its voice retreats from your bloodstream to the far side of the walls.")

def reveal_hearth_ash(gs, room, intro=None):
    gs.ash_revealed = True
    room.items["hearth ash"] = [
        "ash", "cinders", "hearth ash", "pale ash",
        "pale hearth ash", "cold ash", "pale cinders", "hearth cinders"
    ]
    if intro:
        print(intro)
    print("Beneath the screaming blue flame, you notice a bed of pale hearth ash that has somehow escaped burning.")
    print("It does not glow like the rest of the hearth. Instead it seems to drink the blue light out of the flame above it, turning warmth into hush.")

def active_hearth_ash(gs):
    return gs.trance and "hearth ash" in gs.inventory and not gs.teapot_smothered

def witnessed_active_ash(gs):
    return active_hearth_ash(gs) and gs.witness_awakened

def reclaim_attic_items_if_leaving(gs, room, destination):
    if gs.current_room != "Attic" or destination == "Attic":
        return

    if TEAPOT_ITEM in gs.inventory:
        gs.inventory.pop(TEAPOT_ITEM)
        room.items[TEAPOT_ITEM] = TEAPOT_ALIASES[:]
        if gs.teapot_smothered:
            print("As you cross the threshold, the teapot grows suddenly heavy, then weightless. When you look back, it has returned to Grandma's table, breathing bruised steam into the attic air.")
        else:
            print("As you cross the threshold, the teapot grows suddenly heavy, then weightless. When you look back, it sits on Grandma's table again, breathing violet steam exactly where the ceremony wants it.")
        print("Your inventory feels lighter. The teapot has returned to the attic.")

    if TEACUP_ITEM in gs.inventory:
        gs.inventory.pop(TEACUP_ITEM)
        room.items[TEACUP_ITEM] = TEACUP_ALIASES[:]
        if TEAPOT_ITEM in room.items:
            print("As you cross the threshold, the china teacup slips from your hand without falling. When you look back, it sits beside the teapot again, exactly where Grandma's table wants it.")
        else:
            print("As you cross the threshold, the china teacup slips from your hand without falling. When you look back, it has returned to the small table, set in its proper place beside the empty silver ring.")
        print("Your inventory feels lighter. The china teacup has returned to the attic.")

def print_bowl_description(gs, room):
    if TEACUP_ITEM in gs.inventory:
        if in_full_trance(gs):
            print("The china teacup in your hand feels warm, though nothing has been poured yet. Its inner glaze reflects faces that are not yours.")
        elif in_weakened_trance(gs):
            print("The china teacup in your hand feels ordinary for a breath, then too light, as if the room has already begun taking it back.")
        else:
            print("The china teacup is thin, white, and cold in your hand. A hairline crack curls around the rim without quite breaking it.")
    elif TEACUP_ITEM in room.items:
        if in_full_trance(gs):
            print("The china teacup waits beside the teapot. Its empty teacup reflects violet steam and the suggestion of many hands reaching for one place.")
        elif in_weakened_trance(gs):
            print("The china teacup waits beside the teapot, clean and stubborn, as if the ceremony has lost strength but not habit.")
        else:
            print("A single china teacup sits beside the teapot. It is turned toward you with unnerving care, handle angled exactly where your fingers would find it.")
    else:
        print("You cannot find the teacup, though the table still seems arranged around where it ought to be.")

def pour_tea_into_bowl(gs, room):
    if TEAPOT_ITEM in gs.inventory and TEACUP_ITEM in gs.inventory:
        print("The teapot tilts toward the china teacup in your hands. A dark thread of tea pours between them without spilling, as if both pieces remember the motion better than you do.")
    elif TEAPOT_ITEM in gs.inventory:
        print("The teapot pulls toward the china teacup on the table. A dark thread of tea pours into it without your wrist quite choosing the angle.")
    elif TEACUP_ITEM in gs.inventory:
        print("The teapot tilts toward the china teacup in your hands. A dark thread of tea pours into it without splashing, filling the teacup with warmth that feels almost rehearsed.")
    elif TEACUP_ITEM in room.items:
        print("The teapot tilts on the small table. Tea streams into the waiting china teacup, and the teacup receives it with a soft porcelain click, as if it has been thirsty for years.")
    else:
        print("A china teacup settles into view just long enough for the teapot to find it. Tea pours into the sudden white hollow, making a place for your hand before your hand has agreed.")

def item_available(gs, room, item_id):
    return item_id in room.items or item_id in gs.inventory

MOTHER_TARGETS = frozenset(("mother", "mom"))
GRANDMA_TARGETS = frozenset(("grandma", "grandmother"))
GRANDMA_TALK_TARGETS = GRANDMA_TARGETS | frozenset(("amon", "house"))
MISSY_TARGETS = frozenset(("missy", "sister"))
CHARACTER_TARGETS = MOTHER_TARGETS | GRANDMA_TARGETS | MISSY_TARGETS

ROOM_LOOK_TARGETS = frozenset((None, "around", "room", "area", "here", "all", "everything"))
PHOTO_TARGETS = frozenset((
    "photo", "photograph", "family photo", "family photograph",
    "face-down photo", "face-down photograph", "face down photo",
    "face down photograph", "old photo", "old photograph"
))
LEDGER_TARGETS = frozenset((
    "ledger", "ritual ledger", "ritual book", "old ledger",
    "household ledger", "family ledger", "ledger book"
))
INVITATION_TARGETS = frozenset((
    "card", "invitation", "invitation card", "formal invitation",
    "white card", "old invitation", "expected card"
))
NAMEPLATE_TARGETS = frozenset((
    "nameplate", "plate", "brass nameplate", "amon nameplate",
    "narrow nameplate", "narrow brass nameplate", "amon plate", "amon"
))
GRAVE_TARGETS = frozenset((
    "grave", "old grave", "sunken grave", "headstone", "old headstone",
    "crooked headstone", "headstones", "crooked headstones", "marker", "grave marker"
))
JAR_TARGETS = frozenset((
    "jar", "sealed jar", "glass jar", "sealed glass jar",
    "unlabelled jar", "unlabelled jars", "unlabeled jar", "unlabeled jars",
    "thick jar", "thick glass jar", "jars", "souls", "soul jar", "witness jar"
))
LABEL_TARGETS = frozenset((
    "labels", "label", "jar label", "jar labels", "peeling label",
    "peeled label", "sealed jar", "glass jar", "jar", "jars"
))
TEAPOT_ITEM = "teapot"
TEAPOT_ALIASES = [
    "pot", "tea", "silver teapot", "lidded teapot",
    "ritual teapot", "grandma's teapot", "grandmas teapot"
]
TEAPOT_TARGETS = frozenset((TEAPOT_ITEM, *TEAPOT_ALIASES))
TEAPOT_ACTION_TARGETS = TEAPOT_TARGETS | frozenset((
    "steam", "violet steam", "teapot steam", "teapot's steam",
    "teapots steam", "violet vapor", "violet vapour"
))
TEACUP_ITEM = "china teacup"
TEACUP_ALIASES = [
    "cup", "cups", "teacup", "teacups", "china cup", "china cups",
    "tea cup", "tea cups", "china tea cup", "china tea cups",
    "single teacup", "single china teacup", "white teacup",
    "porcelain cup", "porcelain teacup"
]
CUP_TARGETS = frozenset((TEACUP_ITEM, *TEACUP_ALIASES, "china teacups"))
BANDAGE_TARGETS = frozenset((
    "bandage", "white bandage", "bloodied bandage",
    "cloth", "white cloth", "bloodied cloth",
    "mother's bandage", "mothers bandage",
    "hand", "mother's hand", "mothers hand", "wrapped hand"
))
BANDAGE_TOPIC_TARGETS = BANDAGE_TARGETS | frozenset(("blood", "wound"))
WITNESS_READ_TARGETS = LEDGER_TARGETS | LABEL_TARGETS

GATE_TARGETS = frozenset((
    "gate", "gates", "iron gate", "iron gates",
    "rusted gate", "rusted gates", "rusted iron gate", "rusted iron gates"
))
ATTIC_DOOR_TARGETS = frozenset((
    "door", "attic", "attic door", "attic room door",
    "heavy door", "heavy oak door", "oak door", "north door",
    "lock", "brass lock", "dull brass lock", "attic lock"
))
FRONT_DOOR_TARGETS = frozenset((
    "door", "front door", "oak door", "heavy door",
    "heavy oak door", "barred door", "front oak door"
))
ATTIC_DOOR_OPTIONAL_TARGETS = ATTIC_DOOR_TARGETS | frozenset((None,))
KNOCKER_TARGETS = frozenset((
    "knocker", "brass knocker", "gargoyle", "brass gargoyle",
    "gargoyle knocker", "brass gargoyle knocker", "heavy brass knocker",
    "gargoyle jaw", "gargoyle's jaw", "gargoyles jaw"
))
FRONT_KNOCK_TARGETS = FRONT_DOOR_TARGETS | KNOCKER_TARGETS | frozenset((None,))

IN_TARGETS = frozenset(("in", "inside", "house", "foyer", "door", "room", "through door", "inside house"))
OUT_TARGETS = frozenset(("out", "outside", "back", "away", "outside house"))
STAIR_TARGETS = frozenset(("stair", "stairs", "staircase", "steps", "narrow stair", "attic stair", "grand staircase"))
TAKE_ALL_TARGETS = frozenset(("all", "everything", "all items", "items"))

KEY_TARGETS = frozenset((
    "key", "brass key", "small key", "small brass key",
    "old key", "old brass key", "attic key", "cold key", "cold brass key"
))
AXE_TARGETS = frozenset((
    "axe", "heavy axe", "kitchen axe", "big axe", "dull axe",
    "sharp axe", "sharpened axe", "sharp heavy axe", "sharpened heavy axe"
))
STONE_TARGETS = frozenset((
    "stone", "sharpening stone", "whetstone", "whet stone",
    "flat stone", "oily stone"
))
SHARPEN_TARGETS = AXE_TARGETS | STONE_TARGETS
WEAPON_ITEMS = frozenset(("heavy axe", "sharp axe", "silver spoon", "brass key", "sharpening stone"))
LIGHT_BLOCKED_ITEMS = WEAPON_ITEMS | frozenset(("grave dirt", "sealed jar", TEAPOT_ITEM, TEACUP_ITEM))
STUDY_SURFACE_TARGETS = frozenset((
    "desk", "writing desk", "old writing desk", "drawer", "desk drawer",
    "crooked drawer", "papers", "loose papers", "paper trail",
    "bookcase", "bookcases", "tall bookcase", "tall bookcases",
    "books", "shelves", "family records", "records"
))
STUDY_FINDABLE_ITEMS = ("ritual ledger", "invitation card")

PORTRAIT_TARGETS = frozenset((
    "portrait", "portraits", "painting", "paintings", "oil painting",
    "oil paintings", "ancestor painting", "ancestor paintings", "ancestors",
    "ancestor portrait", "ancestor portraits", "amon ancestors",
    "painted ancestors", "watching faces", "painted faces",
    "frame", "frames", "picture", "pictures", "painted frame", "painted frames"
))

GUEST_TOPIC_TARGETS = frozenset((
    "them", "'them'", "\"them\"", "guest", "guests", "company",
    "invisible guest", "invisible guests", "invisible company"
))

HEARTH_TARGETS = frozenset((
    "hearth", "fireplace", "stone hearth", "cold hearth",
    "kitchen hearth", "hearthstone", "hearth stone"
))

FLAME_TARGETS = frozenset((
    "flame", "flames", "blue flame", "blue flames", "fire",
    "blue fire", "hearth fire", "cold fire", "cold blue flame",
    "cold blue fire", "thin blue flame", "hearth flame"
))
KITCHEN_FIRE_TARGETS = HEARTH_TARGETS | FLAME_TARGETS

OBJECT_ALIASES = {
    "rusted gate": "gate",
    "rusted gates": "gates",
    "rusted iron gate": "iron gate",
    "rusted iron gates": "iron gates",
    "brass knocker": "knocker",
    "gargoyle knocker": "knocker",
    "brass gargoyle": "gargoyle",
    "brass gargoyle knocker": "knocker",
    "heavy brass knocker": "knocker",
    "gargoyle jaw": "knocker",
    "gargoyle's jaw": "knocker",
    "gargoyles jaw": "knocker",
    "narrow nameplate": "nameplate",
    "narrow brass nameplate": "brass nameplate",
    "amon plate": "amon nameplate",
    "blackened silver candelabrum": "candelabrum",
    "silver candelabrum": "candelabrum",
    "long table": "table",
    "walnut table": "table",
    "long walnut table": "table",
    "scraped floor": "floor",
    "scraped floorboards": "floorboards",
    "scraped boards": "floorboards",
    "pale scrapes": "floor",
    "fourth chair": "head chair",
    "empty chair": "head chair",
    "empty head chair": "head chair",
    "swollen sideboard": "sideboard",
    "dusty sideboard": "sideboard",
    "face-down photo": "photograph",
    "face-down photograph": "photograph",
    "face down photo": "photograph",
    "face down photograph": "photograph",
    "old photo": "photograph",
    "old photograph": "photograph",
    "writing desk": "desk",
    "old writing desk": "desk",
    "crooked drawer": "drawer",
    "desk drawer": "drawer",
    "loose papers": "papers",
    "tall bookcase": "bookcase",
    "tall bookcases": "bookcase",
    "bookcases": "bookcase",
    "family records": "records",
    "ritual book": "ledger",
    "old ledger": "ledger",
    "household ledger": "ledger",
    "family ledger": "ledger",
    "ledger book": "ledger",
    "ritual ledger": "ledger",
    "formal invitation": "invitation",
    "invitation card": "invitation",
    "white card": "card",
    "old invitation": "invitation",
    "stone hearth": "hearth",
    "cold hearth": "hearth",
    "kitchen hearth": "hearth",
    "hearthstone": "hearth",
    "hearth stone": "hearth",
    "cold blue flame": "blue flame",
    "thin blue flame": "blue flame",
    "cold blue fire": "blue fire",
    "hearth flame": "hearth fire",
    "scarred worktable": "worktable",
    "hanging utensils": "utensils",
    "steep stairwell": "stairwell",
    "steep stairs": "stairs",
    "cellar stair": "cellar stairs",
    "cellar stairwell": "cellar stairs",
    "painted ancestors": "ancestors",
    "amon ancestors": "ancestors",
    "watching faces": "portraits",
    "painted faces": "portraits",
    "ancestor portrait": "portrait",
    "ancestor portraits": "portraits",
    "ancestor painting": "painting",
    "ancestor paintings": "paintings",
    "oil portrait": "portrait",
    "oil portraits": "portraits",
    "behind painted ancestors": "behind ancestors",
    "behind amon ancestors": "behind ancestors",
    "large keyhole": "keyhole",
    "ornate keyhole": "keyhole",
    "large ornate keyhole": "keyhole",
    "brass lock": "lock",
    "dull brass lock": "lock",
    "attic lock": "lock",
    "half-open door": "door",
    "single candle": "candle",
    "guttering candle": "candle",
    "cold window": "window",
    "window glass": "window",
    "small table": "table",
    "violet steam": "steam",
    "teapot steam": "steam",
    "teapot's steam": "steam",
    "teapots steam": "steam",
    "sealed glass jar": "sealed jar",
    "glass jar": "jar",
    "unlabelled jar": "jar",
    "unlabelled jars": "jars",
    "unlabeled jar": "jar",
    "unlabeled jars": "jars",
    "thick glass jar": "jar",
    "soul jar": "jar",
    "witness jar": "jar",
    "old grave": "grave",
    "sunken grave": "grave",
    "grave marker": "marker",
    "old marker": "marker",
    "old headstone": "headstone",
    "crooked headstone": "headstone",
    "crooked headstones": "headstones",
    "loose grave dirt": "grave dirt",
    "grave soil": "grave dirt",
    "loose soil": "grave dirt",
    "disturbed soil": "grave dirt",
    "cemetery dirt": "grave dirt",
    "wet dirt": "grave dirt",
    "wet soil": "grave dirt",
    "small brass key": "brass key",
    "old brass key": "brass key",
    "cold brass key": "brass key",
    "attic key": "brass key",
    "kitchen axe": "heavy axe",
    "big axe": "heavy axe",
    "dull axe": "heavy axe",
    "sharp heavy axe": "sharp axe",
    "sharpened heavy axe": "sharp axe",
    "whetstone": "sharpening stone",
    "whet stone": "sharpening stone",
    "flat stone": "sharpening stone",
    "oily stone": "sharpening stone",
    "silver teaspoon": "silver spoon",
    "tea spoon": "silver spoon",
    "lidded teapot": "teapot",
    "ritual teapot": "teapot",
    "grandma's teapot": "teapot",
    "grandmas teapot": "teapot",
    "single teacup": "china teacup",
    "single china teacup": "china teacup",
    "white teacup": "china teacup",
    "china cup": "china teacup",
    "tea cup": "china teacup",
    "white china teacup": "china teacup",
    "porcelain cup": "china teacup",
    "porcelain teacup": "china teacup",
    "china tea cup": "china teacup",
    "pale ash": "hearth ash",
    "pale hearth ash": "hearth ash",
    "cold ash": "hearth ash",
    "pale cinders": "hearth ash",
    "hearth cinders": "hearth ash",
    "white bandage": "bandage",
    "bloodied bandage": "bandage",
    "white cloth": "bandage",
    "bloodied cloth": "bandage",
    "mother's bandage": "bandage",
    "mothers bandage": "bandage",
    "mother's hand": "hand",
    "mothers hand": "hand",
    "wrapped hand": "hand",
    "sharp tools": "tools",
    "hanging tools": "tools",
    "tools on wall": "tools",
    "rusted garden blades": "tools",
    "cluttered workbench": "workbench",
    "cracked window": "window",
    "warped shed door": "warped door",
    "up stairs": "up",
    "up staircase": "up",
    "down stairs": "down",
    "down staircase": "down",
    "grand staircase": "staircase",
    "front hall": "foyer",
    "hall": "foyer",
    "mother's room": "living room",
    "mothers room": "living room",
    "grandma's room": "attic",
    "grandmas room": "attic",
    "my bedroom": "bedroom",
    "my room": "bedroom",
    "your room": "bedroom",
    "childhood bedroom": "bedroom",
    "childhood room": "bedroom",
    "old bedroom": "bedroom",
    "old room": "bedroom",
}

def normalize_object_name(name):
    if not name:
        return name
    return OBJECT_ALIASES.get(name.strip().lower(), name)

def normalize_command_object(verb, name):
    name = normalize_object_name(name)
    if not name:
        return name
    if verb == "take":
        for prefix in ("up ", "off "):
            if name.startswith(prefix):
                return normalize_object_name(name[len(prefix):])
    return name

OPEN_FRONT_DOOR_DESC = "The heavy oak door stands open, leading north into the dark foyer. The path back to the Front Gate lies south, and the gargoyle knocker looks almost satisfied above the narrow AMON nameplate."

def portrait_lore_text(gs):
    lines = [
        "The oil paintings are arranged like a family court rather than decoration.",
        "The oldest frame bears only the name AMON. The figure inside is narrow-faced and severe, one hand resting on a house plan, the other on a lidded teacup.",
        "ELISE sits in mourning black with a physician's bag at her feet. Her gloved fingers are folded so tightly they look stitched together.",
        "MARIUS stands before what might be the cellar stairs, his expression calm while rows of little glass jars glimmer behind him.",
        "HESTER is painted younger than the others, but her eyes have Grandma's cold patience. A silver spoon lies across the saucer beside her untouched tea."
    ]
    if gs.moved_portraits:
        lines.append("One frame now hangs crooked. Behind it, the exposed carving reads: 'Let invited blood knock, and the listening room shall answer.'")
    elif in_full_trance(gs):
        lines.append("In trance, their painted eyes do not follow you. They wait for you to become worth following.")
    elif in_weakened_trance(gs):
        lines.append("Their eyes have settled back into paint, mostly, though each frame still feels like a listening mouth held shut.")
    else:
        lines.append("Each nameplate is tarnished except at the edges, as if someone has touched the names often and carefully.")
    return "\n".join(lines)

def visible_item_for_read(gs, room, obj):
    if obj in NAMEPLATE_TARGETS:
        return gs.current_room == "Front Door"
    if obj in LEDGER_TARGETS:
        return item_available(gs, room, "ritual ledger")
    if obj in INVITATION_TARGETS:
        return item_available(gs, room, "invitation card")
    if obj in PHOTO_TARGETS:
        return item_available(gs, room, "family photograph")
    if obj in LABEL_TARGETS:
        return gs.current_room == "Cellar" or item_available(gs, room, "sealed jar")
    if obj in GRAVE_TARGETS:
        return gs.current_room == "Cemetery"
    if obj in PORTRAIT_TARGETS:
        return gs.current_room == "Upstairs Hallway"
    if obj in CARVING_TARGETS:
        return gs.current_room == "Upstairs Hallway" and gs.moved_portraits
    return True

DINING_FLOOR_TARGETS = frozenset((
    "floor", "floorboards", "boards", "under table", "beneath table",
    "under chair", "beneath chair", "scraped floor", "scraped floorboards",
    "scraped boards", "pale scrapes", "scrapes"
))

DINING_INITIAL_TARGETS = frozenset((
    "initials", "floor initials", "carved initials", "initials carved",
    "initials carved floor", "initials in floor", "initials on floor",
    "carving", "floor carving", "marks", "carved marks", "letters",
    "carved letters", "tiny initials", "tiny carved initials",
    "circle of initials", "circle of tiny initials", "carved circle",
    "family initials"
))
DINING_SEARCH_TARGETS = DINING_FLOOR_TARGETS | DINING_INITIAL_TARGETS

BEHIND_PAINTING_TARGETS = frozenset((
    "behind painting", "behind paintings", "behind portrait", "behind portraits",
    "behind oil paintings", "behind ancestor paintings", "behind ancestors",
    "behind oil painting", "behind oil portrait", "behind oil portraits",
    "behind ancestor portrait", "behind ancestor portraits",
    "behind painted ancestors", "behind amon ancestors",
    "behind watching faces", "behind painted faces", "behind faces"
))

CARVING_TARGETS = frozenset((
    "writing", "carving", "hidden carving", "hidden line", "line",
    "message", "hidden message", "words", "hidden words",
    "wall writing", "wall carving", "plaster", "carved text",
    "text", "inscription", "hidden inscription"
))

FIXED_TAKE_RESPONSES = {
    "candelabrum": "The candelabrum is too large and settled into the table's ceremony. You can touch the blackened silver, but it will not come with you.",
    "table": "The table is too heavy to take, and the room seems built around its refusal to move.",
    "chair": "The chair scrapes when touched, but taking it would mean dragging half the room's attention with it.",
    "head chair": "The head chair belongs too firmly to the table and to whatever keeps waiting there.",
    "place settings": "The place settings are arranged with ceremonial care. Disturbing them is one thing; carrying them off is another.",
    "sideboard": "The sideboard is too bulky to take, and whatever it has hidden will have to be found without carrying the furniture away.",
    "floor": "The floorboards are nailed down beneath your feet. The marks cut into them are what matter.",
    "floorboards": "The floorboards are nailed down beneath your feet. The marks cut into them are what matter.",
    "initials": "The initials are carved into the floor. You can read them, but not take them.",
    "floor initials": "The initials are carved into the floor. You can read them, but not take them.",
    "door": "The door is part of the house. It can be opened, entered, or knocked upon, but not taken.",
    "front door": "The front door is part of the house. It can be opened, entered, or knocked upon, but not taken.",
    "knocker": "The brass knocker is fixed into the door. It is meant to be lifted and struck, not pocketed.",
    "gargoyle": "The gargoyle is bolted into the door, watching you with the patience of old brass.",
    "nameplate": "The nameplate is screwed tight beneath the knocker. It belongs to the door and to the house's idea of itself.",
    "plate": "The nameplate is screwed tight beneath the knocker. It belongs to the door and to the house's idea of itself.",
    "brass nameplate": "The nameplate is screwed tight beneath the knocker. It belongs to the door and to the house's idea of itself.",
    "amon nameplate": "The nameplate is screwed tight beneath the knocker. It belongs to the door and to the house's idea of itself.",
    "mother": "Mother is not an object to carry. Her shallow breathing makes the thought feel cruel before it is even complete.",
    "mother": "Mother is not an object to carry. Her shallow breathing makes the thought feel cruel before it is even complete.",
    "sofa": "The sofa is too heavy, and Mother lies upon it like the last fragile thing keeping the room human.",
    "desk": "The desk is too heavy to take. Its secrets are more portable than its wood.",
    "drawer": "The drawer sticks in its frame. Whatever matters here will have to be taken from inside it.",
    "papers": "The loose papers are too scattered and brittle to gather usefully. Their pattern matters more than their possession.",
    "bookcase": "The bookcase looms over you, far too heavy and far too judgmental to take.",
    "window": "The window belongs to the wall and to the rain beyond it.",
    "portrait": "The portrait is fixed along the hallway. Its gaze follows you without needing to be carried.",
    "portraits": "The portraits are fixed along the hallway. Their gaze follows you without needing to be carried.",
    "painting": "The painting is fixed along the hallway. Its gaze follows you without needing to be carried.",
    "paintings": "The paintings are fixed along the hallway. Their gaze follows you without needing to be carried.",
    "oil painting": "The painting is fixed along the hallway. Its gaze follows you without needing to be carried.",
    "oil paintings": "The paintings are fixed along the hallway. Their gaze follows you without needing to be carried.",
    "ancestor painting": "The painting is fixed along the hallway. Its gaze follows you without needing to be carried.",
    "ancestor paintings": "The paintings are fixed along the hallway. Their gaze follows you without needing to be carried.",
    "keyhole": "The keyhole is part of the attic door. It gives you a view, not an object.",
    "rocking chair": "The rocking chair shifts back before your hands can claim it. Grandma's room keeps its own furniture.",
    "grandma": "Grandma is not something you can simply take. The room would object long before your hands found purchase.",
    "grandma": "Grandma is not something you can simply take. The room would object long before your hands found purchase.",
    "steam": "The steam curls away through your fingers. It can be smelled, watched, or interrupted, but not held.",
    "teacups": "The teacups are only half visible, suspended in someone else's hidden hands.",
    "jars": "There are too many jars to carry off together, and the shelves seem reluctant to release them.",
    "grave": "The grave is a place, not a possession.",
    "headstone": "The headstone is sunk deep into the wet earth.",
    "headstones": "The headstones belong to the cemetery and to the names beneath them.",
    "hearth": "The hearth is built into the kitchen stone. Only what gathers inside it could be taken.",
    "fireplace": "The fireplace is built into the kitchen stone. Only what gathers inside it could be taken.",
    "flame": "The blue flame slips through any thought of taking it.",
    "blue flame": "The blue flame slips through any thought of taking it.",
    "bed": "The bed is too heavy and too stale with old sleep to take.",
    "wardrobe": "The wardrobe is warped into its corner and far too large to carry.",
    "toys": "The toys look less useful than accusing. None seems willing to become yours again.",
    "stair": "The stair belongs to the house. It is a route, not a keepsake.",
    "stairs": "The stairs belong to the house. They are a route, not a keepsake.",
    "narrow stair": "The narrow stair belongs to the house. It is a route, not a keepsake.",
    "attic stair": "The narrow stair belongs to the house. It is a route, not a keepsake.",
}

def fixed_take_response(gs, room, obj):
    if not obj:
        return None
    if obj in FIXED_TAKE_RESPONSES:
        return FIXED_TAKE_RESPONSES[obj]
    if obj in room.scenery:
        return f"The {obj} is part of this room. You can examine it, but you cannot take it."
    return None

def reveal_portrait_carving(gs, room):
    gs.moved_portraits = True
    room.scenery["portrait"] = "One portrait hangs crooked now. Behind it, a line has been carved directly into the wall."
    room.scenery["portraits"] = room.scenery["portrait"]
    room.scenery["painting"] = room.scenery["portrait"]
    room.scenery["paintings"] = room.scenery["portrait"]
    room.scenery["oil painting"] = room.scenery["portrait"]
    room.scenery["oil paintings"] = room.scenery["portrait"]
    room.scenery["ancestor painting"] = room.scenery["portrait"]
    room.scenery["ancestor paintings"] = room.scenery["portrait"]
    room.scenery["ancestors"] = "The painted ancestors look disturbed now, as if one shifted frame has broken their formation."

WEAKENED_ROOM_TEXTS = {
    "Front Gate": "The gates still seem too much like hands, but the sky above them has settled back into an ordinary, wounded night. North, the house no longer pulls at you so cleanly; south, the cemetery lies still in the fog. The estate only watches.",
    "Foyer": "The chandelier sways though there is no wind. South is the front door, north the kitchen, west the living room, east the dining room, and up the staircase the house still holds its breath. The shadows no longer dance free of the walls, yet they lag a little behind the light.",
    "Living Room": "Mother still lies on the sofa, with the foyer east and the study north. Her shadow has sunk back into the shape of her body. Around the floorboards, the dark cup-stains remain, half-seen and impossible to forget.",
    "Kitchen": "The blue flame has thinned to an unsteady thread. South leads to the foyer, east to the garden, and down to the cellar. The kitchen is a kitchen again, mostly, but the hearth still seems to be holding its breath.",
    "Upstairs Hallway": "The portraits are back in their frames, though none look entirely painted anymore. Down lies the foyer, west your bedroom, and up the narrow stair the attic landing keeps its own counsel. The house holds your name quietly now.",
    "Attic Landing": "The landing has stopped leaning quite so hard around you. Down the narrow stair lies the hallway; north, the attic door remains the house's most stubborn mouth.",
    "Attic": "Grandma remains in the rocking chair, with the open door south to the landing behind you. The room's authority has frayed. The steam hangs low and stubborn above the teapot, and the space feels haunted now more than welcoming.",
    "Cellar": "The jars have gone quiet enough to pass for ordinary storage, if not for the shapes that still seem to drift away whenever you focus on them. Up the stairs, the kitchen's blue light waits like a practical excuse to leave.",
    "Dining Room": "The table is only a table again until you blink. West, the foyer remains plainly reachable. Then a fourth place setting threatens its return before settling back into absence.",
    "Cemetery": "The graves are still. North, the gate leads back toward the house. Even so, the damp earth looks recently disturbed, as though the dead only just agreed to lie back down.",
    "Garden": "The garden is cold and almost clean again. West, the kitchen door leaks blue light; north, the shed leans under the dead trees. The frost on the beds no longer crawls, but it has not forgotten how.",
    "Shed": "The shed smells again of oil, rust, and wet wood. South, the garden path waits through the warped door. The tools have stopped humming, though the sharpening stone still seems a little too awake on the bench."
}

TRANCE_SEARCH_TEXTS = {
    "Cemetery": "In trance, the graves no longer look sealed. Thin lines of green light connect certain stones to the house, as if the dead are still being counted.",
    "Living Room": "The room peels back its gentler lie. Around Mother's sofa, the floorboards are dark with old spill-marks shaped like teacups and kneeling feet.",
    "Dining Room": "The table is set for more than the living. Faint handprints bloom across the polished wood where 'THEM' have leaned in to listen.",
    "Study": "The papers refuse to stay still. One pattern repeats through the drift: invitation, blood, return, and a fourth word that blots itself out whenever you stare too long.",
    "Kitchen": "The hearthstone is scored with circles and tiny knife nicks. This was never only a kitchen.",
    "Cellar": "In trance, the jars are sorted with purpose: memory below, witness above, hunger nearest the stairs.",
    "Front Gate": "The path to the house is no path at all now, but a throat lined with old promises and older footsteps."
}

WEAKENED_SEARCH_TEXTS = {
    "Living Room": "The stain-rings by Mother's sofa remain visible, but only when you let your eyes go soft. The ritual has receded into evidence.",
    "Study": "The papers still gather around certain words: invitation, return, and one term that keeps hiding under crossed-out ink. Whatever power arranged them has lost the strength to keep the pattern steady.",
    "Kitchen": "The hearth marks are still there. They no longer blaze with meaning, but they have not gone innocent.",
    "Cellar": "The cellar shelves still sort themselves in your thoughts: memory below, witness above. The order feels remembered now, not enforced.",
    "Dining Room": "The table remembers 'THEM' better than the room does. Fingerprints of absence fade in and out along the polished wood."
}

TRANCE_LISTEN_TEXTS = {
    "Front Gate": "The cemetery answers the house in tiny, eager scratches. Beneath them all, a lullaby keeps trying to remember its words.",
    "Living Room": "Mother's breathing is no longer alone. Something breathes with her, just a half-beat behind, like a rehearsal for taking over.",
    "Dining Room": "'THEM' murmur around the head chair. They sound pleased whenever the family is spoken of as if it were a meal.",
    "Study": "The books recite names to one another. Some are family names. Some sound like titles no human should inherit.",
    "Kitchen": "The blue flame is singing through clenched teeth. Every pop in the hearth sounds like a tiny bone learning to speak.",
    "Cellar": "The jars hum in different notes, and together they form something like a choir practicing patience.",
    "Cemetery": "Below the soil, something knocks back in shallow little bursts, as if the dead have learned house manners."
}

WEAKENED_LISTEN_TEXTS = {
    "Front Gate": "The cemetery is quiet now, though once in a while the wind catches on the iron like a lullaby forgetting itself.",
    "Living Room": "Mother breathes alone again, though sometimes the room seems to expect a second breath and is disappointed not to hear it.",
    "Dining Room": "No chorus gathers at the table now. Only the occasional scrape of memory runs under the silence and is gone.",
    "Study": "The books have stopped reciting names. Now they only settle themselves too carefully whenever the house is mentioned.",
    "Kitchen": "The hearth crackles like something recovering from an argument. The flame has lost its voice, but not its temper.",
    "Cellar": "The jars no longer sing together. A few still ring softly when the house is challenged, as if old loyalties die slowly.",
    "Cemetery": "The ground holds still, but not peacefully. It sounds like a room where everyone has just stopped talking."
}

TRANCE_SMELL_TEXTS = {
    "Front Gate": "Wet iron, grave-moss, and the sweet rot of promises left outside too long.",
    "Living Room": "Copper, sleeping powder, and the stale perfume of someone kept alive for reasons other than mercy.",
    "Dining Room": "Wax, silver, old blood, and the warm illusion of family just before it curdles.",
    "Study": "Ink, mildew, and the dry animal scent of records handled by hands that never stopped counting.",
    "Kitchen": "Cinders, broth, and the sharp medicinal trace of instruments washed too carefully.",
    "Cellar": "Salt, glass, damp earth, and the sour breath of things preserved against their will.",
    "Cemetery": "Rain-soaked soil and the green, mineral scent of graves being remembered from below."
}

WEAKENED_SMELL_TEXTS = {
    "Front Gate": "Rain, iron, and the cold scent left behind when a storm chooses not to finish.",
    "Living Room": "Lavender, sickness, and only the faint remainder of copper now.",
    "Dining Room": "Wax, dust, and the ghost of a meal no longer being served.",
    "Study": "Paper, mildew, and the dry smell of secrets left open too long.",
    "Kitchen": "Ash, stone, and a sweetness that has finally begun to rot away.",
    "Cellar": "Damp glass and salt, with the preserved edge of something interrupted.",
    "Cemetery": "Wet soil and cooling stone."
}

NORMAL_SMELL_TEXTS = {
    "Kitchen": "Cold ash, damp stone, and something metallic under the sweetness of old tea.",
    "Attic": "Lavender, dust, and the copper tang of something freshly opened.",
    "Cellar": "Mold, brine, and rot sealed behind glass.",
    "Dining Room": "Cold silver, old candles, and the ghost of meals eaten under too many rules.",
    "Study": "Dust, ink, and the dry paper smell of secrets handled too often."
}

def trance_search_text(gs):
    if in_weakened_trance(gs):
        return WEAKENED_SEARCH_TEXTS.get(gs.current_room)
    return TRANCE_SEARCH_TEXTS.get(gs.current_room)

def trance_listen_text(gs):
    if in_weakened_trance(gs):
        return WEAKENED_LISTEN_TEXTS.get(gs.current_room)
    return TRANCE_LISTEN_TEXTS.get(gs.current_room)

def trance_smell_text(gs, obj):
    if obj in (None, "", "room", "air"):
        if in_weakened_trance(gs):
            return WEAKENED_SMELL_TEXTS.get(gs.current_room)
        return TRANCE_SMELL_TEXTS.get(gs.current_room)
    if obj in TEAPOT_TARGETS and gs.current_room == "Attic":
        if in_weakened_trance(gs):
            return "The tea no longer smells persuasive. Under the sweetness is a singed, frustrated bitterness, as if the ritual cannot decide whether it has failed or is merely waiting."
        return "Now the tea smells less like comfort than consent: sweetness over iron, warmth over surrender."
    return None

def trance_read_text(gs, obj):
    if in_weakened_trance(gs):
        if gs.current_room == "Study" and obj in LEDGER_TARGETS:
            return "The ledger resists rearranging itself now. A few lines still stand out: invite the blood, calm the witness, guard the heir. The spell has loosened, but the record remembers."
        if gs.current_room == "Study" and obj in INVITATION_TARGETS:
            return "The invitation looks like paper again, yet certain words still refuse to fade: blood, name, willing."
        if gs.current_room == "Dining Room" and obj in PHOTO_TARGETS:
            return "The extra figures in the photograph are nearly gone. Nearly."
        if gs.current_room == "Cemetery" and obj in GRAVE_TARGETS:
            return "The names stay still now, but the stone remembers having moved."
        return None
    if not in_full_trance(gs):
        return None
    if gs.current_room == "Study" and obj in LEDGER_TARGETS:
        return "In trance, the ledger rearranges itself into a liturgy: invite the blood, calm the witness, open the room, teach the heir."
    if gs.current_room == "Study" and obj in INVITATION_TARGETS:
        return "The invitation card no longer reads like courtesy. It reads like ownership granted in advance."
    if gs.current_room == "Dining Room" and obj in PHOTO_TARGETS:
        return "The family photograph is wrong in trance. Behind Grandma, faint extra figures have developed where no one stood when the picture was taken."
    if gs.current_room == "Cemetery" and obj in GRAVE_TARGETS:
        return "The names on the headstones ripple. Some family dates end, then begin again a few inches lower in the stone."
    return None

def missy_voice_event(gs):
    if gs.current_room == "Front Door" and not gs.door_unlocked:
        return "front_door", "'Don't push,' Missy's voice says inside your mind, small and urgent. 'It likes manners better than strength.'"
    if gs.current_room == "Foyer":
        return "foyer", "'It hears better in the hall,' Missy whispers inside your thoughts. 'Don't say yes just because the house leaves room for you to answer.'"
    if gs.current_room == "Dining Room":
        return "dining_room", "'Don't sit where she sits,' Missy's voice says, though no one stands beside you. 'That chair remembers who obeyed.'"
    if gs.current_room == "Living Room" and not gs.bandage_taken:
        return "living_room_bandage", "'Mother can hear more than she can say,' Missy whispers in your mind. 'Don't let the white cloth fool you. It remembers.'"
    if gs.current_room == "Study":
        return "study", "'The papers are scared of being read,' Missy says somewhere behind your eyes. 'That means they know something useful.'"
    if gs.current_room == "Your Bedroom":
        return "your_bedroom", "'You used to hide from her in here,' Missy's voice says. 'The room still knows the shape of hiding.'"
    if gs.current_room == "Upstairs Hallway":
        return "upstairs_hallway", "'The paintings listen for her,' Missy whispers. 'Make one look away.'"
    if gs.current_room == "Attic Landing" and not gs.attic_unlocked:
        return "attic_landing_locked", "'Keys are not enough,' Missy's thought brushes yours. 'Grandma taught the door to expect a voice.'"
    if gs.current_room == "Kitchen" and in_full_trance(gs) and not gs.ash_revealed:
        return "kitchen_trance_ash", "'The fire is lying,' Missy whispers in your mind. 'Look where it refuses to burn.'"
    if gs.current_room == "Cellar" and "bloodied bandage" in gs.inventory and not gs.witness_awakened:
        return "cellar_bandage", "'Don't break the jar,' Missy's voice says, faint as breath against glass. 'Wake it.'"
    if gs.current_room == "Attic" and not gs.trance and not gs.teapot_smothered:
        return "attic_tea_warning", "'That's not tea,' Missy says inside your skull, so close it hurts. 'They are waiting on the other side of the teacup, and the tea is the door pretending to be warm.'"
    if gs.current_room == "Attic" and gs.ritual_branch == "ash":
        return "attic_ash_branch", "'You made them hear themselves,' Missy's voice says. 'Now don't give them your fear to drink.'"
    return None

def handle_missy_voice(gs):
    event = missy_voice_event(gs)
    if not event:
        return
    key, text = event
    if key in gs.missy_voice_rooms:
        return
    gs.missy_voice_rooms.add(key)
    gs.missy_heard = True
    print(f"\n{text}")

def handle_room_entry(gs, room):
    if gs.current_room == "Attic" and not gs.attic_seen:
        print("\nThe rocking slows before stopping altogether.")
        print("Grandma does not turn, yet the room knows you have arrived. Somewhere in the air, porcelain touches porcelain with a careful, expectant chime.")
        print("'You came properly this time,' Grandma says. 'Good. Sit with the quiet a moment, and let it learn your breathing.'")
        print("The china teacup beside the teapot gives a small click and turns its handle toward you, warm enough already to fog the space above its rim.")
        print("'Drink,' Grandma says. 'Only a sip. Then you will hear the house properly.'")
        gs.attic_seen = True
        gs.tea_invited = True
    elif gs.current_room == "Attic" and gs.ritual_branch == "obedience" and not gs.branch_scene_seen:
        print("\n'THEM' part around you with something almost like courtesy.")
        print("The china teacup settles more deeply into its place in the ceremony, and Grandma inclines her head as though a private vow has just been witnessed.")
        print("'They know you now,' she says. 'Do not waste the kindness of being expected.'")
        gs.branch_scene_seen = True
    elif gs.current_room == "Attic" and gs.ritual_branch == "ash" and not gs.branch_scene_seen:
        print("\nThe attic has lost its false hospitality.")
        print("The steam hangs low and wounded. Around the room, 'THEM' shift with the restless sound of chairs scraping back from a spoiled feast.")
        print("Grandma grips the chair arms until the wood complains. 'If you stay,' she says, 'you stay without blessing.'")
        gs.branch_scene_seen = True
    handle_missy_voice(gs)

def new_game():
    rooms = setup_amon_house()
    return rooms, GameState(rooms)

class GameSession:
    def __init__(self, interactive_prompts=True):
        self.interactive_prompts = interactive_prompts
        self.reset()

    def reset(self):
        self.rooms, self.gs = new_game()
        self.gs.allow_interactive_prompts = self.interactive_prompts
        self.parser = AdvancedParser()
        self.suppress_room_display = False
        self.pending_restart = False
        self.move_count = 0
        self.last_counted_command_key = None
        self.finished = False

    def current_location(self):
        return self.gs.rooms[self.gs.current_room].name

    def print_welcome(self):
        print("WELCOME TO THE HOUSE OF AMON")
        print("----------------------------")
        print("Grandma is back. The tea is brewing. Don't listen to the voices.")

    def start(self):
        self.print_welcome()
        self.print_room_after_turn()

    def print_room_after_turn(self):
        if self.finished:
            return
        if self.suppress_room_display:
            self.suppress_room_display = False
        else:
            print_room(self.gs)

    def command_count_key(self, normalized_command):
        verb, obj, prep, indirect_obj = self.parser.parse(normalized_command)
        obj = normalize_command_object(verb, obj)
        indirect_obj = normalize_object_name(indirect_obj)
        if not verb:
            return normalized_command
        if indirect_obj is None:
            prep = None
        return verb, obj, prep, indirect_obj

    def handle_command(self, user_input):
        normalized_command = " ".join(user_input.strip().lower().split())
        if not normalized_command:
            return not self.finished

        if self.finished:
            print("The game has ended. Restart to begin again.")
            return False

        command_key = self.command_count_key(normalized_command)
        if command_key != self.last_counted_command_key:
            self.move_count += 1
            self.last_counted_command_key = command_key

        if self.pending_restart:
            self.resolve_restart(user_input)
            self.print_room_after_turn()
            return not self.finished

        keep_playing = self._process_command(user_input)
        if keep_playing and not self.finished:
            self.print_room_after_turn()
        return keep_playing and not self.finished

    def resolve_restart(self, user_input):
        self.pending_restart = False
        if user_input.strip().lower() in ("yes", "y"):
            self.reset()
            print("\nThe house exhales, and the night folds back to the beginning.")
            self.print_welcome()
        else:
            print("Restart cancelled. The house keeps its place.")

    def _process_command(self, user_input):
        gs = self.gs
        parser = self.parser
        room = gs.rooms[gs.current_room]
        v, obj, prep, i_obj = parser.parse(user_input)
        obj = normalize_command_object(v, obj)
        i_obj = normalize_object_name(i_obj)

        if not v:
            return True

        # 1. Global Commands
        if v == "help":
            print_help()
            self.suppress_room_display = True

        elif v == "quit":
            print("The voices will follow you...")
            self.finished = True
            return False

        elif v == "restart":
            print("Restart the game from the beginning? Your current progress will be lost.")
            print("Type yes to restart, or no to keep playing.")
            self.pending_restart = True
            self.suppress_room_display = True
            return True
            
        elif v == "inventory":
            describe_inventory(gs)

        elif v == "look":
            print_room(gs, include_entry=False)
            self.suppress_room_display = True

        # 2. Movement Logic
        elif v == "go":
            movement_direction = resolve_movement_direction(gs, room, obj)
            if gs.current_room == "Front Door" and (obj == "north" or obj in IN_TARGETS or obj in FRONT_DOOR_TARGETS) and gs.door_unlocked:
                enter_front_door(gs)
            elif gs.current_room == "Front Door" and (obj == "north" or obj in IN_TARGETS or obj in FRONT_DOOR_TARGETS) and not gs.door_unlocked:
                print("The door is locked from within. The brass gargoyle knocker waits at eye level, polished by visitors who knew better than to shove.")
            elif gs.current_room == "Attic Landing" and (obj == "north" or obj in IN_TARGETS or obj in ATTIC_DOOR_TARGETS):
                if gs.attic_unlocked:
                    gs.current_room = "Attic"
                    print(state_text(
                        gs,
                        "You step through the open attic doorway.",
                        "You step into the attic, and 'THEM' make room without moving.",
                        "You step into the attic. The room admits you, but its welcome has frayed."
                    ))
                elif gs.attic_primed:
                    print("The attic door has heard the key. Now it waits for the courtesy carved into the house: knock, and be named.")
                else:
                    print("The attic door is locked. Grandma is busy with the rite.")
            elif movement_direction:
                move_player(gs, room, movement_direction)
            elif gs.current_room == "Upstairs Hallway" and obj in ATTIC_DOOR_TARGETS:
                print("The attic door waits up the narrow stair, on the landing. Climb the stair first.")
            elif obj == "north" and gs.current_room == "Attic Landing" and not gs.attic_unlocked:
                print("The attic door is locked. Grandma is busy with the rite.")
            elif obj == "up" and gs.current_room == "Attic Landing":
                print("You are already at the attic landing. The attic door is north.")
            elif known_room_name(gs, obj):
                print(f"{room_display_for_target(gs, obj)} is not directly reachable from here. Follow one of the visible exits first.")
            else:
                print(state_text(
                    gs,
                    f"You can't go {obj or 'that way'}.",
                    f"You can't go {obj or 'that way'}. In trance, the refusal feels personal, as if the house has an opinion about your timing.",
                    f"You can't go {obj or 'that way'}. The path no longer twists to mislead you, but it still won't open."
                ))

        elif v == "exit":
            if gs.current_room == "Shed":
                gs.current_room = "Garden"
                print(state_text(
                    gs,
                    "You step out of the shed and back into the garden.",
                    "You step out of the shed. The tools' humming follows you for a few breaths, then sinks back into the walls.",
                    "You step out of the shed. The garden air feels thin and cold, but it is easier to breathe than oil and rust."
                ))
            elif len(room.exits) == 1 or len(set(room.exits.values())) == 1:
                direction = next(iter(room.exits))
                move_player(gs, room, direction)
            else:
                print(state_text(
                    gs,
                    "There is more than one way out from here. Choose a direction.",
                    "There is more than one way out from here, and in trance each one seems to be listening for your preference.",
                    "There is more than one way out from here. The house no longer hides that from you."
                ))

        # 3. Examination Logic
        elif v == "examine":
            if obj in ROOM_LOOK_TARGETS or is_current_room_reference(gs, room, obj):
                print_room_inspection(gs)
                self.suppress_room_display = True
            elif obj == "keyhole" and gs.current_room == "Attic Landing":
                print("\nYou peek through the keyhole. You see china teacups floating in mid-air!")
                print("At the edge of the narrow view, the curved runner of a rocking chair moves slowly in and out of sight.")
                print("Beside it waits a small table, mostly hidden by the angle, with something pale and deliberate set on top.")
            elif obj in BEHIND_PAINTING_TARGETS:
                if gs.current_room == "Foyer":
                    print("There are no paintings in the foyer. The walls here hold shadow and old wallpaper, but no watching faces.")
                    print("The staircase rises toward the upstairs hallway, where the ancestor paintings wait.")
                elif gs.current_room == "Upstairs Hallway":
                    if gs.moved_portraits:
                        print("One portrait already hangs crooked. Behind it, the hidden line remains carved into the wall: 'Let invited blood knock, and the listening room shall answer.'")
                    else:
                        reveal_portrait_carving(gs, room)
                        print("You look behind the paintings. One portrait shifts aside, revealing a hidden carving in the plaster behind it.")
                        print("The carving reads: 'Let invited blood knock, and the listening room shall answer.'")
                else:
                    print("There are no paintings here to look behind.")
            elif obj in ("ash", "hearth ash", "cinders"):
                if "hearth ash" in gs.inventory or "hearth ash" in room.items:
                    print("The ash is pale enough to seem unfinished, as if fire reached it and then lost its nerve.")
                    print("When you turn it in your hand, it clings lightly to your skin and leaves a chill instead of soot.")
                else:
                    print(f"You don't see a {obj} here.")
            elif gs.current_room == "Kitchen" and obj in HEARTH_TARGETS:
                if in_full_trance(gs):
                    print("The hearth is not merely burning now. The blue flame screams silently over a bed of pale ash, and the ash drinks the light instead of reflecting it.")
                    print("Something in the fire has spared those cinders for a reason, but the reason only holds while the house is dreaming through you.")
                elif in_weakened_trance(gs):
                    print("The hearth has quieted, though the stone still remembers its shape of violence. Pale ash rests beneath the thinning blue flame, less hidden now than leftover.")
                else:
                    print("The stone hearth holds a cold blue flame that gives off light without comfort. Pale ash lies beneath it, ordinary at first glance, waiting for some change in your sight.")
            elif gs.current_room == "Kitchen" and obj in FLAME_TARGETS:
                if in_full_trance(gs):
                    print("The blue flame screams in a frequency you feel in your teeth. Beneath it, the ash stays pale and still, untouched by the fire's panic.")
                elif in_weakened_trance(gs):
                    print("The blue flame has thinned to a nervous thread. It still avoids the pale ash below it.")
                else:
                    print("The flame is blue and thin, bending without wind. It makes the kitchen shadows look sharpened rather than warmed.")
            elif gs.current_room == "Your Bedroom" and obj in KEY_TARGETS:
                if "brass key" in room.items or "brass key" in gs.inventory:
                    print("The brass key is small, old, and colder than the room around it. Its teeth are cut in a strange uneven pattern, like a tiny skyline of broken houses.")
                else:
                    print("You do not see a key here.")
            elif gs.current_room == "Your Bedroom" and obj in ("all", "everything", "items", "room"):
                print("You take in the room piece by piece: the unmade bed, the guttering candle, the nightstand, the old toys, the warped wardrobe, the cold window, and the dust disturbed beneath the bed.")
                if "brass key" in room.items:
                    print("The brass key catches the candlelight as the only thing here that seems ready to leave.")
            elif obj in MISSY_TARGETS:
                if gs.missy_heard:
                    print("You search for Missy with your eyes, but there is no figure to find.")
                    print("Her voice lives closer than the room, tucked somewhere inside thought and memory.")
                else:
                    print("You do not see Missy here.")
            elif in_full_trance(gs) and gs.current_room == "Living Room" and obj in MOTHER_TARGETS:
                if gs.bandage_taken:
                    print("Mother's body lies still, one hand unwrapped and exposed. Her shadow keeps trying to sit up before something taller presses it gently back down.")
                else:
                    print("Mother's body lies still, but her shadow keeps trying to sit up before something taller presses it gently back down.")
            elif in_weakened_trance(gs) and gs.current_room == "Living Room" and obj in MOTHER_TARGETS:
                if gs.bandage_taken:
                    print("Mother looks human again, painfully so. Her unwrapped hand rests exposed against the sofa, and the skin around her eyes still carries the aftermath of dreams that did not end when yours did.")
                else:
                    print("Mother looks human again, painfully so, but the skin around her eyes still carries the aftermath of dreams that did not end when yours did.")
            elif gs.current_room == "Living Room" and obj in MOTHER_TARGETS and gs.bandage_taken:
                print("Mother lies on the sofa in waxen exhaustion. Her unwrapped hand rests limp against the velvet, marked by the dark stain the bandage left behind.")
            elif in_full_trance(gs) and gs.current_room == "Living Room" and obj in BANDAGE_TARGETS:
                if gs.bandage_taken:
                    print("The bandage is no longer on Mother's hand. Without it, the wound looks smaller but more honest, a dark mouth the room can no longer cover.")
                else:
                    print("The bandage shines almost white in trance. Beneath it, the wound pulses with the slow, stubborn rhythm of something being reopened by memory.")
            elif in_weakened_trance(gs) and gs.current_room == "Living Room" and obj in BANDAGE_TARGETS:
                if gs.bandage_taken:
                    print("The bandage is gone from Mother's hand. The exposed stain looks less supernatural now, which somehow makes it harder to look at.")
                else:
                    print("The bandage has gone ordinary again, but not innocent. Looking at it now feels like seeing a ritual after the chanting stops.")
            elif gs.current_room == "Living Room" and obj in BANDAGE_TARGETS:
                if gs.bandage_taken:
                    print("The bandage is gone from Mother's hand. A dark red stain remains on the exposed skin beneath.")
                else:
                    print("The white cloth around Mother's hand is fresh enough to shame the dust around it.")
            elif in_full_trance(gs) and gs.current_room == "Dining Room" and obj in ("chair", "head chair", "table"):
                print("The head chair is occupied now, if not by weight then by intention. The air bends around it with the patience of someone expected to be served first.")
            elif gs.current_room == "Dining Room" and obj == "sideboard":
                if "family photograph" in room.items:
                    print("The sideboard's swollen drawers smell of damp wood and old polish. A family photograph lies face-down on its dusty surface.")
                else:
                    print("The sideboard's swollen drawers smell of damp wood and old polish. Its dusty surface holds a clean rectangle where the photograph used to lie.")
            elif gs.current_room == "Dining Room" and obj in DINING_FLOOR_TARGETS:
                if "initials" in room.scenery:
                    print(room.scenery["floor"])
                    print(room.scenery["initials"])
                else:
                    print("Most of the floorboards disappear beneath the long table, but the boards under the head chair are scraped pale by repeated movement.")
            elif gs.current_room == "Dining Room" and obj in DINING_INITIAL_TARGETS:
                if "initials" in room.scenery:
                    print(room.scenery["initials"])
                else:
                    print("You do not see any initials yet. The head chair and the table's shadow still hide the floor beneath them.")
            elif in_full_trance(gs) and gs.current_room == "Study" and obj in STUDY_SURFACE_TARGETS:
                print("The study is no archive in trance. It is an accounting chamber. Every page seems less written than sentenced.")
            elif in_weakened_trance(gs) and gs.current_room == "Study" and obj in STUDY_SURFACE_TARGETS:
                print("The study has stopped performing. Now it merely looks guilty.")
            elif in_full_trance(gs) and gs.current_room == "Cellar" and obj in JAR_TARGETS:
                print("Each jar contains more than liquid now. Faces drift up through the murk, touching the glass from inside whenever your gaze lingers too long.")
            elif in_weakened_trance(gs) and gs.current_room == "Cellar" and obj in JAR_TARGETS:
                print("The faces are harder to catch now. You see them only in the instant before deciding you imagined them.")
            elif obj in PHOTO_TARGETS and ("family photograph" in room.items or "family photograph" in gs.inventory):
                trance_text = trance_read_text(gs, obj)
                if trance_text:
                    print(trance_text)
                else:
                    print("The photograph shows Mother, Missy, and you as children. Grandma stands behind you all with one hand on the back of the head chair, smiling as if she owns the light itself.")
            elif obj in GRANDMA_TARGETS and gs.current_room == "Attic":
                if in_full_trance(gs):
                    print("Grandma's face seems both ancient and newly made, the skin stretched thin over a smile that belongs to someone being greeted from very far away.")
                elif in_weakened_trance(gs):
                    print("Grandma looks older now that the room is no longer flattering her. Not harmless, not defeated, but more mortal than she would like to be seen.")
                else:
                    print("Grandma remains turned from you, but her posture is not frail. One hand rests on the chair arm, still as a spider waiting at the center of its web.")
            elif obj == "table" and gs.current_room == "Attic":
                if TEAPOT_ITEM in room.items:
                    if TEACUP_ITEM in room.items:
                        print("A small table stands beside Grandma, set with the teapot and a single china teacup placed exactly where your hand would reach.")
                    else:
                        print("A small table stands beside Grandma, set with the teapot and a pale ring where the china teacup should be.")
                elif TEACUP_ITEM in room.items:
                    print("The small table beside Grandma holds only the china teacup now, waiting in the clean ring where the service expects it.")
                else:
                    print("The small table beside Grandma is bare now except for a clean silver ring in the dust where the teapot used to rest.")
            elif obj in TEAPOT_TARGETS and gs.current_room == "Attic":
                if in_full_trance(gs):
                    print("The teapot glows from within like a sealed heart. Each breath of steam carries murmurs, laughter, and the weight of a promise you half remember making.")
                elif in_weakened_trance(gs):
                    print("The teapot has lost its inner glow. Its steam still rises, but with effort now, as if the ritual must push each breath uphill.")
                else:
                    print("The teapot is immaculate despite the dust around it. Its lid trembles now and then, as if something inside is breathing.")
            elif obj in CUP_TARGETS and gs.current_room == "Attic":
                if obj in ("teacups", "china teacups", "tea cups"):
                    print_bowl_description(gs, room)
                    print("Beyond it, the air dimples. Other rims and pale reflections appear and vanish as hidden hands test their place settings.")
                else:
                    print_bowl_description(gs, room)
            elif gs.current_room == "Front Door" and obj in FRONT_DOOR_TARGETS:
                if gs.door_unlocked:
                    print("The heavy oak door stands open now, with the dark foyer waiting north. The AMON nameplate beneath the knocker catches a dull glint.")
                else:
                    print("The oak door is barred from the inside. The only parts that look handled are the brass gargoyle knocker and the narrow AMON nameplate beneath it.")
            elif gs.current_room == "Front Gate" and obj in GATE_TARGETS:
                print(state_text(
                    gs,
                    room.scenery.get(obj, room.scenery["gate"]),
                    "In trance, the iron gate is not open so much as holding the path apart. Its bars have become long knuckled fingers, rust flaking from them like dried blood. North, the house pulls with the patience of a mouth about to speak; south, the cemetery breathes back.",
                    "The iron gate has mostly returned to metal, though the bars still seem too much like fingers when seen from the corner of your eye."
                ))
            elif gs.current_room == "Upstairs Hallway" and obj in PORTRAIT_TARGETS:
                print(portrait_lore_text(gs))
            elif gs.current_room == "Upstairs Hallway" and obj in CARVING_TARGETS and gs.moved_portraits:
                print("Behind the shifted portrait, the hidden carving remains exposed.")
                print("The carving reads: 'Let invited blood knock, and the listening room shall answer.'")
            elif obj in room.scenery:
                print(room.scenery[obj])
            else:
                # Check if it's an item in the room or inventory using Aliases
                item_id = resolve_item(gs, obj, "room") or resolve_item(gs, obj, "inventory")
                if item_id:
                    print(f"It's a {item_id}. It looks significant to the House.")
                else:
                    print(f"You don't see a {obj} here.")

        elif v == "read":
            if not visible_item_for_read(gs, room, obj):
                print("There is nothing like that here to read.")
                return True
            trance_text = trance_read_text(gs, obj)
            if trance_text:
                if obj in WITNESS_READ_TARGETS:
                    gs.discovered_witness = True
                print(trance_text)
            elif obj in PORTRAIT_TARGETS and gs.current_room == "Upstairs Hallway":
                print(portrait_lore_text(gs))
            elif obj in CARVING_TARGETS and gs.current_room == "Upstairs Hallway":
                print("The hidden carving reads: 'Let invited blood knock, and the listening room shall answer.'")
            elif obj in LEDGER_TARGETS:
                print("The ledger is mostly household accounting in a severe hand: coal, candles, food, medicine.")
                print("A few entries are marked more heavily than the rest, especially on Fridays, but nothing here openly explains why.")
            elif obj in INVITATION_TARGETS:
                gs.read_invitation = True
                print("In a fine, formal hand it reads: 'You were expected. Knock before the threshold.'")
                print("Someone has pressed too hard on the words below it, leaving only a half-legible mark like a closed eye.")
            elif obj in NAMEPLATE_TARGETS and gs.current_room == "Front Door":
                print("The nameplate reads: AMON.")
                print("The letters are simple and formal, but the way they sit beneath the knocker makes the word feel less like a name than a demand for recognition.")
            elif obj in PHOTO_TARGETS:
                print("The photograph shows Mother, Missy, and you as children. Grandma stands behind you all with one hand on the back of the head chair, smiling as if she owns the light itself.")
            elif gs.current_room == "Dining Room" and obj in DINING_INITIAL_TARGETS:
                if "initials" in room.scenery:
                    print("The carved circle reads like a family swallowed into one mouth: V.G., S.G., O.G., and I.G. Each set of initials is cut toward the head chair.")
                else:
                    print("There are no initials visible to read yet.")
            elif obj in LABEL_TARGETS and gs.current_room == "Cellar":
                if gs.trance:
                    gs.discovered_witness = True
                    print("The cellar labels rewrite themselves in pale, wet script: memory, witness, hunger, obedience.")
                    print("Beneath the sealed jar, one line steadies long enough to be read in full: 'Witness opens to blood and repeats what steam conceals.'")
                else:
                    print("Most labels have peeled off, but one surviving scrap reads: 'For voices that refuse the grave.'")
            elif obj in GRAVE_TARGETS and gs.current_room == "Cemetery":
                print("The oldest headstone is so weathered only one word survives: AMON.")
            else:
                print("There is nothing here you can meaningfully read.")

        elif v == "smell":
            trance_text = trance_smell_text(gs, obj)
            if gs.trance and trance_text:
                print(trance_text)
                if obj in TEAPOT_TARGETS and gs.current_room == "Attic" and witnessed_active_ash(gs):
                    print("As your hand drifts near your pocket, the steam falters for a heartbeat, as if some part of it recoils from the ash you carry.")
            elif obj in (None, "", "room", "air"):
                print(NORMAL_SMELL_TEXTS.get(gs.current_room, "The house smells of old wood, rain, and the faint remains of sickness."))
            elif obj in TEAPOT_TARGETS and gs.current_room == "Attic":
                print("The steam is sweet at first, then wrong beneath it: iron, wilted flowers, and a scent that reminds you of sleep without dreams.")
                if witnessed_active_ash(gs):
                    print("As your hand drifts near your pocket, the steam falters for a heartbeat, as if some part of it recoils from the ash you carry.")
            else:
                print(state_text(
                    gs,
                    f"You smell the {obj}, but learn little you didn't already fear.",
                    f"You smell the {obj}, and the scent arrives with too much meaning and too little explanation.",
                    f"You smell the {obj}. The impression fades quickly, but not cleanly."
                ))

        # 4. Interaction Logic
        elif v == "search":
            if obj in ROOM_LOOK_TARGETS or is_current_room_reference(gs, room, obj):
                print_room(gs, include_entry=False)
                self.suppress_room_display = True
            elif gs.current_room == "Kitchen" and obj in KITCHEN_FIRE_TARGETS:
                if in_full_trance(gs) and not gs.ash_revealed:
                    reveal_hearth_ash(gs, room, "You search the cold blue fire closely, following the places where its light refuses to settle.")
                elif in_full_trance(gs):
                    print("You search the blue flame again. It twists away from the pale ash below it as if afraid to touch what the fire has spared.")
                elif in_weakened_trance(gs):
                    print("You search the thinned blue flame and the stones around it. The hearth has quieted, but the fire still leaves the pale ash strangely undisturbed.")
                else:
                    print("You search around the cold blue flame. It gives off light without warmth, and the ash beneath it looks ordinary until your eyes linger too long.")
            elif gs.trance and gs.current_room == "Kitchen" and not gs.ash_revealed:
                reveal_hearth_ash(gs, room)
            elif gs.current_room == "Front Door":
                if gs.door_unlocked:
                    print("The door is open now. The gargoyle knocker hangs still above the AMON nameplate, its duty satisfied.")
                else:
                    print("You search the door and find no handle, latch, or keyhole on this side. Only the brass gargoyle knocker and the AMON nameplate beneath it have been touched often enough to shine.")
            elif gs.current_room == "Dining Room" and obj in DINING_SEARCH_TARGETS:
                if "initials" in room.scenery:
                    print("With the head chair pulled aside, the marks are plain: V.G., S.G., O.G., and I.G. cut into the boards in a tight ring where the chair had hidden them.")
                else:
                    print("You search near the floor and notice pale scrapes beneath the head chair, as if it has been dragged aside many times and carefully returned.")
            elif obj in BEHIND_PAINTING_TARGETS:
                if gs.current_room == "Foyer":
                    print("You search the foyer walls, but there are no paintings here. The watching faces Mother meant are upstairs.")
                elif gs.current_room == "Upstairs Hallway":
                    if gs.moved_portraits:
                        print("Behind the shifted portrait, the hidden carving remains exposed.")
                    else:
                        reveal_portrait_carving(gs, room)
                        print("You search behind the paintings. One portrait shifts aside, revealing a hidden carving in the plaster behind it.")
                        print("The carving reads: 'Let invited blood knock, and the listening room shall answer.'")
                else:
                    print("There are no paintings here to search behind.")
            elif obj in CARVING_TARGETS and gs.current_room == "Upstairs Hallway" and gs.moved_portraits:
                print("Behind the shifted portrait, the hidden carving remains exposed.")
                print("The carving reads: 'Let invited blood knock, and the listening room shall answer.'")
            else:
                trance_text = trance_search_text(gs) if gs.trance else None
                if trance_text:
                    if gs.current_room == "Cellar":
                        gs.discovered_witness = True
                    print(trance_text)
                elif gs.current_room == "Study":
                    found_items = [item for item in STUDY_FINDABLE_ITEMS if item in room.items]
                    if found_items:
                        print(f"You sort through the study and find: {', '.join(found_items)}.")
                        print("The surrounding papers keep circling inheritance, return, and a third idea hidden beneath angry cross-outs.")
                    else:
                        print("You sort through the study again. The drawer is empty now, and the remaining papers offer only fragments of household accounts, treatment notes, and names crossed out too hard.")
                elif gs.current_room == "Dining Room":
                    if "family photograph" in room.items:
                        print("You search the table and sideboard. A family photograph has been left face-down, as if someone could not bear being watched while eating.")
                    else:
                        print("You search the table and sideboard again. Only the clean rectangle in the dust remains where the photograph used to be.")
                elif room.items:
                    print(f"You search carefully and uncover: {', '.join(room.items.keys())}.")
                elif room.scenery:
                    print(state_text(
                        gs,
                        "You search the area, but find only old dust and neglected corners.",
                        "You search the area, but find only old dust, old memories, and the sense that something is watching.",
                        "You search the area and find traces rather than secrets, as if the house has already hidden the strongest part of itself again."
                    ))
                else:
                    print(state_text(
                        gs,
                        "You search around, but find nothing useful.",
                        "You search around, but the room seems to offer atmosphere instead of answers.",
                        "You search around, but whatever mattered most has already withdrawn a step."
                    ))

        elif v == "listen":
            trance_text = trance_listen_text(gs) if gs.trance else None
            if trance_text and gs.current_room != "Attic":
                print(trance_text)
                if gs.current_room == "Cellar" and "bloodied bandage" in gs.inventory and not gs.witness_awakened:
                    print("One jar answers the humming with a smaller sound: tick... tick... tick. It seems to be listening not to you, but to Mother's blood in your hand.")
            elif gs.current_room == "Front Gate":
                print("The wind hisses through the iron bars. Far off, you hear something scratching beneath the cemetery soil.")
            elif gs.current_room == "Upstairs Hallway":
                if in_full_trance(gs):
                    print("The hallway answers itself in borrowed voices. The portraits are empty, but something inside the walls keeps trying out your name until it fits.")
                elif in_weakened_trance(gs):
                    print("The hallway has given your name back, mostly. Once in a while a portrait seems about to speak it, then remembers its manners.")
                else:
                    print("The rocking chair above creaks in a slow rhythm. Between each groan, someone whispers your name.")
            elif gs.current_room == "Attic":
                if gs.ritual_branch == "ash":
                    print("The room no longer hums with welcome. The guests murmur in clipped, wounded bursts, and every pause feels like something preparing to lunge without feet.")
                elif witnessed_active_ash(gs):
                    print("The teacups still chime, but not as confidently now. Whenever your hand strays near the ash, the steam gives a small, angry hiss, and 'THEM' fall briefly out of rhythm.")
                elif gs.attic_choice == "disrupt":
                    print("The attic no longer sounds welcoming. Something paces just beyond sight, and every little clink now lands like a threat reconsidering your name.")
                elif gs.ritual_branch == "obedience":
                    print("Porcelain rings in layered harmonies around you. 'THEM' breathe close, pleased and attentive, as if your pulse has joined the service.")
                elif in_full_trance(gs):
                    print("The room is full of layered listening: porcelain chiming, breath where no lungs are visible, and the low approval of guests who think you are almost ready.")
                else:
                    print("China teacups clink softly in the air. Beneath that sound is the faintest murmur of conversation, as though the room is hosting a gathering just out of sight.")
            elif gs.current_room == "Dining Room":
                print("From somewhere just beyond the table, you hear the faint scrape of chairs being drawn back by 'THEM'.")
            elif gs.current_room == "Study":
                print("Paper rustles though no window is open. Every so often a book thumps softly deeper on the shelf.")
            else:
                print(state_text(
                    gs,
                    "You stand still and listen. The house answers with groans, settling wood, and distant weather.",
                    "You stand still and listen. The house answers with groans, sighs, and things better left unidentified.",
                    "You stand still and listen. The house has quieted, but not enough to be trusted."
                ))

        elif v == "talk":
            if obj in MOTHER_TARGETS and gs.current_room == "Living Room":
                print(state_text(
                    gs,
                    "You whisper to Mother, but her breathing is shallow and distant. Her fingers twitch once beneath the bandage.",
                    "You whisper to Mother. In trance, her lips do not move, but some frightened part of her still seems to hear you from very far away.",
                    "You whisper to Mother. Her breathing stays frail, but it belongs to her more fully now, as if the house has loosened its hand at last."
                ))
            elif obj in MOTHER_TARGETS and gs.current_room == "Dining Room":
                print("There is no answer here, only the memory of meals where Mother spoke softly so Grandma would not have to raise her voice.")
            elif obj in GRANDMA_TALK_TARGETS and gs.current_room == "Attic":
                if gs.ritual_branch == "ash":
                    print("Grandma half-rises from the chair and then thinks better of giving the room your height. 'You may still be useful,' she says, 'but you are no longer welcome.'")
                elif gs.attic_choice == "disrupt":
                    print("Grandma rises just enough for the chair to protest beneath her. 'You had one graceful moment,' she says. 'Now we discover what sort of guest you truly are.'")
                elif gs.ritual_branch == "obedience":
                    print("Grandma turns enough for you to feel included in her smile without ever being certain it was meant kindly. 'Good,' she says. 'They dislike hesitation more than sin.'")
                elif in_full_trance(gs):
                    print("Grandma turns her head just enough for one eye to catch the light. 'Now you hear 'THEM' properly,' she says. 'That is how every true conversation in this house begins.'")
                elif in_weakened_trance(gs):
                    print("Grandma studies you more carefully now. 'You hear less than before,' she says, 'but more than is good for any child to keep.'")
                else:
                    print("Grandma does not turn around. 'You came all this way to stand there?' she asks softly. 'Sit, listen, and let the tea decide how much truth you can bear.'")
            elif obj in MISSY_TARGETS:
                if gs.missy_heard:
                    print("You answer Missy in thought, because there is no body in the room to face.")
                    print("'I can hear you better when you stop looking for me,' her voice says, soft and frightened inside your mind.")
                else:
                    print("You call for Missy, but no voice answers yet.")
            else:
                print(state_text(
                    gs,
                    "Your voice falls flat in the dark.",
                    "Your voice falls flat in the dark, and the room seems to keep the echo for itself.",
                    "Your voice carries, but only partway. Whatever once rushed to answer is listening from farther off now."
                ))

        elif v == "ask":
            if obj in GRANDMA_TARGETS and gs.current_room == "Attic":
                if not i_obj:
                    if gs.attic_choice is None:
                        gs.attic_choice = "question"
                        print("You question Grandma before taking the place she has arranged for you.")
                        print("'Too far?' she says, though you never gave the words aloud. 'Every family reaches farther than its bones. That is how a house survives its dead.'")
                        print("The teacups fall silent around the table. The room has not punished the question yet, but it has written your doubt into the evening.")
                    elif gs.ritual_branch == "ash":
                        print("Grandma gives you a look sharpened by the wounded room. 'You have already answered with ash,' she says. 'Questions now are decoration.'")
                    elif gs.ritual_branch == "obedience":
                        print("Grandma smiles as if your question has arrived too late to matter. 'You may ask from inside the cup now,' she says.")
                    elif in_full_trance(gs):
                        print("Grandma listens to the shape of your doubt. 'Good,' she says. 'Questions make better handles than fear.'")
                    else:
                        print("Grandma does not turn. 'Ask plainly, dear. A house this old dislikes mumbling almost as much as disobedience.'")
                elif i_obj in GUEST_TOPIC_TARGETS:
                    if gs.ritual_branch == "ash":
                        print("Grandma's answer is almost drowned by the room itself. 'Ask 'THEM' now,' she says. 'You have already insulted their teacup, so perhaps they will favor honesty over courtesy.'")
                    elif gs.ritual_branch == "obedience":
                        print("Grandma smiles as if your question flatters everyone present. 'They have accepted your seat for tonight,' she says. 'Do not mistake acceptance for mercy.'")
                    elif in_full_trance(gs):
                        print("Grandma smiles as if introducing old friends. 'They are hunger, memory, witness, and welcome,' she says. 'You have names for smaller things. I do not name them to reduce them.'")
                    elif in_weakened_trance(gs):
                        print("Grandma glances at the dim air around the teacups. 'They have stepped back, not gone,' she says. 'A rude house still remembers what watched it eat.'")
                    else:
                        print("Grandma smiles without warmth. 'They are older than family, older than prayer, and far kinder than doctors.'")
                elif i_obj in ("ancestor", "ancestors", "family", "portraits", "paintings", "oil paintings", "ancestor paintings"):
                    if gs.ritual_branch == "ash":
                        print("Grandma looks toward the door, as if she can see through the house to the hallway of portraits. 'The ancestors are quiet now because you have made them uncertain,' she says. 'Do not mistake quiet for absence.'")
                    elif gs.ritual_branch == "obedience":
                        print("Grandma's smile deepens. 'They kept the door for you,' she says. 'Every painted face upstairs is a vessel that learned to hold a little memory and a little hunger.'")
                    elif in_full_trance(gs):
                        print("Grandma smiles as if naming honored guests. 'The ancestors are not dead in the way doctors mean dead,' she says. 'They are memory, witness, and appetite, painted thin enough for children to call them portraits.'")
                    elif in_weakened_trance(gs):
                        print("Grandma glances toward the dim hall beyond the attic door. 'They have stepped back into their frames,' she says. 'That is manners, not surrender.'")
                    else:
                        print("Grandma gives a soft, scolding laugh. 'Family is only another word for those who were invited before you,' she says. 'The paintings remember how to listen.'")
                elif i_obj in ("house", "amon"):
                    if gs.ritual_branch == "ash":
                        print("'You have wounded Amon, not ended it,' Grandma says. 'A house can bleed through more than steam.'")
                    else:
                        print("'Amon is not the house,' Grandma says. 'The house is only where it learned to wait. Wood rots. Names remain. Invitations remain longer still.'")
                elif i_obj == "tea":
                    if gs.ritual_branch == "ash":
                        print("'Tea was the gentle bridge,' Grandma says. 'Now if the room wants you, it will have to choose a rougher road.'")
                    elif witnessed_active_ash(gs):
                        print("Grandma's voice lowers. 'Tea is a bridge held up by breath,' she says. 'There are things in a house that bless a fire, and things that teach it silence. Be careful which lesson you carry upstairs.'")
                    elif gs.ritual_branch == "obedience":
                        print("'You swallowed more than tea,' Grandma says softly. 'Now the house knows the shape of your listening.'")
                    elif in_full_trance(gs):
                        print("'Tea is the bridge,' Grandma says. 'Blood remembers the way, steam carries the footstep, and the teacup teaches the living how not to be lonely.'")
                    elif in_weakened_trance(gs):
                        print("'The bridge is cracked,' Grandma says. 'That is not the same as destroyed. Houses have longer patience than children.'")
                    else:
                        print("'Tea is memory made warm enough to swallow,' Grandma says. 'The first sip opens the room. The second teaches the room your name.'")
                elif i_obj in MOTHER_TARGETS:
                    if gs.attic_choice is None:
                        gs.attic_choice = "question"
                        print("Grandma goes still. Even the steam seems to pause and listen.")
                        print("'Mother mistook love for resistance,' she says at last. 'Do not ask me to apologize for finishing what fear began.'")
                        print("The room cools around you. You feel, unmistakably, that you have stepped past courtesy and into judgment.")
                    else:
                        print("'Mother forgot how to listen without fear,' Grandma says. 'The house has been correcting her.'")
                elif i_obj in MISSY_TARGETS:
                    gs.missy_heard = True
                    if gs.attic_choice is None:
                        gs.attic_choice = "question"
                        print("Grandma's fingers tighten on the arm of the chair until the wood answers with a low complaint.")
                        print("'Little girls mistake disobedience for courage,' she says. 'Ask me about her again, and you may hear an answer you cannot survive politely.'")
                        print("Somewhere above you, though there is no higher room, a chorus of soft laughter passes through the rafters.")
                    else:
                        print("Grandma's fingers tighten on the arm of the chair. 'Little girls mistake disobedience for courage,' she says. 'The house is patient with neither for long.'")
                else:
                    print("Grandma tilts her head. 'Ask better questions, dear.'")
            elif obj in MOTHER_TARGETS and gs.current_room == "Living Room":
                if i_obj in GRANDMA_TARGETS:
                    gs.spoke_with_mother = True
                    print(state_text(
                        gs,
                        "Mother barely opens her eyes. 'Don't let her choose for you,' she whispers.",
                        "Mother's warning reaches you like a voice heard through water. 'Don't let her choose for you,' it insists, as if repeating itself keeps her anchored.",
                        "Mother barely opens her eyes. 'She can't hold all of you now,' she whispers. 'Keep what is yours.'"
                    ))
                elif i_obj in MISSY_TARGETS:
                    gs.spoke_with_mother = True
                    gs.missy_heard = True
                    print(state_text(
                        gs,
                        "Mother's lips tremble. 'She hides where Grandma never sits,' she whispers, and then the strength leaves her.",
                        "Mother's answer drifts in as if the room resents giving it up: 'She hides where Grandma never sits.' The words seem costly to her.",
                        "Mother's lips tremble. 'She hid from the house as much as from Grandma,' she whispers. 'Maybe that saved something.'"
                    ))
                elif i_obj in BANDAGE_TOPIC_TARGETS:
                    gs.spoke_with_mother = True
                    print(state_text(
                        gs,
                        "Mother's eyes drift toward the wrapped hand. 'Blood answers what the mouth won't,' she whispers. 'If anything in this house still witnesses, let it taste the truth.'",
                        "Mother's eyes drift toward the wrapped hand as if pulled there. 'Blood answers what the mouth won't,' she whispers. 'If anything in this house still witnesses, let it taste the truth.'",
                        "Mother looks at the bandage with open dread now. 'It remembers more than I do,' she whispers. 'Use it before the house starts remembering for us again.'"
                    ))
                else:
                    print("Mother is too weak to answer clearly.")
            elif obj in MISSY_TARGETS and gs.current_room in ("Front Gate", "Foyer", "Upstairs Hallway"):
                if gs.missy_heard:
                    print("You shape the question silently, the way you would touch a bruise to learn if it still hurts.")
                    print("Missy's voice answers from inside thought rather than air: 'I can only stay where she forgets to look.'")
                else:
                    gs.missy_heard = True
                    print("No answer comes aloud, but for a moment you would swear Missy is listening from somewhere inside your thoughts.")
            elif obj in MISSY_TARGETS and gs.missy_heard:
                print("You shape the question silently, the way you would touch a bruise to learn if it still hurts.")
                print("Missy's voice answers from inside thought rather than air: 'I can only stay where she forgets to look.'")
            else:
                print(state_text(
                    gs,
                    "No useful answer comes.",
                    "No useful answer comes. In trance, even silence sounds deliberate.",
                    "No useful answer comes. The silence feels less arranged than before, but no kinder."
                ))

        elif v == "show":
            shown_item, target_name, requested_item = parse_show_command(gs, obj, i_obj)
            if shown_item and target_name in GRANDMA_TARGETS and gs.current_room == "Attic":
                if shown_item == "brass key":
                    print("Grandma's shoulders stiffen. 'So you found the old obedience key,' she murmurs.")
                elif shown_item in ("sharp axe", "heavy axe"):
                    print("Grandma laughs softly. 'Steel only matters if the hand holding it has chosen a side.'")
                elif shown_item == "hearth ash":
                    if gs.ritual_branch == "ash":
                        print("Grandma's mouth tightens. 'Show off the grave-dust if you like,' she says. 'It only proves you learned from witnesses instead of family.'")
                    elif active_hearth_ash(gs):
                        print("Grandma's fingers still on the chair. 'Careful what you bring that close to the steam,' she says.")
                        print("For the first time, the violet steam above the teapot shrinks away from something in your hand.")
                    else:
                        print("Grandma glances at the ash and gives a dry little smile. 'Cold dust is not wisdom by itself,' she says.")
                elif shown_item == "family photograph":
                    print("Grandma glances at the photograph and chuckles under her breath. 'Pictures are for those who fear forgetting,' she says. 'This house has never needed help with memory.'")
                else:
                    print(f"Grandma glances at the {shown_item} and seems less interested than you hoped.")
            elif shown_item == "family photograph" and target_name in MOTHER_TARGETS and gs.current_room == "Living Room":
                gs.spoke_with_mother = True
                print(state_text(
                    gs,
                    "Mother's eyes open for half a second. 'Read what she leaves written,' she whispers. 'Then look behind the watching faces upstairs.'",
                    "Mother's eyes catch on the photograph as if it hurts to recognize it. 'Read what she leaves written,' she whispers. 'Then look behind the watching faces upstairs.'",
                    "Mother stares at the photograph longer than before. 'That was before the house learned to look back,' she whispers. 'Still... the clue remains where it always was.'"
                ))
            elif requested_item in PHOTO_TARGETS and target_name in MOTHER_TARGETS and gs.current_room == "Living Room":
                print("You have nothing like that to show Mother.")
            elif shown_item and target_name in MOTHER_TARGETS and gs.current_room == "Living Room":
                print(f"Mother stirs at the sight of the {shown_item}, as if recognition almost reaches her.")
            elif shown_item:
                print(state_text(
                    gs,
                    f"You hold up the {shown_item}, but no one here seems ready to answer it.",
                    f"You hold up the {shown_item}. The room notices before anyone else does, but gives nothing away.",
                    f"You hold up the {shown_item}. The gesture matters less than it would have a moment ago, though the house still keeps score."
                ))
            else:
                print("You have nothing like that to show.")

        elif v == "open":
            if gs.current_room == "Front Door" and obj in FRONT_DOOR_TARGETS:
                if gs.door_unlocked:
                    print("The door is already open enough to pass through.")
                else:
                    print("It refuses to budge. No handle gives way under your hand; only the brass gargoyle knocker seems meant to move.")
            elif gs.current_room == "Attic Landing" and obj in ATTIC_DOOR_TARGETS:
                key_item = resolve_item(gs, i_obj, "inventory") if i_obj else None
                if key_item == "brass key" and not gs.attic_unlocked:
                    unlock_attic_door(gs, room)
                elif gs.attic_unlocked:
                    print("The attic door already stands open before you.")
                elif gs.attic_primed:
                    print("The first resistance is gone. Beyond the wood, the room is listening now, holding its breath for the courtesy it believes it is owed.")
                else:
                    print("The attic door stands motionless, but not asleep. The keyhole watches like an unblinking eye, and the wood feels older than the house around it.")
            elif gs.current_room == "Upstairs Hallway" and obj in ATTIC_DOOR_TARGETS:
                print("The attic door waits up the narrow stair, on the small landing beneath the roofline.")
            elif obj in JAR_TARGETS and gs.current_room == "Cellar":
                print("You think better of opening that here.")
            elif obj in ("desk", "drawer") and gs.current_room == "Study":
                found_items = [item for item in STUDY_FINDABLE_ITEMS if item in room.items]
                if found_items:
                    print(f"The drawer gives with a dry snap. Inside: {', '.join(found_items)}.")
                    print("The papers around them are already disturbed, as if someone expected you.")
                else:
                    print("The drawer gives with a dry snap, but it is empty now. Only dust and a few curled paper scraps remain inside.")
            else:
                print(state_text(
                    gs,
                    "It doesn't open.",
                    "It doesn't open. In trance, the refusal feels ceremonial rather than mechanical.",
                    "It doesn't open. The spell has weakened, but the old stubbornness remains."
                ))

        elif v == "enter":
            if gs.current_room == "Front Door" and (obj in (None, "house", "foyer") or obj in FRONT_DOOR_TARGETS):
                if gs.door_unlocked:
                    enter_front_door(gs)
                else:
                    print("The house is still barred against you. The brass gargoyle knocker waits at eye level, polished by visitors who knew how to announce themselves.")
            elif gs.current_room == "Upstairs Hallway" and obj in (None, "attic", "stair", "stairs", "narrow stair", "attic stair", "landing"):
                gs.current_room = "Attic Landing"
                print(state_text(
                    gs,
                    "You climb the narrow stair to the attic landing.",
                    "You climb the narrow stair, and each step seems to wait until your foot commits before becoming solid.",
                    "You climb the narrow stair to the attic landing. The house lets the distance stay ordinary for once."
                ))
            elif gs.current_room == "Attic Landing" and (obj in (None, "room") or obj in ATTIC_DOOR_TARGETS):
                if gs.attic_unlocked:
                    gs.current_room = "Attic"
                    print(state_text(
                        gs,
                        "You step through the open attic doorway.",
                        "You step into the attic, and 'THEM' make room without moving.",
                        "You step into the attic. The room admits you, but its welcome has frayed."
                    ))
                elif gs.attic_primed:
                    print("The attic door has heard the key. Now it waits for the courtesy carved into the house: knock, and be named.")
                else:
                    print("The attic door is still closed at the top of the narrow stair. The lock watches from its ornate keyhole.")
            else:
                print(state_text(
                    gs,
                    f"You can't enter {obj or 'that'} from here.",
                    f"You can't enter {obj or 'that'} from here. In trance, even the idea of entry feels negotiated.",
                    f"You can't enter {obj or 'that'} from here. The house no longer invites mistakes as generously."
                ))

        elif v == "close":
            if gs.current_room == "Front Door" and obj in FRONT_DOOR_TARGETS and gs.door_unlocked:
                print("You pull the door until it nearly shuts, but the house seems to want it ajar.")
            elif gs.current_room == "Attic Landing" and obj in ATTIC_DOOR_TARGETS and gs.attic_unlocked:
                print("You start to pull the attic door closed, but the laughter beyond it makes you stop.")
            else:
                print(state_text(
                    gs,
                    "You leave it as it is.",
                    "You leave it as it is. The room seems pleased not to be interrupted.",
                    "You leave it as it is. The house no longer insists, but it still prefers its own arrangements."
                ))

        elif v == "move":
            if obj == "rocking chair" and gs.current_room == "Attic":
                print("Before your hands can truly settle on the wood, the chair gives a warning creak and rocks back by itself, as though your touch requires permission.")
            elif obj in BANDAGE_TARGETS and gs.current_room == "Living Room":
                take_mother_bandage(gs, room)
            elif gs.current_room == "Attic Landing" and obj in KEY_TARGETS and i_obj in ATTIC_DOOR_TARGETS:
                unlock_attic_door(gs, room)
            elif obj in PORTRAIT_TARGETS and gs.current_room == "Upstairs Hallway":
                if gs.moved_portraits:
                    print("One portrait is already shifted aside, leaving the hidden carving visible behind it.")
                else:
                    reveal_portrait_carving(gs, room)
                    print("One portrait shifts aside, revealing a hidden carving in the plaster behind it.")
                    print("The carving reads: 'Let invited blood knock, and the listening room shall answer.'")
            elif obj in ("chair", "head chair") and gs.current_room == "Dining Room":
                room.scenery["floor"] = "The floorboards beneath the head chair are scraped nearly white. The scratches gather around a deliberate carving rather than random damage."
                room.scenery["floorboards"] = room.scenery["floor"]
                room.scenery["initials"] = "A circle of tiny initials is carved into the boards beneath the head chair: V.G., S.G., O.G., and I.G. Each set points inward toward the chair, as if every name was seated there in turn."
                room.scenery["floor initials"] = room.scenery["initials"]
                print("The head chair grates across the floor. Carved into the wood beneath it is a circle of tiny initials, all family names.")
            elif obj in ("papers", "desk") and gs.current_room == "Study":
                if gs.discovered_witness:
                    print("You disturb the papers and uncover a page marked in red: 'Invitation first. Feeding second. Witness always from the bloodline.'")
                else:
                    print("You disturb the papers and uncover a page marked in red. Most of it has been scratched through, but two phrases remain: 'Invitation first' and 'from the bloodline.'")
            elif obj in JAR_TARGETS and gs.current_room == "Cellar":
                print("Something pale stirs in the liquid as the jar slides across the shelf.")
            else:
                print(state_text(
                    gs,
                    "You move it, but gain nothing except nerves.",
                    "You move it, and the room briefly rearranges its attention around you.",
                    "You move it, but whatever answer might once have surfaced now holds back."
                ))

        elif v == "knock":
            knock_target = obj or i_obj
            if gs.current_room == "Front Door" and knock_target in FRONT_KNOCK_TARGETS:
                unlock_front_door(gs, room)
            elif gs.current_room == "Attic Landing" and knock_target in ATTIC_DOOR_OPTIONAL_TARGETS and gs.attic_primed:
                print("\nYou knock once. The sound is swallowed immediately.")
                print("From beyond the door, something whispers your name with the tenderness of recognition and the chill of ownership.")
                print("The attic lock slides back of its own accord.")
                gs.attic_unlocked = True
                gs.attic_primed = False
                room.exits["north"] = "Attic"
                room.desc = "The attic landing waits under the sloped roof. Down the narrow stair lies the upstairs hallway; north, the attic door now stands open as if it has recognized you."
                room.scenery["door"] = "The heavy door stands open. Something upstairs has accepted your arrival."
                room.scenery["attic door"] = room.scenery["door"]
            elif gs.current_room == "Upstairs Hallway" and knock_target in ATTIC_DOOR_TARGETS:
                print("Your knock would not reach from here. The attic door waits up the narrow stair, on the landing.")
            else:
                print(state_text(
                    gs,
                    "Nothing happens.",
                    "Nothing happens, though the silence that follows feels almost judgmental.",
                    "Nothing happens. The house hears you, but does not bother to answer."
                ))
        
        elif v == "unlock":
            if gs.current_room == "Attic Landing" and obj in ATTIC_DOOR_TARGETS:
                unlock_attic_door(gs, room)
            elif gs.current_room == "Upstairs Hallway" and obj in ATTIC_DOOR_TARGETS:
                print("The attic door is up the narrow stair. You will need to stand on the landing to work the lock.")
            else:
                print(state_text(
                    gs,
                    "Nothing to unlock here.",
                    "Nothing to unlock here. In trance, that certainty feels like the house correcting you.",
                    "Nothing to unlock here. The place is quieter about your mistakes now, but not forgiving."
                ))

        elif v == "take":
            if gs.current_room == "Living Room" and obj in BANDAGE_TARGETS and not gs.bandage_taken:
                take_mother_bandage(gs, room)
            elif obj in TAKE_ALL_TARGETS:
                if room.items:
                    taken_items = list(room.items.keys())
                    for item_id in taken_items:
                        move_item(room.items, gs.inventory, item_id)
                    gathered = ", ".join(taken_items)
                    print(state_text(
                        gs,
                        f"You gather up: {gathered}.",
                        f"You gather up: {gathered}. In trance, each item feels like it came with a second, hidden weight.",
                        f"You gather up: {gathered}. They feel ordinary again, which somehow makes the memory of them worse."
                    ))
                else:
                    print("There is nothing here to take.")
            else:
                item_id = resolve_item(gs, obj, "room")
                if item_id:
                    move_item(room.items, gs.inventory, item_id)
                    print(state_text(
                        gs,
                        f"You took the {item_id}.",
                        f"You took the {item_id}. The house seems to notice the subtraction immediately.",
                        f"You took the {item_id}. It leaves the room more ordinary, but not more innocent."
                    ))
                else:
                    fixed_response = fixed_take_response(gs, room, obj)
                    if fixed_response:
                        print(fixed_response)
                    else:
                        print(f"There is no {obj} here.")

        elif v == "drop":
            item_id = resolve_item(gs, obj, "inventory")
            if item_id:
                move_item(gs.inventory, room.items, item_id)
                print(state_text(
                    gs,
                    f"You dropped the {item_id}.",
                    f"You dropped the {item_id}. The room seems relieved to have it back in circulation.",
                    f"You dropped the {item_id}. The gesture feels practical again, though the house still watches where it lands."
                ))
            else:
                print(f"You aren't carrying a {obj}.")

        elif v == "sharpen":
            if obj in AXE_TARGETS or i_obj in SHARPEN_TARGETS:
                sharpen_axe(gs)
            elif obj in STONE_TARGETS:
                print("The stone is already made for sharpening. It needs an edge to answer.")
            else:
                print(f"You can't sharpen {obj or 'that'}.")

        elif v == "use":
            held_item = resolve_item(gs, obj, "inventory") if obj else None
            target_name = i_obj or prep
            target_item = resolve_item(gs, target_name, "inventory") if target_name else None

            if gs.current_room == "Front Door" and not held_item and (obj in KNOCKER_TARGETS or obj in FRONT_DOOR_TARGETS):
                unlock_front_door(gs, room)
            elif held_item == "brass key" and target_name in ATTIC_DOOR_TARGETS and gs.current_room == "Attic Landing":
                unlock_attic_door(gs, room)
            elif held_item == "brass key" and target_name in ATTIC_DOOR_TARGETS and gs.current_room == "Upstairs Hallway":
                print("The attic door is up the narrow stair. You will need to stand on the landing to work the lock.")
            elif target_item == "brass key" and obj in ATTIC_DOOR_TARGETS and gs.current_room == "Attic Landing":
                unlock_attic_door(gs, room)
            elif held_item and is_weapon(held_item) and target_name in CHARACTER_TARGETS:
                handle_attack(gs, room, target_name, held_item)
                if gs.game_over:
                    self.finished = True
                    return False
            elif held_item == "bloodied bandage" and target_name in JAR_TARGETS and gs.current_room == "Cellar":
                awaken_witness_jar(gs)
            elif target_item == "bloodied bandage" and obj in JAR_TARGETS and gs.current_room == "Cellar":
                awaken_witness_jar(gs)
            elif held_item and target_name in JAR_TARGETS and gs.current_room == "Cellar":
                handle_attack(gs, room, target_name, held_item)
            elif is_axe_sharpening_pair(held_item, target_name):
                sharpen_axe(gs)
            elif held_item == "hearth ash" and target_name in TEAPOT_ACTION_TARGETS and gs.current_room == "Attic":
                smother_teapot_with_ash(gs, room)
            elif target_item == "hearth ash" and obj in TEAPOT_ACTION_TARGETS and gs.current_room == "Attic":
                smother_teapot_with_ash(gs, room)
            elif held_item == "hearth ash" and target_name in TEAPOT_ACTION_TARGETS:
                print("The ash stays cold in your hand. The teapot's steam is anchored upstairs; whatever this can do, it must happen in Grandma's attic.")
            elif held_item == "hearth ash" and gs.current_room == "Attic":
                if gs.trance:
                    print("The ash sits cold in your hand. Around the teapot, the steam seems to notice it first.")
                    print("If the witness spoke truly, it is not the metal that matters, but the breath rising from it.")
                else:
                    print("The ash sits cold in your hand. Without the tea's change in your blood, it is only what the fire left behind.")
            elif held_item and target_name:
                print(state_text(
                    gs,
                    f"You try using the {held_item} on the {target_name}, but nothing happens.",
                    f"You try using the {held_item} on the {target_name}, but nothing in the House responds.",
                    f"You try using the {held_item} on the {target_name}. Whatever link might have existed fails to catch."
                ))
            elif held_item:
                print(state_text(
                    gs,
                    f"You turn the {held_item} over in your hands, but using it how?",
                    f"You turn the {held_item} over in your hands. In trance it seems to imply a purpose without confessing it.",
                    f"You turn the {held_item} over in your hands. The compulsion has weakened, leaving only suspicion."
                ))
            else:
                print("Use what?")

        elif v == "pour":
            held_item = resolve_item(gs, obj, "inventory") if obj else None
            target_name = i_obj

            if held_item == TEAPOT_ITEM:
                if target_name in ("floor", "ground"):
                    if gs.current_room == "Attic":
                        if gs.attic_choice is None:
                            gs.attic_choice = "disrupt"
                            print("You tip the teapot before any blessing is spoken. Dark drops strike the floorboards and the whole attic recoils.")
                            print("The waiting teacups vanish. The steam twists into sharp, angry threads.")
                            print("Grandma's voice loses all softness. 'So,' she says, 'you would rather break the ceremony than learn it.'")
                        else:
                            print(decision_tone(
                                gs,
                                "You tip the teapot. A few dark drops strike the floorboards and the whole attic seems to tense around you.",
                                obedience="You tip the teapot after having already accepted the teacup. The room tightens in immediate betrayal, as if you have broken rank rather than simply spilled tea.",
                                question="You tip the teapot. It feels less like clumsiness than escalation now, and the room treats it that way.",
                                disrupt="You tip the teapot again. The room has already judged you once; this only confirms its opinion.",
                                ash="You tip what remains of the teapot's authority across the floorboards. The gesture feels less defiant now than final."
                            ))
                            print(decision_tone(
                                gs,
                                "Grandma's voice goes flat. 'Spilled invitations are answered by the wrong guests,' she says.",
                                obedience="Grandma's voice goes flat. 'So even after being welcomed, you choose insult over gratitude,' she says.",
                                question="Grandma's voice goes flat. 'Curiosity was rude enough,' she says. 'Waste is worse.'",
                                disrupt="Grandma's voice goes flat. 'Yes,' she says. 'This is what you are now.'",
                                ash="Grandma watches the spill without surprise. 'There. Even the manners are dead now,' she says."
                            ))
                    else:
                        print("You tip the teapot. The liquid spatters across the floor, and for one terrible second the room seems to inhale.")
                elif target_name in CUP_TARGETS:
                    if gs.current_room == "Attic":
                        print(decision_tone(
                            gs,
                            "You pour slowly. One by one, hidden teacups gather around the stream, revealed only by the changing shape of the tea as each presence receives its share.",
                            obedience="You pour slowly and with unexpected steadiness. The hidden teacups gather like they already knew your hands would learn the motion.",
                            question="You pour despite your doubts. The guests accept the tea anyway, but the room seems to watch for hesitation in every drop.",
                            disrupt="You try to pour after breaking the ceremony's rhythm. The motion works, but the welcome does not return.",
                            ash="You pour, but the gesture no longer restores anything. The room remembers the form more clearly than the power behind it."
                        ))
                    else:
                        print("A hidden teacup rises to meet the stream before vanishing again.")
                else:
                    print("You tip the teapot slightly, but the house seems to be waiting for a more meaningful choice.")
            elif held_item:
                print(state_text(
                    gs,
                    f"You pour from the {held_item}, but nothing about that helps.",
                    f"You pour from the {held_item}, but the room declines to make meaning out of it.",
                    f"You pour from the {held_item}. Whatever ritual charge once clung to the gesture slips away before it lands."
                ))
            else:
                print("Pour what?")

        elif v == "light":
            item_id = resolve_any_item(gs, obj) if obj else None
            if item_id in LIGHT_BLOCKED_ITEMS:
                print(f"The {item_id} is not something you can light.")
            elif obj in KITCHEN_FIRE_TARGETS and gs.current_room == "Kitchen":
                print("The blue flame is already alive, thin and watchful.")
            elif obj in ("candle", "lamp"):
                print("You have no flame to offer it yet.")
            else:
                print(state_text(
                    gs,
                    "You have nothing suitable to light with.",
                    "You have nothing suitable to light with. In trance, even the dark seems aware of your lack.",
                    "You have nothing suitable to light with. The room no longer leans in to help you imagine otherwise."
                ))

        elif v == "attack":
            weapon_name = i_obj if prep in ("with", "using") else None
            handle_attack(gs, room, obj, weapon_name)
            if gs.game_over:
                self.finished = True
                return False

        elif v == "drink":
            drink_target = obj or i_obj
            if gs.current_room == "Attic" and (drink_target in TEAPOT_TARGETS or drink_target in CUP_TARGETS or i_obj in CUP_TARGETS):
                if gs.teapot_smothered:
                    print("The ash has deadened the steam. Whatever bridge the tea once offered is now fouled and bitter.")
                elif gs.attic_choice == "disrupt":
                    print("The tea has gone wrong. Whatever welcome the room meant to offer has curled inward on itself.")
                else:
                    pour_tea_into_bowl(gs, room)
                    gs.ritual_branch = "obedience"
                    gs.branch_scene_seen = False
                    room.trance_desc = "The room is crowded with 'THEM', flickering translucent figures with voids where their faces should be. South through the open door lies the landing and the hallway beyond, but they have drawn nearer now, studying you with intimate patience."
                    if gs.attic_choice is None:
                        gs.attic_choice = "comply"
                        print("\nYou lift the teacup without another question. The room seems to ease around you, pleased by your obedience.")
                    else:
                        print(decision_tone(
                            gs,
                            "\nGrandma inclines her head as if honoring your choice to go on despite what you asked.",
                            question="\nGrandma inclines her head as if noting that even your questions have led you back where she expected.",
                            obedience="\nGrandma inclines her head, as if you have finally done the obvious thing properly.",
                            disrupt="\nGrandma watches you closely, surprised that you would reach for the teacup after trying to offend the room.",
                            ash="\nThe teacup no longer offers what it once did."
                        ))
                    gs.trance = True
                    gs.weakened_trance = False
                    print(decision_tone(
                        gs,
                        "You drink the tea. Warmth blooms through you first, then distance, then a terrible tenderness.",
                        obedience="You drink the tea. Warmth blooms through you first, then surrender, then the eerie relief of no longer resisting what the room wants.",
                        question="You drink the tea anyway. The warmth that follows feels less like comfort than consent granted a second too late.",
                        disrupt="You drink the tea after having already disturbed the room. The sensation arrives jagged, as if the bridge were built while you were stepping onto it."
                    ))
                    print(decision_tone(
                        gs,
                        "The room loosens its human shape. Steam becomes voice, darkness becomes company, and 'THEM' step nearer without ever fully taking form.",
                        obedience="The room loosens its human shape. Steam becomes voice, darkness becomes company, and 'THEM' step nearer as if your obedience has given them permission.",
                        question="The room loosens its human shape, but not gently. Steam becomes voice, darkness becomes company, and 'THEM' step nearer to inspect what doubt looks like from the inside.",
                        disrupt="The room loosens its human shape with a shudder. Steam becomes voice, darkness becomes company, and 'THEM' step nearer, curious whether you are guest or trespasser."
                    ))
                    print(decision_tone(
                        gs,
                        "You see 'THEM'.",
                        obedience="You see 'THEM' and feel, for one terrible moment, that they approve.",
                        question="You see 'THEM' and understand at once that curiosity was never protection.",
                        disrupt="You see 'THEM' and know they have not yet decided what to do with you."
                    ))
            else:
                print(state_text(
                    gs,
                    "Nothing to drink here.",
                    "Nothing to drink here. In trance, even thirst feels like it belongs to the house before it belongs to you.",
                    "Nothing to drink here. The wanting passes more easily now, but not entirely."
                ))

        # 5. Catch-all
        else:
            print(state_text(
                gs,
                "I don't understand that command.",
                "I don't understand that command. The house, unfortunately, may still pretend that it does.",
                "I don't understand that command. Whatever once rushed to interpret you has fallen quieter."
            ))
        return True

def play():
    session = GameSession(interactive_prompts=True)
    session.start()

    while not session.finished:
        user_input = input("\n> ")
        session.handle_command(user_input)

if __name__ == "__main__":
    play()
