# 5.1 – Creating the Game Item Builder

In this lesson, we’re going to introduce **items** into our game world.

But instead of jumping straight into inventories and picking things up, we’ll take a step back and build a **solid foundation** first. This is how professional games are made: systems first, gameplay second.

By the end of this lesson, you will:

* Understand what *magic methods* are in Python
* Learn what `__str__()` does and why it’s useful
* Create a **Builder** for defining game items
* Introduce the **Repository pattern** to store item definitions
* Load item data when the game starts

---

## Items vs Item Definitions

Before writing any code, we need to clarify something important.

There is a difference between:

* **An item definition** → what a *type* of item is
* **An item instance** → a *specific copy* of that item in the world

For now, we are creating **item definitions**.

Examples:

* “Key”
* “Ring”
* “Apple”

Later, we’ll create multiple *instances* of these definitions (multiple keys, multiple apples, etc.).

---

## Creating the ItemDefinition Class

Create a new file:

```
game/core/itemdefinition.py
```

And start with this class:

```python
class ItemDefinition:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
```

So far, this is simple:

* `name` → what the item is called
* `description` → a short explanation shown to the player

---

## Magic Methods and `__str__()`

Now let’s add this:

```python
def __str__(self) -> str:
    return self.name
```

### What is a magic method?

A **magic method** is a method with double underscores:

```text
__something__
```

Python automatically calls these methods in specific situations.

Examples:

* `__init__()` → called when an object is created
* `__str__()` → called when Python needs a *string representation* of an object

### Why is `__str__()` useful?

Without it:

```python
item = ItemDefinition("Key", "A key to open a door")
print(item)
```

Would show something ugly like:

```
<core.itemdefinition.ItemDefinition object at 0x123abc>
```

With `__str__()` implemented:

```python
print(item)
```

Now it prints:

```
Key
```

This is **extremely useful** for:

* Debugging
* Logging
* UI lists (inventories, tooltips, dialogs)

---

## Introducing the Builder Pattern

As the game grows, items will gain more properties:

* weight
* value
* durability
* effects

Passing everything into a constructor quickly becomes messy.

That’s where the **Builder pattern** comes in.

---

## Creating the ItemDefinitionBuilder

Add this class below `ItemDefinition`:

```python
class ItemDefinitionBuilder:
    def __init__(self) -> None:
        self.__name: str = ""
        self.__description: str = ""
```

Notice the double underscore (`__name`).

This makes the attribute **private**, meaning:

* it should only be modified through methods
* it protects the internal state of the builder

---

### Fluent Builder Methods

Now add the builder methods:

```python
def name(self, name: str) -> 'ItemDefinitionBuilder':
    self.__name = name
    return self

def description(self, description: str) -> 'ItemDefinitionBuilder':
    self.__description = description
    return self
```

Each method:

* sets one property
* returns `self`

This allows **method chaining**:

```python
ItemDefinitionBuilder().name("Key").description("A key to open a door")
```

This style is:

* readable
* flexible
* beginner-friendly

---

### The `build()` Method

Finally, add:

```python
def build(self) -> ItemDefinition:
    return ItemDefinition(self.__name, self.__description)
```

This is the moment where the builder **creates the actual object**.

---

## Using the Builder

Here’s how we create an item definition now:

```python
key = ItemDefinitionBuilder() \
    .name("Key") \
    .description("A key to open a door") \
    .build()
```

This may look longer than calling a constructor—but it scales **much better** as items become more complex.

---

## Introducing the Repository Pattern

Now we need a place to store **all item definitions**.

That’s what a **Repository** is.

> A repository is responsible for **storing, finding, and managing domain objects**.

The game should never ask:

> “Where are items stored?”

It should ask:

> “Give me the item called ‘Key’.”

---

## Creating the ItemRepository

Add this class:

```python
class ItemRepository:
    _instance: Optional['ItemRepository'] = None
```

This repository is a **singleton**, meaning:

* only one instance exists
* everyone accesses the same data

---

### Enforcing a Singleton

```python
def __init__(self) -> None:
    if ItemRepository._instance is not None:
        raise RuntimeError("ItemRepository is a singleton. Use ItemRepository.get_instance()")
    self.items: List[ItemDefinition] = []
```

This prevents accidental creation of multiple repositories.

---

### Accessing the Repository

```python
@classmethod
def get_instance(cls) -> 'ItemRepository':
    if cls._instance is None:
        cls._instance = cls()
    return cls._instance
```

This ensures:

* lazy initialization
* global access without global variables

---

### Finding Items

```python
def find_by_name(self, name: str) -> ItemDefinition | None:
    for item in self.items:
        if item.name == name:
            return item
    return None
```

This allows the game to ask:

```python
repo.find_by_name("Key")
```

---

## Loading Item Data

For now, we’ll load item data **in code**, which is perfect for teaching.

Add this method:

```python
def load_data(self) -> None:
    self.items = [
        ItemDefinitionBuilder().name("Key").description("A key to open a door").build(),
        ItemDefinitionBuilder().name("Ring").description("Nice jewelry...").build(),
    ]
    print(f"{type(self)}: Loaded item data")
```

Later, this can be replaced with:

* XML
* JSON
* database files

The game code will **not change**.

---

## Bootstrapping the Repository

Finally, we load item data when the game starts.

In `main.py`:

```python
if __name__ == "__main__":
    ItemRepository.get_instance().load_data()
    view = GameScreen()
    view.mainloop()
```

This is called **application bootstrapping**:

* data is prepared
* UI starts after everything is ready

---

## Why This Design Matters

Even though this looks like “a lot of code for simple items”, it gives us:

* clean separation of responsibilities
* flexible item creation
* centralized item management
* future-proof design

And most importantly:

> **This is how real game engines are structured.**

---

## What’s Next

In the next lesson, we’ll finally *use* these items in gameplay:

* placing a key in the world
* picking it up
* storing it in the hero’s inventory

Now that the foundation is solid, everything else becomes easy.

Well done — this is real engine architecture, step by step.
