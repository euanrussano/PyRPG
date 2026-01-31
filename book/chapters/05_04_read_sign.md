# 5.4 – Reading Signs

In this lesson, we’re going to add **signs** to our world — simple objects the player can read by bumping into them.

Signs are special because, unlike doors or chests:

* They **don’t disappear**
* They **can be triggered multiple times**
* They **only show a message**

This makes them perfect for introducing **repeatable events** and a very important Python concept: **`@staticmethod`**.

By the end of this lesson, your player will be able to walk up to a sign and read it as many times as they want.

---

## What Makes Signs Different?

Let’s compare signs to the events we already have:

| Event Type | Triggered Once? | Changes Tile? | Gives Reward? |
| ---------- | --------------- | ------------- | ------------- |
| Door       | ✅ Yes           | ✅ Yes         | ❌ No          |
| Chest      | ✅ Yes           | ✅ Yes         | ✅ Gold        |
| **Sign**   | ❌ No            | ❌ No          | ❌ No          |

This means:

* We **must not delete the event** after triggering
* The event should run **every time the player bumps into it**

---

## Step 1 – Allow Events to Run More Than Once

Open **`game/tilemap/event.py`** and modify the `EventTile` class.

### Before

```python
class EventTile:
    def __init__(self, tile: Optional[Tile] = None, event: Optional[Event] = None):
        self.tile = tile
        self.__event = None
```

### After

```python
class EventTile:
    def __init__(
        self,
        tile: Optional[Tile] = None,
        event: Optional[Event] = None,
        run_once: bool = True
    ):
        self.tile = tile
        self.__event = None
        self.run_once = run_once
```

### What did we add?

* `run_once` controls **event lifetime**
* Default is `True`, so existing behavior stays the same
* Signs will set this to `False`

---

### Update the `trigger` Method

Still in `event.py`, update `trigger`:

```python
def trigger(self, session):
    if self.__event is not None:
        self.__event.trigger(session)

    # remove event only if it should run once
    if self.run_once:
        self.__event = None
```

Now:

* Doors & chests still disappear
* Signs stay forever

---

## Step 2 – Add a Sign Tile

Open **`game/tilemap/tile_ids.py`** and add a new tile ID:

```python
SIGN = 31
```

Then open **`game/tilemap/tileset.py`** and register it:

```python
# Sign (non-walkable)
(TileID.SIGN, False),
```

This makes signs:

* Visible
* Solid (player can’t walk through them)

---

## Step 3 – Introduce `@staticmethod`

Now we’ll clean up our factory code and introduce a **new Python concept**.

Open **`game/tilemap/tilemap.py`** and find this method:

```python
def create_empty_events(self, width: int, height: int):
```

### Change it to:

```python
@staticmethod
def create_empty_events(width: int, height: int) -> List[List[EventTile]]:
    events = []
    for _ in range(width):
        row = []
        for _ in range(height):
            row.append(EventTile())
        events.append(row)
    return events
```

---

### What Is `@staticmethod`?

A **static method**:

* Belongs to the **class**, not an instance
* Does **not use `self`**
* Is called like this:

```python
TilemapFactory.create_empty_events(10, 10)
```

This is perfect here because:

* The method does not depend on factory state
* It’s just a utility function
* It avoids accidental misuse of `self`

This is **cleaner, safer, and easier to teach**.

---

## Step 4 – Place a Sign in the Forest

Open **`game/tilemap/tilemap.py`** and update `ForestTilemapFactory`.

### Update the method signature:

```python
def create(self, place_random_chests: bool = False, place_sign: bool = False) -> Tilemap:
```

### Inside the tile loop, add:

```python
elif place_sign:
    if random.random() < 0.1:
        events[i][j].run_once = False
        events[i][j].tile = tileset.get_tile(TileID.SIGN)
        event = ShowMessageEvent("You found a sign!")
        events[i][j].set_event(event)

        # only place one sign
        place_sign = False
```

### What’s happening here?

* We place **exactly one sign**
* It uses `run_once = False`
* It shows a message every time the player bumps into it

---

## Step 5 – Enable Signs in the World

Open **`game/core/world.py`** and update the forest creation:

```python
farm = Location(
    "Forest",
    1,
    0,
    forestFactory.create(place_sign=True)
)
```

Now the forest map contains:

* Trees
* A sign
* Interactive behavior

---

## What We Accomplished

In this lesson, we:

* Created **repeatable events**
* Introduced the **`@staticmethod` decorator**
* Added **sign tiles**
* Implemented **non-destructive interactions**
* Expanded our event system without breaking existing logic

Most importantly, we now have an **event system flexible enough** to support:

* NPCs
* Dialog trees
* Quests
* Cutscenes

![Signs](images/05_04_sign.png)

---

## Design Insight

Signs are a great example of **behavior over data**.

The tile itself does nothing special.
The **event attached to it** defines how the game reacts.

This is exactly how professional RPG engines work — including RPG Maker.

