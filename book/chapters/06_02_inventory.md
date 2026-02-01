## 6.2 – Finding a Lost Key in the Farm and Picking It Up (Hero Inventory)

In this lesson, we’re going to take a big step toward a real RPG experience: **items that exist in the world, can be picked up, and are stored in the hero’s inventory**.

By the end of this chapter, the player will be able to:

* Discover a **key** lying somewhere in the forest
* Pick it up simply by stepping on it
* See the item appear in the hero’s **inventory panel**
* Understand the difference between *item definitions* and *item instances*

This lesson ties together everything we’ve built so far: tilemaps, events, repositories, builders, and UI updates.

---

## Item Definitions vs Item Instances

Before we place a key in the world, we need to clarify an important design idea.

### ItemDefinition – the “type” of an item

An `ItemDefinition` describes **what an item is**, not a specific copy of it:

```python
class ItemDefinition:
    def __init__(self, id: TileID, name: str, description: str):
        self.id = id
        self.name = name
        self.description = description
```

Examples of item definitions:

* Key
* Ring
* Potion

There is **only one definition** of a Key in the game.

---

### ItemInstance – a concrete item the hero owns

When the hero picks something up, we create an `ItemInstance`:

```python
class ItemInstance:
    def __init__(self, item_definition: ItemDefinition):
        self.item_definition = item_definition
```

Why do this?

* You may have **multiple keys**
* Each key could later have its own state (broken, cursed, upgraded, etc.)

This mirrors real RPG engines and keeps your design future-proof.

---

## Loading Items at Game Start (Repository Pattern)

We store all item definitions in a central place: the **ItemRepository**.

```python
ItemRepository.get_instance().load_data()
```

This happens **once**, when the application starts.

Inside `load_data`, we use the **Builder pattern** to define items cleanly:

```python
ItemDefinitionBuilder() \
    .id(TileID.KEY) \
    .name("Key") \
    .description("A key to open a door") \
    .build()
```

This keeps item creation readable and avoids giant constructors.

---

## Adding Inventory to the Hero

The hero now has an inventory:

```python
class Hero:
    def __init__(self, name):
        ...
        self.__inventory: List[ItemInstance] = []

    @property
    def inventory(self):
        return self.__inventory
```

When the hero picks up an item:

```python
def add_item(self, item: ItemInstance):
    self.__inventory.append(item)
```

The hero doesn’t care *how* the item was created — just that it’s an item instance.

---

## Placing the Key in the World

Now let’s put the key on the map.

Inside `ForestTilemapFactory.create`, we randomly choose an empty tile and place the key there:

```python
events[x][y].tile = tileset.get_tile(TileID.KEY)
```

We attach a **CompositeEvent** to that tile:

```python
event = CompositeEvent([
    ShowMessageEvent("You found a key!"),
    ChangeTileEvent(tileset.get_tile(TileID.EMPTY)),
    AddItemEvent(ItemRepository.get_instance().find_by_id(TileID.KEY))
])
```

This single interaction now does three things:

1. Shows a message
2. Removes the key from the ground
3. Adds the key to the hero’s inventory

This is the power of the **Composite pattern**: small events, combined into meaningful behavior.

---

## Picking Up the Key (Step-on Interaction)

Unlike doors or signs, the key triggers when the hero **steps on the tile**.

Your movement logic already supports this:

```python
self.try_trigger_event(new_x, new_y)
```

Because the key tile is walkable, the hero can move onto it, triggering the pickup automatically.

---

## Updating the Inventory UI

To visualize the inventory, we use a `Treeview` widget from `tkinter.ttk`.

### Creating the inventory table

```python
columns = ("name", "qty")
self.inventory_table = ttk.Treeview(parent, columns=columns, show="headings")
self.inventory_table.heading("name", text="Name")
self.inventory_table.heading("qty", text="Qty")
```

### Updating inventory after picking up an item

```python
def update_inventory(self, hero: Hero):
    self.inventory_table.delete(*self.inventory_table.get_children())
    aggregates = {}
    for item in hero.inventory:
        aggregates[item.name] = aggregates.get(item.name, 0) + 1

    for name, qty in aggregates.items():
        self.inventory_table.insert("", tk.END, values=(name, qty))
```

We aggregate items by name so multiple keys appear as:

```
Key | 2
```

instead of separate rows.

---

## Why This Design Matters

This lesson quietly introduces **real RPG architecture concepts**:

* Repository pattern for global data
* Builder pattern for readable object creation
* Composite events for flexible gameplay
* Instance vs definition separation
* UI updates driven by game state

All without overengineering.

You now have a system that can support:

* Multiple items
* Stackable items
* Quest items
* Equipment
* Crafting ingredients

---

## Result

At the end of this lesson, your game has:

* A lost key in the forest
* A hero who can pick it up
* A visible inventory panel
* A clean, extensible item system

In the next chapter, we’ll **use the key to unlock a door**, connecting items and world interactions into a full gameplay loop.

![Key](img/06_02_key.png)