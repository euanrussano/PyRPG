# 4.4 – Moving Between Maps

In this lesson, we’ll make our world feel bigger by allowing the hero to move **between maps** automatically.

**Goal:**
When the hero walks into the border of the current map and tries to advance:

* If there is a map on that side → enter it
* If there is no map → stay where you are

No dropdown menus. No teleport buttons. Just walking.

---

## Step 1 — Remove the map selection dropdown from the UI

We previously had a temporary dropdown that allowed switching maps manually. Now that maps change by walking, we don’t need it.

Open:

```
game/main.py
```

Find the method:

```python
def create_left_panel(self, parent):
```

Inside it, delete this entire block:

```python
map_selection_label = tk.Label(parent, text="Select map:", **label_config)
map_selection_label.grid(row=5, column=0, **grid_config)
map_options = ["0", "1", "2"]
self.map_selection = tk.StringVar()
self.map_selection.set(map_options[0])
map_selection_menu = tk.OptionMenu(parent, self.map_selection, *map_options, command=self.change_map)
map_selection_menu.grid(row=5, column=1, **grid_config)
```

Then also delete the `change_map` method completely:

```python
def change_map(self, event):
    loc_id = int(self.map_selection.get())
    self.session.change_location(loc_id)
```

✅ Now the UI no longer contains manual map switching.

---

## Step 2 — Adjust hero rendering Y coordinate (small bug fix)

Still in:

```
game/main.py
```

Find this method:

```python
def world_to_canvas(self, world_x, world_y):
```

Change:

```python
y = height - world_y * self.tile_size
```

To:

```python
y = height - world_y * self.tile_size - self.tile_size
```

This fixes the hero being drawn one tile too low because our tile origin is top-left.

---

## Step 3 — Update hero stats function to receive the Hero object

In `game/main.py`, find:

```python
def update_hero_stats(self, name: str, level: int, xp: int, gold: int, energy: int):
```

Replace the entire function with:

```python
def update_hero_stats(self, hero: Hero):
    self.hero_name_label.config(text=f"{hero.name}")
    self.hero_level_label.config(text=f"{hero.level}")
    self.hero_xp_label.config(text=f"{hero.xp}")
    self.hero_gold_label.config(text=f"{hero.gold}")
    self.hero_energy_label.config(text=f"{hero.energy}")
```

Now we pass around the hero object instead of multiple parameters.

---

## Step 4 — Remove `change_location` from the session interface

Open:

```
game/session.py
```

In the interface `IGameSession`, delete this abstract method:

```python
@abstractmethod
def change_location(self, loc_id: int):
    pass
```

We no longer switch maps by ID manually.

---

## Step 5 — Render hero stats when the game starts

In:

```
game/session.py
```

Find:

```python
def start(self):
    self.view.render(self.current_location, self.hero)
```

Change it to:

```python
def start(self):
    self.view.update_hero_stats(self.hero)
    self.view.render(self.current_location, self.hero)
```

Now the UI shows hero info immediately.

---

## Step 6 — Detect when the hero is trying to leave the current map

Now we implement the actual “moving between maps”.

In `game/session.py`, find:

```python
def move_hero(self, dx: int, dy: int):
```

After computing:

```python
new_x = self.hero.x + dx
new_y = self.hero.y + dy
```

Add these checks:

```python
if new_x < 0 or new_x >= self.current_location.tilemap.width:
    self._try_change_location(dx, dy)
    return
elif new_y < 0 or new_y >= self.current_location.tilemap.height:
    self._try_change_location(dx, dy)
    return
```

This means:

* If hero tries to move outside X range → attempt map change
* If hero tries to move outside Y range → attempt map change

---

## Step 7 — Add `_try_change_location` helper method

Still in `game/session.py`, **add this method inside `GameSession`** (put it near the bottom, after `move_right`, for example):

```python
def _try_change_location(self, dx: int, dy: int) -> None:
    location = self.current_location
    hero = self.hero

    new_global_x = location.x + dx
    new_global_y = location.y + dy

    new_location = self.world.get_location(new_global_x, new_global_y)
    if new_location is None:
        return

    self.current_location = new_location

    tilemap = new_location.tilemap

    if dx != 0:
        hero.x = 0 if dx > 0 else tilemap.width - 1
    if dy != 0:
        hero.y = 0 if dy > 0 else tilemap.height - 1

    self.view.render(new_location, hero)
```

What this does:

* Converts movement `(dx, dy)` into world grid movement
* Checks if a map exists there
* If it exists, changes location and positions hero at the edge
* Renders the new map

---

## Step 8 — Make Tilemap safer with bounds checking

Open:

```
game/tilemap.py
```

Inside `class Tilemap`, add this method:

```python
def has_tile(self, x: int, y: int):
    return x >= 0 and x < self.width and y >= 0 and y < self.height
```

Now update `get_tile`:

Find:

```python
def get_tile(self, x: int, y: int):
    return self.tiles[x][y]
```

Replace with:

```python
def get_tile(self, x: int, y: int):
    if not self.has_tile(x, y):
        return Tile(TileID.EMPTY)
    return self.tiles[x][y]
```

Finally, update `is_blocked`:

Find:

```python
def is_blocked(self, new_x: int, new_y: int):
    return not self.get_tile(new_x, new_y).is_walkable
```

Replace with:

```python
def is_blocked(self, new_x: int, new_y: int):
    if not self.has_tile(new_x, new_y):
        return True
    return not self.get_tile(new_x, new_y).is_walkable
```

Now out-of-bounds tiles are treated as blocked.

---

## Step 9 — Build the world locations more explicitly

Open:

```
game/world.py
```

In `WorldFactory.create()`, replace the part that adds locations with this:

```python
forest = Location("Forest", 0, -1, forestFactory.create())
town = Location("Town", 0, 0, townFactory.create())
farm = Location("Farm", 1, 0, forestFactory.create())

world.add_location(forest)
world.add_location(town)
world.add_location(farm)
```

This makes it clearer what locations exist and where.

---

## What We Accomplished

In this lesson, we:

* Removed the map dropdown and switched to movement-based navigation
* Detected border movement and changed maps automatically
* Added `_try_change_location()` to keep logic clean
* Made Tilemap safer with bounds checking
* Built a simple connected world grid with multiple locations

