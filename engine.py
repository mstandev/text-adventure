# engine.py

class AdvancedParser:
    def __init__(self):
        self.synonyms = {
            "go": ("walk", "run", "north", "south", "east", "west", "up", "down", "n", "s", "e", "w", "u", "d"),
            "take": ("get", "grab", "pick", "collect", "take"),
            "drop": ("drop", "leave", "discard"),
            "examine": ("look", "check", "inspect", "examine", "peek", "x"),
            "use": ("apply", "put", "place", "give", "cast", "scatter", "use"),
            "inventory": ("i", "items", "bag", "inventory"),
            "unlock": ("unlock",),
            "drink": ("sip", "gulp", "consume", "drink"),
            "knock": ("bang", "rap", "tap", "knock", "use"),
            "look": ("l", "view", "describe"),
            "search": ("search", "feel", "probe"),
            "listen": ("listen", "hear"),
            "talk": ("talk", "speak"),
            "ask": ("ask",),
            "show": ("show",),
            "read": ("read",),
            "smell": ("smell", "sniff"),
            "exit": ("exit",),
            "open": ("open",),
            "enter": ("enter",),
            "close": ("close", "shut"),
            "move": ("move", "push", "pull", "drag", "lift", "turn", "rotate", "shift", "slide", "straighten", "adjust", "tilt"),
            "pour": ("pour", "spill"),
            "light": ("light", "ignite", "burn"),
            "sharpen": ("sharpen", "hone", "whet"),
            "attack": ("attack", "kill", "hit", "strike", "swing", "slash", "murder", "stab", "chop", "break", "smash", "damage", "crack"),
            "restart": ("restart", "reset", "startover"),
            "help": ("help", "commands", "?")
        }
        self.verb_lookup = {}
        for verb, aliases in self.synonyms.items():
            self.verb_lookup.setdefault(verb, verb)
            for alias in aliases:
                self.verb_lookup.setdefault(alias, verb)
        self.direction_map = {
            "n": "north", "north": "north", "s": "south", "south": "south",
            "e": "east", "east": "east", "w": "west", "west": "west",
            "u": "up", "up": "up", "d": "down", "down": "down"
        }
        self.prepositions = frozenset(("with", "using", "on", "in", "at", "to", "about", "into", "across", "over", "from"))
        self.ignored = frozenset(("the", "a", "an", "some"))

    def parse(self, user_input):
        tokens = [w for w in user_input.lower().split() if w not in self.ignored]
        if not tokens: return None, None, None, None
        raw_verb = tokens[0]
        if raw_verb in self.direction_map:
            return "go", self.direction_map[raw_verb], None, None
        verb = self.verb_lookup.get(raw_verb, raw_verb)
        obj, prep, i_obj = None, None, None
        for i in range(1, len(tokens)):
            if tokens[i] in self.prepositions:
                prep = tokens[i]
                obj = " ".join(tokens[1:i])
                i_obj = " ".join(tokens[i+1:])
                break
        if prep and not obj and i_obj:
            obj = i_obj
            i_obj = None
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
        self.weakened_trance = False
        self.current_room = "Front Gate"
        self.door_unlocked = False
        self.attic_unlocked = False
        self.attic_primed = False
        self.read_invitation = False
        self.moved_portraits = False
        self.spoke_with_mother = False
        self.attic_seen = False
        self.tea_invited = False
        self.attic_choice = None
        self.bandage_taken = False
        self.witness_awakened = False
        self.ash_revealed = False
        self.teapot_smothered = False
        self.ritual_branch = None
        self.branch_scene_seen = False
        self.discovered_witness = False
        self.missy_heard = False
        self.missy_voice_rooms = set()
        self.front_gate_hint_seen = False
        self.dead_characters = set()
        self.game_over = False

    def get_matches(self, name, context="room"):
        """Returns a list of item_ids that match the given alias."""
        source = self.rooms[self.current_room].items if context == "room" else self.inventory
        matches = []
        for item_id, aliases in source.items():
            if name == item_id or name in aliases:
                matches.append(item_id)
        return matches
