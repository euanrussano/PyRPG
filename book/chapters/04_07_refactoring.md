# 4.7 – Restructuring the Project into Modules

Up to this point, our game has grown organically: new files were added as new features appeared. This is completely normal — and exactly how most projects start.

However, as the codebase grows, a **flat folder full of Python files quickly becomes confusing**. In this lesson, we’ll refactor the project into **clear modules**, without changing any game behavior.

This is a **pure refactoring lesson**:

* No new features
* No gameplay changes
* Only better structure and cleaner imports

---

## Why Restructure Now?

Before this lesson, our `game/` folder looked something like this:

```
game/
├── hero.py
├── session.py
├── world.py
├── tilemap.py
├── tileset.py
├── spritesheet.py
├── main.py
...
```

Problems with this structure:

* All concepts live at the same level
* Rendering, world logic, and game rules are mixed
* Imports become fragile as files increase
* It’s hard to explain “what belongs where”

This lesson fixes that by grouping files into **meaningful modules**.

---

## Step 1 — Turn `game/` into a Python package

First, we tell Python that `game/` is a package.

Create this file:

```
game/__init__.py
```

It can be empty. Its presence alone is enough.

Why this matters:

* Python now treats `game/` as a module root
* Absolute imports inside the project become reliable

---

## Step 2 — Create module folders

Inside `game/`, create the following folders:

```
game/
├── core/
├── graphics/
├── tilemap/
```

Now add an empty `__init__.py` file inside each one:

```
game/core/__init__.py
game/graphics/__init__.py
game/tilemap/__init__.py
```

At this point, we have **three new modules**:

* `core` → game rules and domain logic
* `graphics` → rendering and visuals
* `tilemap` → tiles, maps, and terrain

---

## Step 3 — Move core game logic into `core/`

Now we move the files that define *how the game works*.

### Move the hero

```bash
mv game/hero.py game/core/hero.py
```

### Move the session

```bash
mv game/session.py game/core/session.py
```

### Move the world

```bash
mv game/world.py game/core/world.py
```

At this point, the `core` module contains:

* `Hero`
* `World`
* `GameSession`

---

## Step 4 — Fix imports inside `core/session.py`

Open:

```
game/core/session.py
```

### Update tilemap imports

Change:

```python
from tilemap import Tilemap, TilemapLoader
```

To:

```python
from tilemap.tilemap import Tilemap, TilemapLoader
```

### Update world imports (relative import)

Change:

```python
from world import Location, World
```

To:

```python
from .world import Location, World, WorldFactory
```

### Update hero import

Change:

```python
from hero import Hero
```

To:

```python
from .hero import Hero
```

### Update world creation

Find:

```python
self.world = World.create()
```

Replace with:

```python
self.world = WorldFactory().create()
```

Now `GameSession` uses the factory instead of constructing the world itself.

---

## Step 5 — Fix imports inside `core/world.py`

Open:

```
game/core/world.py
```

Change the tilemap import at the top:

```python
from tilemap import Tilemap, ForestTilemapFactory, TownTilemapFactory
```

To:

```python
from tilemap.tilemap import Tilemap, ForestTilemapFactory, TownTilemapFactory
```

No other changes are required here.

---

## Step 6 — Move graphics-related code

Rendering code belongs in its own module.

Move the spritesheet file:

```bash
mv game/spritesheet.py game/graphics/spritesheet.py
```

No internal changes are needed — only imports elsewhere will change.

---

## Step 7 — Move tile-related code into `tilemap/`

Now we group everything related to tiles and maps.

### Move files

```bash
mv game/tile_ids.py game/tilemap/tile_ids.py
mv game/tilemap.py game/tilemap/tilemap.py
mv game/tileset.py game/tilemap/tileset.py
```

---

## Step 8 — Fix imports inside `tilemap/tilemap.py`

Open:

```
game/tilemap/tilemap.py
```

### Update imports

Change:

```python
from tile_ids import TREES, TileID
from tileset import Tile, Tileset, get_tileset
```

To:

```python
from .tile_ids import TREES, TileID
from .tileset import Tile, Tileset, get_tileset
```

The leading `.` means:

> “Import from the same module folder.”

This is a **relative import**, and it only works because `tilemap/` is now a package.

---

## Step 9 — Fix imports inside `tilemap/tileset.py`

Open:

```
game/tilemap/tileset.py
```

Change:

```python
from tile_ids import TileID
```

To:

```python
from .tile_ids import TileID
```

---

## Step 10 — Update imports in `main.py`

Finally, we update the entry point of the game.

Open:

```
game/main.py
```

### Replace old flat imports

Change:

```python
from hero import Hero
from session import GameSession, IGameSession
from spritesheet import Spritesheet
from tilemap import Tile, TilemapLoader
from tileset import Tileset, get_tileset
from world import Location
```

To:

```python
from core.hero import Hero
from core.session import GameSession, IGameSession
from graphics.spritesheet import Spritesheet
from tilemap.tilemap import Tile
from tilemap.tileset import get_tileset
from core.world import Location
```

Now all imports clearly reflect **where each concept lives**.

---

## Step 11 — Remove obsolete developer script

The file `generate_forest.py` was a temporary development tool and is no longer needed.

Delete it:

```bash
rm game/generate_forest.py
```

---

## How to Run the Project (Important!)

After this refactor, **do not run internal files directly**.

From inside the `game/` folder, always run:

```bash
python main.py
```

This ensures Python understands:

* `game` is the project root
* `core`, `tilemap`, and `graphics` are packages

---

## What We Accomplished

In this lesson, we:

* Turned the project into a proper Python package
* Grouped files into meaningful modules
* Introduced absolute and relative imports correctly
* Cleaned up fragile flat imports
* Improved readability without changing behavior

Your project is now **structured like a real-world codebase**, while still being simple enough for beginners.

From this point on, adding new systems will feel natural instead of chaotic.
