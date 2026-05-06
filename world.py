# world.py
from engine import Room

def setup_amon_house():
    rooms = {}

    rooms["Front Gate"] = Room(
        "The Front Gate",
        "The rusted iron gates of the Amon estate stand before you, their hinges weeping orange tears of rust. North, a leaf-choked path climbs toward the house and the dark weight of its front door. South, beyond a low run of stone, the family cemetery waits in the fog. Dead leaves gather around your shoes and crunch like old bone whenever you shift your weight.",
        "The gates have transformed into skeletal hands, clawing at a sky the color of a fresh bruise. North, the path to the house feels like a long, cold throat. South, the cemetery exhales through its crooked stones. The leaves at your feet skitter without wind, as if the grounds themselves are trying to decide which way you belong.",
        {"north": "Front Door", "south": "Cemetery"}
    )

    rooms["Cemetery"] = Room(
        "The Family Cemetery",
        "Rows of crooked headstones lean in the fog like forgotten teeth. The low wall and iron gate lie north, back toward the estate path and the watching house. Wet earth darkens your shoes, and one old grave has a patch of loose soil disturbed near its marker. The cemetery is quiet in the way a room becomes quiet when people stop speaking about you.",
        "The headstones pulse with sickly green luminescence, each name brightening just after you look away. North, the gate stands like a set of ribs, with the house beyond it listening to the cemetery breathe. Beneath the disturbed soil, muffled scratching moves once, then stops, as if embarrassed to have been heard.",
        {"north": "Front Gate"},
        items={"grave dirt": ["dirt", "soil"]}
    )

    rooms["Front Door"] = Room(
        "The Front Door",
        "A heavy oak door stands north before you, barred from the inside. The path back to the gate lies south, but the house fills your attention like a held breath. At eye level, a brass knocker in the shape of a gargoyle leers from the center panel, its open mouth polished by long use and bad weather.",
        "The door pulses like a beating heart, and the wood seems less built than grown around whatever waits inside. South, the path to the gate thins into shadow. North, the door waits with the patience of something that knows the difference between force and invitation, while the gargoyle's eyes flicker red.",
        {"south": "Front Gate"}, # North is locked!
        scenery={
            "knocker": "The gargoyle knocker is heavy brass, mounted exactly where a visitor's hand would fall. Its open mouth looks made for a hard, ringing knock.",
            "gargoyle": "The brass gargoyle is not just decoration. Its lower jaw hangs as a knocker, polished bright where other hands have lifted it.",
            "door": "The oak is ancient and scarred. It is currently locked tight, but the brass gargoyle knocker sits ready at the center panel."
        }
    )

    rooms["Foyer"] = Room(
        "The Foyer",
        "Dust motes drift through the weak light of a dying chandelier. The front door is south behind you, and a grand staircase rises up from the center of the hall into the gloom. North, the smell of old smoke and cold metal seeps from the kitchen. West, a dim living room waits in stale silence. East, the dining room holds a long table set for a meal that never happened.",
        "The shadows have detached from the walls and turn in a silent, mocking waltz. South, the front door looks farther away than it should. North, the kitchen breathes blue heat; west, Mother's room exhales sickness; east, the dining room waits with the patience of a family secret. The staircase upward stretches too far, a black spiral of whispering voices.",
        {"south": "Front Door", "north": "Kitchen", "west": "Living Room", "east": "Dining Room", "up": "Upstairs Hallway"}
    )

    rooms["Living Room"] = Room(
        "The Living Room",
        "Mother lies on a velvet sofa, her face a mask of waxen exhaustion. The foyer waits east through a dark archway, and a narrow doorway north leads into a study crowded with books and papers. A white bandage on Mother's hand is the only bright thing in the room, brighter even than the dust filmed across the furniture.",
        "Mother's shadow stands over her, a tall, faceless thing that turns as you enter. East, the foyer shivers with detached shadows; north, the study's papers whisper against one another. The room smells of copper and unwashed tea cups, and the bandage gleams like a small accusation beneath the thing that is almost her shape.",
        {"east": "Foyer", "north": "Study"},
        scenery={
            "mother": "She looks as if she has been sleeping for a hundred years and suffering through every minute of it.",
            "bandage": "The white cloth around Mother's hand is fresh enough to shame the dust around it.",
            "sofa": "The velvet sofa sags beneath Mother and smells faintly of lavender water and sickness."
        }
    )

    rooms["Dining Room"] = Room(
        "The Dining Room",
        "A long walnut table dominates the room east of the foyer, laid for a family meal that never came. The only doorway leads west, back to the hall. Three place settings sit beneath a blackened silver candelabrum, and at the head of the table a fourth chair waits in stern silence. A sideboard crouches against the wall, its drawers swollen with damp.",
        "The table stretches far beyond the walls, laid for more guests than the room could ever hold. West, the foyer looks thin and ordinary, a painted exit on the wrong kind of wall. Invisible diners shift their cutlery in the dark, and the empty head chair rocks gently as if someone impatient has just risen from it.",
        {"west": "Foyer"},
        items={"family photograph": ["photo", "photograph", "family photo"]},
        scenery={
            "table": "The plates are spotless, but one napkin is dotted with the brown shadow of dried blood.",
            "chair": "The chair at the head of the table is carved with tiny eyes along its backrest.",
            "candelabrum": "The silver has gone black in places. Wax has pooled like old tears down its arms.",
            "place settings": "Three ordinary settings face a fourth position that feels more ceremonial than domestic."
        }
    )

    rooms["Study"] = Room(
        "The Study",
        "Tall bookcases crowd the walls, bowing beneath ledgers, hymnals, and family records. South, the doorway returns to Mother's room and the stale hush around her sofa. A writing desk sits beneath the rain-streaked window, its crooked drawer not quite closed, and loose papers lie across the rug like pale leaves.",
        "The books whisper in overlapping voices. South, Mother's room waits like a held sob, too near and too far at once. The desk drawer chatters softly against its frame, and the loose papers on the floor rearrange themselves whenever you blink, forming names you almost recognize.",
        {"south": "Living Room"},
        items={"ritual ledger": ["ledger", "book"], "invitation card": ["card", "invitation"]},
        scenery={
            "desk": "An old writing desk with one drawer slightly crooked, as if it has been forced open before.",
            "papers": "Birth dates, death dates, treatment notes, and household accounts. Someone kept records of everything.",
            "bookcase": "Dusty shelves of scripture, medicine, and family history lean over you like judges.",
            "window": "Rain beads against the glass. The cemetery is just visible beyond the black trees."
        }
    )

    rooms["Kitchen"] = Room(
        "The Kitchen",
        "A cold blue flame flickers in the stone hearth, casting long, shivering shadows over hanging utensils and a scarred worktable. South leads back to the foyer and the rest of the house. East, a back door opens toward the garden, while down a steep stairwell damp air rises from the cellar. The room feels practical at first glance, but too many tools have been cleaned too well.",
        "The blue flame is screaming in a frequency you feel in your teeth. South, the foyer tilts like a stage set losing its nails; east, the garden door bends as if the night is pressing inward; down, the cellar breathes wet glass and old secrets. The hanging utensils throw shadows like meat hooks.",
        {"south": "Foyer", "east": "Garden", "down": "Cellar"},
        items={"heavy axe": ["axe", "weapon"], "silver spoon": ["spoon"]}
    )

    rooms["Upstairs Hallway"] = Room(
        "The Upstairs Hallway",
        "Oil paintings of the Amon ancestors line the upstairs hallway, their eyes following every move. The staircase descends to the foyer, and a doorway west opens into your childhood bedroom. Overhead, a ladder leads to a heavy attic door with a large ornate keyhole. From above comes the slow creak of a rocking chair, steady as a pulse.",
        "The ancestors are no longer in their frames. Down, the foyer churns with shadow; west, your bedroom breathes behind its door; up, the attic door waits above the ladder, not locked so much as listening. Empty canvases gape along the hallway while voices try your name from inside the walls.",
        {"down": "Foyer", "west": "King's Bedroom"}, # Removed 'up' so it starts locked
        scenery={
            "door": "It's a heavy oak door with a large, ornate keyhole.",
            "keyhole": "You see a faint flickering light on the other side. You hear voices laughing insanely.",
            "portraits": "The eyes in the paintings seem to track your every move."
        }
    )

    rooms["King's Bedroom"] = Room(
        "King's Bedroom",
        "Your childhood bedroom lies west of the upstairs hall, though nothing about it feels like refuge. The hallway waits east through the half-open door. The bed is unmade, the air is stale, and a single candle gutters on the nightstand, casting weak light over old toys, a warped wardrobe, and the dust beneath the bed.",
        "The walls are breathing. East, the hallway calls through the door in borrowed voices, while the window looks out onto a world replaced by swirling purple mist. The toys on the floor have turned their faces away from you. Somewhere in this room, childhood has hidden what adulthood forgot.",
        {"east": "Upstairs Hallway"},
        items={"brass key": ["key", "brass"]}
    )

    rooms["Attic"] = Room(
        "The Attic (Grandma's Room)",
        "The attic is narrow and close beneath the roof beams. The ladder back down waits behind you, open to the upstairs hall. Grandma sits in her rocking chair with her back to you, placed as if she has always belonged at the room's center. Beside her, a small table holds the silver teapot called Amon, and violet steam coils from its spout.",
        "The attic is crowded with flickering, translucent figures, each one hollow where a face should be. Down the ladder lies the hallway, though the guests seem to prefer you not notice it. They press around the rocking chair, around the table, around the violet steam rising from Amon's spout, gathering the room's attention around Grandma and you.",
        {"down": "Upstairs Hallway"},
        items={"teapot": ["amon", "pot", "tea"]},
        scenery={
            "grandma": "She sits with her back to you in the rocking chair, as if she has been waiting long enough to become part of the furniture.",
            "rocking chair": "Dark wood polished by years of use. It moves in a patient rhythm that suggests it remembers every body it has carried.",
            "steam": "The violet steam rises in delicate coils, but now and then it gathers into shapes too deliberate to be called accidental.",
            "table": "A small table set with a single teapot and the expectation of company.",
            "cups": "You cannot see any cups at first, only the spaces where they ought to be."
        }
    )

    rooms["Cellar"] = Room(
        "The Damp Cellar",
        "The cellar crouches beneath the kitchen, low, damp, and crowded with stone shelves. The stairway up returns to the kitchen and its cold blue flame. Rows of unlabelled jars sit in the dark, filled with liquids too thick to reflect your face, and the floor is slick with something that is not water.",
        "The jars vibrate with trapped voices, and tiny pale hands press against the glass from within. Up the stairs, the kitchen flame screams faintly through the floorboards, but every shelf seems to lean inward before letting you go. Down here, the glass has the room's full attention.",
        {"up": "Kitchen"},
        items={"sealed jar": ["jar", "souls"]}
    )

    rooms["Garden"] = Room(
        "The Garden",
        "The garden lies east of the kitchen, where the night air is freezing but almost clean. West, the kitchen door leaks a thin line of blue light. North, a small tool shed leans beside the wall beneath dead oak trees, while broken flower beds lie under a skin of frost.",
        "The trees have become gallows, their branches reaching down like nooses. West, the kitchen's blue light cuts through the door like a wound; north, the shed hums with sharp metal. The ground is soft and spongy, as if you are walking on a giant sleeping lung.",
        {"west": "Kitchen", "north": "Shed"}
    )

    rooms["Shed"] = Room(
        "The Tool Shed",
        "The tool shed is cramped with the scent of oil, rust, and wet wood. The garden path lies south through the warped door. Sharp tools hang from hooks on the walls, glinting whenever moonlight slips through the cracks, and a sharpening stone sits on a cluttered workbench beneath a cracked window.",
        "The tools drip with a dark oily substance that looks like old blood. South, the garden waits under its gallows trees, breathing against the warped door. Above the workbench, the hanging tools hum softly, hungry for the sharpening stone and for hands willing to make edges useful.",
        {"south": "Garden"},
        items={"sharpening stone": ["stone"]}
    )

    return rooms
