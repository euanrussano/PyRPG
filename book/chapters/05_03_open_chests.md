
# 5.3 – Opening Chests

In the previous lesson, we learned how to open doors using events. We combined small actions—changing a tile and showing a message—into a single interaction.

In this lesson, we’ll reuse **the exact same event system** to implement something new: **treasure chests**.

By the end of this lesson:

* Chests will appear randomly on the farm
* The player can open a chest by bumping into it
* Opening a chest gives **random gold (1–3)**
* Each chest can only be opened once

Most importantly, we’ll do this **without changing the event architecture**. That’s how we know our design is working.


## What Is a Chest in Game Terms?

Let’s describe a chest in terms of game behavior, not graphics.

A chest:

* Blocks movement
* Has a visible tile (closed chest)
* Triggers when the player bumps into it
* Gives a reward
* Disappears after being opened

Notice something important:
**A chest is just an event tile**, exactly like a door.

So instead of inventing something new, we’ll *compose existing events*.

---

## Step 1 – Giving the Hero Gold

Before a chest can give gold, the hero needs a way to receive it.

Open:

```
game/core/hero.py
```

Add this method to the `Hero` class:

```python
def add_gold(self, amount):
    self.gold += amount
```

This keeps all hero state changes inside the `Hero` class, which is good practice.

---

## Step 2 – Letting the Session Handle Gold Changes

The UI should update whenever gold changes, so we route this through the game session.

Open:

```
game/core/session.py
```

Add:

```python
def add_gold(self, amount: int):
    self.hero.add_gold(amount)
    self.view.update_hero_stats(self.hero)
```

Now events don’t need to know anything about the UI—they just talk to the session.

---

## Step 3 – Creating a GiveGoldEvent

Now we create a new event type.

Open:

```
game/tilemap/event.py
```

Add the following class:

```python
class GiveGoldEvent(Event):
    def __init__(self, amount: int):
        super().__init__()
        self.amount = amount

    def trigger(self, session):
        session.add_gold(self.amount)
```

This event does one thing, and one thing only:

* gives gold to the player

Small, focused events are easy to reuse and combine.

---

## Step 4 – Adding Randomness (RNG)

Chests should feel rewarding and unpredictable.

Python gives us randomness via the `random` module:

* `random.random()` → a float between 0 and 1
* `random.randint(a, b)` → a random integer between `a` and `b`

We’ll use this to:

* decide **where chests appear**
* decide **how much gold they give**

---

## Step 5 – Placing Random Chests in the Forest

Open:

```
game/tilemap/tilemap.py
```

Update `ForestTilemapFactory.create` so it can optionally place chests:

```python
class ForestTilemapFactory(TilemapFactory):
    def create(self, place_random_chests: bool = False) -> 'Tilemap':
        random.seed(1)

        width = 10
        height = 10
        tileset: Tileset = get_tileset()
        tiles = []
        events = self.create_empty_events(width, height)
```

We use `random.seed(1)` so results are predictable during development.
This is very helpful when debugging.

---

### Generating tiles and chests

Inside the nested loop, update the logic:

```python
for i in range(width):
    row = []
    for j in range(height):
        id = TileID.EMPTY

        if random.random() < 0.3:
            id = random.choice(TREES)

        elif place_random_chests:
            if random.random() < 0.1:
                gold_amount = random.randint(1, 3)

                events[i][j].tile = tileset.get_tile(TileID.CHEST_CLOSED)

                event = CompositeEvent([
                    ShowMessageEvent("You found a chest!"),
                    GiveGoldEvent(gold_amount),
                    ShowMessageEvent(f"You got {gold_amount} gold"),
                    ChangeTileEvent(tileset.get_tile(TileID.EMPTY)),
                ])

                events[i][j].set_event(event)

        row.append(tileset.get_tile(id))
    tiles.append(row)
```

Let’s break this down:

### Why this works

* **10% chance** to place a chest
* Chest tile is drawn in the *event layer*
* Gold amount is randomly chosen (1–3)
* The event:

  1. Shows a message
  2. Gives gold
  3. Shows another message
  4. Removes the chest visually

All of this happens **once**, because events are consumed after triggering.

---

## Step 6 – Returning the Tilemap with Events

At the end of `create`, return:

```python
return Tilemap(tiles, events)
```

Now the forest map supports interactive chests.

---

## Step 7 – Enabling Chests in the World

Open:

```
game/core/world.py
```

Update the world factory:

```python
forest = Location("Farm", 0, -1, forestFactory.create(place_random_chests=True))
```

Now the farm contains randomly scattered chests.

---

## Step 8 – Testing the Result

Run the game and move the hero onto the farm.

You should observe:

* Closed chests scattered across the map
* Bumping into a chest:

  * Opens it
  * Adds gold
  * Logs messages in the diary
  * Removes the chest

All of this happens using the **same event system** we built earlier.

![Open Chests](images/05_03_open_chests.png)

---

## What We Accomplished

In this lesson, we:

* Reused the event system without modifying it
* Introduced randomness (RNG)
* Created a reusable `GiveGoldEvent`
* Built one-time treasure chests
* Combined multiple behaviors using `CompositeEvent`

Most importantly, we proved that our design scales naturally.

In the next lesson, we’ll use this same approach to create **signs and readable objects**, showing that events don’t always have to change the world—sometimes they just communicate information.
