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
        print(room.trance_desc if gs.trance else room.desc)
        
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
        if v == "quit":
            print("The voices will follow you...")
            break
            
        elif v == "inventory":
            if not gs.inventory:
                print("Your pockets are empty.")
            else:
                print(f"Inventory: {', '.join(gs.inventory.keys())}")

        elif v == "look":
            # Just continues the loop to re-print the description
            continue

        # 2. Movement Logic
        elif v == "go":
            if obj in room.exits:
                gs.current_room = room.exits[obj]
                print(f"You head {obj}...")
            elif obj == "north" and gs.current_room == "Front Door" and not gs.door_unlocked:
                print("The door is locked. Perhaps you should announce yourself?")
            elif obj == "up" and gs.current_room == "Upstairs Hallway" and not gs.attic_unlocked:
                print("The Attic door is locked. Grandma is busy with her 'guests'.")
            else:
                print(f"You can't go {obj or 'that way'}.")

        # 3. Examination Logic
        elif v == "examine":
            if not obj:
                print(room.trance_desc if gs.trance else room.desc)
            elif obj == "keyhole" and gs.current_room == "Upstairs Hallway":
                print("\nYou peek through the keyhole. You see tea cups floating in mid-air!")
            elif obj in room.scenery:
                print(room.scenery[obj])
            else:
                # Check if it's an item in the room or inventory using Aliases
                item_id = resolve_item(gs, obj, "room") or resolve_item(gs, obj, "inventory")
                if item_id:
                    print(f"It's a {item_id}. It looks significant to the House.")
                else:
                    print(f"You don't see a {obj} here.")

        # 4. Interaction Logic
        elif v == "knock":
            if gs.current_room == "Front Door" and (obj == "knocker" or obj == "door"):
                if not gs.door_unlocked:
                    print("\n*CLANG... CLANG... CLANG*")
                    print("Grandma: 'I knew it was You at the door!'")
                    print("You hear the heavy bolt slide back. The door is now open.")
                    
                    # UPDATE THE ROOM DYNAMICALLY
                    gs.door_unlocked = True
                    room.exits["north"] = "Foyer"
                    room.desc = "The heavy oak door stands open, leading into the dark Foyer. The gargoyle knocker looks almost satisfied."
                    room.scenery["door"] = "The door is now unlocked and slightly ajar."
                else:
                    print("The door is already open.")
            else:
                print("Nothing happens.")
        
        elif v == "unlock":
            if gs.current_room == "Upstairs Hallway" and (obj == "door" or obj == "attic"):
                item_id = resolve_item(gs, "key", "inventory")
                if item_id == "brass key":
                    if not gs.attic_unlocked:
                        print("\nCLICK. The Attic door is now unlocked.")
                        
                        # UPDATE THE HALLWAY DYNAMICALLY
                        gs.attic_unlocked = True
                        room.exits["up"] = "Attic"
                        room.desc = "Portraits of ancestors watch you. Your bedroom is west. Up the ladder, the Attic door stands unlocked and open."
                        room.scenery["door"] = "The heavy door is unlocked. You can head up now."
                    else:
                        print("It's already unlocked.")
                else:
                    print("You need a specific key for this door.")
            else:
                print("Nothing to unlock here.")

        elif v == "take":
            item_id = resolve_item(gs, obj, "room")
            if item_id:
                # Move item from room dictionary to inventory dictionary
                aliases = room.items.pop(item_id)
                gs.inventory[item_id] = aliases
                print(f"You took the {item_id}.")
            else:
                print(f"There is no {obj} here.")

        elif v == "drink":
            if obj == "tea" and gs.current_room == "Attic":
                gs.trance = True
                print("\nYou drink the tea. The world spins, twists and deforms. Time seems to stretch and collapse. You see 'THEM'!")
            else:
                print("Nothing to drink here.")

        # 5. Catch-all
        else:
            print("I don't understand that command.")

if __name__ == "__main__":
    play()
