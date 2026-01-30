# 3.3 - Creating the Game Session (Presenter) Class

In this lesson, we're going to introduce a very important architectural pattern that will help us organize our code as the game grows more complex. We'll create a **Presenter** class that acts as the "brain" of our game, managing the game logic and connecting our visual interface (the view) with our game data (the model).

But before we dive into the code, we need to understand several intermediate concepts. Don't worry if some of these seem advanced—I'll explain them clearly, and you'll see why they're necessary for building a well-structured game.

## Understanding the Model-View-Presenter (MVP) Pattern

As programmers, one of our biggest challenges is keeping code organized as projects grow. Imagine if all your game logic, display code, and data were mixed together in one giant file—it would become a nightmare to maintain!

The **Model-View-Presenter (MVP)** pattern is a way of organizing code into three distinct parts:

### The Model
The **Model** represents your game's data and business logic. In our RPG, the `Hero` class is a model—it holds data about the hero (name, level, health) and will eventually contain logic for things like leveling up or taking damage.

Think of the Model as the "what"—what data exists in your game.

### The View
The **View** is what the player sees and interacts with—the graphical interface. In our game, the `GameScreen` class (with its Tkinter widgets) is the view.

Think of the View as the "how"—how the game looks and how the player interacts with it.

### The Presenter
The **Presenter** is the middleman that connects the Model and the View. It contains the game logic, responds to user actions, updates the model, and tells the view what to display.

Think of the Presenter as the "when"—when things happen and what to do about them.

Here's how they work together:

```
Player clicks a button → View notifies Presenter → Presenter updates Model → Presenter tells View to refresh display
```

This separation has huge benefits:
- **Easier to test**: You can test game logic without needing the GUI
- **Easier to modify**: You can change the GUI without touching game logic, or vice versa
- **Easier to understand**: Each part has a clear responsibility
- **Easier to collaborate**: Different programmers can work on different parts

## Understanding Interfaces (Abstract Base Classes)

Before we create our Presenter, we need to understand **interfaces**.

An interface is like a contract or a promise. It says: "Any class that implements this interface must have these specific methods."

Why is this useful? Imagine you're building a racing game with different types of vehicles: cars, motorcycles, boats. They all need to be able to `accelerate()` and `brake()`, but each does it differently. An interface lets you define that contract without specifying exactly how each vehicle does it.

In Python, we create interfaces using **Abstract Base Classes (ABC)**. Here's a simple example:

```python
from abc import ABC, abstractmethod

class Vehicle(ABC):
    @abstractmethod
    def accelerate(self):
        pass
    
    @abstractmethod
    def brake(self):
        pass

class Car(Vehicle):
    def accelerate(self):
        print("Car accelerating with gas pedal")
    
    def brake(self):
        print("Car braking with brake pedal")

class Boat(Vehicle):
    def accelerate(self):
        print("Boat accelerating with throttle")
    
    def brake(self):
        print("Boat slowing down by reducing throttle")
```

If you try to create a class that inherits from `Vehicle` but doesn't implement `accelerate()` and `brake()`, Python will give you an error. This ensures that all vehicles have the methods they're supposed to have.

## Understanding Type Hinting

As our code becomes more complex, it helps to be explicit about what types of data our functions expect and return. This is called **type hinting**.

Here's a simple example:

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"
```

The `: str` after `name` means "this parameter should be a string."
The `-> str` means "this function returns a string."

Type hints don't change how Python runs your code—they're like comments that help you (and other programmers) understand what types of data to use. Many code editors also use type hints to give you helpful warnings if you use the wrong type.

For more complex types, we import from the `typing` module:

```python
from typing import List, Dict, Optional

def get_hero_names(heroes: List[Hero]) -> List[str]:
    return [hero.name for hero in heroes]
```

This says: "give me a list of Hero objects, and I'll return a list of strings."

## Understanding Circular Import Problems

Before we look at our code, there's one more concept to understand: **circular imports**.

Imagine this scenario:
- File A imports something from File B
- File B imports something from File A

This creates a circular dependency that Python can't resolve, and your program will crash.

In our game, we have this problem:
- `session.py` needs to know about the `GameScreen` class (for type hinting)
- `main.py` needs to know about the `GameSession` class (to create a session)

Python provides a clever solution using `TYPE_CHECKING`. We'll see this in action shortly.

## Creating the Game Session Interface

Now let's create our Presenter! Create a new file called `session.py` next to your `main.py` and `hero.py` files.

Add the following code:

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import GameScreen

from hero import Hero


# presenter interface: defines the methods called from view to presenter
class IGameSession(ABC):
    @abstractmethod
    def start(self):
        pass
```

Let's break this down piece by piece:

### Import Statements

```python
from __future__ import annotations
```

This is a special import that allows us to use more modern type hinting syntax. Specifically, it lets us reference classes in type hints before they're fully defined, which helps avoid circular import issues.

```python
from abc import ABC, abstractmethod
```

These imports give us the tools to create abstract base classes (interfaces):
- `ABC` is the base class we inherit from to create an interface
- `abstractmethod` is a decorator that marks methods as required

```python
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import GameScreen
```

This is the solution to our circular import problem!

- `TYPE_CHECKING` is a special constant that is `True` only when type checkers (like the ones in code editors) are running
- When actually running the program, `TYPE_CHECKING` is `False`, so the import doesn't happen
- This means we can use `GameScreen` in type hints without actually importing it during runtime

This pattern lets us have type hints for better code completion and error checking, without causing circular import problems.

```python
from hero import Hero
```

We import our Hero class because we'll need to create a hero when the game starts.

### The IGameSession Interface

```python
class IGameSession(ABC):
    @abstractmethod
    def start(self):
        pass
```

Here we define our Presenter interface:

- `class IGameSession(ABC):` creates a new interface called `IGameSession` that inherits from `ABC`
  - The `I` prefix is a common convention meaning "Interface"
- `@abstractmethod` is a **decorator** that marks the `start` method as required
  - Any class that inherits from `IGameSession` must implement a `start` method
- `def start(self):` defines the method signature
- `pass` is a placeholder—we're not implementing the method here, just defining that it must exist

## Creating the GameSession Class

Now let's create the actual implementation. In the same `session.py` file, add this code below the interface:

```python
class GameSession(IGameSession):
    def __init__(self, view: GameScreen) -> None:
        super().__init__()
        self.hero = None
        self.view = view

    def start(self):
        self.hero = Hero("John")
```

Let's examine this carefully:

### Class Declaration

```python
class GameSession(IGameSession):
```

`GameSession` inherits from `IGameSession`, meaning it must implement all the abstract methods defined in the interface (in this case, the `start` method).

### The Constructor

```python
    def __init__(self, view: GameScreen) -> None:
```

This is our constructor with type hints:
- `view: GameScreen` means the `view` parameter should be a `GameScreen` object
- `-> None` means this method doesn't return anything (constructors never do)

```python
        super().__init__()
```

This line calls the parent class's constructor. Even though `IGameSession` doesn't have a custom `__init__`, it's good practice to call `super().__init__()` when working with inheritance.

```python
        self.hero = None
        self.view = view
```

We initialize two attributes:
- `self.hero = None` starts as `None` because we haven't created the hero yet
- `self.view = view` stores a reference to the view (the `GameScreen` object)

This `view` reference is crucial—it's how the Presenter will communicate with the View to update the display.

### The Start Method

```python
    def start(self):
        self.hero = Hero("John")
```

This implements the `start` method required by the interface. When called, it:
- Creates a new `Hero` object with the name "John"
- Stores it in `self.hero`

Right now it's simple, but later we'll add more initialization logic here—loading saved games, setting up the game world, etc.

## Connecting the Presenter to the View

Now we need to modify our `main.py` file to use the new `GameSession` class. Update your `GameScreen` class:

```python
import tkinter as tk

from session import GameSession, IGameSession

class GameScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PyRPG")
        self.geometry("1200x800")

        # Create main layout
        self.create_layout()

        self.session: IGameSession = GameSession(self)
        self.session.start()

    # ... rest of your existing code (create_layout, etc.)
```

Let's look at what changed:

### Import Statement

```python
from session import GameSession, IGameSession
```

We import both the interface (`IGameSession`) and the implementation (`GameSession`).

### Creating the Session

```python
        self.session: IGameSession = GameSession(self)
```

This line does several important things:
- `self.session` creates an attribute to store our game session
- `: IGameSession` is a type hint saying this attribute should be an `IGameSession` interface
- `= GameSession(self)` creates a new `GameSession` object
- `(self)` passes the `GameScreen` itself as the `view` parameter

Notice we're passing `self`—the GameScreen object—to the GameSession constructor. This gives the Presenter a reference to the View.

### Starting the Game

```python
        self.session.start()
```

We call the `start` method to initialize the game session, which creates the hero.

## Why Use an Interface Here?

You might wonder: why create an `IGameSession` interface when we only have one `GameSession` implementation?

Good question! Here are the reasons:

1. **Future flexibility**: Later, you might want different types of game sessions (tutorial mode, versus mode, story mode). The interface makes it easy to swap implementations.

2. **Better code organization**: The interface clearly documents what methods the session must have.

3. **Easier testing**: You can create a mock session for testing without needing the full implementation.

4. **Professional practice**: This is how professional software is structured, especially for larger projects.

Think of it as planning ahead—we're building a foundation that can grow with our game.

## Understanding the Flow

Let's trace what happens when our game starts:

1. Python creates a `GameScreen` object
2. `GameScreen.__init__` runs:
   - Sets up the window
   - Creates the layout
   - Creates a `GameSession`, passing itself (`self`) as the view
3. `GameSession.__init__` runs:
   - Stores the reference to the view
   - Sets `hero` to `None`
4. `session.start()` is called:
   - Creates a new `Hero` named "John"
   - Stores it in `self.hero`

Now we have:
- A View (GameScreen) that can display things
- A Presenter (GameSession) that manages game logic
- A Model (Hero) that stores game data
- The View and Presenter connected to each other

## What's Next?

Right now, we're creating a hero named "John" automatically, but the player can't see or interact with it yet. In the next lessons, we'll:

1. Add methods to display the hero's information in the GUI
2. Create buttons and interactions that call methods on the Presenter
3. Have the Presenter update the Model and tell the View to refresh

This MVP pattern might seem like extra work now, but as our game grows more complex—with combat, inventory, quests, and more—you'll see how this structure keeps everything organized and manageable.

You're learning to think and code like a professional game developer. Each piece we add is building toward a solid, maintainable game engine!

Link to GitHub commit for this code:
[here](https://github.com/euanrussano/PyRPG/commit/f16c708f3159e9521dc5dc9dcc6e067675453780)