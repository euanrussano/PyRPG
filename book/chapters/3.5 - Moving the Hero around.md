# 3.5 - Moving the Hero Around

In this lesson, we're going to make our game interactive by adding keyboard controls! The player will be able to move the hero around the game world using the arrow keys. We'll also implement boundary checking to ensure the hero can't move to invalid positions.

This is where our game starts to feel like a real game—you'll be able to control your character and explore the world!

## What We'll Build

By the end of this lesson, our game will:
1. Respond to arrow key presses
2. Move the hero up, down, left, and right
3. Validate movements to ensure they're legal
4. Update the display to show the hero's new position

## Understanding Event Handling in Tkinter

Before we dive into the code, we need to understand how programs respond to user input.

### What is an Event?

An **event** is something that happens during program execution—usually caused by user interaction. Examples include:
- Pressing a key
- Clicking a mouse button
- Moving the mouse
- Resizing a window
- The window loading

### Event-Driven Programming

Most GUI applications use **event-driven programming**. Instead of running from top to bottom like a script, the program:
1. Sets up the interface
2. Waits for events
3. Responds to events when they occur
4. Goes back to waiting

Think of it like a waiter at a restaurant:
- They set up the table (initialize the GUI)
- They wait for customers to ask for something (wait for events)
- They respond when called (handle the event)
- They go back to waiting for the next request

### Event Binding in Tkinter

Tkinter uses **event binding** to connect events to functions. The basic pattern is:

```python
widget.bind(event_pattern, handler_function)
```

- `event_pattern` is a string describing what event to watch for
- `handler_function` is the function to call when that event occurs

Common event patterns:
- `"<Button-1>"` - Left mouse click
- `"<Double-Button-1>"` - Left mouse double-click
- `"<Key>"` - Any key press
- `"<Up>"`, `"<Down>"`, `"<Left>"`, `"<Right>"` - Arrow keys
- `"<Return>"` - Enter key
- `"<Escape>"` - Escape key
- `"<a>"` - The 'a' key specifically

### Event Objects

When an event occurs, Tkinter creates an **event object** containing information about the event and passes it to your handler function.

For keyboard events, the event object contains properties like:
- `event.char` - The character typed (for regular keys)
- `event.keysym` - The symbolic name of the key (like "Up", "a", "Return")
- `event.keycode` - A numeric code for the key

For now, we won't need to use these properties, but it's good to know they exist.

## Understanding Grid Coordinates and Movement

Before we implement movement, let's think about how movement works in a grid-based game.

### Grid Coordinates

Our game world uses a grid coordinate system, just like a chess board:
- The x-coordinate increases as you move right
- The y-coordinate increases as you move down
- Position (0, 0) is the top-left corner

```
(0,0) (1,0) (2,0) (3,0) ...
(0,1) (1,1) (2,1) (3,1) ...
(0,2) (1,2) (2,2) (3,2) ...
...
```

### Movement Deltas

To move in the grid, we use **deltas** (changes in position):
- Moving right: increase x by 1 → `dx = 1, dy = 0`
- Moving left: decrease x by 1 → `dx = -1, dy = 0`
- Moving down: increase y by 1 → `dx = 0, dy = 1`
- Moving up: decrease y by 1 → `dx = 0, dy = -1`

The Greek letter delta (Δ) represents "change in" mathematics. So `dx` means "change in x" and `dy` means "change in y."

We can apply these deltas to the current position:

```python
new_x = current_x + dx
new_y = current_y + dy
```

## Adding Position to the Hero

First, we need to update our `Hero` class to track position. Modify `hero.py`:

```python
class Hero:
    def __init__(self, name):
        self.name = name
        self.level = 1
        self.xp = 0
        self.gold = 0
        self.max_energy = 10
        self.energy = self.max_energy
        
        # Position in the game world
        self.x = 5
        self.y = 5
```

We've added two new attributes:
- `self.x = 5` - The hero starts at x-coordinate 5
- `self.y = 5` - The hero starts at y-coordinate 5

We chose (5, 5) to place the hero near the middle of our 10x10 viewport.

## Binding Keyboard Events

Now let's modify the `GameScreen` class in `main.py` to respond to arrow key presses. Update the `__init__` method:

```python
def __init__(self, viewport_width=10, viewport_height=10):
    super().__init__()
    self.title("PyRPG")
    self.geometry("1200x800")
    self.viewport = (viewport_width, viewport_height)

    self.hero_sprite = None
    self.hero_photo = None
    self.tile_size = 64

    # Create main layout
    self.create_layout()

    # Force the window to update and calculate actual sizes
    self.update_idletasks()
    
    # Now calculate the actual tile size based on rendered canvas
    self.calculate_tile_size()

    # Load sprites (now tile_size has a proper value)
    self.load_tileset()

    self.session: IGameSession = GameSession(self)

    # Bind key events
    self.bind("<Up>", self.session.move_up)
    self.bind("<Down>", self.session.move_down)
    self.bind("<Left>", self.session.move_left)
    self.bind("<Right>", self.session.move_right)

    self.session.start()
```

The new part is:

```python
# Bind key events
self.bind("<Up>", self.session.move_up)
self.bind("<Down>", self.session.move_down)
self.bind("<Left>", self.session.move_left)
self.bind("<Right>", self.session.move_right)
```

Let's break this down:

### The bind Method

```python
self.bind("<Up>", self.session.move_up)
```

- `self.bind()` attaches an event handler to the window
- `"<Up>"` is the event pattern for the up arrow key
- `self.session.move_up` is the function to call when the up arrow is pressed

Notice we're calling `bind` on `self` (the window), not on a specific widget. This means the window will respond to these keys regardless of which widget has focus.

### Why Bind to the Session?

Notice we're binding directly to methods in the session:

```python
self.bind("<Up>", self.session.move_up)
```

We could have created methods in the view like:

```python
def on_up_arrow(self, event):
    self.session.move_up(event)
```

But that would be unnecessary extra code. Since the session methods are exactly what we want to call, we can bind to them directly.

This demonstrates our MVP pattern:
- **View** detects the event (key press)
- **View** immediately delegates to **Presenter** (session)
- **Presenter** handles the logic and updates the **Model** (hero)

### Binding Order Matters

Notice we bind the keys **after** creating the session but **before** calling `session.start()`:

```python
self.session: IGameSession = GameSession(self)

# Bind key events
self.bind("<Up>", self.session.move_up)
# ...

self.session.start()
```

This ensures the session object exists before we try to reference its methods.

## Updating the Session Interface

Now we need to update our `IGameSession` interface in `session.py` to include the movement methods:

```python
class IGameSession(ABC):
    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def move_up(self, event):
        pass

    @abstractmethod
    def move_down(self, event):
        pass

    @abstractmethod
    def move_left(self, event):
        pass

    @abstractmethod
    def move_right(self, event):
        pass
```

Each method takes an `event` parameter because Tkinter will pass the event object when calling these handlers.

Even though we don't use the event object in our implementation, we must accept it because that's how Tkinter event handlers work. If we didn't include the `event` parameter, we'd get an error when Tkinter tried to call the function.

## Implementing Movement in the Session

Now let's implement the movement logic in the `GameSession` class. Update `session.py`:

```python
class GameSession(IGameSession):
    def __init__(self, view: GameScreen) -> None:
        super().__init__()
        self.hero: Hero | None = None
        self.view = view

    def start(self):
        self.hero = Hero("John")
        self.view.update_hero_position(self.hero.x, self.hero.y)
        self.view.update_hero_stats(self.hero.name, self.hero.level, self.hero.xp, self.hero.gold, self.hero.energy)

    def add_gold(self):
        if self.hero is None:
            return
        self.hero.gold += 10
        self.view.update_hero_stats(self.hero.name, self.hero.level, self.hero.xp, self.hero.gold, self.hero.energy)

    def move_hero(self, dx: int, dy: int):
        if self.hero is None:
            return
        if abs(dx) > 1 or abs(dy) > 1:
            return
        if abs(dx) + abs(dy) != 1:
            return
        
        self.hero.x += dx
        self.hero.y += dy
        
        self.view.update_hero_position(self.hero.x, self.hero.y)

    def move_down(self, event):
        self.move_hero(0, 1)

    def move_up(self, event):
        self.move_hero(0, -1)
        
    def move_left(self, event):
        self.move_hero(-1, 0)
        
    def move_right(self, event):
        self.move_hero(1, 0)
```

Let's examine each part:

### Updated Type Hint

```python
self.hero: Hero | None = None
```

The `Hero | None` type hint uses the **union operator** (`|`) introduced in Python 3.10. It means "`self.hero` can be either a `Hero` object or `None`."

This is equivalent to the older syntax:

```python
from typing import Optional
self.hero: Optional[Hero] = None
```

Why is this important? It helps us remember that `self.hero` might be `None` (before `start()` is called), so we need to check before using it.

### Updated start Method

```python
def start(self):
    self.hero = Hero("John")
    self.view.update_hero_position(self.hero.x, self.hero.y)
    self.view.update_hero_stats(self.hero.name, self.hero.level, self.hero.xp, self.hero.gold, self.hero.energy)
```

Now we're getting the position from the hero object (`self.hero.x`, `self.hero.y`) instead of hardcoding it.

### The move_hero Method (Core Logic)

```python
def move_hero(self, dx: int, dy: int):
    if self.hero is None:
        return
    if abs(dx) > 1 or abs(dy) > 1:
        return
    if abs(dx) + abs(dy) != 1:
        return
    
    self.hero.x += dx
    self.hero.y += dy
    
    self.view.update_hero_position(self.hero.x, self.hero.y)
```

This is the central movement logic. Let's break it down:

#### Safety Check

```python
if self.hero is None:
    return
```

If the hero hasn't been created yet, do nothing. This prevents crashes if somehow a movement is triggered before `start()` is called.

#### Validation: Single Step Only

```python
if abs(dx) > 1 or abs(dy) > 1:
    return
```

The `abs()` function returns the **absolute value** (removes the negative sign):
- `abs(5)` returns `5`
- `abs(-5)` returns `5`

This check ensures that `dx` and `dy` are each no more than 1 step. It prevents the hero from teleporting across the map if someone passes invalid values like `move_hero(10, 0)`.

#### Validation: Orthogonal Movement Only

```python
if abs(dx) + abs(dy) != 1:
    return
```

This ensures the hero moves exactly one step in exactly one direction (not diagonally, not staying still).

Valid movements:
- `dx=1, dy=0` → `abs(1) + abs(0) = 1` ✓
- `dx=0, dy=-1` → `abs(0) + abs(1) = 1` ✓

Invalid movements:
- `dx=0, dy=0` → `abs(0) + abs(0) = 0` ✗ (not moving)
- `dx=1, dy=1` → `abs(1) + abs(1) = 2` ✗ (diagonal)
- `dx=1, dy=-1` → `abs(1) + abs(1) = 2` ✗ (diagonal)

This is a clever way to validate movement with a single condition!

#### Applying the Movement

```python
self.hero.x += dx
self.hero.y += dy
```

Update the hero's position by adding the deltas. The `+=` operator is shorthand:
- `self.hero.x += dx` is the same as `self.hero.x = self.hero.x + dx`

#### Updating the Display

```python
self.view.update_hero_position(self.hero.x, self.hero.y)
```

Tell the view to redraw the hero at the new position.

### The Directional Movement Methods

```python
def move_down(self, event):
    self.move_hero(0, 1)

def move_up(self, event):
    self.move_hero(0, -1)
    
def move_left(self, event):
    self.move_hero(-1, 0)
    
def move_right(self, event):
    self.move_hero(1, 0)
```

These are the handlers bound to the arrow keys. Each one:
1. Accepts the `event` parameter (required for Tkinter event handlers)
2. Calls `move_hero()` with the appropriate delta values
3. Doesn't use the event object (we don't need any information from it)

Notice the pattern:
- **Down**: `y` increases (moving down the grid)
- **Up**: `y` decreases (moving up the grid)
- **Left**: `x` decreases (moving left)
- **Right**: `x` increases (moving right)

### Why Separate move_hero from Directional Methods?

You might wonder why we have both `move_hero(dx, dy)` and four separate directional methods. Why not just:

```python
def move_up(self, event):
    self.hero.y -= 1
    self.view.update_hero_position(self.hero.x, self.hero.y)
```

Having a central `move_hero()` method provides several benefits:

1. **Validation in one place**: All movement validation happens in one method
2. **Easier to extend**: Later we can add things like collision detection, energy cost, or animation
3. **Code reuse**: Other systems (like AI or scripted events) can use `move_hero()`
4. **Easier to debug**: You can add logging or breakpoints in one place

This is an example of **refactoring**—organizing code to be more maintainable even if it seems like more code initially.

## Understanding the Movement Flow

Let's trace what happens when you press the up arrow key:

1. **Event Detection**: Tkinter detects the up arrow key press
2. **Event Dispatch**: Tkinter looks up what function is bound to `"<Up>"`
3. **Handler Called**: Tkinter calls `session.move_up(event)`
4. **Delegation**: `move_up()` calls `move_hero(0, -1)`
5. **Validation**: `move_hero()` checks:
   - Is there a hero? ✓
   - Is `abs(0) > 1` or `abs(-1) > 1`? No ✓
   - Is `abs(0) + abs(-1) == 1`? Yes ✓
6. **Model Update**: `self.hero.y -= 1` (decreases y by 1)
7. **View Update**: `self.view.update_hero_position(x, y)` is called
8. **Display Refresh**: The canvas redraws the hero sprite at the new position

All of this happens in milliseconds, creating the illusion of smooth movement!

## Testing Your Movement

Run your game:

```bash
python main.py
```

Now try pressing the arrow keys:
- **Up Arrow** → Hero moves up (y decreases)
- **Down Arrow** → Hero moves down (y increases)
- **Left Arrow** → Hero moves left (x decreases)
- **Right Arrow** → Hero moves right (x increases)

You should see the hero sprite move around the canvas in response to your key presses!

## Current Limitations

You might notice that right now:
1. The hero can move off the screen (outside the viewport)
2. The hero can move to negative coordinates
3. There are no boundaries or walls

These are intentional—we'll address boundaries in the next section. For now, we're focusing on getting basic movement working.

## Adding Boundary Checking

Right now, the hero can move anywhere, including off-screen or into invalid coordinates. Let's add boundaries.

First, we need to know the size of our game world. For now, let's match it to our viewport. Update the `GameSession.__init__` method:

```python
def __init__(self, view: GameScreen) -> None:
    super().__init__()
    self.hero: Hero | None = None
    self.view = view
    self.world_width = 10
    self.world_height = 10
```

Now update the `move_hero` method to check boundaries:

```python
def move_hero(self, dx: int, dy: int):
    if self.hero is None:
        return
    if abs(dx) > 1 or abs(dy) > 1:
        return
    if abs(dx) + abs(dy) != 1:
        return
    
    # Calculate new position
    new_x = self.hero.x + dx
    new_y = self.hero.y + dy
    
    # Check boundaries
    if new_x < 0 or new_x >= self.world_width:
        return
    if new_y < 0 or new_y >= self.world_height:
        return
    
    # Movement is valid, apply it
    self.hero.x = new_x
    self.hero.y = new_y
    
    self.view.update_hero_position(self.hero.x, self.hero.y)
```

Let's examine the boundary checking:

### Calculating the New Position

```python
new_x = self.hero.x + dx
new_y = self.hero.y + dy
```

We calculate where the hero **would** be after moving, without actually moving yet. This lets us check if the move is valid before applying it.

### Checking Horizontal Boundaries

```python
if new_x < 0 or new_x >= self.world_width:
    return
```

This prevents movement if:
- `new_x < 0` → Moving too far left (negative coordinates)
- `new_x >= self.world_width` → Moving too far right (beyond world width)

Note we use `>=` not `>` because coordinates are zero-indexed. If world width is 10, valid x positions are 0-9.

### Checking Vertical Boundaries

```python
if new_y < 0 or new_y >= self.world_height:
    return
```

Same logic for vertical boundaries:
- `new_y < 0` → Moving too far up
- `new_y >= self.world_height` → Moving too far down

### Applying Valid Movements

```python
self.hero.x = new_x
self.hero.y = new_y
```

Only if we pass all the checks do we actually update the hero's position.

Now test your game again. Try moving to the edges—you'll find the hero stops at the boundaries instead of disappearing off-screen!

## Understanding the Guard Clause Pattern

Notice how we structure our validation:

```python
if self.hero is None:
    return
if abs(dx) > 1 or abs(dy) > 1:
    return
if abs(dx) + abs(dy) != 1:
    return
if new_x < 0 or new_x >= self.world_width:
    return
if new_y < 0 or new_y >= self.world_height:
    return

# If we get here, everything is valid
self.hero.x = new_x
self.hero.y = new_y
self.view.update_hero_position(self.hero.x, self.hero.y)
```

This pattern is called **guard clauses** or **early returns**. We check each condition and return early if it fails, rather than nesting everything in if-statements:

```python
# Don't do this (deeply nested):
if self.hero is not None:
    if abs(dx) <= 1 and abs(dy) <= 1:
        if abs(dx) + abs(dy) == 1:
            new_x = self.hero.x + dx
            if new_x >= 0 and new_x < self.world_width:
                # ... and so on
```

Guard clauses keep code flat and readable. Each check is clear and independent.

## What We've Learned

In this lesson, we covered:

1. **Event-Driven Programming**: How programs wait for and respond to events
2. **Event Binding**: Connecting keyboard events to handler functions in Tkinter
3. **Event Objects**: What information Tkinter provides about events
4. **Grid Coordinates**: How position works in a tile-based game
5. **Movement Deltas**: Using dx and dy to represent direction
6. **Type Unions**: The `Hero | None` syntax for optional types
7. **Validation Logic**: Checking if movements are legal
8. **Boundary Checking**: Preventing invalid positions
9. **Guard Clauses**: Clean validation with early returns
10. **Refactoring**: Organizing code for maintainability

## What's Next

Our hero can now move around within boundaries, but the world is still empty. In the next lessons, we'll:

1. Add a tilemap system to create an actual game world with grass, water, trees, etc.
2. Implement collision detection so the hero can't walk through walls
3. Add different terrain types that affect movement
4. Create a camera system so the viewport can scroll when the hero moves near edges

Movement is working beautifully! You're building the core mechanics of a real RPG game, piece by piece. Great job!