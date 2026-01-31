# 5.1 – Laying the Ground for Events

Until now, our maps were completely static: a tile was a tile, and nothing on the map could *do* anything.

In this lesson, we’ll take the first step toward interactive maps by introducing an **event layer**, inspired by RPG Maker XP.

This lesson is intentionally **foundational**:

* Events won’t do much *yet*
* There will be no interaction logic
* We are only building the **structure**

Think of this as laying the rails before running the train.

---

## What We’re Building

By the end of this lesson, we will have:

* A second layer on top of the tilemap: the **event layer**
* An `Event` interface (empty for now)
* An `EventTile` that can:

  * draw itself on top of tiles
  * block movement
* A visible **door drawn as an event**, not a tile

No behavior yet — that comes later.

---

## Step 1 — Introducing the Event concept

Create a new file:

```
game/tilemap/event.py
```

Add the following code:

```python
from abc import ABC
from typing import Optional

from tilemap.tileset import Tile


class Event(ABC):
    """
    Base class for all future events (doors, NPCs, switches, chests).
    For now, it acts only as a marker.
    """
    pass
```

At this stage, `Event` is just a **conceptual placeholder**.
Its real power will come in later lessons.

---

## Step 2 — Creating EventTile (the event layer cell)

In the same file (`event.py`), add:

```python
class EventTile:
    def __init__(self, tile: Optional[Tile] = None, event: Optional[Event] = None):
        self.event = event
        self.tile = tile
```

An `EventTile` represents **one cell** in the event layer.

Key idea:

* A tilemap cell always exists
* An event cell *may* exist
* Events are optional

---

## Step 3 — Introducing `@property`

Now add this method to `EventTile`:

```python
    @property
    def is_walkable(self):
        if self.tile is None:
            return True
        return self.tile.is_walkable
```

### Why `@property`?

Normally, we’d write:

```python
event_tile.is_walkable()
```

But with `@property`, we can write:

```python
event_tile.is_walkable
```

This gives us:

* **Cleaner code**
* **Readable intent**
* The illusion of an attribute, backed by logic

This is perfect for *domain concepts* like walkability.

Later, this property can:

* Check event state
* Ask the event if it blocks movement
* Combine multiple rules

Without changing the calling code.

---

## Step 4 — Extending Tilemap to support events

Open:

```
game/tilemap/tilemap.py
```

At the top, add the import:

```python
from tilemap.event import EventTile
```

---

### Update the Tilemap constructor

Replace the constructor with:

```python
class Tilemap:
    def __init__(self, tiles: List[List[Tile]], events: List[List[EventTile]] | None = None):
        self.tiles = tiles
        self.width = len(tiles)
        self.height = len(tiles[0])

        if events is None:
            self.events = [[EventTile() for _ in range(self.height)] for _ in range(self.width)]
        else:
            assert len(events) == self.width and len(events[0]) == self.height
            self.events = events
```

What this does:

* Allows maps **with or without events**
* Automatically creates an empty event layer when none is provided
* Keeps tiles and events perfectly aligned

---

## Step 5 — Update collision logic to include events

Still in `Tilemap`, update `is_blocked`:

```python
def is_blocked(self, new_x: int, new_y: int):
    if not self.has_tile(new_x, new_y):
        return True

    if not self.get_tile(new_x, new_y).is_walkable:
        return True

    if not self.events[new_x][new_y].is_walkable:
        return True

    return False
```

Important detail:

* **Tiles are checked first**
* **Events are checked second**

This mirrors RPG Maker’s logic:

> Terrain blocks first, then events.

---

## Step 6 — Rendering events on top of tiles

Open:

```
game/main.py
```

### Import EventTile

At the top, add:

```python
from tilemap.event import EventTile
```

---

### Update `render`

Change:

```python
self.update_tilemap(tilemap.width, tilemap.height, tilemap.tiles)
```

To:

```python
self.update_tilemap(tilemap.width, tilemap.height, tilemap.tiles, tilemap.events)
```

---

### Update `update_tilemap`

Replace the method signature:

```python
def update_tilemap(self, width: int, height: int, tiles: List[List[Tile]]):
```

With:

```python
def update_tilemap(self, width: int, height: int, tiles: List[List[Tile]], events: List[List[EventTile]]):
```

---

### Draw tiles and events separately

Replace the drawing logic with:

```python
for i in range(width):
    for j in range(height):
        self.draw_tile(tiles[i][j], i, j)

        event_tile = events[i][j]
        if event_tile.tile is not None:
            self.draw_tile(event_tile.tile, i, j)
```

---

### Extract `draw_tile`

Add this helper method:

```python
def draw_tile(self, tile: Tile, world_x: int, world_y: int):
    if tile.id != -1:
        tile_img = self.sprite_sheet.get_sprite(tile.id)
        x, y = self.to_screen_coords(world_x, world_y)
        self.canvas.create_image(x, y, image=tile_img, anchor='nw')
```

This makes rendering logic:

* Reusable
* Easier to extend later (animations, transparency, etc.)

---

## Step 7 — Adding a door as an event (graphics only)

Now we create a **visual event**, without behavior.

Open:

```
game/tilemap/tilemap.py
```

Inside `TownTilemapFactory.create`, initialize events alongside tiles:

```python
tiles = []
events = []
```

Inside the loop:

```python
row = []
event_row = []

...
row.append(tileset.get_tile(id))
event_row.append(EventTile())

tiles.append(row)
events.append(event_row)
```

---

### Modify `create_building`

Update the method signature:

```python
def create_building(self, tiles, events, x, y, width, height, is_door_open=False, can_open_door=False):
```

Replace the door logic with:

```python
if can_open_door:
    tiles[x+1][y] = tileset.get_tile(TileID.EMPTY)
    events[x+1][y].tile = tileset.get_tile(TileID.BUILDING_DOOR_CLOSED)
else:
    id = TileID.BUILDING_DOOR_OPEN if is_door_open else TileID.BUILDING_DOOR_CLOSED
    tiles[x+1][y] = tileset.get_tile(id)
```

What’s happening here:

* The **tile layer is empty**
* The **event layer draws the door**
* Movement logic already respects it

This is the key architectural shift.

---

## Step 8 — Returning Tilemap with events

Finally, return the tilemap like this:

```python
return Tilemap(tiles, events)
```

---

## What We Accomplished

In this lesson, we:

* Introduced an **event layer** on top of the tilemap
* Created the `Event` abstraction
* Implemented `EventTile` as a layered cell
* Learned and applied the `@property` decorator
* Updated collision logic to respect events
* Rendered events visually on top of tiles
* Added a door as an event (graphics only)

At this point, your map is no longer static — it’s **ready for interaction**.

---

## What Comes Next

In the next lesson, we’ll:

* Attach real behavior to events
* Open doors on interaction
* Introduce event state
* Move closer to RPG Maker–style event pages

This foundation will carry *everything* that comes after.
