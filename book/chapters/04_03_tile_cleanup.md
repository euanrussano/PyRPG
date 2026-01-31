# 4.3 - Organizing Tiles and IDs

In this lesson, we're going to clean up our tile system by introducing proper organization with tile IDs, separating concerns between the tileset and spritesheet, and making tiles carry their own walkability information. This refactoring will make our code much more maintainable and set us up perfectly for implementing collision detection.

## Creating the Tile ID System

First, let's create a new file `tile_ids.py` to centralize all our tile identifiers:

```python
# tile_ids.py
from enum import IntEnum

class TileID(IntEnum):
    EMPTY = -1
    
    # Trees
    TREE_1 = 84
    TREE_2 = 85
    TREE_3 = 86
    COCONUT_TREE = 87

    # Folks
    FOLK_1 = 4
    FOLK_2 = 5
    FOLK_3 = 6
    FOLK_4 = 7
    FOLK_5 = 8
    FOLK_6 = 14
    FOLK_7 = 15
    
    # Building
    BUILDING_CORNER_TL = 0
    BUILDING_CORNER_TR = 3
    BUILDING_CORNER_BL = 32
    BUILDING_CORNER_BR = 35
    BUILDING_WALL_LEFT = 16
    BUILDING_WALL_RIGHT = 19
    BUILDING_WALL_HORIZONTAL = 1
    BUILDING_DOOR_CLOSED = 36
    BUILDING_DOOR_OPEN = 37
    BUILDING_WINDOW = 33

    # Furniture
    FURNITURE_TABLE_ROUND = 54
    FURNITURE_TABLE_SQUARE = 55
    FURNITURE_BENCH = 56
    FURNITURE_BED = 62

    CHEST_CLOSED = 57

# Helper groups
TREES = [TileID.TREE_1, TileID.TREE_2, TileID.TREE_3]
```

**Why use IntEnum?**

`IntEnum` gives us the best of both worlds:
- Named constants for clarity in our code
- Integer values that work with our existing sprite system
- Type safety and autocomplete in our IDE

The helper group `TREES` makes it easy to randomly select tree tiles in our forest generator.

## Separating Spritesheet from Tileset

Right now our `Tileset` class is doing two different jobs: loading sprite images from a PNG file and managing tile properties. Let's split these responsibilities.

### Creating the Spritesheet Class

Create a new file `spritesheet.py`:

```python
from PIL import Image, ImageTk

class Spritesheet:
    def __init__(self, filename: str, size: int):
        self.size = size
        self.filename = filename
        self.sprite_size = 8
        self.sprites = []
        self.create_sprites()

    def create_sprites(self):
        img: Image.Image = Image.open(self.filename)
        n_cols = img.width // self.sprite_size
        n_rows = img.height // self.sprite_size
        
        for j in range(n_rows):
            for i in range(n_cols):
                # Crop out one sprite
                sprite = img.crop((
                    i * self.sprite_size, 
                    j * self.sprite_size, 
                    (i + 1) * self.sprite_size, 
                    (j + 1) * self.sprite_size
                ))
                # Resize to display size
                sprite = sprite.resize((self.size, self.size))
                sprite_photo = ImageTk.PhotoImage(sprite)
                self.sprites.append(sprite_photo)
        
        img.close()

    def get_sprite(self, index: int):
        return self.sprites[index]
```

The `Spritesheet` class has one simple job: load a PNG file and provide access to individual sprite images by index.

## Redesigning the Tile and Tileset Classes

Now let's redesign our `Tileset` to focus on tile properties rather than images.

### The New Tile Class

In `tileset.py`, start with a simple `Tile` class:

```python
# tileset.py
from tile_ids import TileID
from typing import Dict, Optional

class Tile:
    def __init__(self, id: int, is_walkable: bool = True):
        self.id = id
        self.is_walkable = is_walkable
```

Each `Tile` now carries its own walkability information!

### The Tileset as a Singleton

The `Tileset` should be a single source of truth for tile properties throughout the game:

```python
class Tileset:
    _instance: Optional['Tileset'] = None
    
    def __init__(self):
        if Tileset._instance is not None:
            raise RuntimeError("Tileset is a singleton. Use Tileset.get_instance()")
        
        self.tiles: Dict[TileID, Tile] = {}
        self.create_tiles()
    
    @classmethod
    def get_instance(cls) -> 'Tileset':
        """Get the singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
```

**Why a singleton?**

There should only ever be one tileset in the game. The singleton pattern prevents accidental creation of multiple tilesets and provides a global access point.

### Registering Tiles with Properties

Now we register each tile with its properties:

```python
def create_tiles(self):
    """Register all tiles with their metadata"""
    tiles_data = [
        # Special
        (TileID.EMPTY, True),
        
        # Trees (non-walkable)
        (TileID.TREE_1, False),
        (TileID.TREE_2, False),
        (TileID.TREE_3, False),
        (TileID.COCONUT_TREE, False),
        
        # Folks (non-walkable - can't walk through people)
        (TileID.FOLK_1, False),
        (TileID.FOLK_2, False),
        (TileID.FOLK_3, False),
        (TileID.FOLK_4, False),
        (TileID.FOLK_5, False),
        (TileID.FOLK_6, False),
        (TileID.FOLK_7, False),
        
        # Building components (non-walkable - solid walls)
        (TileID.BUILDING_CORNER_TL, False),
        (TileID.BUILDING_CORNER_TR, False),
        (TileID.BUILDING_CORNER_BL, False),
        (TileID.BUILDING_CORNER_BR, False),
        (TileID.BUILDING_WALL_LEFT, False),
        (TileID.BUILDING_WALL_RIGHT, False),
        (TileID.BUILDING_WALL_HORIZONTAL, False),
        (TileID.BUILDING_DOOR_CLOSED, False),
        (TileID.BUILDING_DOOR_OPEN, True),  # Can walk through open door!
        (TileID.BUILDING_WINDOW, False),
        
        # Furniture (non-walkable)
        (TileID.FURNITURE_TABLE_ROUND, False),
        (TileID.FURNITURE_TABLE_SQUARE, False),
        (TileID.FURNITURE_BENCH, False),
        (TileID.FURNITURE_BED, False),
        
        # Chest (non-walkable)
        (TileID.CHEST_CLOSED, False),
    ]
    
    for tile_id, walkable in tiles_data:
        self.tiles[tile_id] = Tile(tile_id, walkable)

def get_tile(self, tile_id: TileID) -> Tile:
    """Get tile by its ID"""
    if tile_id not in self.tiles:
        # Return empty tile as fallback
        return self.tiles.get(TileID.EMPTY, Tile(TileID.EMPTY, True))
    return self.tiles[tile_id]
```

Notice how we can now see at a glance which tiles are walkable! The open door is walkable, but the closed door isn't.

### Providing Global Access

At the end of `tileset.py`, add:

```python
# Create the singleton instance at module load
_tileset_instance = Tileset.get_instance()

# Provide a simple function to access it
def get_tileset() -> Tileset:
    """Get the global tileset instance"""
    return _tileset_instance
```

Now anywhere in our code, we can simply do:

```python
from tileset import get_tileset

tileset = get_tileset()
tile = tileset.get_tile(TileID.TREE_1)
```

## Updating the Tilemap Factories

Now let's update our factories to use the new system. In `tilemap.py`, update the imports and remove the old `Tile` class definition:

```python
from abc import ABC, abstractmethod
from typing import List
import random

from tile_ids import TREES, TileID
from tileset import Tile, get_tileset
```

### The Forest Factory

```python
class ForestTilemapFactory(TilemapFactory):
    def create(self) -> 'Tilemap':
        tileset = get_tileset()
        tiles = []
        
        for _ in range(10):    
            row = []
            for _ in range(10):
                id = TileID.EMPTY
                if random.random() < 0.3:
                    id = random.choice(TREES)
                row.append(tileset.get_tile(id))
            tiles.append(row)
        
        return Tilemap(tiles)
```

Notice we're now getting actual `Tile` objects from the tileset, which already have their walkability set!

### The Town Factory

```python
class TownTilemapFactory(TilemapFactory):
    def create(self) -> 'Tilemap':
        tileset = get_tileset()
        tiles = []
        
        for _ in range(10):    
            row = []
            for _ in range(10):
                row.append(tileset.get_tile(TileID.EMPTY))
            tiles.append(row)
        
        # Create 4 buildings (first one has open door)
        self.create_building(tiles, 2, 2, 4, 4, is_door_open=True)
        self.create_building(tiles, 7, 2, 3, 3)
        self.create_building(tiles, 2, 7, 3, 3)
        self.create_building(tiles, 7, 7, 3, 3)
        
        return Tilemap(tiles)
```

### Updating the Building Creation

```python
def create_building(self, tiles: List[List[Tile]], x: int, y: int, 
                   width: int, height: int, is_door_open: bool = False):
    """
    Create a building with y-axis pointing up
    (x, y) is the bottom-left corner of the building
    """
    tileset = get_tileset()
    
    # 4 corners
    tiles[x][y] = tileset.get_tile(TileID.BUILDING_CORNER_BL)
    tiles[x+width-1][y] = tileset.get_tile(TileID.BUILDING_CORNER_BR)
    tiles[x][y+height-1] = tileset.get_tile(TileID.BUILDING_CORNER_TL)
    tiles[x+width-1][y+height-1] = tileset.get_tile(TileID.BUILDING_CORNER_TR)
    
    # Vertical walls
    for i in range(y+1, y+height-1):
        tiles[x][i] = tileset.get_tile(TileID.BUILDING_WALL_LEFT)
        tiles[x+width-1][i] = tileset.get_tile(TileID.BUILDING_WALL_RIGHT)
    
    # Horizontal walls
    for i in range(x+1, x+width-1):
        tiles[i][y] = tileset.get_tile(TileID.BUILDING_WALL_HORIZONTAL)
        tiles[i][y+height-1] = tileset.get_tile(TileID.BUILDING_WALL_HORIZONTAL)

    # Door
    door_id = TileID.BUILDING_DOOR_OPEN if is_door_open else TileID.BUILDING_DOOR_CLOSED
    tiles[x+1][y] = tileset.get_tile(door_id)
    
    # Window
    if x+2 < x+width:
        tiles[x+2][y] = tileset.get_tile(TileID.BUILDING_WINDOW)
```

Much clearer! We can see exactly what each tile is, and whether doors are open or closed.

## Updating the Tilemap Loader

For loading from CSV files:

```python
class TilemapLoader:
    def load(self, filename: str) -> 'Tilemap':
        tiles = []
        tileset = get_tileset()
        
        with open(filename, 'r') as f:
            for line in f:
                row = []
                for c in line.split(","):
                    id = TileID(int(c))
                    row.append(tileset.get_tile(id))
                tiles.append(row)
        
        return Tilemap(tiles)
```

## Updating the View

In `main.py`, we need to use both the spritesheet (for images) and tileset (for properties):

```python
from spritesheet import Spritesheet
from tileset import get_tileset

class GameScreen(tk.Tk):
    def __init__(self, viewport_width=10, viewport_height=10):
        # ... existing code ...
        
        self.calculate_tile_size()

        # Create spritesheet for images
        self.sprite_sheet = Spritesheet("assets/tileset.png", self.tile_size)
        
        # Get tileset singleton for properties
        self.tileset = get_tileset()

        # Load sprites
        self.load_hero_sprite()
        
        # ... rest of init ...
```

### Loading Sprites

```python
def load_hero_sprite(self):
    self.hero_photo = self.sprite_sheet.get_sprite(config.hero_sprite)
```

### Rendering the Tilemap

Update the rendering to use the spritesheet:

```python
def update_tilemap(self, width: int, height: int, tiles: List[List[Tile]]):
    self.canvas.delete(tk.ALL)
    
    for i in range(width):
        for j in range(height):
            tile = tiles[i][j]
            if tile.id == -1:
                continue
            
            # Get sprite image from spritesheet
            tile_img = self.sprite_sheet.get_sprite(tile.id)
            x, y = self.to_screen_coords(i, j)
            self.canvas.create_image(x, y, image=tile_img, anchor='nw')
```

## What We Accomplished

In this lesson, we:
- Created a `TileID` enum for type-safe, named tile identifiers
- Separated `Spritesheet` (handles images) from `Tileset` (handles properties)
- Made `Tile` objects carry their own walkability information
- Implemented the Tileset as a singleton with global access
- Updated all factories to use the new tile system
- Made our building creation code much more readable

Now our code is organized, maintainable, and ready for collision detection. In the next lesson, we'll implement hero movement with proper collision checking!

---

# 4.4 - Moving Around the Map

Now that we have tiles with walkability information, let's implement proper collision detection so our hero can't walk through walls, trees, or other obstacles!

## Adding Collision Detection to Tilemap

First, let's add a method to check if a position is blocked. In `tilemap.py`, add to the `Tilemap` class:

```python
class Tilemap:
    def __init__(self, tiles: List[List[Tile]]):
        self.tiles = tiles
        self.width = len(tiles)
        self.height = len(tiles[0])

    def get_tile(self, x: int, y: int) -> Tile:
        return self.tiles[x][y]
    
    def is_blocked(self, x: int, y: int) -> bool:
        """Check if a position is blocked (non-walkable or out of bounds)"""
        # Out of bounds is blocked
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True
        
        # Check tile walkability
        tile = self.get_tile(x, y)
        return not tile.is_walkable
```

This method returns `True` if:
- The position is outside the map boundaries
- The tile at that position is not walkable

## Fixing Coordinate System

Before we implement movement, we need to fix our coordinate system to have y-axis pointing up (like a mathematical coordinate system).

### Screen Coordinate Conversion

In `main.py`, add a helper method:

```python
def to_screen_coords(self, world_x: int, world_y: int) -> Tuple[int, int]:
    """Convert world coordinates to screen coordinates"""
    height = self.canvas.winfo_height()
    x = world_x * self.tile_size
    # Flip y-axis: higher world_y = higher on screen
    y = height - (world_y + 1) * self.tile_size
    return (x, y)
```

Don't forget to add the import at the top:

```python
from typing import List, Tuple
```

### Updating Hero Position Rendering

```python
def update_hero_position(self, world_x: int, world_y: int):
    """Update hero sprite position"""
    x, y = self.to_screen_coords(world_x, world_y)
    
    if self.hero_sprite:
        self.canvas.delete(self.hero_sprite)
    
    self.hero_sprite = self.canvas.create_image(x, y, 
                                                image=self.hero_photo, 
                                                anchor='nw')
```

### Updating Tilemap Rendering

```python
def update_tilemap(self, width: int, height: int, tiles: List[List[Tile]]):
    self.canvas.delete(tk.ALL)
    
    for i in range(width):
        for j in range(height):
            tile = tiles[i][j]
            if tile.id == -1:
                continue
            
            tile_img = self.sprite_sheet.get_sprite(tile.id)
            x, y = self.to_screen_coords(i, j)
            self.canvas.create_image(x, y, image=tile_img, anchor='nw')
```

### Creating a Unified Render Method

Add a method that renders everything together:

```python
def render(self, location: Location, hero: Hero):
    """Render the complete scene: tilemap and hero"""
    tilemap = location.tilemap
    self.update_tilemap(tilemap.width, tilemap.height, tilemap.tiles)
    self.update_hero_position(hero.x, hero.y)
```

This ensures the hero is always drawn after the tilemap, so it appears on top!

