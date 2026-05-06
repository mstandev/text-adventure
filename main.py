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
    
    choice = input("> ")
    if choice.isdigit() and 0 < int(choice) <= len(matches):
        return matches[int(choice)-1]
    elif choice in matches:
        return choice
    return None

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

def print_help():
    print("Commands: go, look, examine, read, smell, take, drop, inventory, search, listen, talk, ask, show, open, close, move, knock, unlock, use, pour, light, drink, attack, quit")
    print("Examples: north, examine door, take item, read note, ask person about topic, use item on target, attack target with item")

def in_full_trance(gs):
    return gs.trance and not gs.weakened_trance

def in_weakened_trance(gs):
    return gs.trance and gs.weakened_trance

def room_text(gs, room):
    if in_weakened_trance(gs):
        texts = {
            "Front Gate": "The gates still seem too much like hands, but the sky above them has settled back into an ordinary, wounded night. North, the house no longer pulls at you so cleanly; south, the cemetery lies still in the fog. The estate only watches.",
            "Foyer": "The chandelier sways though there is no wind. South is the front door, north the kitchen, west the living room, east the dining room, and up the staircase the house still holds its breath. The shadows no longer dance free of the walls, yet they lag a little behind the light.",
            "Living Room": "Mother still lies on the sofa, with the foyer east and the study north. Her shadow has sunk back into the shape of her body. Around the floorboards, the dark cup-stains remain, half-seen and impossible to forget.",
            "Study": "The study has stopped whispering in chorus. South, Mother's room waits beyond the doorway. The pages shift only when you look away now, and the records feel less enchanted than embarrassed to have been caught.",
            "Kitchen": "The blue flame has thinned to an unsteady thread. South leads to the foyer, east to the garden, and down to the cellar. The kitchen is a kitchen again, mostly, but the hearth still seems to be holding its breath.",
            "Upstairs Hallway": "The portraits are back in their frames, though none look entirely painted anymore. Down lies the foyer, west your bedroom, and above the ladder the attic door still keeps its own counsel. The house holds your name quietly now.",
            "Attic": "Grandma remains in the rocking chair, with the ladder down behind you. The room's authority has frayed. The steam hangs low and stubborn above the teapot, and the space feels haunted now more than welcoming.",
            "Cellar": "The jars have gone quiet enough to pass for ordinary storage, if not for the shapes that still seem to drift away whenever you focus on them. Up the stairs, the kitchen's blue light waits like a practical excuse to leave.",
            "Dining Room": "The table is only a table again until you blink. West, the foyer remains plainly reachable. Then a fourth place setting threatens its return before settling back into absence.",
            "Cemetery": "The graves are still. North, the gate leads back toward the house. Even so, the damp earth looks recently disturbed, as though the dead only just agreed to lie back down.",
            "Garden": "The garden is cold and almost clean again. West, the kitchen door leaks blue light; north, the shed leans under the dead trees. The frost on the beds no longer crawls, but it has not forgotten how.",
            "Shed": "The shed smells again of oil, rust, and wet wood. South, the garden path waits through the warped door. The tools have stopped humming, though the sharpening stone still seems a little too awake on the bench."
        }
        return texts.get(gs.current_room, room.desc + " Something of the tea remains in your senses, but the house no longer holds you quite so tightly.")
    return room.trance_desc if gs.trance else room.desc

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
    return item_id in ("heavy axe", "sharp axe", "silver spoon", "brass key", "sharpening stone")

def visible_character(gs, target):
    if target in ("mother", "mom"):
        return gs.current_room == "Living Room" and "mother" not in gs.dead_characters
    if target in ("grandma", "grandmother"):
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

def handle_attack(gs, room, target, weapon_name=None):
    weapon = resolve_attack_weapon(gs, weapon_name)

    if not target:
        print("Violence needs a target, and the house waits to see whether you will name one.")
        return False

    if target in ("amon", "teapot", "tea", "steam", "violet steam"):
        print("The teapot is not alive in any merciful sense. If you mean to break the ceremony, the steam is what matters.")
        return False

    if target in ("mother", "mom"):
        if not visible_character(gs, target):
            print("Mother is not here.")
            return False
        if not weapon:
            print("You raise your hands toward Mother, and for one lucid instant her eyes open with complete understanding.")
        else:
            print(f"You raise the {weapon} over Mother, and for one lucid instant her eyes open with complete understanding.")
        print("There is no struggle. That is the worst part. The house goes silent, not shocked, but satisfied that you have finally mistaken weakness for permission.")
        print("Mother's breath leaves her. Somewhere upstairs, Grandma begins to laugh without joy.")
        print("\nBAD END: THE KINDNESS YOU SPENT")
        print("You have ended Mother's suffering by becoming another part of it. When the police come, the house lets them find exactly enough truth to bury you in.")
        gs.dead_characters.add("mother")
        gs.game_over = True
        return True

    if target in ("grandma", "grandmother"):
        if not visible_character(gs, target):
            print("Grandma is not within reach.")
            return False
        if weapon != "sharp axe":
            print("You move against Grandma, but the attempt has no clean edge. Her chair rocks once, and the unseen guests close ranks around her.")
            print("'No,' she says, almost kindly. 'Not with fear. Not with that.'")
            return False
        if not gs.teapot_smothered:
            print("You swing the sharp axe before Amon has been silenced. The blade stops inches from Grandma's neck, caught in a crowd of hands you cannot see.")
            print("The invisible guests turn the edge back toward you with patient ceremonial strength.")
            print("\nBAD END: THE WRONG FIRST BLOW")
            print("Grandma lives. The tea cools. By morning, the axe is clean and your name has become one more whisper in the attic.")
            gs.game_over = True
            return True
        print("You swing the sharp axe after the ash has choked Amon's breath. This time no invisible hand arrives in time.")
        print("Grandma turns just enough to look offended rather than afraid. Then the chair stops rocking.")
        print("For one impossible second the house is free of her voice. Then every other voice rushes to fill the vacancy.")
        print("\nBAD END: GRANDMA'S EMPTY CHAIR")
        print("Grandma is dead, but the guests remain. With no elder to bargain through, they learn your shape directly. You leave the attic alive and spend the rest of your life hearing chairs rock in empty rooms.")
        gs.dead_characters.add("grandma")
        gs.game_over = True
        return True

    if target in ("missy", "sister"):
        if gs.missy_heard:
            print("You lash out at the place where Missy's presence seems nearest, but there is no body there to harm.")
            print("The air chills with a child's hurt silence. Whatever Missy is now, she is beyond your reach, and the house seems ashamed of you for trying.")
        else:
            print("Missy is not here in any way your hands can reach.")
        return False

    print(f"You can't attack {target or 'that'}.")
    return False

def item_available(gs, room, item_id):
    return item_id in room.items or item_id in gs.inventory

def visible_item_for_read(gs, room, obj):
    if obj in ("ledger", "ritual ledger"):
        return item_available(gs, room, "ritual ledger")
    if obj in ("card", "invitation", "invitation card"):
        return item_available(gs, room, "invitation card")
    if obj in ("photo", "photograph", "family photograph"):
        return item_available(gs, room, "family photograph")
    if obj in ("labels", "jar", "jars", "sealed jar"):
        return gs.current_room == "Cellar" or item_available(gs, room, "sealed jar")
    if obj in ("grave", "headstone", "headstones"):
        return gs.current_room == "Cemetery"
    if obj == "portraits":
        return gs.current_room == "Upstairs Hallway"
    return True

def trance_search_text(gs):
    if in_weakened_trance(gs):
        texts = {
            "Living Room": "The stain-rings by Mother's sofa remain visible, but only when you let your eyes go soft. The ritual has receded into evidence.",
            "Study": "The papers still gather around certain words: invitation, return, and one term that keeps hiding under crossed-out ink. Whatever power arranged them has lost the strength to keep the pattern steady.",
            "Kitchen": "The hearth marks are still there. They no longer blaze with meaning, but they have not gone innocent.",
            "Cellar": "The cellar shelves still sort themselves in your thoughts: memory below, witness above. The order feels remembered now, not enforced.",
            "Dining Room": "The table remembers invisible company better than the room does. Fingerprints of absence fade in and out along the polished wood."
        }
        return texts.get(gs.current_room)
    texts = {
        "Cemetery": "In trance, the graves no longer look sealed. Thin lines of green light connect certain stones to the house, as if the dead are still being counted.",
        "Living Room": "The room peels back its gentler lie. Around Mother's sofa, the floorboards are dark with old spill-marks shaped like cups and kneeling feet.",
        "Dining Room": "The table is set for more than the living. Faint handprints bloom across the polished wood where invisible guests have leaned in to listen.",
        "Study": "The papers refuse to stay still. One pattern repeats through the drift: invitation, blood, return, and a fourth word that blots itself out whenever you stare too long.",
        "Kitchen": "The hearthstone is scored with circles and tiny knife nicks. This was never only a kitchen.",
        "Cellar": "In trance, the jars are sorted with purpose: memory below, witness above, hunger nearest the stairs.",
        "Front Gate": "The path to the house is no path at all now, but a throat lined with old promises and older footsteps."
    }
    return texts.get(gs.current_room)

def trance_listen_text(gs):
    if in_weakened_trance(gs):
        texts = {
            "Front Gate": "The cemetery is quiet now, though once in a while the wind catches on the iron like a lullaby forgetting itself.",
            "Living Room": "Mother breathes alone again, though sometimes the room seems to expect a second breath and is disappointed not to hear it.",
            "Dining Room": "No chorus gathers at the table now. Only the occasional scrape of memory runs under the silence and is gone.",
            "Study": "The books have stopped reciting names. Now they only settle themselves too carefully whenever the house is mentioned.",
            "Kitchen": "The hearth crackles like something recovering from an argument. The flame has lost its voice, but not its temper.",
            "Cellar": "The jars no longer sing together. A few still ring softly when the house is challenged, as if old loyalties die slowly.",
            "Cemetery": "The ground holds still, but not peacefully. It sounds like a room where everyone has just stopped talking."
        }
        return texts.get(gs.current_room)
    texts = {
        "Front Gate": "The cemetery answers the house in tiny, eager scratches. Beneath them all, a lullaby keeps trying to remember its words.",
        "Living Room": "Mother's breathing is no longer alone. Something breathes with her, just a half-beat behind, like a rehearsal for taking over.",
        "Dining Room": "Invisible guests murmur around the head chair. They sound pleased whenever the family is spoken of as if it were a meal.",
        "Study": "The books recite names to one another. Some are family names. Some sound like titles no human should inherit.",
        "Kitchen": "The blue flame is singing through clenched teeth. Every pop in the hearth sounds like a tiny bone learning to speak.",
        "Cellar": "The jars hum in different notes, and together they form something like a choir practicing patience.",
        "Cemetery": "Below the soil, something knocks back in shallow little bursts, as if the dead have learned house manners."
    }
    return texts.get(gs.current_room)

def trance_smell_text(gs, obj):
    if obj in (None, "", "room", "air"):
        if in_weakened_trance(gs):
            texts = {
                "Front Gate": "Rain, iron, and the cold scent left behind when a storm chooses not to finish.",
                "Living Room": "Lavender, sickness, and only the faint remainder of copper now.",
                "Dining Room": "Wax, dust, and the ghost of a meal no longer being served.",
                "Study": "Paper, mildew, and the dry smell of secrets left open too long.",
                "Kitchen": "Ash, stone, and a sweetness that has finally begun to rot away.",
                "Cellar": "Damp glass and salt, with the preserved edge of something interrupted.",
                "Cemetery": "Wet soil and cooling stone."
            }
            return texts.get(gs.current_room)
        texts = {
            "Front Gate": "Wet iron, grave-moss, and the sweet rot of promises left outside too long.",
            "Living Room": "Copper, sleeping powder, and the stale perfume of someone kept alive for reasons other than mercy.",
            "Dining Room": "Wax, silver, old blood, and the warm illusion of family just before it curdles.",
            "Study": "Ink, mildew, and the dry animal scent of records handled by hands that never stopped counting.",
            "Kitchen": "Cinders, broth, and the sharp medicinal trace of instruments washed too carefully.",
            "Cellar": "Salt, glass, damp earth, and the sour breath of things preserved against their will.",
            "Cemetery": "Rain-soaked soil and the green, mineral scent of graves being remembered from below."
        }
        return texts.get(gs.current_room)
    if obj in ("tea", "teapot", "amon") and gs.current_room == "Attic":
        if in_weakened_trance(gs):
            return "The tea no longer smells persuasive. Under the sweetness is a singed, frustrated bitterness, as if the ritual cannot decide whether it has failed or is merely waiting."
        return "Now the tea smells less like comfort than consent: sweetness over iron, warmth over surrender."
    return None

def trance_read_text(gs, obj):
    if in_weakened_trance(gs):
        if gs.current_room == "Study" and obj in ("ledger", "ritual ledger"):
            return "The ledger resists rearranging itself now. A few lines still stand out: invite the blood, calm the witness, guard the heir. The spell has loosened, but the record remembers."
        if gs.current_room == "Study" and obj in ("card", "invitation", "invitation card"):
            return "The invitation looks like paper again, yet certain words still refuse to fade: blood, name, willing."
        if gs.current_room == "Dining Room" and obj in ("photo", "photograph", "family photograph"):
            return "The extra figures in the photograph are nearly gone. Nearly."
        if gs.current_room == "Cemetery" and obj in ("grave", "headstone", "headstones"):
            return "The names stay still now, but the stone remembers having moved."
        return None
    if not in_full_trance(gs):
        return None
    if gs.current_room == "Study" and obj in ("ledger", "ritual ledger"):
        return "In trance, the ledger rearranges itself into a liturgy: invite the blood, calm the witness, open the room, teach the heir."
    if gs.current_room == "Study" and obj in ("card", "invitation", "invitation card"):
        return "The invitation card no longer reads like courtesy. It reads like ownership granted in advance."
    if gs.current_room == "Dining Room" and obj in ("photo", "photograph", "family photograph"):
        return "The family photograph is wrong in trance. Behind Grandma, faint extra figures have developed where no one stood when the picture was taken."
    if gs.current_room == "Cemetery" and obj in ("grave", "headstone", "headstones"):
        return "The names on the headstones ripple. Some family dates end, then begin again a few inches lower in the stone."
    return None

def handle_room_entry(gs, room):
    if gs.current_room == "Attic" and not gs.attic_seen:
        print("\nThe rocking slows before stopping altogether.")
        print("Grandma does not turn, yet the room knows you have arrived. Somewhere in the air, porcelain touches porcelain with a careful, expectant chime.")
        print("'You came properly this time,' Grandma says. 'Good. Sit with the quiet a moment, and let it learn your breathing.'")
        gs.attic_seen = True
        gs.tea_invited = True
    elif gs.current_room == "Attic" and gs.ritual_branch == "obedience" and not gs.branch_scene_seen:
        print("\nThe invisible company parts around you with something almost like courtesy.")
        print("A cup you still cannot fully see settles into the air at your place, and Grandma inclines her head as though a private vow has just been witnessed.")
        print("'They know you now,' she says. 'Do not waste the kindness of being expected.'")
        gs.branch_scene_seen = True
    elif gs.current_room == "Attic" and gs.ritual_branch == "ash" and not gs.branch_scene_seen:
        print("\nThe attic has lost its false hospitality.")
        print("The steam hangs low and wounded. Around the room, unseen guests shift with the restless sound of chairs scraping back from a spoiled feast.")
        print("Grandma grips the chair arms until the wood complains. 'If you stay,' she says, 'you stay without blessing.'")
        gs.branch_scene_seen = True

def play():
    rooms = setup_amon_house()
    gs = GameState(rooms)
    parser = AdvancedParser()
    
    print("WELCOME TO THE HOUSE OF AMON")
    print("----------------------------")
    print("Grandma is back. The tea is brewing. Don't listen to the voices.")

    while True:
        room = gs.rooms[gs.current_room]
        print(f"\n--- {room.name} ---")
        print(room_text(gs, room))
        handle_room_entry(gs, room)
        
        # Display items using the new dictionary format
        if room.items:
            if isinstance(room.items, dict):
                item_names = ", ".join(room.items.keys())
            else:
                item_names = ", ".join(room.items)
            print(f"Items here: {item_names}")

        user_input = input("\n> ")
        v, obj, prep, i_obj = parser.parse(user_input)

        if not v: continue

        # 1. Global Commands
        if v == "help":
            print_help()

        elif v == "quit":
            print("The voices will follow you...")
            break
            
        elif v == "inventory":
            describe_inventory(gs)

        elif v == "look":
            # Just continues the loop to re-print the description
            continue

        # 2. Movement Logic
        elif v == "go":
            if obj in room.exits:
                destination = room.exits[obj]
                gs.current_room = destination
                print(state_text(
                    gs,
                    f"You head {obj}...",
                    f"You head {obj}, and the house seems to adjust around your choice before you arrive.",
                    f"You head {obj}. The house yields the path, though reluctantly."
                ))
            elif obj == "north" and gs.current_room == "Front Door" and not gs.door_unlocked:
                print("The door is locked from within. The brass gargoyle knocker waits at eye level, polished by visitors who knew better than to shove.")
            elif obj == "up" and gs.current_room == "Upstairs Hallway" and not gs.attic_unlocked:
                print("The Attic door is locked. Grandma is busy with her 'guests'.")
            else:
                print(state_text(
                    gs,
                    f"You can't go {obj or 'that way'}.",
                    f"You can't go {obj or 'that way'}. In trance, the refusal feels personal, as if the house has an opinion about your timing.",
                    f"You can't go {obj or 'that way'}. The path no longer twists to mislead you, but it still won't open."
                ))

        # 3. Examination Logic
        elif v == "examine":
            if not obj:
                print(room_text(gs, room))
            elif obj == "keyhole" and gs.current_room == "Upstairs Hallway":
                print("\nYou peek through the keyhole. You see tea cups floating in mid-air!")
            elif obj in ("ash", "hearth ash", "cinders"):
                if "hearth ash" in gs.inventory or "hearth ash" in room.items:
                    print("The ash is pale enough to seem unfinished, as if fire reached it and then lost its nerve.")
                    print("When you turn it in your hand, it clings lightly to your skin and leaves a chill instead of soot.")
                else:
                    print(f"You don't see a {obj} here.")
            elif in_full_trance(gs) and gs.current_room == "Living Room" and obj in ("mother", "mom"):
                print("Mother's body lies still, but her shadow keeps trying to sit up before something taller presses it gently back down.")
            elif in_weakened_trance(gs) and gs.current_room == "Living Room" and obj in ("mother", "mom"):
                print("Mother looks human again, painfully so, but the skin around her eyes still carries the aftermath of dreams that did not end when yours did.")
            elif in_full_trance(gs) and gs.current_room == "Living Room" and obj in ("bandage", "hand"):
                print("The bandage shines almost white in trance. Beneath it, the wound pulses with the slow, stubborn rhythm of something being reopened by memory.")
            elif in_weakened_trance(gs) and gs.current_room == "Living Room" and obj in ("bandage", "hand"):
                print("The bandage has gone ordinary again, but not innocent. Looking at it now feels like seeing a ritual after the chanting stops.")
            elif in_full_trance(gs) and gs.current_room == "Dining Room" and obj in ("chair", "head chair", "table"):
                print("The head chair is occupied now, if not by weight then by intention. The air bends around it with the patience of someone expected to be served first.")
            elif in_full_trance(gs) and gs.current_room == "Study" and obj in ("desk", "papers", "bookcase"):
                print("The study is no archive in trance. It is an accounting chamber. Every page seems less written than sentenced.")
            elif in_weakened_trance(gs) and gs.current_room == "Study" and obj in ("desk", "papers", "bookcase"):
                print("The study has stopped performing. Now it merely looks guilty.")
            elif in_full_trance(gs) and gs.current_room == "Cellar" and obj in ("jars", "sealed jar", "jar"):
                print("Each jar contains more than liquid now. Faces drift up through the murk, touching the glass from inside whenever your gaze lingers too long.")
            elif in_weakened_trance(gs) and gs.current_room == "Cellar" and obj in ("jars", "sealed jar", "jar"):
                print("The faces are harder to catch now. You see them only in the instant before deciding you imagined them.")
            elif obj in ("grandma", "grandmother") and gs.current_room == "Attic":
                if in_full_trance(gs):
                    print("Grandma's face seems both ancient and newly made, the skin stretched thin over a smile that belongs to someone being greeted from very far away.")
                elif in_weakened_trance(gs):
                    print("Grandma looks older now that the room is no longer flattering her. Not harmless, not defeated, but more mortal than she would like to be seen.")
                else:
                    print("Grandma remains turned from you, but her posture is not frail. One hand rests on the chair arm, still as a spider waiting at the center of its web.")
            elif obj in ("teapot", "tea", "amon") and gs.current_room == "Attic":
                if in_full_trance(gs):
                    print("The teapot glows from within like a sealed heart. Each breath of steam carries murmurs, laughter, and the weight of a promise you half remember making.")
                elif in_weakened_trance(gs):
                    print("The teapot has lost its inner glow. Its steam still rises, but with effort now, as if the ritual must push each breath uphill.")
                else:
                    print("The silver teapot is immaculate despite the dust around it. Its lid trembles now and then, as if something inside is breathing.")
            elif obj in ("cups", "teacups") and gs.current_room == "Attic":
                print("For an instant you see nothing. Then the air dimples. Handles, rims, and pale reflections appear and vanish as invisible hands test their place settings.")
            elif gs.current_room == "Front Door" and obj in ("door", "front door"):
                if gs.door_unlocked:
                    print("The heavy oak door stands open now, with the dark foyer waiting north.")
                else:
                    print("The oak door is barred from the inside. The only part that looks handled is the brass gargoyle knocker set into the center panel.")
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
                continue
            trance_text = trance_read_text(gs, obj)
            if trance_text:
                if obj in ("ledger", "ritual ledger", "labels", "jar", "jars", "sealed jar"):
                    gs.discovered_witness = True
                print(trance_text)
            elif obj == "portraits" and gs.current_room == "Upstairs Hallway":
                if gs.moved_portraits:
                    print("Behind the shifted frame, a hidden line is carved into the wall: 'Let invited blood knock, and the listening room shall answer.'")
                else:
                    print("Tiny nameplates beneath the frames read like a family warning: AMON, ELISE, MARIUS, HESTER. Several dates have been scratched away.")
            elif obj in ("ledger", "ritual ledger"):
                print("The ledger is mostly household accounting in a severe hand: coal, candles, food, medicine.")
                print("A few entries are marked more heavily than the rest, especially on Fridays, but nothing here openly explains why.")
            elif obj in ("card", "invitation", "invitation card"):
                gs.read_invitation = True
                print("In a fine, formal hand it reads: 'Welcome home. Knock and enter.'")
                print("Someone has pressed too hard on the words below it, leaving only a half-legible flourish where more text may once have been.")
            elif obj in ("photo", "photograph", "family photograph"):
                print("The photograph shows Mother, Missy, and you as children. Grandma stands behind you all with one hand on the back of the head chair, smiling as if she owns the light itself.")
            elif obj in ("labels", "jar", "jars", "sealed jar") and gs.current_room == "Cellar":
                if gs.trance:
                    gs.discovered_witness = True
                    print("The cellar labels rewrite themselves in pale, wet script: memory, witness, hunger, obedience.")
                    print("Beneath the sealed jar, one line steadies long enough to be read in full: 'Witness opens to blood and repeats what steam conceals.'")
                else:
                    print("Most labels have peeled off, but one surviving scrap reads: 'For voices that refuse the grave.'")
            elif obj in ("grave", "headstone", "headstones") and gs.current_room == "Cemetery":
                print("The oldest headstone is so weathered only one word survives: AMON.")
            else:
                print("There is nothing here you can meaningfully read.")

        elif v == "smell":
            trance_text = trance_smell_text(gs, obj)
            if gs.trance and trance_text:
                print(trance_text)
                if obj in ("tea", "teapot", "amon") and gs.current_room == "Attic" and "hearth ash" in gs.inventory and gs.witness_awakened and not gs.teapot_smothered:
                    print("As your hand drifts near your pocket, the steam falters for a heartbeat, as if some part of it recoils from the ash you carry.")
            elif obj in (None, "", "room", "air"):
                if gs.current_room == "Kitchen":
                    print("Cold ash, damp stone, and something metallic under the sweetness of old tea.")
                elif gs.current_room == "Attic":
                    print("Lavender, dust, and the copper tang of something freshly opened.")
                elif gs.current_room == "Cellar":
                    print("Mold, brine, and rot sealed behind glass.")
                elif gs.current_room == "Dining Room":
                    print("Cold silver, old candles, and the ghost of meals eaten under too many rules.")
                elif gs.current_room == "Study":
                    print("Dust, ink, and the dry paper smell of secrets handled too often.")
                else:
                    print("The house smells of old wood, rain, and the faint remains of sickness.")
            elif obj in ("tea", "teapot", "amon") and gs.current_room == "Attic":
                print("The steam is sweet at first, then wrong beneath it: iron, wilted flowers, and a scent that reminds you of sleep without dreams.")
                if "hearth ash" in gs.inventory and gs.witness_awakened and not gs.teapot_smothered:
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
            if gs.trance and gs.current_room == "Kitchen" and not gs.ash_revealed:
                gs.ash_revealed = True
                room.items["hearth ash"] = ["ash", "cinders", "hearth ash"]
                print("Beneath the screaming blue flame, you notice a bed of pale hearth ash that has somehow escaped burning.")
                print("It does not glow like the rest of the hearth. Instead it seems to drink the blue light out of the flame above it, turning warmth into hush.")
            elif gs.current_room == "Front Door":
                if gs.door_unlocked:
                    print("The door is open now. The gargoyle knocker hangs still, its duty satisfied.")
                else:
                    print("You search the door and find no handle, latch, or keyhole on this side. Only the brass gargoyle knocker has been touched often enough to shine.")
            else:
                trance_text = trance_search_text(gs) if gs.trance else None
                if trance_text:
                    if gs.current_room == "Cellar":
                        gs.discovered_witness = True
                    print(trance_text)
                elif gs.current_room == "Study":
                    print("You sort through the study and find: ritual ledger, invitation card. The papers keep circling invitation, inheritance, and a third idea hidden beneath angry cross-outs.")
                elif gs.current_room == "Dining Room":
                    print("You search the table and sideboard. A family photograph has been left face-down, as if someone could not bear being watched while eating.")
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
                elif "hearth ash" in gs.inventory and gs.witness_awakened and not gs.teapot_smothered:
                    print("The cups still chime, but not as confidently now. Whenever your hand strays near the ash, the steam gives a small, angry hiss, and the unseen guests fall briefly out of rhythm.")
                elif gs.attic_choice == "disrupt":
                    print("The attic no longer sounds welcoming. Something paces just beyond sight, and every little clink now lands like a threat reconsidering your name.")
                elif gs.ritual_branch == "obedience":
                    print("Porcelain rings in layered harmonies around you. The unseen guests breathe close, pleased and attentive, as if your pulse has joined the service.")
                elif in_full_trance(gs):
                    print("The room is full of layered listening: porcelain chiming, breath where no lungs are visible, and the low approval of guests who think you are almost ready.")
                else:
                    print("Porcelain teacups clink softly in the air. Beneath that sound is the faintest murmur of conversation, as though the room is hosting a gathering just out of sight.")
            elif gs.current_room == "Dining Room":
                print("From somewhere just beyond the table, you hear the faint scrape of chairs being drawn back by unseen guests.")
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
            if obj in ("mother", "mom") and gs.current_room == "Living Room":
                print(state_text(
                    gs,
                    "You whisper to Mother, but her breathing is shallow and distant. Her fingers twitch once beneath the bandage.",
                    "You whisper to Mother. In trance, her lips do not move, but some frightened part of her still seems to hear you from very far away.",
                    "You whisper to Mother. Her breathing stays frail, but it belongs to her more fully now, as if the house has loosened its hand at last."
                ))
            elif obj in ("mother", "mom") and gs.current_room == "Dining Room":
                print("There is no answer here, only the memory of meals where Mother spoke softly so Grandma would not have to raise her voice.")
            elif obj in ("grandma", "amon") and gs.current_room == "Attic":
                if gs.ritual_branch == "ash":
                    print("Grandma half-rises from the chair and then thinks better of giving the room your height. 'You may still be useful,' she says, 'but you are no longer welcome.'")
                elif gs.attic_choice == "disrupt":
                    print("Grandma rises just enough for the chair to protest beneath her. 'You had one graceful moment,' she says. 'Now we discover what sort of guest you truly are.'")
                elif gs.ritual_branch == "obedience":
                    print("Grandma turns enough for you to feel included in her smile without ever being certain it was meant kindly. 'Good,' she says. 'They dislike hesitation more than sin.'")
                elif in_full_trance(gs):
                    print("Grandma turns her head just enough for one eye to catch the light. 'Now you hear them properly,' she says. 'That is how every true conversation in this house begins.'")
                elif in_weakened_trance(gs):
                    print("Grandma studies you more carefully now. 'You hear less than before,' she says, 'but more than is good for any child to keep.'")
                else:
                    print("Grandma does not turn around. 'You came all this way to stand there?' she asks softly. 'Sit, listen, and let the tea decide how much truth you can bear.'")
            else:
                print(state_text(
                    gs,
                    "Your voice falls flat in the dark.",
                    "Your voice falls flat in the dark, and the room seems to keep the echo for itself.",
                    "Your voice carries, but only partway. Whatever once rushed to answer is listening from farther off now."
                ))

        elif v == "ask":
            if obj in ("grandma", "grandmother") and gs.current_room == "Attic":
                if i_obj == "them":
                    if gs.ritual_branch == "ash":
                        print("Grandma's answer is almost drowned by the room itself. 'Ask them now,' she says. 'You have already insulted their cup, so perhaps they will favor honesty over courtesy.'")
                    elif gs.ritual_branch == "obedience":
                        print("Grandma smiles as if your question flatters everyone present. 'They have accepted your seat for tonight,' she says. 'Do not mistake acceptance for mercy.'")
                    elif in_full_trance(gs):
                        print("Grandma smiles as if introducing old friends. 'They are hunger, memory, witness, and welcome,' she says. 'You have names for smaller things. We do not name them to reduce them.'")
                    elif in_weakened_trance(gs):
                        print("Grandma glances at the dim air around the cups. 'They have stepped back, not gone,' she says. 'A rude house still remembers its guests.'")
                    else:
                        print("Grandma smiles without warmth. 'They are older than family, older than prayer, and far kinder than doctors.'")
                elif i_obj in ("house", "amon"):
                    if gs.ritual_branch == "ash":
                        print("'You have wounded Amon, not ended it,' Grandma says. 'A house can bleed through more than steam.'")
                    else:
                        print("'Amon is not the house,' Grandma says. 'The house is only where it learned to wait. Wood rots. Names remain. Invitations remain longer still.'")
                elif i_obj == "tea":
                    if gs.ritual_branch == "ash":
                        print("'Tea was the gentle bridge,' Grandma says. 'Now if the room wants you, it will have to choose a rougher road.'")
                    elif "hearth ash" in gs.inventory and gs.witness_awakened and not gs.teapot_smothered:
                        print("Grandma's voice lowers. 'Tea is a bridge held up by breath,' she says. 'There are things in a house that bless a fire, and things that teach it silence. Be careful which lesson you carry upstairs.'")
                    elif gs.ritual_branch == "obedience":
                        print("'You swallowed more than tea,' Grandma says softly. 'Now the house knows the shape of your listening.'")
                    elif in_full_trance(gs):
                        print("'Tea is the bridge,' Grandma says. 'Blood remembers the way, steam carries the footstep, and the cup teaches the living how not to be lonely.'")
                    elif in_weakened_trance(gs):
                        print("'The bridge is cracked,' Grandma says. 'That is not the same as destroyed. Houses have longer patience than children.'")
                    else:
                        print("'Tea is memory made warm enough to swallow,' Grandma says. 'The first sip opens the room. The second teaches the room your name.'")
                elif i_obj in ("mother", "mom"):
                    if gs.attic_choice is None:
                        gs.attic_choice = "question"
                        print("Grandma goes still. Even the steam seems to pause and listen.")
                        print("'Your mother mistook love for resistance,' she says at last. 'Do not ask me to apologize for finishing what fear began.'")
                        print("The room cools around you. You feel, unmistakably, that you have stepped past courtesy and into judgment.")
                    else:
                        print("'Your mother forgot how to listen without fear,' Grandma says. 'The house has been correcting her.'")
                elif i_obj in ("missy", "sister"):
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
            elif obj in ("mother", "mom") and gs.current_room == "Living Room":
                if i_obj in ("grandma", "grandmother"):
                    gs.spoke_with_mother = True
                    print(state_text(
                        gs,
                        "Mother barely opens her eyes. 'Don't let her choose for you,' she whispers.",
                        "Mother's warning reaches you like a voice heard through water. 'Don't let her choose for you,' it insists, as if repeating itself keeps her anchored.",
                        "Mother barely opens her eyes. 'She can't hold all of you now,' she whispers. 'Keep what is yours.'"
                    ))
                elif i_obj in ("missy", "sister"):
                    gs.spoke_with_mother = True
                    gs.missy_heard = True
                    print(state_text(
                        gs,
                        "Mother's lips tremble. 'She hides where Grandma never sits,' she whispers, and then the strength leaves her.",
                        "Mother's answer drifts in as if the room resents giving it up: 'She hides where Grandma never sits.' The words seem costly to her.",
                        "Mother's lips tremble. 'She hid from the house as much as from Grandma,' she whispers. 'Maybe that saved something.'"
                    ))
                elif i_obj in ("bandage", "blood", "hand"):
                    gs.spoke_with_mother = True
                    print(state_text(
                        gs,
                        "Mother's eyes drift toward the wrapped hand. 'Blood answers what the mouth won't,' she whispers. 'If anything in this house still witnesses, let it taste the truth.'",
                        "Mother's eyes drift toward the wrapped hand as if pulled there. 'Blood answers what the mouth won't,' she whispers. 'If anything in this house still witnesses, let it taste the truth.'",
                        "Mother looks at the bandage with open dread now. 'It remembers more than I do,' she whispers. 'Use it before the house starts remembering for us again.'"
                    ))
                else:
                    print("Mother is too weak to answer clearly.")
            elif obj in ("missy", "sister") and gs.current_room in ("Front Gate", "Foyer", "Upstairs Hallway"):
                gs.missy_heard = True
                print("No answer comes, but for a moment you would swear your sister is listening from somewhere nearby.")
            else:
                print(state_text(
                    gs,
                    "No useful answer comes.",
                    "No useful answer comes. In trance, even silence sounds deliberate.",
                    "No useful answer comes. The silence feels less arranged than before, but no kinder."
                ))

        elif v == "show":
            shown_item = resolve_item(gs, obj, "inventory") if obj else None
            if shown_item and i_obj in ("grandma", "grandmother") and gs.current_room == "Attic":
                if shown_item == "brass key":
                    print("Grandma's shoulders stiffen. 'So you found the old obedience key,' she murmurs.")
                elif shown_item in ("sharp axe", "heavy axe"):
                    print("Grandma laughs softly. 'Steel only matters if the hand holding it has chosen a side.'")
                elif shown_item == "hearth ash":
                    if gs.ritual_branch == "ash":
                        print("Grandma's mouth tightens. 'Show off the grave-dust if you like,' she says. 'It only proves you learned from witnesses instead of elders.'")
                    else:
                        print("Grandma's fingers still on the chair. 'Careful what you bring that close to the steam,' she says.")
                        print("For the first time, the violet coil above the teapot shrinks away from something in your hand.")
                elif shown_item == "family photograph":
                    print("Grandma glances at the photograph and chuckles under her breath. 'Pictures are for those who fear forgetting,' she says. 'This house has never needed help with memory.'")
                else:
                    print(f"Grandma glances at the {shown_item} and seems less interested than you hoped.")
            elif shown_item == "family photograph" and i_obj in ("mother", "mom") and gs.current_room == "Living Room":
                gs.spoke_with_mother = True
                print(state_text(
                    gs,
                    "Mother's eyes open for half a second. 'Read what she leaves written,' she whispers. 'Then look behind the watching faces upstairs.'",
                    "Mother's eyes catch on the photograph as if it hurts to recognize it. 'Read what she leaves written,' she whispers. 'Then look behind the watching faces upstairs.'",
                    "Mother stares at the photograph longer than before. 'That was before the house learned to look back,' she whispers. 'Still... the clue remains where it always was.'"
                ))
            elif obj in ("photo", "photograph", "family photo", "family photograph") and i_obj in ("mother", "mom") and gs.current_room == "Living Room":
                print("You have nothing like that to show Mother.")
            elif shown_item and i_obj in ("mother", "mom") and gs.current_room == "Living Room":
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
            if gs.current_room == "Front Door" and obj == "door":
                if gs.door_unlocked:
                    print("The door is already open enough to pass through.")
                else:
                    print("It refuses to budge. No handle gives way under your hand; only the brass gargoyle knocker seems meant to move.")
            elif gs.current_room == "Upstairs Hallway" and obj in ("door", "attic"):
                if gs.attic_unlocked:
                    print("The attic door groans open above you.")
                elif gs.attic_primed:
                    print("The first resistance is gone. Beyond the wood, the room is listening now, holding its breath for the courtesy it believes it is owed.")
                else:
                    print("The attic door stands motionless, but not asleep. The keyhole watches like an unblinking eye, and the wood feels older than the house around it.")
            elif obj in ("sealed jar", "jar") and gs.current_room == "Cellar":
                print("You think better of opening that here.")
            elif obj in ("desk", "drawer") and gs.current_room == "Study":
                print("The drawer gives with a dry snap. Inside are a ritual ledger and an invitation card, already disturbed as if someone expected you.")
            else:
                print(state_text(
                    gs,
                    "It doesn't open.",
                    "It doesn't open. In trance, the refusal feels ceremonial rather than mechanical.",
                    "It doesn't open. The spell has weakened, but the old stubbornness remains."
                ))

        elif v == "close":
            if gs.current_room == "Front Door" and obj == "door" and gs.door_unlocked:
                print("You pull the door until it nearly shuts, but the house seems to want it ajar.")
            elif gs.current_room == "Upstairs Hallway" and obj in ("door", "attic") and gs.attic_unlocked:
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
            elif obj == "portraits" and gs.current_room == "Upstairs Hallway":
                gs.moved_portraits = True
                room.scenery["portraits"] = "One portrait hangs crooked now. Behind it, a line has been carved directly into the wall."
                print("One portrait shifts aside, revealing a hidden carving in the plaster behind it.")
            elif obj in ("chair", "head chair") and gs.current_room == "Dining Room":
                print("The head chair grates across the floor. Carved into the wood beneath it is a circle of tiny initials, all family names.")
            elif obj in ("papers", "desk") and gs.current_room == "Study":
                if gs.discovered_witness:
                    print("You disturb the papers and uncover a page marked in red: 'Invitation first. Feeding second. Witness always from the bloodline.'")
                else:
                    print("You disturb the papers and uncover a page marked in red. Most of it has been scratched through, but two phrases remain: 'Invitation first' and 'from the bloodline.'")
            elif obj in ("jars", "sealed jar") and gs.current_room == "Cellar":
                print("Something pale stirs in the liquid as the jar slides across the shelf.")
            else:
                print(state_text(
                    gs,
                    "You move it, but gain nothing except nerves.",
                    "You move it, and the room briefly rearranges its attention around you.",
                    "You move it, but whatever answer might once have surfaced now holds back."
                ))

        elif v == "knock":
            if gs.current_room == "Front Door" and (obj in (None, "knocker", "gargoyle", "door", "front door")):
                if not gs.door_unlocked:
                    print("\n*CLANG... CLANG... CLANG*")
                    print("Grandma: 'I knew it was You at the door!'")
                    print("You hear the heavy bolt slide back. The door is now open.")
                    
                    # UPDATE THE ROOM DYNAMICALLY
                    gs.door_unlocked = True
                    room.exits["north"] = "Foyer"
                    room.desc = "The heavy oak door stands open, leading north into the dark foyer. The path back to the Front Gate lies south, and the gargoyle knocker looks almost satisfied."
                    room.scenery["door"] = "The door is now unlocked and slightly ajar."
                else:
                    print("The door is already open.")
            elif gs.current_room == "Upstairs Hallway" and (obj == "door" or obj == "attic") and gs.attic_primed:
                print("\nYou knock once. The sound is swallowed immediately.")
                print("From beyond the door, something whispers your name with the tenderness of recognition and the chill of ownership.")
                print("The attic lock slides back of its own accord.")
                gs.attic_unlocked = True
                gs.attic_primed = False
                room.exits["up"] = "Attic"
                room.desc = "Portraits of ancestors watch you from both sides of the hallway. The stairs lead down to the foyer, your bedroom lies west, and up the ladder the attic door now stands open as if it has recognized you."
                room.scenery["door"] = "The heavy door stands open. Something upstairs has accepted your arrival."
            else:
                print(state_text(
                    gs,
                    "Nothing happens.",
                    "Nothing happens, though the silence that follows feels almost judgmental.",
                    "Nothing happens. The house hears you, but does not bother to answer."
                ))
        
        elif v == "unlock":
            if gs.current_room == "Upstairs Hallway" and (obj == "door" or obj == "attic"):
                item_id = resolve_item(gs, "key", "inventory")
                if item_id == "brass key":
                    if gs.attic_unlocked:
                        print("It's already unlocked.")
                    elif not gs.read_invitation:
                        print("The brass key slips into place as if it remembers your hand, yet the lock refuses to turn.")
                        print("For a moment the metal grows warm against your fingers, and you feel the door withholding itself, not from force, but from ignorance.")
                    elif not gs.moved_portraits:
                        print("The key yields a little, then binds as though another hand has taken hold of it from within.")
                        print("Somewhere along the hallway wall, wood taps once against plaster. The watching faces seem to know why you are being refused.")
                    elif not gs.attic_primed:
                        print("\nThe key turns with a grudging click, then stops at a second catch.")
                        print("A breath escapes the seam of the door, carrying a whisper soft as dust across a coffin lid: 'Knock, and be named.'")
                        gs.attic_primed = True
                        room.scenery["door"] = "The lock has given way once, but the room beyond still insists on invitation, as if a key can open the metal but not the will behind it."
                    else:
                        print("The key has done all it can. What remains is older than locksmithing: the room is waiting to hear you ask entry in the language it prefers.")
                else:
                    print("You need a specific key for this door.")
            else:
                print(state_text(
                    gs,
                    "Nothing to unlock here.",
                    "Nothing to unlock here. In trance, that certainty feels like the house correcting you.",
                    "Nothing to unlock here. The place is quieter about your mistakes now, but not forgiving."
                ))

        elif v == "take":
            if gs.current_room == "Living Room" and obj in ("bandage", "hand") and not gs.bandage_taken:
                gs.bandage_taken = True
                gs.inventory["bloodied bandage"] = ["bandage", "cloth", "bloodied bandage"]
                room.scenery["bandage"] = "The bandage is gone. A dark red stain slowly reappears through the cloth left beneath Mother's hand."
                print(state_text(
                    gs,
                    "You carefully loosen the bandage from Mother's hand. It comes away warm and spotted through with old blood.",
                    "You carefully loosen the bandage from Mother's hand. In trance it feels less like cloth than a kept promise, still warm with the ritual that wanted to claim it.",
                    "You carefully loosen the bandage from Mother's hand. It feels lighter than before, but more accusing, as if now it belongs to a choice instead of a spell."
                ))
            elif obj == "all":
                if room.items:
                    taken_items = list(room.items.keys())
                    for item_id in taken_items:
                        move_item(room.items, gs.inventory, item_id)
                    gathered = ", ".join(taken_items)
                    print(state_text(
                        gs,
                        f"You gather up: {gathered}.",
                        f"You gather up: {gathered}. In trance, each item feels like it came with a second, invisible weight.",
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

        elif v == "use":
            held_item = resolve_item(gs, obj, "inventory") if obj else None
            target_name = i_obj or prep

            if gs.current_room == "Front Door" and not held_item and obj in ("knocker", "gargoyle", "door", "front door"):
                if not gs.door_unlocked:
                    print("\n*CLANG... CLANG... CLANG*")
                    print("Grandma: 'I knew it was You at the door!'")
                    print("You hear the heavy bolt slide back. The door is now open.")
                    gs.door_unlocked = True
                    room.exits["north"] = "Foyer"
                    room.desc = "The heavy oak door stands open, leading north into the dark foyer. The path back to the Front Gate lies south, and the gargoyle knocker looks almost satisfied."
                    room.scenery["door"] = "The door is now unlocked and slightly ajar."
                else:
                    print("The door is already open.")
            elif held_item and is_weapon(held_item) and target_name in ("mother", "mom", "grandma", "grandmother", "missy", "sister"):
                handle_attack(gs, room, target_name, held_item)
                if gs.game_over:
                    break
            elif held_item == "sharpening stone" and target_name == "axe":
                target_item = resolve_item(gs, "axe", "inventory")
                if target_item == "heavy axe":
                    gs.inventory.pop("heavy axe")
                    gs.inventory["sharp axe"] = ["axe", "weapon", "sharp axe"]
                    print("You work the blade against the stone until it gleams. The heavy axe is now a sharp axe.")
                else:
                    print("You have nothing here that benefits from sharpening.")
            elif held_item == "bloodied bandage" and target_name in ("jar", "sealed jar", "souls") and gs.current_room == "Cellar":
                gs.witness_awakened = True
                gs.discovered_witness = True
                print(state_text(
                    gs,
                    "You press the bloodied bandage to the glass. The jar clouds instantly, then clears from within.",
                    "You press the bloodied bandage to the glass. The jar answers as if it has been waiting for exactly this proof.",
                    "You press the bloodied bandage to the glass. The response is weaker than it would once have been, but still immediate enough to make your stomach turn."
                ))
                print("A pale face forms just beneath the surface and mouths words directly into your thoughts:")
                print("'When Amon is fed, the house opens. When Amon is broken, cast hearth ash across the steam or the guests will keep drinking from the air.'")
            elif held_item == "hearth ash" and target_name in ("teapot", "amon", "tea", "steam", "violet steam") and gs.current_room == "Attic":
                gs.teapot_smothered = True
                gs.ritual_branch = "ash"
                gs.branch_scene_seen = False
                if gs.trance:
                    gs.weakened_trance = True
                room.desc = "Grandma remains in the rocking chair, with the ladder down to the hallway behind you. The violet steam now hangs in bruised, broken ribbons above the teapot, and the room feels offended rather than welcoming."
                room.trance_desc = "The guests no longer wait in reverence. The ladder down remains visible but distant, while their shapes pull at the dim air in restless, wounded knots around the teapot's darkened mouth."
                if gs.attic_choice is None:
                    gs.attic_choice = "disrupt"
                print("You cast the hearth ash across the teapot. The violet steam stutters, darkens, and sinks low.")
                print("For the first time, Grandma sounds uncertain. 'Who taught you that?' she whispers.")
                if gs.trance:
                    print("Something inside your head unlatches. The house does not disappear, but its voice retreats from your bloodstream to the far side of the walls.")
            elif held_item == "hearth ash" and gs.current_room == "Attic":
                print("The ash sits cold in your hand. Around the teapot, the steam seems to notice it first.")
                print("If the witness spoke truly, it is not the silver that matters, but the breath rising from it.")
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

            if held_item == "teapot":
                if target_name in ("floor", "ground"):
                    if gs.current_room == "Attic":
                        if gs.attic_choice is None:
                            gs.attic_choice = "disrupt"
                            print("You tip the teapot before any blessing is spoken. Dark drops strike the floorboards and the whole attic recoils.")
                            print("The invisible cups vanish. The steam twists into sharp, angry threads.")
                            print("Grandma's voice loses all softness. 'So,' she says, 'you would rather break the ceremony than learn it.'")
                        else:
                            print(decision_tone(
                                gs,
                                "You tip the teapot. A few dark drops strike the floorboards and the whole attic seems to tense around you.",
                                obedience="You tip the teapot after having already accepted the cup. The room tightens in immediate betrayal, as if you have broken rank rather than simply spilled tea.",
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
                elif target_name in ("cup", "teacup"):
                    if gs.current_room == "Attic":
                        print(decision_tone(
                            gs,
                            "You pour slowly. One by one, invisible cups gather around the stream, revealed only by the changing shape of the tea as each unseen guest receives its share.",
                            obedience="You pour slowly and with unexpected steadiness. The invisible cups gather like they already knew your hands would learn the motion.",
                            question="You pour despite your doubts. The guests accept the tea anyway, but the room seems to watch for hesitation in every drop.",
                            disrupt="You try to pour after breaking the ceremony's rhythm. The motion works, but the welcome does not return.",
                            ash="You pour, but the gesture no longer restores anything. The room remembers the form more clearly than the power behind it."
                        ))
                    else:
                        print("An invisible cup rises to meet the stream before vanishing again.")
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
            if item_id in ("heavy axe", "sharp axe", "brass key", "sharpening stone", "silver spoon", "grave dirt", "sealed jar", "teapot"):
                print(f"The {item_id} is not something you can light.")
            elif obj in ("hearth", "fireplace") and gs.current_room == "Kitchen":
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
                break

        elif v == "drink":
            if obj == "tea" and gs.current_room == "Attic":
                if gs.teapot_smothered:
                    print("The ash has deadened the steam. Whatever bridge the tea once offered is now fouled and bitter.")
                elif gs.attic_choice == "disrupt":
                    print("The tea has gone wrong. Whatever welcome the room meant to offer has curled inward on itself.")
                else:
                    gs.ritual_branch = "obedience"
                    gs.branch_scene_seen = False
                    room.trance_desc = "The room is crowded with 'Them', flickering translucent figures with voids where their faces should be. Down the ladder lies the hallway, but they have drawn nearer now, studying you with intimate patience."
                    if gs.attic_choice is None:
                        gs.attic_choice = "comply"
                        print("\nYou lift the tea without another question. The room seems to ease around you, pleased by your obedience.")
                    else:
                        print(decision_tone(
                            gs,
                            "\nGrandma inclines her head as if honoring your choice to go on despite what you asked.",
                            question="\nGrandma inclines her head as if noting that even your questions have led you back where she expected.",
                            obedience="\nGrandma inclines her head, as if you have finally done the obvious thing properly.",
                            disrupt="\nGrandma watches you closely, surprised that you would reach for the cup after trying to offend the room.",
                            ash="\nThe cup no longer offers what it once did."
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
                        "The room loosens its human shape. Steam becomes voice, darkness becomes company, and the unseen guests step nearer without ever fully taking form.",
                        obedience="The room loosens its human shape. Steam becomes voice, darkness becomes company, and the unseen guests step nearer as if your obedience has given them permission.",
                        question="The room loosens its human shape, but not gently. Steam becomes voice, darkness becomes company, and the unseen guests step nearer to inspect what doubt looks like from the inside.",
                        disrupt="The room loosens its human shape with a shudder. Steam becomes voice, darkness becomes company, and the unseen guests step nearer, curious whether you are guest or trespasser."
                    ))
                    print(decision_tone(
                        gs,
                        "You see 'THEM'!",
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

if __name__ == "__main__":
    play()
