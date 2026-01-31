Perfect, this fits *exactly* as a continuation of the previous lessons.
Below is **Lesson 4.6**, written as a **hands-on coding tutorial**, guiding the reader step by step and explicitly mapping to the diff you shared.

---

# 4.6 – Improving the World: Factory and Guard Clauses

In the previous lesson, we connected our maps and allowed the hero to move between them. Our world is now functional — but the code can be improved.

In this lesson, we’ll focus on **code quality and design**, by:

* Introducing a **World Factory**
* Adding **guard clauses**
* Replacing `None`-based logic with a **domain-specific exception**

These changes don’t add new gameplay features, but they make the code safer, clearer, and easier to extend — exactly what we want in a growing project.

---

## Step 1 — Create a domain-specific error for missing locations

So far, our `World` class returned `None` when a location didn’t exist. This forces every caller to remember to check for `None`, which is error-prone.

Instead, we’ll introduce a **custom exception** that clearly expresses what went wrong.

Open:

```
game/world.py
```

Just below the `Location` class, add this new exception:

```python
class LocationNotFoundError(Exception):
    def __init__(self, x: int, y: int):
        super().__init__(f"Location ({x}, {y}) does not exist in the world.")
        self.x = x
        self.y = y
```

Why this is important:

* The error name explains *exactly* what failed
* The message is meaningful for debugging
* The coordinates are preserved for logging or inspection

This is a **domain error**, not a generic `ValueError`.

---

## Step 2 — Add a guard method: `has_location`

Before throwing errors, it’s often useful to have a **safe check**.

Still in `game/world.py`, inside the `World` class, add:

```python
def has_location(self, x: int, y: int) -> bool:
    for location in self.locations:
        if location.x == x and location.y == y:
            return True
    return False
```

This method answers a simple question:

> “Does a location exist at these world coordinates?”

It will be used as a **guard clause** in the next step.

---

## Step 3 — Make `get_location` strict and fail fast

Now we refactor `get_location` so it **never returns `None`**.

Find the existing method:

```python
def get_location(self, x: int, y: int) -> Location | None:
```

Replace it entirely with:

```python
def get_location(self, x: int, y: int) -> Location:
    if not self.has_location(x, y):
        raise LocationNotFoundError(x, y)

    for location in self.locations:
        if location.x == x and location.y == y:
            return location

    raise LocationNotFoundError(x, y)
```

What changed:

* The return type is now **always `Location`**
* Missing locations cause an immediate, explicit failure
* No silent `None` values

This is a classic **fail-fast design**.

---

## Step 4 — Remove unused and unsafe APIs

Now that `get_location` is strict, some older methods are no longer needed.

In `game/world.py`, delete the following methods completely:

```python
def get_location_by_id(self, id: int) -> Location | None:
    if id < 0 or id >= len(self.locations):
        return None
    return self.locations[id]
```

This method:

* Encourages fragile, index-based access
* Breaks as soon as the world layout changes

From now on, **world coordinates define everything**.

---

## Step 5 — Extract world creation into a factory

Currently, world creation logic lives inside the `World` class as a static method. This mixes **world behavior** with **world construction**.

We’ll fix that by introducing a `WorldFactory`.

Still in `game/world.py`, remove the old static method:

```python
@staticmethod
def create() -> 'World':
    ...
```

Then, **below the `World` class**, add:

```python
class WorldFactory:
    def create(self) -> World:
        world = World()

        forestFactory = ForestTilemapFactory()
        townFactory = TownTilemapFactory()

        forest = Location("Forest", 0, -1, forestFactory.create())
        town = Location("Town", 0, 0, townFactory.create())
        farm = Location("Farm", 1, 0, forestFactory.create())

        world.add_location(forest)
        world.add_location(town)
        world.add_location(farm)

        return world
```

Why this matters:

* `World` now focuses only on **world rules**
* `WorldFactory` focuses on **how the world is built**
* Multiple worlds can be created later (tests, scenarios, save files)

---

## Step 6 — Why guard clauses matter

Let’s look at this line again:

```python
if not self.has_location(x, y):
    raise LocationNotFoundError(x, y)
```

This is a **guard clause**.

Instead of nesting logic deeply or returning invalid values, we:

* Check invalid conditions early
* Exit immediately with a clear error
* Keep the “happy path” clean and readable

This style will appear again and again in future systems.

---

## What We Accomplished

In this lesson, we:

* Introduced a custom `LocationNotFoundError`
* Replaced `None`-based APIs with fail-fast methods
* Added `has_location` as a guard clause
* Removed fragile ID-based world access
* Extracted world construction into `WorldFactory`
* Cleaned up responsibilities inside the `World` class

Our world code is now **safer, clearer, and more scalable**.

In the next lesson, we’ll start taking advantage of this improved structure to add more complex world behavior without turning the code into a mess.
