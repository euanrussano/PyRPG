# 7.1 - Refactoring Events for Dynamic Entities

In this lesson, we're going to refactor our event system from a grid-based approach to a dynamic list-based approach. This change is crucial for supporting moving entities like town folks, wandering NPCs, or any interactive object that needs to change position. Right now, our events are locked to specific grid positions, which won't work for characters that move around!

## Understanding the Problem

Currently, our events are stored in a 2D grid:

```python
# Old approach - events locked to grid positions
events: List[List[EventTile]] = [
    [EventTile(), EventTile(), EventTile()],
    [EventTile(), EventTile(), EventTile()],
    # ...
]
```

**Problems with this approach:**
1. **Memory waste** - We create an empty `EventTile` for every single tile, even if 99% have no events
2. **Can't move** - Events are permanently bound to grid coordinates
3. **Inflexible** - Adding a moving NPC would require constantly updating the grid

## The Solution: Dynamic Event List

Instead, let's store events in a simple list where each event knows its own position:

```python
# New approach - events in a dynamic list
events: List[MapEvent] = [
    MapEvent(x=5, y=3, tile=chest_tile, event=chest_event),
    MapEvent(x=2, y=7, tile=door_tile, event=door_event),
    # Only create events where we need them!
]
```

**Benefits:**
- ✅ Only store events that actually exist
- ✅ Events can move by changing their `x` and `y`
- ✅ Easy to add/remove events dynamically
- ✅ Perfect for NPCs, enemies, projectiles, etc.

## Renaming EventTile to MapEvent

First, let's rename `EventTile` to `MapEvent` and add position tracking. In `event.py`:

```python
class Event(ABC):
    def __init__(self):
        self.owner: Optional['MapEvent'] = None  # Updated reference
    
    @abstractmethod
    def trigger(self, session):
        pass
```

Now create the new `MapEvent` class:

```python
class MapEvent:
    def __init__(self, x: int, y: int, tile: Optional[Tile] = None, 
                 event: Optional[Event] = None, run_once: bool = True):
        self.x = x  # Position in the world!
        self.y = y
        self.tile = tile
        self.__event = None
        self.run_once = run_once
        self.is_active = True

        if event is not None:
            self.set_event(event)

    def set_event(self, event: Event):
        self.__event = event
        event.owner = self

    @property
    def is_walkable(self):
        if self.tile is None:
            return True
        return self.tile.is_walkable

    def has_event(self):
        return self.__event is not None
    
    def trigger(self, session):
        if not self.is_active:
            return

        if self.__event is not None:
            self.__event.trigger(session)

            if self.run_once:
                self.__event = None
```

The key difference is that `MapEvent` now stores `x` and `y` coordinates!

## Updating the Tilemap Class

In `tilemap.py`, update the `Tilemap` class to use a list instead of a grid:

```python
class Tilemap:
    def __init__(self, tiles: List[List[Tile]], events: List[MapEvent] = ()):
        self.tiles = tiles
        self.width = len(tiles)
        self.height = len(tiles[0])
        self.events = events  # Now a simple list!
```

**Finding Events by Position:**

```python
def get_map_event(self, x: int, y: int) -> MapEvent | None:
    """Find an event at a specific position"""
    if not self.has_tile(x, y): 
        return None
    
    # Search through events for one at this position
    map_event = next((event for event in self.events 
                      if event.x == x and event.y == y), None)
    return map_event
```

This searches through the event list and returns the first event at the given coordinates, or `None` if there isn't one.

**Updating Collision Detection:**

```python
def is_blocked(self, new_x: int, new_y: int) -> bool:
    # Check bounds
    if not self.has_tile(new_x, new_y): 
        return True
    
    # Check tile walkability
    if not self.get_tile(new_x, new_y).is_walkable: 
        return True
    
    # Check if an event is blocking this position
    map_event = self.get_map_event(new_x, new_y)
    if map_event and not map_event.is_walkable:
        return True
    
    return False
```

Now we search for events at the position instead of indexing a grid!

## Updating Tilemap Factories

Let's update our factories to create events dynamically instead of pre-allocating a grid.

### Removing the Grid Creation Helper

Delete this old helper method:

```python
# DELETE THIS - we don't need it anymore!
@staticmethod
def create_empty_events(width: int, height: int):
    # ...
```

### Forest Factory - Creating Events on Demand

```python
class ForestTilemapFactory(TilemapFactory):
    def create(self, place_random_chests: bool = False, 
               place_sign: bool = False, 
               place_key: bool = False) -> 'Tilemap':
        
        width = 10
        height = 10
        tileset = get_tileset()
        tiles = []
        events = []  # Start with empty list!
        
        for i in range(width):    
            row = []
            for j in range(height):
                id = TileID.EMPTY
                if random.random() < 0.3:
                    id = random.choice(TREES)
                elif place_random_chests:
                    if random.random() < 0.1:
                        # Create event at position (i, j)
                        gold_amount = random.randint(1, 3)
                        event = CompositeEvent([
                            ShowMessageEvent("You found a chest!"),
                            GiveGoldEvent(gold_amount),
                            ShowMessageEvent(f"You got {gold_amount} gold"),
                            ChangeTileEvent(tileset.get_tile(TileID.EMPTY)),
                        ])
                        map_event = MapEvent(i, j, tileset.get_tile(TileID.CHEST_CLOSED))
                        map_event.set_event(event)
                        events.append(map_event)  # Add to list!
                
                row.append(tileset.get_tile(id))
            tiles.append(row)
        
        return Tilemap(tiles, events)
```

Let's break down the chest creation:

**Creating a MapEvent:**
```python
map_event = MapEvent(i, j, tileset.get_tile(TileID.CHEST_CLOSED))
```

We create the event at position `(i, j)` with a chest tile.

**Setting the Event Logic:**
```python
map_event.set_event(event)
```

Attach the composite event (show message, give gold, etc.).

**Adding to the List:**
```python
events.append(map_event)
```

Just append it! No need to worry about grid positions.

### Placing Signs

```python
elif place_sign:
    if random.random() < 0.1:
        map_event = MapEvent(i, j)
        map_event.run_once = False  # Can trigger multiple times
        map_event.tile = tileset.get_tile(TileID.SIGN)
        event = ShowMessageEvent("You found a sign!")
        map_event.set_event(event)
        events.append(map_event)
        place_sign = False  # Only one sign
```

### Placing the Key

```python
# Place key in a random empty spot
if place_key:
    is_key_placed = False
    while not is_key_placed:
        x = random.randint(0, width-1)
        y = random.randint(0, height-1)
        if tiles[x][y].id == TileID.EMPTY:
            map_event = MapEvent(x, y)
            map_event.tile = tileset.get_tile(TileID.KEY)
            event = CompositeEvent([
                ShowMessageEvent("You found a key!"),
                ChangeTileEvent(tileset.get_tile(TileID.EMPTY)),
                AddItemEvent(ItemRepository.get_instance().find_by_id(TileID.KEY))
            ])
            map_event.set_event(event)
            events.append(map_event)
            is_key_placed = True
```

## Updating the Town Factory

In `TownTilemapFactory`, we also switch to a list:

```python
class TownTilemapFactory(TilemapFactory):
    def create(self) -> 'Tilemap':
        tileset = get_tileset()
        tiles = []
        events = []  # List instead of grid!
        
        for _ in range(10):    
            row = []
            for _ in range(10):
                id = TileID.EMPTY
                row.append(tileset.get_tile(id))
            tiles.append(row)
        
        # Create buildings - pass the events list
        self.create_building(tiles, events, 2, 2, 4, 4, door_type=DoorType.SIMPLE)
        self.create_building(tiles, events, 7, 2, 3, 3, door_type=DoorType.LOCKED)
        self.create_building(tiles, events, 2, 7, 3, 3, door_type=DoorType.CLOSED)
        self.create_building(tiles, events, 7, 7, 3, 3, door_type=DoorType.OPEN)
        
        return Tilemap(tiles, events)
```

### Updating Building Creation

Change the signature to accept a list:

```python
def create_building(
    self, 
    tiles: List[List['Tile']], 
    events: List['MapEvent'],  # Changed from grid to list!
    x: int, 
    y: int, 
    width: int, 
    height: int, 
    door_type: DoorType = DoorType.CLOSED
):
    # ... create walls and corners ...
    
    # Simple door
    if door_type == DoorType.SIMPLE:
        tiles[x+1][y] = tileset.get_tile(TileID.EMPTY)
        map_event = MapEvent(x+1, y)  # Create at door position
        map_event.tile = tileset.get_tile(TileID.BUILDING_DOOR_CLOSED)
        event = CompositeEvent([
            ChangeTileEvent(tileset.get_tile(TileID.BUILDING_DOOR_OPEN)),
            ShowMessageEvent("You opened the door")
        ])
        map_event.set_event(event)
        events.append(map_event)  # Add to list!
```

### Locked Door

```python
elif door_type == DoorType.LOCKED:
    tiles[x+1][y] = tileset.get_tile(TileID.EMPTY)
    map_event = MapEvent(x+1, y)
    map_event.tile = tileset.get_tile(TileID.BUILDING_DOOR_CLOSED)
    event = IfEvent(
        condition=HasItemCondition(TileID.KEY),
        then_event=CompositeEvent([
            RemoveItemEvent(TileID.KEY),
            ShowMessageEvent("You unlocked the door."),
            ChangeTileEvent(tileset.get_tile(TileID.BUILDING_DOOR_OPEN)),
            DeactivateEvent()
        ]),
        else_event=ShowMessageEvent("The door is locked.")
    )
    map_event.set_event(event)
    map_event.run_once = False
    events.append(map_event)
```

## Updating the Rendering

In `main.py`, update the rendering to iterate through the event list:

```python
def update_tilemap(self, width: int, height: int, 
                   tiles: List[List[Tile]], 
                   events: List[MapEvent]):  # Now a list!
    self.canvas.delete(tk.ALL)
    
    # Draw base tiles
    for i in range(width):
        for j in range(height):
            tile = tiles[i][j]
            self.draw_tile(tile, i, j)

    # Draw event tiles on top
    for event in events:
        tile = event.tile
        if tile is not None:
            self.draw_tile(tile, event.x, event.y)
```

Notice how clean this is - we just iterate through events and draw them at their stored positions!

## Updating the Session

In `session.py`, update the event triggering:

```python
def try_trigger_event(self, x: int, y: int):
    tilemap = self.current_location.tilemap
    map_event = tilemap.get_map_event(x, y)
    
    if not map_event:
        return
    
    if map_event.has_event():
        map_event.trigger(self)
        self.view.render(self.current_location, self.hero)
```

We search for an event at the position instead of indexing a grid!

## What We Accomplished

In this lesson, we:
- Renamed `EventTile` to `MapEvent` to better reflect its purpose
- Changed from a grid-based event system to a dynamic list
- Added position tracking (`x`, `y`) to each `MapEvent`
- Updated all factories to create events on-demand
- Modified rendering to iterate through event lists
- Prepared our architecture for moving entities

## Why This Matters

This refactoring is crucial for future features:
- **NPCs** - Can walk around and carry their interaction events with them
- **Enemies** - Can patrol and move while maintaining their combat events
- **Projectiles** - Can fly through the air as moving events
- **Dynamic spawning** - Can add/remove events at runtime
- **Performance** - Only store events that actually exist

Now we're ready to add town folks that walk around and interact with the player! The events will follow them wherever they go. 🎯