# world.py
from engine import Room

def setup_amon_house():
    rooms = {}

    rooms["Front Gate"] = Room(
        "The Front Gate",
        "The rusted iron gates of the Amon estate stand before you, their hinges weeping orange tears of rust. Before you lies the path to the house. It is choked with dead leaves that crunch like bone under your feet. Behind you is the Amon family cemetery.",
        "The gates have transformed into skeletal hands, clawing at a sky the color of a fresh bruise. The path ahead feels like a long, cold throat leading into the belly of a beast. The path behind feels like a breath from the dead.",
        {"north": "Front Door", "south": "Cemetery"}
    )

    rooms["Cemetery"] = Room(
        "The Family Cemetery",
        "Rows of crooked headstones lean in the fog like forgotten teeth. The air is heavy with the scent of wet earth and ancient silence. A low stone wall separates the living from the dead.",
        "The headstones pulse with a sickly green luminescence. You can hear the muffled sound of scratching coming from beneath the soil. 'They' are restless tonight.",
        {"north": "Front Gate"},
        items={"grave dirt": ["dirt", "soil"]}
    )

    rooms["Front Door"] = Room(
        "The Front Door",
        "A heavy oak door stands before you, barred from the inside. A brass knocker in the shape of a gargoyle leers at you.",
        "The door pulses like a beating heart. The gargoyle's eyes flicker red.",
        {"south": "Front Gate"}, # North is locked!
        scenery={
            "knocker": "It's a heavy brass gargoyle. Its mouth is open as if to scream.",
            "door": "The oak is ancient and scarred. It is currently locked tight."
        }
    )

    rooms["Foyer"] = Room(
        "The Foyer",
        "Dust motes dance in the weak light of a dying chandelier. A grand staircase spirals upward into the gloom, and the smell of mothballs and decay is thick.",
        "The shadows on the walls have detached themselves, dancing in a silent, mocking waltz. The stairs seem to stretch infinitely upward into a void of whispering voices.",
        {"south": "Front Door", "north": "Kitchen", "west": "Living Room", "up": "Upstairs Hallway"}
    )

    rooms["Living Room"] = Room(
        "The Living Room",
        "Mother lies on the velvet sofa, her face a mask of waxen exhaustion. She is trapped in a sleep that looks more like a coma. A white bandage on her hand is the only bright thing in the room.",
        "Mother's shadow stands over her, a tall, faceless entity that turns to look at you as you enter. The room smells of copper and unwashed tea cups.",
        {"east": "Foyer"}
    )

    rooms["Kitchen"] = Room(
        "The Kitchen",
        "A cold, blue flame flickers in the stone hearth, casting long, shivering shadows. A door to the east leads to the garden.",
        "The blue flame is screaming-a high, silent frequency that vibrates in your teeth. The shadows of the utensils on the wall look like meat hooks.",
        {"south": "Foyer", "east": "Garden", "down": "Cellar"},
        items={"heavy axe": ["axe", "weapon"], "silver spoon": ["spoon"]}
    )

    rooms["Upstairs Hallway"] = Room(
        "The Upstairs Hallway",
        "Oil paintings of the Amon ancestors line the walls. Their eyes seem to follow your every move. Above you hear a rocking chair creaking rhythmically. A doorway to the west is your bedroom. A ladder leads up to the Attic.  The Attic door is heavy oak with a large, ornate keyhole.",
        "The ancestors are no longer in their frames. The canvases are empty, and the voices of 'Them' echo through the hallway: 'King... come to us, King...'",
        {"down": "Foyer", "west": "King's Bedroom"}, # Removed 'up' so it starts locked
        scenery={
            "door": "It's a heavy oak door with a large, ornate keyhole.",
            "keyhole": "You see a faint flickering light on the other side. You hear voices laughing insanely.",
            "portraits": "The eyes in the paintings seem to track your every move."
        }
    )

    rooms["King's Bedroom"] = Room(
        "King's Bedroom",
        "Your childhood room. The bed is unmade, and the air is stale. It offers no comfort now. A single candle gutters on the nightstand, casting a weak, flickering light.",
        "The walls are breathing. The window looks out onto a world that has been replaced by a swirling, purple mist. You are not alone in this room.",
        {"east": "Upstairs Hallway"},
        items={"brass key": ["key", "brass"]}
    )

    rooms["Attic"] = Room(
        "The Attic (Grandma's Room)",
        "Grandma sits in her rocking chair, her back to you. On the small table sits the silver teapot, Amon. A thin trail of violet steam rises from the spout, coiling like a snake.",
        "The room is crowded with 'Them'-flickering, translucent figures with voids where their faces should be. They are waiting for the tea. They are waiting for you.",
        {"down": "Upstairs Hallway"},
        items={"teapot": ["amon", "pot", "tea"]}
    )

    rooms["Cellar"] = Room(
        "The Damp Cellar",
        "The walls are weeping moisture. Rows of unlabelled jars sit on stone shelves, filled with dark, swirling liquids. The floor is slick with something that isn't water.",
        "The jars are vibrating with the trapped souls of the house. You can see tiny, pale hands pressing against the glass from the inside.",
        {"up": "Kitchen"},
        items={"sealed jar": ["jar", "souls"]}
    )

    rooms["Garden"] = Room(
        "The Garden",
        "The night air is freezing, but it feels pure. The wind howls through the dead oak trees, and the moon is a sharp blade in the sky. To the north, a small tool shed leans precariously.",
        "The trees have become gallows, their branches reaching down like nooses. The ground is soft and spongy, as if you are walking on a giant, sleeping lung.",
        {"west": "Kitchen", "north": "Shed"}
    )

    rooms["Shed"] = Room(
        "The Tool Shed",
        "A cramped space filled with the scent of oil and rust. Sharp tools hang from hooks on the walls, glinting in the dark. A sharpening stone sits on a cluttered workbench.",
        "The tools are dripping with a dark, oily substance that looks like old blood. They seem to hum with a hunger for the sharpening stone.",
        {"south": "Garden"},
        items={"sharpening stone": ["stone"]}
    )

    return rooms
