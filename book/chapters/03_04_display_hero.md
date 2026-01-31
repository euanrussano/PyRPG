# 3.4 - Displaying the Hero

In this lesson, we're going to bring our hero to life on the screen! We'll display the hero as a visual sprite on the game canvas and show the hero's statistics in the stats panel. Along the way, we'll learn about working with images, understanding coordinate systems, and creating interactive buttons.

This is where our game starts to feel real—you'll actually see your character on screen!

## What We'll Build

By the end of this lesson, our game will:
1. Display a hero sprite on the game canvas at a specific position
2. Show the hero's stats (name, level, XP, gold, energy) in the left panel
3. Have a button that adds gold to the hero when clicked

## Understanding Game Graphics: Tilesets

Before we write code, let's understand how 2D games typically handle graphics.

### What is a Tileset?

A **tileset** (also called a sprite sheet) is a single image file that contains many smaller images arranged in a grid. Instead of having hundreds of separate image files, game developers pack all their graphics into one or a few tilesets.

Here's why tilesets are useful:
- **Efficient loading**: Load one file instead of hundreds
- **Organized**: All related graphics in one place
- **Performance**: Graphics cards handle large textures efficiently
- **Easy to manage**: Artists can see all sprites at once

For our game, we have a file called `tileset.png` in the `assets` folder. This contains various sprites including our hero character.

### Setting Up the Assets Folder

First, make sure you have the following structure:

```
your-rpg-project/
├── main.py
├── hero.py
├── session.py
└── assets/
    └── tileset.png
```

If you don't have the assets folder yet, create it next to your Python files, then place your `tileset.png` file inside it.

## Understanding Pillow (PIL)

Python's built-in Tkinter can display images, but it has limited image manipulation capabilities. That's where **Pillow** comes in.

**Pillow** (imported as `PIL`) is a powerful image processing library for Python. It allows us to:
- Open and save various image formats (PNG, JPEG, GIF, etc.)
- Crop images (extract a portion of an image)
- Resize images
- Rotate, flip, and transform images
- Apply filters and effects

### Installing Pillow

If you haven't installed Pillow yet, open your terminal and run:

```bash
pip install Pillow
```

Or if you're using a virtual environment (recommended):

```bash
# Activate your virtual environment first, then:
pip install Pillow
```

## Understanding the Viewport and Coordinate Systems

Before we dive into the code, we need to understand how our game world maps to the screen.

### The Game World vs. The Screen

Imagine your game world is huge—maybe 100x100 tiles. But your screen can only show a small portion of it at once—maybe 10x10 tiles. This visible area is called the **viewport**.

Think of it like looking through a window: the world outside is much larger than what you can see through the window at any given moment.

### Coordinate Systems

We need to work with two coordinate systems:

1. **World Coordinates**: The position in the entire game world
   - Example: The hero is at position (45, 67) in the world

2. **Screen Coordinates**: The position on the visible canvas in pixels
   - Example: The hero appears at pixel (320, 480) on screen

### Tile Size

Since our game uses a grid-based system (like chess or most RPGs), we measure everything in **tiles**. A tile is a single square in our grid.

The **tile size** is how many pixels each tile occupies on screen. For example:
- If `tile_size = 64`, each tile is 64x64 pixels
- A 10x10 viewport with 64px tiles needs a 640x640 pixel canvas

The tile size is calculated based on the available canvas space:

```python
tile_size = canvas_width // viewport_width
```

The `//` operator is integer division—it divides and rounds down to the nearest whole number.

## Understanding *args and **kwargs

Before we look at the code, let's understand a powerful Python feature you'll see used in our layout code.

### What Are *args and **kwargs?

These are special syntax elements that allow functions to accept a variable number of arguments.

#### *args - Positional Arguments

`*args` allows a function to accept any number of positional arguments as a tuple:

```python
def print_all(*args):
    for arg in args:
        print(arg)

print_all("Hello", "World", 42)
# Output:
# Hello
# World
# 42
```

#### **kwargs - Keyword Arguments

`**kwargs` allows a function to accept any number of keyword arguments as a dictionary:

```python
def print_info(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")

print_info(name="Arthur", level=5, gold=100)
# Output:
# name: Arthur
# level: 5
# gold: 100
```

#### Unpacking with * and **

You can also use `*` and `**` to **unpack** collections when calling functions:

```python
# Dictionary unpacking
label_config = {'bg': 'green', 'anchor': 'w'}
label = tk.Label(parent, text="Name:", **label_config)
# This is equivalent to:
label = tk.Label(parent, text="Name:", bg='green', anchor='w')

# Tuple unpacking
numbers = (1, 2, 3)
print(*numbers)  # Equivalent to: print(1, 2, 3)
```

This is incredibly useful for avoiding repetition. Instead of typing the same parameters over and over, you define them once in a dictionary and unpack them where needed.

## Modifying the GameScreen Class

Now let's update our `main.py` file to display the hero. I'll show you the complete code first, then break down each new part.

### Updated Constructor

```python
class GameScreen(tk.Tk):
    def __init__(self, viewport_width=10, viewport_height=10):
        super().__init__()
        self.title("PyRPG")
        self.geometry("1200x800")
        self.viewport = (viewport_width, viewport_height)

        self.hero_sprite = None
        self.hero_photo = None
        self.tile_size = 64  # Default tile size, will be recalculated after layout

        # Create main layout
        self.create_layout()

        # Force the window to update and calculate actual sizes
        self.update_idletasks()
        
        # Now calculate the actual tile size based on rendered canvas
        self.calculate_tile_size()

        # Load sprites (now tile_size has a proper value)
        self.load_tileset()

        self.session: IGameSession = GameSession(self)
        self.session.start()
```

Let's break down the new elements:

#### Constructor Parameters

```python
def __init__(self, viewport_width=10, viewport_height=10):
```

We've added **default parameters** to the constructor. These specify how many tiles are visible on screen:
- `viewport_width=10` means we'll see 10 tiles horizontally
- `viewport_height=10` means we'll see 10 tiles vertically

Default parameters allow you to create a `GameScreen` without specifying these values:

```python
# Uses defaults (10, 10)
view = GameScreen()

# Or specify custom viewport
view = GameScreen(15, 12)
```

#### Viewport Storage

```python
self.viewport = (viewport_width, viewport_height)
```

We store the viewport dimensions as a **tuple**—an immutable (unchangeable) pair of values. We use a tuple instead of a list because viewport size shouldn't change during the game.

#### Sprite Attributes

```python
self.hero_sprite = None
self.hero_photo = None
```

- `self.hero_sprite` will store the canvas item ID for the hero's image
- `self.hero_photo` will store the actual image object (we need to keep a reference to prevent garbage collection)

#### The Initialization Sequence

Notice the careful order of operations:

```python
self.create_layout()          # 1. Create all widgets
self.update_idletasks()       # 2. Force Tkinter to calculate sizes
self.calculate_tile_size()    # 3. Calculate tile size based on actual canvas size
self.load_tileset()           # 4. Load and prepare images
self.session.start()          # 5. Start the game session
```

This order is critical! We can't calculate tile size until the canvas exists and has a real size.

### The update_idletasks() Method

```python
self.update_idletasks()
```

This is a Tkinter method that forces the window to complete all pending layout calculations. Without it, when we try to get the canvas width, Tkinter returns a default value (usually 1) because it hasn't actually rendered the canvas yet.

Think of it as telling Tkinter: "Stop and actually figure out how big everything is before continuing."

## Calculating Tile Size

Add this new method to calculate the tile size:

```python
def calculate_tile_size(self):
    """Calculate tile size based on actual canvas dimensions"""
    canvas_width = self.canvas.winfo_width()
    canvas_height = self.canvas.winfo_height()
    
    # Use the smaller dimension to ensure tiles fit
    self.tile_size = min(
        canvas_width // self.viewport[0],
        canvas_height // self.viewport[1]
    )
    
    # Ensure tile_size is at least 1
    if self.tile_size < 1:
        self.tile_size = 32  # Fallback default
        
    print(f"Canvas size: {canvas_width}x{canvas_height}")
    print(f"Viewport: {self.viewport}")
    print(f"Tile size: {self.tile_size}")
```

Let's break this down:

#### Getting Canvas Dimensions

```python
canvas_width = self.canvas.winfo_width()
canvas_height = self.canvas.winfo_height()
```

The `winfo_width()` and `winfo_height()` methods return the actual rendered size in pixels. This only works after `update_idletasks()` has been called.

#### Calculating Tile Size

```python
self.tile_size = min(
    canvas_width // self.viewport[0],
    canvas_height // self.viewport[1]
)
```

We calculate two possible tile sizes:
- Horizontal: `canvas_width // viewport_width`
- Vertical: `canvas_height // viewport_height`

We use `min()` to choose the smaller one. Why? To ensure tiles fit in both dimensions. If the canvas is 800x600 and viewport is 10x10:
- Horizontal tile size: 800 // 10 = 80 pixels
- Vertical tile size: 600 // 10 = 60 pixels
- We choose 60 to ensure everything fits

#### Fallback Protection

```python
if self.tile_size < 1:
    self.tile_size = 32
```

This protects against edge cases where the calculation might fail. A tile size of 0 or negative would crash the program.

## Loading the Tileset

Add this method to load and prepare the hero sprite:

```python
def load_tileset(self):
    tileset: Image.Image = Image.open("assets/tileset.png")
    hero_img = tileset.crop((5*8, 0, 6*8, 8)).resize((self.tile_size, self.tile_size))
    self.hero_photo = ImageTk.PhotoImage(hero_img)
```

Let's examine each line:

#### Opening the Image

```python
tileset: Image.Image = Image.open("assets/tileset.png")
```

- `Image.open()` is a Pillow function that loads an image file
- The type hint `: Image.Image` indicates this is a Pillow Image object
- The path `"assets/tileset.png"` is relative to where you run the script

#### Cropping the Hero Sprite

```python
hero_img = tileset.crop((5*8, 0, 6*8, 8))
```

The `crop()` method extracts a rectangular portion of the image. It takes a tuple of four values: `(left, top, right, bottom)` in pixels.

In our tileset, each sprite is 8x8 pixels. The hero is at position 5 (the 6th sprite from the left) in the first row:
- Left edge: `5 * 8 = 40` pixels
- Top edge: `0` pixels (first row)
- Right edge: `6 * 8 = 48` pixels
- Bottom edge: `8` pixels

This extracts an 8x8 pixel image of the hero.

#### Resizing the Sprite

```python
.resize((self.tile_size, self.tile_size))
```

The extracted sprite is 8x8 pixels, but our tiles might be 64x64 pixels (or whatever we calculated). The `resize()` method scales the image to match our tile size.

This is **method chaining**—calling a method directly on the result of another method. It's equivalent to:

```python
hero_img = tileset.crop((5*8, 0, 6*8, 8))
hero_img = hero_img.resize((self.tile_size, self.tile_size))
```

#### Converting for Tkinter

```python
self.hero_photo = ImageTk.PhotoImage(hero_img)
```

Tkinter can't directly use Pillow images. We must convert them to `PhotoImage` objects using `ImageTk.PhotoImage()`.

**IMPORTANT**: We store this in `self.hero_photo`. If we don't keep a reference to the PhotoImage, Python's garbage collector will delete it and the image won't display!

## Displaying the Hero on the Canvas

Add this method to draw the hero at a specific position:

```python
def update_hero_position(self, world_x: int, world_y: int):
    """Update hero sprite position"""
    x = world_x * self.tile_size
    y = world_y * self.tile_size
    
    if self.hero_sprite:
        self.canvas.delete(self.hero_sprite)
    self.hero_sprite = self.canvas.create_image(x, y, image=self.hero_photo, anchor='nw')
```

Let's break this down:

#### Converting World to Screen Coordinates

```python
x = world_x * self.tile_size
y = world_y * self.tile_size
```

If the hero is at world position (5, 5) and tile_size is 64:
- Screen x = 5 * 64 = 320 pixels
- Screen y = 5 * 64 = 320 pixels

#### Removing the Old Sprite

```python
if self.hero_sprite:
    self.canvas.delete(self.hero_sprite)
```

If a hero sprite already exists on the canvas, we delete it. Otherwise, we'd create multiple overlapping sprites.

Canvas items are identified by IDs (numbers). When we create an item, the canvas returns its ID, which we store in `self.hero_sprite`.

#### Creating the New Sprite

```python
self.hero_sprite = self.canvas.create_image(x, y, image=self.hero_photo, anchor='nw')
```

- `create_image()` adds an image to the canvas
- `x, y` are the pixel coordinates
- `image=self.hero_photo` is the PhotoImage to display
- `anchor='nw'` means the x,y position refers to the northwest (top-left) corner
  - Without this, it defaults to 'center', which would offset our grid alignment

The method returns an ID which we store for future reference.

## Displaying Hero Stats

Add this method to update the stats labels:

```python
def update_hero_stats(self, name: str, level: int, xp: int, gold: int, energy: int):
    self.hero_name_label.config(text=f"{name}")
    self.hero_level_label.config(text=f"{level}")
    self.hero_xp_label.config(text=f"{xp}")
    self.hero_gold_label.config(text=f"{gold}")
    self.hero_energy_label.config(text=f"{energy}")
```

This is straightforward—we use the `config()` method to change the text of each label.

The `f"{name}"` syntax is an **f-string** (formatted string literal). It lets you embed variables directly in strings:

```python
name = "Arthur"
message = f"Hello, {name}!"  # "Hello, Arthur!"
```

While `f"{name}"` is equivalent to just `name` here, using f-strings consistently makes it easier to add formatting later:

```python
self.hero_gold_label.config(text=f"{gold} gold")
self.hero_energy_label.config(text=f"{energy}/{max_energy}")
```

## Creating the Stats Panel

Update the `create_left_top_panel` method:

```python
def create_left_top_panel(self, parent):
    # Configure parent
    parent.configure(bg='green')

    # Create a common style config
    label_config = {'bg': 'green', 'anchor': 'w'}
    grid_config = {'padx': 5, 'pady': 5, 'sticky': 'w'}
    
    # Hero stats widgets
    tk.Label(parent, text="Name: ", **label_config).grid(row=0, column=0, **grid_config)
    self.hero_name_label = tk.Label(parent, text="<name here>", **label_config)
    self.hero_name_label.grid(row=0, column=1, **grid_config)

    tk.Label(parent, text="Level: ", **label_config).grid(row=1, column=0, **grid_config)
    self.hero_level_label = tk.Label(parent, text="<level here>", **label_config)
    self.hero_level_label.grid(row=1, column=1, **grid_config)

    tk.Label(parent, text="XP: ", **label_config).grid(row=2, column=0, **grid_config)
    self.hero_xp_label = tk.Label(parent, text="<xp here>", **label_config)
    self.hero_xp_label.grid(row=2, column=1, **grid_config)
    
    tk.Label(parent, text="Gold: ", **label_config).grid(row=3, column=0, **grid_config)
    self.hero_gold_label = tk.Label(parent, text="<gold here>", **label_config)
    self.hero_gold_label.grid(row=3, column=1, **grid_config)
    
    tk.Label(parent, text="Energy: ", **label_config).grid(row=4, column=0, **grid_config)
    self.hero_energy_label = tk.Label(parent, text="<energy here>", **label_config)
    self.hero_energy_label.grid(row=4, column=1, **grid_config)

    tk.Button(parent, text="Free Gold!!", command=self.add_gold).grid(row=5, column=0, columnspan=2, **grid_config)
```

### Using **kwargs for Cleaner Code

Notice how we define common configurations:

```python
label_config = {'bg': 'green', 'anchor': 'w'}
grid_config = {'padx': 5, 'pady': 5, 'sticky': 'w'}
```

Then unpack them with `**`:

```python
tk.Label(parent, text="Name: ", **label_config)
```

This is equivalent to:

```python
tk.Label(parent, text="Name: ", bg='green', anchor='w')
```

But much cleaner! If you want to change the background color of all labels, you only change one line instead of five.

### The Button and Callbacks

```python
tk.Button(parent, text="Free Gold!!", command=self.add_gold).grid(row=5, column=0, columnspan=2, **grid_config)
```

This creates a button with several important parameters:

- `text="Free Gold!!"` - the text displayed on the button
- `command=self.add_gold` - the function to call when clicked
- `columnspan=2` - makes the button span both columns

#### Understanding Callbacks

The `command` parameter takes a **callback function**—a function that will be called later when an event happens (in this case, a button click).

**CRITICAL**: Notice we write `command=self.add_gold` NOT `command=self.add_gold()`

- `self.add_gold` passes the function itself
- `self.add_gold()` would call the function immediately and pass its return value

This is a common mistake for beginners!

### The Button Handler

Add this method to handle the button click:

```python
def add_gold(self):
    self.session.add_gold()
```

When the button is clicked, this method:
1. Gets called automatically by Tkinter
2. Calls the `add_gold()` method on the game session

This demonstrates the MVP pattern in action:
- **View** (button) detects the click
- **View** notifies the **Presenter** (session)
- **Presenter** will update the **Model** (hero) and tell the **View** to refresh

We'll implement the session's `add_gold()` method next.

## Updating the GameSession

Now update your `session.py` file to actually use these new view methods:

```python
class GameSession(IGameSession):
    def __init__(self, view: GameScreen) -> None:
        super().__init__()
        self.hero = None
        self.view = view

    def start(self):
        self.hero = Hero("John")
        self.refresh_hero_display()
        
    def refresh_hero_display(self):
        """Update the view with current hero data"""
        self.view.update_hero_stats(
            self.hero.name,
            self.hero.level,
            self.hero.xp,
            self.hero.gold,
            self.hero.energy
        )
        self.view.update_hero_position(5, 5)
    
    def add_gold(self):
        """Add gold to the hero"""
        self.hero.gold += 10
        self.refresh_hero_display()
```

Let's examine these methods:

### The start Method

```python
def start(self):
    self.hero = Hero("John")
    self.refresh_hero_display()
```

After creating the hero, we call `refresh_hero_display()` to show the hero on screen.

### The refresh_hero_display Method

```python
def refresh_hero_display(self):
    self.view.update_hero_stats(
        self.hero.name,
        self.hero.level,
        self.hero.xp,
        self.hero.gold,
        self.hero.energy
    )
    self.view.update_hero_position(5, 5)
```

This method centralizes all hero display updates. It:
1. Updates the stats panel with current hero data
2. Updates the hero's position on the canvas (currently hardcoded to 5, 5)

Having this in one place means we only need to call `refresh_hero_display()` whenever anything about the hero changes.

### The add_gold Method

```python
def add_gold(self):
    self.hero.gold += 10
    self.refresh_hero_display()
```

This is the handler for our button click:
1. Increases the hero's gold by 10
2. Refreshes the display to show the new amount

The `+=` operator is shorthand for `self.hero.gold = self.hero.gold + 10`.

## Testing Your Game

Now run your game:

```bash
python main.py
```

You should see:
1. A green stats panel on the left showing John's information
2. A hero sprite in the center canvas at position (5, 5)
3. A "Free Gold!!" button at the bottom of the stats panel

Click the button and watch the gold amount increase!

## What We've Learned

In this lesson, we covered a lot of ground:

1. **Tilesets**: How 2D games organize graphics in sprite sheets
2. **Pillow (PIL)**: Loading, cropping, and resizing images
3. **Coordinate Systems**: Converting between world coordinates and screen pixels
4. **Viewport**: The visible portion of the game world
5. ***args and **kwargs**: Accepting and unpacking variable arguments
6. **Callbacks**: Functions that are called in response to events
7. **Type Hints**: Making code more readable and maintainable
8. **MVP Pattern in Action**: How View, Presenter, and Model work together

## What's Next

Our hero can now be seen on screen, but it can't move! In the next lesson, we'll add keyboard controls to move the hero around the game world. We'll learn about:
- Event handling in Tkinter
- Updating game state
- Handling boundaries and collision detection

We're building up our game piece by piece, and each lesson adds more interactivity and functionality. You're doing great!

Link to GitHub commit for this code:
[here](https://github.com/euanrussano/PyRPG/commit/f23c2aa3dba7d1fd5d0ae2f2c12698f3977f9045)