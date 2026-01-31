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


## Implementing Movement with Collision Detection

Now let's update the `GameSession` to check for collisions before moving the hero.

### Initializing the Hero

In `session.py`, create the hero during initialization:

```python
class GameSession(IGameSession):
    def __init__(self, view: GameScreen) -> None:
        super().__init__()
        self.hero: Hero = Hero("John")
        self.view = view
        self.world = World.create()
        loc = self.world.get_location(0, 0)
        assert loc is not None
        self.current_location: Location = loc
```

### Starting the Game

Simplify the `start` method:

```python
def start(self):
    self.view.render(self.current_location, self.hero)
```

We just render everything - no need for separate tilemap and hero updates!

### Movement with Collision Detection

Now the important part - checking collisions before moving:

```python
def move_hero(self, dx: int, dy: int):
    if self.hero is None:
        return
    
    # Only allow single-tile movements
    if abs(dx) > 1 or abs(dy) > 1:
        return
    
    # Only allow cardinal directions (not diagonal)
    if abs(dx) + abs(dy) != 1:
        return
    
    # Calculate new position
    new_x = self.hero.x + dx
    new_y = self.hero.y + dy

    # Check if blocked
    if self.current_location.tilemap.is_blocked(new_x, new_y):
        return  # Can't move there!
    
    # Move is valid - update hero position
    self.hero.x = new_x
    self.hero.y = new_y
    
    # Re-render the scene
    self.view.render(self.current_location, self.hero)
```

Let's break down the validation:

**Movement Constraints:**
```python
if abs(dx) > 1 or abs(dy) > 1:
    return
```
This prevents moving more than one tile at a time.

**Cardinal Directions Only:**
```python
if abs(dx) + abs(dy) != 1:
    return
```
This ensures we only move up, down, left, or right - not diagonally.

**Collision Check:**
```python
if self.current_location.tilemap.is_blocked(new_x, new_y):
    return
```
This is where the magic happens! We check the target position before moving.

### Fixing Movement Direction

With our y-axis pointing up, we need to fix the movement controls:

```python
def move_down(self, event):
    self.move_hero(0, -1)  # Down means decreasing y

def move_up(self, event):
    self.move_hero(0, 1)  # Up means increasing y
    
def move_left(self, event):
    self.move_hero(-1, 0)
    
def move_right(self, event):
    self.move_hero(1, 0)
```

## Testing Collision Detection

Run your game and try moving around! You should notice:

1. **You can walk on empty tiles** - they're marked as walkable
2. **You can't walk through trees** - they're marked as non-walkable
3. **You can't walk through walls** - they're marked as non-walkable
4. **You CAN walk through open doors** - they're marked as walkable!
5. **You can't walk through closed doors** - they're marked as non-walkable
6. **You can't walk off the edge of the map** - bounds checking works

## What We Accomplished

In this lesson, we:
- Added collision detection to the `Tilemap` class
- Fixed the coordinate system so y-axis points up
- Created a unified render method for clean rendering
- Implemented proper movement validation with collision checking
- Fixed movement directions to work with the new coordinate system

Now our hero properly interacts with the game world! Try walking around the town - you'll see the hero can explore freely but can't walk through buildings. And if you switch to a map with an open door, you can walk right through it!