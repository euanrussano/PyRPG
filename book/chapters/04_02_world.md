# 4.2 - Creating the World

In this lesson, we're going to expand our single tilemap into a complete game world! We'll create a world system that connects multiple locations together - a forest, a town, and a farm. This will give our hero places to explore and set the foundation for the full game experience.

## A Bit of Cleanup

Before we build the world system, let's reorganize our tilemap code to make it more flexible.

### Renaming TilemapFactory to TilemapLoader

First, let's rename our existing `TilemapFactory` class to `TilemapLoader`, since it's specifically loading tilemaps from files:

```python
class TilemapLoader:
    def load(self, filename: str) -> 'Tilemap':
        tiles = []
        with open(filename, 'r') as f:
            for line in f:
                row = []
                for tile_id in line.strip().split(','):
                    row.append(Tile(int(tile_id)))
                tiles.append(row)
        return Tilemap(tiles)
```

The name `TilemapLoader` better describes what this class does - it loads tilemap data from a CSV file.

### Creating the TilemapFactory Interface

Now let's create an abstract base class that defines how tilemap factories should work:

```python
from abc import ABC, abstractmethod

class TilemapFactory(ABC):
    @abstractmethod
    def create(self) -> 'Tilemap':
        pass
```

This interface establishes a contract: any tilemap factory must implement a `create()` method that returns a `Tilemap` object. This gives us flexibility to create tilemaps in different ways - loading from files, generating procedurally, or building them programmatically.

## Creating Different Tilemap Factories

Now we can create specialized factories for each type of location in our game world.

### The Forest Tilemap Factory

Let's create a factory that procedurally generates a forest tilemap:

```python
import random

class ForestTilemapFactory(TilemapFactory):
    def create(self) -> 'Tilemap':
        tiles = []
        for _ in range(10):    
            row = []
            for _ in range(10):
                id = -1
                if random.random() < 0.3:
                    id = random.choice([84, 85, 86])
                row.append(Tile(id))
            tiles.append(row)
        return Tilemap(tiles)
```

Let's break this down:

**The Generation Loop:**
```python
for _ in range(10):    
    row = []
    for _ in range(10):
```

We're creating a 10x10 grid of tiles.

**Random Tree Placement:**
```python
id = -1
if random.random() < 0.3:
    id = random.choice([84, 85, 86])
```

Each tile starts empty (id = -1). There's a 30% chance it becomes a tree, randomly chosen from three different tree tile types (tiles 84, 85, and 86 from our tileset).

### The Town Tilemap Factory

The town factory creates a more structured layout with buildings:

```python
class TownTilemapFactory(TilemapFactory):
    def create(self) -> 'Tilemap':
        tiles = []
        for _ in range(10):    
            row = []
            for _ in range(10):
                id = -1
                row.append(Tile(id))
            tiles.append(row)
        
        # Create 4 buildings
        self.create_building(tiles, 2, 2, 4, 4)
        self.create_building(tiles, 7, 2, 3, 3)
        self.create_building(tiles, 2, 7, 3, 3)
        self.create_building(tiles, 7, 7, 3, 3)
        
        return Tilemap(tiles)
```

We start with an empty 10x10 grid, then add four buildings at strategic positions.

**The Building Helper Method:**

```python
def create_building(self, tiles: List[List['Tile']], x: int, y: int, width: int, height: int):
    # 4 corners
    tiles[x][y].id = 32
    tiles[x+width-1][y].id = 35
    tiles[x][y+height-1].id = 0
    tiles[x+width-1][y+height-1].id = 3
    
    # 2 horizontal edges
    for i in range(y+1, y+height-1):
        tiles[x][i].id = 16
        tiles[x+width-1][i].id = 19
    
    # 2 vertical edges
    for i in range(x+1, x+width-1):
        tiles[i][y].id = 1
        tiles[i][y+height-1].id = 1
    
    # Door
    tiles[x+1][y].id = 2
    
    # Window if not at the edge
    if x+2 < width:
        tiles[x+2][y].id = 33
```

This method constructs a building tile-by-tile: corners, edges, a door, and a window. Each building becomes a little procedural structure in our town!

## Creating the World System

Now let's build the classes that tie all our locations together.

### The Location Class

Create a new file `world.py`:

```python
from tilemap import Tilemap

class Location:
    def __init__(self, name: str, x: int, y: int, tilemap: Tilemap):
        self.name = name
        self.x = x
        self.y = y
        self.tilemap = tilemap
```

A `Location` represents a place in the world with:
- A name (like "Forest" or "Town")
- Coordinates (x, y) in the world grid
- A tilemap that defines what the location looks like

### The World Class

```python
class World:
    def __init__(self):
        self.locations = []

    def add_location(self, location: Location):
        for existing_location in self.locations:
            if existing_location.x == location.x and existing_location.y == location.y:
                raise ValueError(f"Location {location.x}, {location.y} already exists in the world.")
        self.locations.append(location)
```

The `World` class manages all locations and prevents duplicates at the same coordinates.

**Finding Locations:**

```python
def get_location(self, x: int, y: int) -> Location | None:
    for location in self.locations:
        if location.x == x and location.y == y:
            return location
    return None

def get_location_by_id(self, id: int) -> Location | None:
    if id < 0 or id >= len(self.locations):
        return None
    return self.locations[id]
```

These methods let us retrieve locations either by their world coordinates or by their index in the locations list.

### Creating the World

Let's add a factory method to create our complete world:

```python
@staticmethod
def create() -> 'World':
    world = World()
    forestFactory = ForestTilemapFactory()
    townFactory = TownTilemapFactory()
    
    # Forest
    world.add_location(Location("Forest", 0, -1, forestFactory.create()))
    
    # Town
    world.add_location(Location("Town", 0, 0, townFactory.create()))
    
    # Farm (reuses the forest generator)
    world.add_location(Location("Farm", 1, 0, forestFactory.create()))
    
    return world
```

Our world has three locations arranged in a grid: the town at (0, 0), the forest to the north at (0, -1), and the farm to the east at (1, 0).

## Updating the Game Session

Now we need to update our game session to use the new world system.

In `session.py`, update the imports and initialization:

```python
from world import Location, World

class GameSession(IGameSession):
    def __init__(self, view: GameScreen) -> None:
        super().__init__()
        self.hero: Hero | None = None
        self.view = view
        self.world = World.create()
        loc = self.world.get_location(0, 0)
        assert loc is not None
        self.current_location: Location = loc
```

We create the world and start the hero in the town (location 0, 0).

**Starting the Game:**

```python
def start(self):
    tilemap = self.current_location.tilemap
    self.view.update_tilemap(tilemap.width, tilemap.height, tilemap.tiles)
    
    self.hero = Hero("John")
    self.view.update_hero_position(self.hero.x, self.hero.y)
    self.view.update_hero_name(self.hero.name)
    self.view.update_hero_energy(self.hero.energy)
```

**Changing Locations:**

```python
def change_location(self, loc_id: int):
    loc = self.world.get_location_by_id(loc_id)
    if loc is None:
        return
    self.current_location = loc
    self.view.render(self.current_location, self.hero)
```

This method switches to a different location and re-renders everything.

## Fixing the Rendering Issue

When we tested switching between maps, we discovered a problem: the hero disappeared! This happened because redrawing the tilemap cleared the canvas, including the hero sprite.

### Creating a Unified Render Method

In `main.py`, add a new render method to `GameScreen`:

```python
def render(self, location: Location, hero: Hero):
    self.update_tilemap(location.tilemap.width, location.tilemap.height, location.tilemap.tiles)
    self.update_hero_position(hero.x, hero.y)
```

This method ensures we redraw both the tilemap and the hero together, in the correct order.

**Fixing the Tilemap Drawing:**

```python
def update_tilemap(self, width: int, height: int, tiles: List[List[Tile]]):
    self.canvas.delete(tk.ALL)
    
    for x in range(width):
        for y in range(height):
            # Drawing coordinates are upside down
            tile = tiles[x][height - y - 1]
            if tile.id == -1:
                continue
            tile_img = self.tileset.get_tile(tile.id)
            self.canvas.create_image(x * self.tile_size, y * self.tile_size,
                                    image=tile_img, anchor='nw')
```

Note the coordinate flip: `tiles[x][height - y - 1]`. This accounts for the difference between how we store tiles in our array (origin at bottom-left) versus how we draw them on the canvas (origin at top-left).

## Testing the World

To make testing easier, let's add a temporary map selection dropdown in the GUI:

```python
def create_left_panel(self, parent):
    # ... existing code ...
    
    map_selection_label = tk.Label(parent, text="Select map:", **label_config)
    map_selection_label.grid(row=5, column=0, **grid_config)
    
    map_options = ["0", "1", "2"]
    self.map_selection = tk.StringVar()
    self.map_selection.set(map_options[0])
    
    map_selection_menu = tk.OptionMenu(parent, self.map_selection, 
                                       *map_options, command=self.change_map)
    map_selection_menu.grid(row=5, column=1, **grid_config)

def change_map(self, event):
    loc_id = int(self.map_selection.get())
    self.session.change_location(loc_id)
```

Now you can use the dropdown to switch between the town (0), forest (1), and farm (2) and see each location render correctly with the hero!

## What We Accomplished

In this lesson, we:
- Refactored our tilemap code into a more flexible factory pattern
- Created procedural generators for forest and town tilemaps
- Built a world system that connects multiple locations together
- Fixed rendering issues to ensure the hero displays correctly
- Added temporary testing UI to switch between locations

Our game now has a real world to explore! In the next lesson, we'll work on allowing the hero to move between these locations naturally.