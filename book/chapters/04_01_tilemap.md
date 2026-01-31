# 4.1 - Creating the Tilemap System

In this lesson, we're going to transform our empty black canvas into a living, breathing game world! We'll create a tilemap system that loads level data from a file and displays it on screen. This is a fundamental feature of almost every 2D game.

By the end of this lesson, you'll have a forest scene with trees displayed on your game canvas, and you'll understand how professional 2D games organize and render their worlds.

## What is a Tilemap?

A **tilemap** is a grid-based representation of a game level. Instead of creating the entire level as one giant image, we build it from small, reusable tiles—like building with LEGO blocks.

Think of it like this:
- **Tileset**: The palette of available tiles (grass, water, trees, walls, etc.)
- **Tilemap**: The blueprint that says "put grass here, a tree there, water over here"

### Why Use Tilemaps?

1. **Memory Efficient**: Instead of storing a 1920x1080 pixel image, we store a 60x34 grid of numbers
2. **Easy to Edit**: Level designers can edit simple text files or use visual editors
3. **Modular**: Swap out tilesets to completely change a level's appearance
4. **Collision Detection**: Grid-based collision is much simpler than pixel-perfect collision
5. **Procedural Generation**: Easy to generate levels algorithmically

For example, this grid:
```
-1, -1, -1
-1, 84, -1
-1, -1, -1
```

Represents: "Empty space, empty space, empty space / Empty space, tree, empty space / Empty space, empty space, empty space"

The number `84` refers to tile #84 in our tileset (a tree sprite), and `-1` means "no tile" (transparent/empty).

## Understanding the Architecture

Before we code, let's understand the pieces we're building:

### 1. Tile Class
A simple wrapper around a tile ID number. This allows us to add properties later (like walkable/unwalkable, damage, etc.)

### 2. Tilemap Class
Stores the grid of tiles and provides methods to access them.

### 3. TilemapFactory Class
Loads tilemap data from a file and creates Tilemap objects. This separates file I/O from the data structure.

### 4. Tileset Class
Manages loading and providing tile images from the sprite sheet.

This separation of concerns makes our code modular, testable, and maintainable.

## Creating the Tile Class

Let's start simple. Create a new file called `tilemap.py`:

```python
class Tile:
    def __init__(self, id: int):
        self.id = id
```

That's it! A tile is just a wrapper around an ID number. 

Why create a class for something so simple? Because later we might want to add:
- `self.walkable = True/False` (can the player walk on it?)
- `self.damage = 5` (does it hurt the player?)
- `self.animation_frames = [84, 85, 86]` (animated tiles!)

Starting with a class makes it easy to extend later without rewriting code.

## Creating the Tilemap Class

In the same `tilemap.py` file, add:

```python
from typing import List

class Tilemap:
    def __init__(self, tiles: List[List[Tile]]):
        self.tiles = tiles
        self.width = len(tiles)
        self.height = len(tiles[0])

    def get_tile(self, x: int, y: int):
        return self.tiles[x][y]
```

Let's break this down:

### The Constructor

```python
def __init__(self, tiles: List[List[Tile]]):
    self.tiles = tiles
```

- `tiles: List[List[Tile]]` is a type hint for a **2D list** (list of lists)
- This represents our grid: `tiles[x][y]` gives us the tile at position (x, y)

### Storing Dimensions

```python
self.width = len(tiles)
self.height = len(tiles[0])
```

We store the dimensions for convenience:
- `len(tiles)` is the number of columns (width)
- `len(tiles[0])` is the number of rows in the first column (height)

We assume all columns have the same height (a rectangular grid).

### The get_tile Method

```python
def get_tile(self, x: int, y: int):
    return self.tiles[x][y]
```

This provides a cleaner interface than accessing `self.tiles[x][y]` directly. Later, we could add bounds checking:

```python
def get_tile(self, x: int, y: int):
    if 0 <= x < self.width and 0 <= y < self.height:
        return self.tiles[x][y]
    return None  # Out of bounds
```

## Creating the TilemapFactory Class

Now let's create a factory to load tilemaps from CSV files. Add to `tilemap.py`:

```python
class TilemapFactory:
    def create_tilemap(self, filename: str) -> Tilemap:
        tiles = []
        with open(filename, 'r') as f:
            for line in f:
                row = []
                for c in line.split(","):
                    row.append(Tile(int(c)))
                tiles.append(row)
        return Tilemap(tiles)
```

Let's examine this carefully:

### The Factory Pattern

A **factory** is a class or method whose job is to create other objects. Instead of writing:

```python
tilemap = Tilemap(complicated_loading_code_here)
```

We write:

```python
tilemap = TilemapFactory().create_tilemap("forest.csv")
```

This separates the "how to create" from the "what to use" and makes testing easier.

### Reading the CSV File

```python
with open(filename, 'r') as f:
```

The `with` statement ensures the file is properly closed even if an error occurs. The `'r'` means "read mode."

### Parsing Lines

```python
for line in f:
    row = []
    for c in line.split(","):
        row.append(Tile(int(c)))
    tiles.append(row)
```

For each line in the file:
1. Create an empty row
2. Split the line by commas: `"84,85,-1"` → `['84', '85', '-1']`
3. Convert each string to an integer and create a Tile
4. Add the row to our tiles list

### Why Not Use csv Module?

Actually, you're right to question this! Let's improve it using Python's built-in `csv` module:

```python
import csv

class TilemapFactory:
    def create_tilemap(self, filename: str) -> Tilemap:
        tiles = []
        with open(filename, 'r') as f:
            csv_reader = csv.reader(f)
            for row in csv_reader:
                tiles.append([Tile(int(tile_id)) for tile_id in row])
        return Tilemap(tiles)
```

This is much cleaner! The `csv` module handles:
- Stripping whitespace
- Handling newlines
- Dealing with edge cases (quoted values, escaped commas, etc.)

The list comprehension `[Tile(int(tile_id)) for tile_id in row]` is a concise way to create a list of Tiles from a list of strings.

## Creating the Tileset Class

Now let's refactor our tileset code into its own class. Create a new file called `tileset.py`:

```python
from PIL import Image, ImageTk

class Tileset:
    def __init__(self, out_tile_size: int):
        self.tile_size = 8
        self.out_tile_size = out_tile_size
        self.tiles = [] 
        self.create_tiles()

    def create_tiles(self):
        tileset: Image.Image = Image.open("assets/tileset.png")
        n_cols  = tileset.width // self.tile_size
        n_rows = tileset.height // self.tile_size
        self.tiles = []
        for j in range(n_rows):
            for i in range(n_cols):
                tile = tileset.crop((i*self.tile_size, j*self.tile_size, 
                                   (i+1)*self.tile_size, (j+1)*self.tile_size))
                tile = tile.resize((self.out_tile_size, self.out_tile_size))
                tile = ImageTk.PhotoImage(tile)
                self.tiles.append(tile)
        tileset.close()

    def get_tile(self, index):
        return self.tiles[index]
```

Let's break this down:

### Constructor Parameters

```python
def __init__(self, out_tile_size: int):
    self.tile_size = 8
    self.out_tile_size = out_tile_size
```

- `self.tile_size = 8`: The size of tiles in the source image (8x8 pixels)
- `self.out_tile_size`: The size we want tiles to be when displayed (e.g., 64x64 pixels)

We need both because:
- The tileset image has small 8x8 tiles (efficient file size)
- We want to display them larger on screen (visible to players)

### Loading All Tiles

```python
n_cols  = tileset.width // self.tile_size
n_rows = tileset.height // self.tile_size
```

Calculate how many tiles fit in the tileset image:
- If the tileset is 128 pixels wide and tiles are 8 pixels: `128 // 8 = 16 columns`
- If the tileset is 96 pixels tall and tiles are 8 pixels: `96 // 8 = 12 rows`

### The Double Loop

```python
for j in range(n_rows):
    for i in range(n_cols):
```

We iterate through rows first (j), then columns (i). This matters because it determines the indexing:
- Tile 0 is at (0, 0)
- Tile 1 is at (1, 0)
- Tile 2 is at (2, 0)
- ...
- Tile 16 is at (0, 1) (next row)

This **row-major order** is standard for sprite sheets.

### Cropping and Resizing

```python
tile = tileset.crop((i*self.tile_size, j*self.tile_size, 
                   (i+1)*self.tile_size, (j+1)*self.tile_size))
tile = tile.resize((self.out_tile_size, self.out_tile_size))
```

For tile at column `i`, row `j`:
- Left edge: `i * 8`
- Top edge: `j * 8`
- Right edge: `(i+1) * 8`
- Bottom edge: `(j+1) * 8`

Then we resize from 8x8 to whatever size we need for display.

### Converting to PhotoImage

```python
tile = ImageTk.PhotoImage(tile)
self.tiles.append(tile)
```

We convert to PhotoImage immediately and store it. This ensures:
1. All tiles are ready to display (no conversion needed during gameplay)
2. References are kept (won't be garbage collected)
3. One-time conversion cost during loading (not every frame)

**Note**: This couples the Tileset to Tkinter. In a larger project, you might separate this, but for our tutorial it's acceptable and keeps things simple.

## Creating a Config File

Before we continue, let's create a configuration file for constants. Create `config.py`:

```python
hero_sprite = 5
```

This stores the tile index for the hero sprite. Using a config file:
- Keeps magic numbers out of code
- Makes it easy to tweak values
- Centralizes game configuration
- Makes the code more readable

Later you might add:
```python
hero_sprite = 5
tree_sprite = 84
grass_sprite = -1
default_map = "assets/forest.csv"
viewport_width = 10
viewport_height = 10
```

## Generating a Sample Tilemap

We need a tilemap to display! Let's create a simple Python script to generate a random forest. Create `generate_forest.py` in your game folder (this is a utility script, not part of the game):

```python
import csv
import random

with open('assets/forest.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    for _ in range(10):
        row = []
        for _ in range(10):
            if random.random() < 0.3:
                row.append(random.choice([84, 85, 86]))
            else:
                row.append(-1)
        writer.writerow(row)
```

Let's understand this script:

### CSV Writer

```python
writer = csv.writer(file)
```

The `csv.writer()` creates an object that handles proper CSV formatting for us.

### Generating Random Tiles

```python
if random.random() < 0.3:
    row.append(random.choice([84, 85, 86]))
else:
    row.append(-1)
```

- `random.random()` returns a number between 0 and 1
- `< 0.3` means 30% chance
- If true: pick a random tree tile (84, 85, or 86 are different tree sprites in our tileset)
- If false: use -1 (empty space)

This creates a sparse forest with about 30% tree coverage.

### Running the Script

Run this script once to generate your forest:

```bash
python generate_forest.py
```

This creates `assets/forest.csv` with content like:

```
-1,-1,-1,-1,-1,-1,-1,-1,-1,-1
-1,-1,-1,84,85,85,-1,85,86,-1
-1,86,-1,86,-1,-1,86,-1,84,-1
-1,-1,84,-1,-1,-1,-1,-1,-1,-1
86,-1,-1,86,-1,-1,-1,-1,84,85
85,-1,84,-1,-1,-1,-1,86,-1,85
84,-1,84,85,-1,-1,85,-1,-1,-1
-1,-1,-1,-1,-1,84,-1,-1,-1,85
84,-1,-1,-1,-1,-1,-1,-1,84,-1
-1,85,-1,85,84,-1,-1,84,-1,85
```

Each number represents a tile:
- `-1`: Empty (no tile)
- `84`, `85`, `86`: Different tree sprites

## Updating the GameSession

Now let's update `session.py` to load and use the tilemap:

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from tilemap import Tilemap, TilemapFactory
if TYPE_CHECKING:
    from main import GameScreen

from hero import Hero

# ... (IGameSession interface stays the same)

class GameSession(IGameSession):
    def __init__(self, view: GameScreen, map_file: str = "assets/forest.csv") -> None:
        super().__init__()
        self.tilemap: Tilemap | None = None
        self.hero: Hero | None = None
        self.view = view
        self.map_file = map_file

    def start(self):
        self.tilemap = TilemapFactory().create_tilemap(self.map_file)
        self.view.update_tilemap(self.tilemap.width, self.tilemap.height, self.tilemap.tiles)
        
        self.hero = Hero("John")
        self.view.update_hero_position(self.hero.x, self.hero.y)
        self.view.update_hero_stats(self.hero.name, self.hero.level, self.hero.xp, self.hero.gold, self.hero.energy)

    # ... (movement methods stay the same)
```

Let's examine the changes:

### New Imports

```python
from tilemap import Tilemap, TilemapFactory
```

We import both classes so we can use them.

### Updated Constructor

```python
def __init__(self, view: GameScreen, map_file: str = "assets/forest.csv") -> None:
    super().__init__()
    self.tilemap: Tilemap | None = None
    self.hero: Hero | None = None
    self.view = view
    self.map_file = map_file
```

We added:
- `map_file` parameter with a default value
- `self.tilemap` to store the loaded tilemap
- `self.map_file` to remember which file to load

The default value means we can create a session without specifying a map:
```python
session = GameSession(view)  # Uses forest.csv by default
# or
session = GameSession(view, "assets/dungeon.csv")  # Custom map
```

### Updated start Method

```python
def start(self):
    self.tilemap = TilemapFactory().create_tilemap(self.map_file)
    self.view.update_tilemap(self.tilemap.width, self.tilemap.height, self.tilemap.tiles)
    
    self.hero = Hero("John")
    # ... rest stays the same
```

Before creating the hero, we:
1. Load the tilemap from the file
2. Tell the view to display it

This ensures the world exists before the hero appears in it.

## Updating the GameScreen

Now let's update `main.py` to display the tilemap. Here are the key changes:

### New Imports

```python
from typing import List
from tilemap import Tile
from tileset import Tileset
import config
```

### Creating the Tileset

In `__init__`, replace the `load_tileset()` call:

```python
# Create tileset
self.tileset = Tileset(self.tile_size)        

# Load sprites (now tile_size has a proper value)
self.load_hero_sprite()
```

### Updated load_hero_sprite Method

Replace the old `load_tileset()` method with:

```python
def load_hero_sprite(self):
    self.hero_photo = self.tileset.get_tile(config.hero_sprite)
```

Much simpler! We just get tile #5 (the hero) from our tileset. The tileset handles all the cropping, resizing, and PhotoImage conversion.

### New update_tilemap Method

Add this new method:

```python
def update_tilemap(self, width: int, height: int, tiles: List[List[Tile]]):
    self.canvas.delete(tk.ALL)
    for x in range(width):
        for y in range(height):
            tile = tiles[x][y]
            if tile.id == -1:
                continue
            tile_img = self.tileset.get_tile(tile.id)
            self.canvas.create_image(x * self.tile_size, y * self.tile_size, 
                                    image=tile_img, anchor='nw')
```

Let's break this down carefully:

#### Clearing the Canvas

```python
self.canvas.delete(tk.ALL)
```

`tk.ALL` is a special constant that means "delete everything." This clears the canvas completely before redrawing.

#### The Double Loop

```python
for x in range(width):
    for y in range(height):
```

We iterate through every position in the tilemap grid.

#### Getting the Tile

```python
tile = tiles[x][y]
if tile.id == -1:
    continue
```

We get the tile at position (x, y). If its ID is -1 (empty), we skip it with `continue`, which jumps to the next iteration of the loop.

#### Drawing the Tile

```python
tile_img = self.tileset.get_tile(tile.id)
self.canvas.create_image(x * self.tile_size, y * self.tile_size, 
                        image=tile_img, anchor='nw')
```

We:
1. Get the image for this tile ID from the tileset
2. Calculate the pixel position: `x * tile_size`, `y * tile_size`
3. Draw it on the canvas

The `anchor='nw'` (northwest/top-left) ensures tiles align perfectly on the grid.

## Understanding the Rendering Order

Notice that in `GameSession.start()`, we call:

```python
self.view.update_tilemap(...)  # Draw the world
# Then later:
self.view.update_hero_position(...)  # Draw the hero
```

This order matters! The canvas draws things in layers:
1. First layer: tilemap (background)
2. Second layer: hero (foreground)

If we reversed the order, the hero would be drawn first, then covered by tiles!

Later, we might have multiple layers:
1. Ground layer (grass, dirt)
2. Decoration layer (flowers, rocks)
3. Character layer (hero, NPCs, enemies)
4. Effects layer (magic spells, particles)

## Testing Your Tilemap

Run your game:

```bash
python main.py
```

You should now see:
1. A forest scene with randomly placed trees
2. The hero sprite positioned on the map
3. Empty spaces where there are no trees

Try moving the hero with the arrow keys. The hero should move through the forest!

## Current Limitations

Right now:
- The hero can walk through trees (no collision detection)
- All tiles are treated the same (trees, grass, water all act identically)
- We only have one layer (can't have ground + decorations)

We'll address these in upcoming lessons!

## What We've Learned

In this lesson, we covered:

1. **Tilemap Architecture**: Separating Tile, Tilemap, TilemapFactory, and Tileset
2. **Factory Pattern**: Using factories to create complex objects
3. **CSV File I/O**: Reading level data from files
4. **2D Lists**: Representing grids with `List[List[T]]`
5. **Sprite Sheet Processing**: Extracting individual tiles from a sprite sheet
6. **Canvas Layering**: Understanding render order
7. **Configuration Files**: Centralizing constants
8. **Procedural Generation**: Creating random level data
9. **Separation of Concerns**: Each class has a single, clear responsibility

## What's Next

Our world now exists, but it's still quite basic. In the next lessons, we'll:

1. Add collision detection so the hero can't walk through trees
2. Create multiple map layers (ground, decorations, objects)
3. Implement a camera system so the viewport can scroll
4. Add different terrain types with different properties
5. Load more complex maps with walls, water, and structures

You've built a real tilemap system—the same kind used in countless 2D games! This is a major milestone. Great work!