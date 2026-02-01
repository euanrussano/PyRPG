# 6.2 - Using a Key to Unlock a Door

In this lesson, we're going to implement a locked door that requires a key from the player's inventory. This introduces conditional events - events that check certain conditions before executing. We'll create a door that checks if the hero has a key, and responds differently based on whether they do or not.

## Understanding the Problem

We want to create a door that:
- Is locked by default
- Checks if the hero has a key when they try to open it
- Opens and shows a success message if they have the key
- Shows a "door is locked" message if they don't have the key
- Consumes the key when used (one-time use)

This requires us to implement conditional logic in our event system!

## Creating Conditional Events

First, let's create a system for checking conditions. In `event.py`, add the abstract condition class:

```python
from abc import ABC, abstractmethod

class Condition(ABC):
    @abstractmethod
    def is_met(self, session) -> bool:
        pass
```

A `Condition` is simply something that can be checked - it returns `True` or `False`.

## Checking Inventory for Items

Now let's create a specific condition that checks if the hero has a particular item:

```python
from tilemap.tile_ids import TileID

class HasItemCondition(Condition):
    def __init__(self, item_id: TileID):
        self.item_id = item_id

    def is_met(self, session) -> bool:
        for item in session.hero.inventory:
            if item.item_definition.id == self.item_id:
                return True
        return False
```

This condition searches through the hero's inventory and returns `True` if it finds an item with the matching ID.

## The If Event

Now we can create an event that takes different actions based on a condition:

```python
class IfEvent(Event):
    def __init__(
        self,
        condition: Condition,
        then_event: Event,
        else_event: Event | None = None
    ):
        super().__init__()
        self.condition = condition
        self.then_event = then_event
        self.else_event = else_event

    def trigger(self, session):
        # Ensure child events know who owns the tile
        self.then_event.owner = self.owner
        if self.else_event:
            self.else_event.owner = self.owner

        if self.condition.is_met(session):
            self.then_event.trigger(session)
        elif self.else_event is not None:
            self.else_event.trigger(session)
```

Let's break this down:

**Constructor:**
```python
def __init__(self, condition, then_event, else_event=None):
```

The `IfEvent` takes:
- A condition to check
- A `then_event` to run if the condition is true
- An optional `else_event` to run if the condition is false

**Triggering:**
```python
if self.condition.is_met(session):
    self.then_event.trigger(session)
elif self.else_event is not None:
    self.else_event.trigger(session)
```

When triggered, it checks the condition and runs the appropriate event. Note that we pass `owner` to child events - this is important so they know which tile they're operating on!

## Deactivating Events

We need a way to make an event stop triggering. Add the `DeactivateEvent`:

```python
class DeactivateEvent(Event):
    def __init__(self):
        super().__init__()

    def trigger(self, session):
        if self.owner:
            self.owner.is_active = False
```

This event deactivates the tile it belongs to, preventing future triggers.

## Updating EventTile

In `event.py`, update the `EventTile` class to support activation state:

```python
class EventTile:
    def __init__(self, tile: Optional[Tile] = None, event: Optional[Event] = None, run_once: bool = True):
        self.tile = tile
        self.__event = None
        self.run_once = run_once
        self.is_active = True  # Add this!

        if event is not None:
            self.set_event(event)
    
    # ... existing methods ...
    
    def trigger(self, session):
        if not self.is_active:  # Check if active
            return

        if self.__event is not None:
            self.__event.trigger(session)

            if self.run_once:
                self.__event = None
```

Now events won't trigger if the tile is deactivated!

## Removing Items from Inventory

We need the ability to consume items. In `hero.py`, add:

```python
from tilemap.tile_ids import TileID

class Hero:
    # ... existing code ...
    
    def remove_item(self, item_id: TileID) -> bool:
        """Remove an item from inventory by its ID"""
        item_to_remove = None
        for item_instance in self.__inventory:
            if item_instance.item_definition.id == item_id:
                item_to_remove = item_instance
                break
        
        if item_to_remove:
            self.__inventory.remove(item_to_remove)
            return True
        return False
```

This searches for an item with the given ID and removes it if found.

## Session Support for Removing Items

In `session.py`, add a method to remove items and update the view:

```python
from tilemap.tile_ids import TileID

class GameSession(IGameSession):
    # ... existing code ...
    
    def remove_item(self, item_id: TileID):
        self.hero.remove_item(item_id)
        self.view.update_inventory(self.hero)
```

## Creating the Remove Item Event

In `event.py`, create an event that removes an item:

```python
class RemoveItemEvent(Event):
    def __init__(self, item_id: TileID):
        super().__init__()
        self.item_id = item_id

    def trigger(self, session):
        session.remove_item(self.item_id)
```

## Defining Door Types

To make our building creation more flexible, let's define different door types. In `tilemap.py`, add:

```python
from enum import Enum, auto

class DoorType(Enum):
    OPEN = auto()        # Open passage
    CLOSED = auto()      # Closed passage (just visual)
    SIMPLE = auto()      # Opens by bumping
    LOCKED = auto()      # Needs a key
```

## Creating a Locked Door

Now let's update our `create_building` method in `TownTilemapFactory` to support different door types:

```python
def create_building(
    self, 
    tiles: List[List['Tile']], 
    events: List[List['EventTile']], 
    x: int, 
    y: int, 
    width: int, 
    height: int, 
    door_type: DoorType = DoorType.CLOSED
):
    """
    Create a building with y-axis pointing up
    (x, y) is the bottom-left corner of the building
    """
    tileset = get_tileset()
    
    # ... create corners and walls (same as before) ...
    
    # Door on the bottom wall
    if door_type == DoorType.SIMPLE:
        # Door that opens when bumped
        tiles[x+1][y] = tileset.get_tile(TileID.EMPTY)
        events[x+1][y].tile = tileset.get_tile(TileID.BUILDING_DOOR_CLOSED)
        event = CompositeEvent([
            ChangeTileEvent(tileset.get_tile(TileID.BUILDING_DOOR_OPEN)),
            ShowMessageEvent("You opened the door")
        ])
        events[x+1][y].set_event(event)
        
    elif door_type == DoorType.LOCKED:
        # Door that requires a key
        tiles[x+1][y] = tileset.get_tile(TileID.EMPTY)
        events[x+1][y].tile = tileset.get_tile(TileID.BUILDING_DOOR_CLOSED)
        
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
        
        events[x+1][y].set_event(event)
        events[x+1][y].run_once = False  # Can try multiple times!
        
    elif door_type == DoorType.CLOSED:
        # Just a closed door (no interaction)
        tiles[x+1][y] = tileset.get_tile(TileID.BUILDING_DOOR_CLOSED)
        
    elif door_type == DoorType.OPEN:
        # Already open door
        tiles[x+1][y] = tileset.get_tile(TileID.BUILDING_DOOR_OPEN)
    
    # ... window creation (same as before) ...
```

Let's break down the locked door logic:

**Setting Up the Tile:**
```python
tiles[x+1][y] = tileset.get_tile(TileID.EMPTY)
events[x+1][y].tile = tileset.get_tile(TileID.BUILDING_DOOR_CLOSED)
```

The actual tile is empty (walkable), but we display a closed door sprite through the event system.

**The Conditional Logic:**
```python
event = IfEvent(
    condition=HasItemCondition(TileID.KEY),
    then_event=CompositeEvent([...]),
    else_event=ShowMessageEvent("The door is locked.")
)
```

If the hero has the key, run the "then" events. Otherwise, show the locked message.

**Success Path:**
```python
then_event=CompositeEvent([
    RemoveItemEvent(TileID.KEY),
    ShowMessageEvent("You unlocked the door."),
    ChangeTileEvent(tileset.get_tile(TileID.BUILDING_DOOR_OPEN)),
    DeactivateEvent()
])
```

When successful:
1. Remove the key from inventory
2. Show success message
3. Change the door to open
4. Deactivate the event (so it doesn't trigger again)

**Important Settings:**
```python
events[x+1][y].run_once = False
```

We set `run_once` to `False` so the player can try multiple times if they don't have the key yet!

## Using Different Door Types

Now when creating buildings in the town, we can specify different door types:

```python
class TownTilemapFactory(TilemapFactory):
    def create(self) -> 'Tilemap':
        # ... setup code ...
        
        # Create 4 buildings with different door types
        self.create_building(tiles, events, 2, 2, 4, 4, door_type=DoorType.SIMPLE)
        self.create_building(tiles, events, 7, 2, 3, 3, door_type=DoorType.LOCKED)
        self.create_building(tiles, events, 2, 7, 3, 3, door_type=DoorType.CLOSED)
        self.create_building(tiles, events, 7, 7, 3, 3, door_type=DoorType.OPEN)
        
        return Tilemap(tiles, events)
```

## Testing the Locked Door

Run your game and try the following:

1. **Without the key:** Walk up to the locked door (building at position 7, 2). You should see the message "The door is locked."

2. **Get the key:** Find and pick up the key in the forest.

3. **With the key:** Return to the locked door and walk into it. You should see "You unlocked the door." and the door opens! The key disappears from your inventory.

4. **After unlocking:** The door stays open and won't trigger again.

## What We Accomplished

In this lesson, we:
- Created a `Condition` system for checking game state
- Implemented `HasItemCondition` to check inventory
- Created `IfEvent` for conditional logic in events
- Added `DeactivateEvent` to prevent events from re-triggering
- Implemented item removal from inventory
- Created a `DoorType` enum for different door behaviors
- Built a locked door that requires a key and consumes it when opened

This conditional event system is incredibly powerful! You can now create puzzles, quests, and interactive elements that respond to the player's inventory, stats, or any other game state. The same pattern can be used for locked chests, NPC dialogue choices, quest requirements, and much more!