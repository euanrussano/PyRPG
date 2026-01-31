# 5.2 – Opening Doors

In the previous lesson, we introduced the idea of **events** as a separate layer on top of the tilemap. We were able to *draw* doors as events, but they didn’t actually do anything yet.

In this lesson, we’re going to take the next big step: **making doors open**.

By the end of this lesson:

* Bumping into a closed door will open it
* The door graphic will change from closed to open
* A message will be recorded in the hero’s diary

Along the way, we’ll introduce a few important programming concepts in a very practical context:

* private attributes
* the `@property` decorator
* composing behavior from small pieces (Composite pattern)
* building complex objects step by step (Builder idea)

---

## What Does “Opening a Door” Really Mean?

Before writing any code, let’s clarify what *opening a door* means in our game.

From the player’s perspective:

* The door blocks movement
* The player bumps into it
* The door opens
* The player gets feedback (“You opened the door”)

From the engine’s perspective, this means:

1. The **event tile** changes its visual tile
2. The event runs **only once**
3. A message is sent to the game session

So opening a door is not *one action* — it’s **several small actions combined**.

---

## Step 1 – Making events explicit with an Event base class

Open the file:

```
game/tilemap/event.py
```

Replace the empty `Event` class with the following:

```python
from abc import ABC, abstractmethod
from typing import Optional

class Event(ABC):
    def __init__(self):
        self.owner: Optional['EventTile'] = None

    @abstractmethod
    def trigger(self, session):
        pass
```

### Why do we need this class?

Every event in the game:

* lives on an `EventTile`
* reacts when something happens (movement, interaction, etc.)

By defining a common `trigger(session)` method, we ensure that *all* events behave in a predictable way.

---

## Step 2 – Keeping events private inside EventTile

Still in `event.py`, update `EventTile` so that the event is stored **privately**:

```python
class EventTile:
    def __init__(self, tile=None, event: Optional[Event] = None):
        self.tile = tile
        self.__event = None

        if event is not None:
            self.set_event(event)
```

### Why make `__event` private?

Using a private attribute (`__event`) means:

* Other parts of the code cannot modify the event directly
* All access goes through `EventTile`
* The tile stays in control of its own behavior

This helps prevent subtle bugs later.

---

## Step 3 – Using @property for walkability

Add this to `EventTile`:

```python
@property
def is_walkable(self):
    if self.tile is None:
        return True
    return self.tile.is_walkable
```

### What is `@property`?

The `@property` decorator lets us access a method **like a normal attribute**:

```python
event_tile.is_walkable
```

instead of:

```python
event_tile.is_walkable()
```

This is ideal for concepts like:

* “Can I walk here?”
* “Is this tile blocked?”

Later, we can add more logic inside this property without changing any calling code.

---

## Step 4 – Attaching and triggering events

Now add the remaining methods to `EventTile`:

```python
def set_event(self, event: Event):
    self.__event = event
    self.__event.owner = self

def has_event(self):
    return self.__event is not None

def trigger(self, session):
    if self.__event is not None:
        self.__event.trigger(session)

    # for now, events run only once
    self.__event = None
```

Important design choice:

* Events are **one-shot**
* After triggering, the event is removed

This matches typical RPG behavior for doors, chests, and signs.

---

## Step 5 – Small, focused events

Instead of creating one big “door event”, we’ll build **small events that do one thing well**.

### Changing a tile

Add this class to `event.py`:

```python
class ChangeTileEvent(Event):
    def __init__(self, tile):
        super().__init__()
        self.tile = tile

    def trigger(self, session):
        if self.owner:
            self.owner.tile = self.tile
```

This event:

* knows *what* tile to change to
* uses `owner` to know *where* it lives

---

### Showing a message

Now add:

```python
class ShowMessageEvent(Event):
    def __init__(self, message: str):
        super().__init__()
        self.message = message

    def trigger(self, session):
        session.add_message(self.message)
```

This event:

* doesn’t change the world
* communicates feedback to the player

---

## Step 6 – Combining events with CompositeEvent

Sometimes, one action should trigger **multiple effects**.

For example:

* open the door
* show a message

Instead of creating a special “DoorEvent”, we combine existing events.

Add this class:

```python
from typing import List

class CompositeEvent(Event):
    def __init__(self, events: List[Event]):
        super().__init__()
        self.events = events

    def trigger(self, session):
        for event in self.events:
            event.owner = self.owner
            event.trigger(session)
```

### What’s happening here?

A `CompositeEvent`:

* behaves like a normal event
* internally triggers multiple smaller events

This idea is known as the **Composite pattern**, but you don’t need to memorize the name — just remember:

> *Complex behavior is built from simple pieces.*

---

## Step 7 – Creating a door event in the tilemap factory

Open:

```
game/tilemap/tilemap.py
```

Inside `TownTilemapFactory.create_building`, update the door logic:

```python
if can_open_door:
    tiles[x+1][y] = tileset.get_tile(TileID.EMPTY)
    events[x+1][y].tile = tileset.get_tile(TileID.BUILDING_DOOR_CLOSED)

    event = CompositeEvent([
        ChangeTileEvent(tileset.get_tile(TileID.BUILDING_DOOR_OPEN)),
        ShowMessageEvent("You opened the door")
    ])

    events[x+1][y].set_event(event)
```

What this does:

* the tile layer stays empty
* the event layer draws the closed door
* bumping into the door opens it and shows a message

---

## Step 8 – Triggering events from movement

Open:

```
game/core/session.py
```

Add this method:

```python
def try_trigger_event(self, x: int, y: int):
    tilemap = self.current_location.tilemap
    event_tile = tilemap.get_event_tile(x, y)
    if event_tile.has_event():
        event_tile.trigger(self)
```

This allows movement to activate events naturally.

---

## Step 9 – Recording messages in the hero’s diary

Open:

```
game/core/hero.py
```

Add:

```python
self.__diary = []

@property
def diary(self):
    return self.__diary

def add_diary_entry(self, entry):
    self.__diary.append(entry)
```

The diary:

* stores game history
* decouples game logic from the UI
* makes testing easier

---

## Step 10 – Displaying the diary

In `GameSession`:

```python
def add_message(self, msg: str):
    self.hero.add_diary_entry(msg)
    self.view.update_diary(self.hero)
```

And in `GameScreen`:

```python
def update_diary(self, hero):
    self.diary_listbox.delete(0, tk.END)
    for entry in hero.diary:
        self.diary_listbox.insert(tk.END, entry)
```

Now the player gets immediate feedback when opening a door.

---

## What We Accomplished

In this lesson, we:

* Created real, interactive doors
* Used private attributes to protect internal state
* Learned how `@property` improves readability
* Built behavior by composing small events
* Added player feedback through a diary system

At this point, your game world is no longer static — **it reacts to the player**.

In the next lesson, we’ll reuse this same system to open chests and reward items, without changing the event architecture at all.
