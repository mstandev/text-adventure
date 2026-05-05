# engine.py

class AdvancedParser:
    def __init__(self):
        self.synonyms = {
            "go": ["walk", "run", "move", "north", "south", "east", "west", "up", "down", "n", "s", "e", "w", "u", "d"],
            "take": ["get", "grab", "pick", "collect", "take"],
            "examine": ["look", "read", "check", "inspect", "examine", "peek"],
            "use": ["apply", "put", "place", "pour", "give", "use"],
            "inventory": ["i", "items", "bag", "inventory"],
            "unlock": ["open", "unlock"],
            "drink": ["sip", "gulp", "consume", "drink"],
            "knock": ["bang", "rap", "tap", "knock", "use"],
            "look": ["l", "view", "describe"]
        }
        self.direction_map = {
            "n": "north", "north": "north", "s": "south", "south": "south",
            "e": "east", "east": "east", "w": "west", "west": "west",
            "u": "up", "up": "up", "d": "down", "down": "down"
        }
        self.prepositions = ["with", "on", "in", "at", "to"]
        self.ignored = ["the", "a", "an", "some"]

    def parse(self, user_input):
        tokens = [w for w in user_input.lower().split() if w not in self.ignored]
        if not tokens: return None, None, None, None
        raw_verb = tokens[0]
        if raw_verb in self.direction_map:
            return "go", self.direction_map[raw_verb], None, None
        verb = next((m for m, s in self.synonyms.items() if raw_verb == m or raw_verb in s), raw_verb)
        obj, prep, i_obj = None, None, None
        for i in range(1, len(tokens)):
            if tokens[i] in self.prepositions:
                prep = tokens[i]
                obj = " ".join(tokens[1:i])
                i_obj = " ".join(tokens[i+1:])
                break
        if not prep and len(tokens) > 1:
            obj = " ".join(tokens[1:])
        if verb == "go" and obj in self.direction_map:
            obj = self.direction_map[obj]
        return verb, obj, prep, i_obj

class Room:
    def __init__(self, name, desc, trance_desc, exits, items=None, scenery=None):
        self.name = name
        self.desc = desc
        self.trance_desc = trance_desc
        self.exits = exits
        self.items = items or {} # {"internal_id": ["alias1", "alias2"]}
        self.scenery = scenery or {}

class GameState:
    def __init__(self, rooms):
        self.rooms = rooms
        self.inventory = {}
        self.trance = False
        self.current_room = "Front Gate"
        self.door_unlocked = False
        self.attic_unlocked = False

    def get_matches(self, name, context="room"):
        """Returns a list of item_ids that match the given alias."""
        source = self.rooms[self.current_room].items if context == "room" else self.inventory
        matches = []
        for item_id, aliases in source.items():
            if name == item_id or name in aliases:
                matches.append(item_id)
        return matches
