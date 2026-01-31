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