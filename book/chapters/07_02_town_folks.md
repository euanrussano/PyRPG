# 7.2 - Placing Town Folks

In this lesson, we're going to bring our town to life by adding NPCs (Non-Player Characters) that move around! We'll create "John the Greeter" who wanders randomly around town and greets anyone who bumps into him. This will demonstrate how our refactored event system enables dynamic, moving entities.

## Understanding Moving Entities

With our new list-based event system from the previous lesson, we can now create entities that:
- Have a position that changes over time
- Carry their interaction events with them
- Move according to different strategies (random, patrol, chase, etc.)

## Creating Movement Strategies

First, let's define an abstraction for how entities move. In `event.py`, add:

```python
import random
from typing import Tuple

class MovementStrategy(ABC):
    """Abstract base class for movement behaviors"""
    @abstractmethod
    def decide(self, owner: 'MapEvent') -> Tuple[int, int]:
        pass
```

A movement strategy takes the entity as input and returns a direction to move: `(dx, dy)`.

### Implementing Random Movement

Now let's create our first concrete strategy:

```python
class RandomMovementStrategy(MovementStrategy):
    def decide(self, owner: 'MapEvent') -> Tuple[int, int]:
        dx = random.randint(-1, 1)  # -1, 0, or 1
        dy = random.randint(-1, 1)
        return dx, dy
```

This strategy randomly picks a direction. The values can be:
- `-1` = move left/down
- `0` = don't move
- `1` = move right/up

## Defining Movement Speed

Different entities should move at different speeds. Add this enum:

```python
from enum import IntEnum

class MoveSpeed(IntEnum):
    SLOW = 1000    # Move every 1000ms (1 second)
    NORMAL = 500   # Move every 500ms (half second)
    FAST = 300     # Move every 300ms
```

These values represent milliseconds between movements.

## Adding Movement to MapEvent

Update the `MapEvent` class to support movement:

```python
class MapEvent:
    def __init__(self, x: int, y: int, tile: Optional[Tile] = None, 
                 event: Optional[Event] = None, run_once: bool = True):
        self.x = x
        self.y = y
        self.tile = tile
        self.__event = None
        self.run_once = run_once
        self.is_active = True

        # Movement properties
        self.movement: MovementStrategy | None = None
        self.move_speed = MoveSpeed.NORMAL
        self.move_timer = 0

        if event is not None:
            self.set_event(event)
    
    # ... existing methods ...
```

We track:
- `movement` - The strategy (or `None` if stationary)
- `move_speed` - How fast to move
- `move_timer` - Accumulates time until next move

## Implementing the Update Method

Add the update logic that calculates movement each frame:

```python
def update(self, delta: int) -> Tuple[int, int]:
    """Update the entity and return movement delta (dx, dy)"""
    if not self.movement:
        return 0, 0  # No movement strategy = stationary
    
    # Accumulate time
    self.move_timer += delta
    if self.move_timer < self.move_speed:
        return 0, 0  # Not time to move yet
    
    # Reset timer
    self.move_timer = 0
    
    # Ask the movement strategy for a direction
    dx = 0
    dy = 0
    if self.movement:
        dx, dy = self.movement.decide(self)
    
    # Only move in cardinal directions (not diagonal)
    if dx != 0:
        return dx, 0
    else:
        return 0, dy
```

Let's break this down:

**Timer Accumulation:**
```python
self.move_timer += delta
if self.move_timer < self.move_speed:
    return 0, 0
```

We add the elapsed time (`delta`) and only move when we've accumulated enough time.

**Strategy Decision:**
```python
if self.movement:
    dx, dy = self.movement.decide(self)
```

We delegate the decision to the movement strategy. This makes it easy to swap in different AI behaviors!

**Cardinal Directions Only:**
```python
if dx != 0:
    return dx, 0
else:
    return 0, dy
```

If we got a horizontal movement, use that. Otherwise use vertical. This prevents diagonal movement and gives NPCs a more natural grid-based feel.

## Creating Town Folk

In `tilemap.py`, add the import for movement:

```python
from tilemap.event import ChangeTileEvent, CompositeEvent, MapEvent, GiveGoldEvent, \
    ShowMessageEvent, AddItemEvent, IfEvent, HasItemCondition, DeactivateEvent, \
    RemoveItemEvent, RandomMovementStrategy, MovementStrategy
```

Now add a helper method to create NPCs:

```python
class TownTilemapFactory(TilemapFactory):
    # ... existing methods ...
    
    def create_folk(self, x: int, y: int, tile_id: TileID, 
                    greet: str, movement: MovementStrategy) -> MapEvent:
        """Create a town folk NPC"""
        map_event = MapEvent(x, y)
        map_event.tile = get_tileset().get_tile(tile_id)
        map_event.run_once = False  # Can greet multiple times!
        
        # Set greeting event
        event = ShowMessageEvent(greet)
        map_event.set_event(event)
        
        # Set movement
        map_event.movement = movement
        
        return map_event
```

This creates a complete NPC with:
- A sprite (tile_id)
- An interaction (greeting message)
- Movement behavior
- Repeatable interaction (run_once = False)

## Adding John to the Town

Update the `create` method in `TownTilemapFactory`:

```python
def create(self) -> 'Tilemap':
    tileset = get_tileset()
    tiles = []
    events = []
    
    # Create empty tiles grid
    for _ in range(10):    
        row = []
        for _ in range(10):
            id = TileID.EMPTY
            row.append(tileset.get_tile(id))
        tiles.append(row)
    
    # Create buildings
    self.create_building(tiles, events, 2, 2, 4, 4, door_type=DoorType.SIMPLE)
    self.create_building(tiles, events, 7, 2, 3, 3, door_type=DoorType.LOCKED)
    self.create_building(tiles, events, 2, 7, 3, 3)
    self.create_building(tiles, events, 7, 7, 3, 3)

    # Create John the Greeter
    folk = self.create_folk(
        x=1, 
        y=1, 
        tile_id=TileID.FOLK_1,
        greet="Hey I'm John. Nice day btw...",
        movement=RandomMovementStrategy()
    )
    events.append(folk)
    
    return Tilemap(tiles, events)
```

John appears at position (1, 1) and will wander around randomly!

## Implementing the Game Loop

Now we need to make the game update regularly. In `main.py`, add the update interval constant at the top:

```python
update_interval = 100  # Update every 100ms

class GameScreen(tk.Tk):
    # ... rest of the class
```

Add an update method to `GameScreen`:

```python
class GameScreen(tk.Tk):
    # ... existing code ...
    
    def update(self):
        """Game loop - called periodically"""
        self.session.update(update_interval)
        self.after(update_interval, self.update)  # Schedule next update
```

This creates a game loop that runs every 100 milliseconds and schedules itself to run again.

Start the loop when the game begins:

```python
if __name__ == "__main__":
    ItemRepository.get_instance().load_data()
    view = GameScreen()
    view.after(update_interval, view.update)  # Start the game loop
    view.mainloop()
```

## Updating Entities in the Session

In `session.py`, add the update method to the interface:

```python
class IGameSession(ABC):
    # ... existing abstract methods ...
    
    @abstractmethod
    def update(self, delta: int):
        pass
```

Now implement it in `GameSession`:

```python
def update(self, delta: int):
    """Update all moving entities in the current location"""
    for map_event in self.current_location.tilemap.events:
        # Get desired movement from the entity
        dx, dy = map_event.update(delta)
        
        # Calculate new position
        nx = map_event.x + dx
        ny = map_event.y + dy

        # Check x bounds
        if nx < 0 or nx >= self.current_location.tilemap.width:
            dx = 0
        # Check y bounds  
        elif ny < 0 or ny >= self.current_location.tilemap.height:
            dy = 0

        # Check collision with tiles
        if self.current_location.tilemap.is_blocked(nx, ny):
            dx = 0
            dy = 0

        # Don't move if hero is already adjacent to current position
        if self.hero.x in range(map_event.x-1, map_event.x+2) and \
           self.hero.y in range(map_event.y-1, map_event.y+2):
            dx = 0
            dy = 0
            
        # Don't move if hero would be adjacent to new position
        if self.hero.x in range(nx-1, nx+2) and self.hero.y in range(ny-1, ny+2):
            dx = 0
            dy = 0

        # Apply movement
        map_event.x += dx
        map_event.y += dy

    # Re-render the scene
    self.view.render(self.current_location, self.hero)
```

Let's break down the collision checks:

**Bounds Checking:**
```python
if nx < 0 or nx >= self.current_location.tilemap.width:
    dx = 0
elif ny < 0 or ny >= self.current_location.tilemap.height:
    dy = 0
```

Prevent moving off the map. Note the `elif` - if x is out of bounds, we don't need to check y.

**Tile Collision:**
```python
if self.current_location.tilemap.is_blocked(nx, ny):
    dx = 0
    dy = 0
```

Don't walk through walls, trees, or other non-walkable tiles.

**Hero Avoidance - Current Position:**
```python
if self.hero.x in range(map_event.x-1, map_event.x+2) and \
   self.hero.y in range(map_event.y-1, map_event.y+2):
    dx = 0
    dy = 0
```

This prevents the NPC from moving if the hero is already adjacent. The ranges create a 3x3 neighborhood:
- `range(map_event.x-1, map_event.x+2)` creates `[x-1, x, x+1]`

**Hero Avoidance - Target Position:**
```python
if self.hero.x in range(nx-1, nx+2) and self.hero.y in range(ny-1, ny+2):
    dx = 0
    dy = 0
```

This additionally prevents moving INTO a position next to the hero. Together, these two checks ensure NPCs maintain a respectful distance!

**Applying Movement:**
```python
map_event.x += dx
map_event.y += dy
```

After all checks pass, update the position!

**Re-rendering:**
```python
self.view.render(self.current_location, self.hero)
```

Redraw the scene to show the new positions.

## Testing John the Greeter

Run your game and visit the town. You should see:

1. **John appears** at position (1, 1) with a folk sprite
2. **John moves randomly** every 500ms in cardinal directions
3. **John avoids walls** - he won't walk through buildings
4. **John keeps his distance** - he maintains a buffer zone around the hero
5. **John greets you** - walk up to him and bump into him to see his greeting: "Hey I'm John. Nice day btw..."

Try the following experiments:
- **Follow John around** - he'll avoid you as you get close
- **Trap John in a corner** - watch how he tries to find a way out
- **Bump into John** - every time you touch him, he greets you again (because `run_once = False`)

## What We Accomplished

In this lesson, we:
- Created a movement strategy system with the Strategy pattern
- Implemented `RandomMovementStrategy` for wandering behavior
- Added speed control with movement timers
- Created a game loop that updates entities every 100ms
- Implemented comprehensive collision detection for moving entities
- Added hero avoidance so NPCs maintain personal space
- Built a helper method to easily create town folk
- Made John the Greeter, our first wandering NPC!

## Extending the System

Now that you have the foundation, you can easily add more NPCs and behaviors:

**Add More Town Folk:**
```python
# Create Sally the Merchant
merchant = self.create_folk(
    x=3, 
    y=5, 
    tile_id=TileID.FOLK_2,
    greet="Welcome to my shop! ...Oh wait, I don't have one yet.",
    movement=RandomMovementStrategy()
)
events.append(merchant)

# Create Bob the Elder (slow moving)
elder = self.create_folk(
    x=8, 
    y=8, 
    tile_id=TileID.FOLK_3,
    greet="Back in my day, we didn't have fancy graphics!",
    movement=RandomMovementStrategy()
)
elder.move_speed = MoveSpeed.SLOW
events.append(elder)
```

**Create New Movement Strategies:**
```python
class StationaryStrategy(MovementStrategy):
    """Doesn't move at all"""
    def decide(self, owner: 'MapEvent') -> Tuple[int, int]:
        return 0, 0

class PatrolStrategy(MovementStrategy):
    """Patrols between two points"""
    def __init__(self, x1: int, y1: int, x2: int, y2: int):
        self.start = (x1, y1)
        self.end = (x2, y2)
        self.going_to_end = True
    
    def decide(self, owner: 'MapEvent') -> Tuple[int, int]:
        target = self.end if self.going_to_end else self.start
        
        # Reached target?
        if owner.x == target[0] and owner.y == target[1]:
            self.going_to_end = not self.going_to_end
            return 0, 0
        
        # Move toward target
        dx = 0 if owner.x == target[0] else (1 if owner.x < target[0] else -1)
        dy = 0 if owner.y == target[1] else (1 if owner.y < target[1] else -1)
        
        return dx, dy
```

The movement strategy system is incredibly flexible and makes it easy to create diverse NPC behaviors. Welcome to your living, breathing town! 🏘️

![John the Greeter](images/07_02_folk.png)