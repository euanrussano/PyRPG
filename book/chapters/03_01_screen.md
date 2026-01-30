# Creating the Game Screen

In this lesson, we'll start to create the game by creating the screen. For that, we will use Tkinter, a Python library for creating GUIs. I chose Tkinter, becuase is part of the standard Python distribution and is easy to use. 

## A short introduction to Tkinter

Tkinter is a Python binding to the Tk GUI toolkit. It is the standard Python interface to Tk and is bundled with most standard Python distributions.

Tkinter is event driven, meaning that programs react to events such as button clicks and key presses. Programmers write functions that are called when an event occurs, for example when a button is clicked. This makes it easy to write programs that are interactive and responsive.

The main concept of Tkinter is that of a widget. A widget is a small part of the graphical user interface such as a button, label, or text box. Widgets are arranged in a hierarchical structure, with a single root widget at the top of the hierarchy. This root widget is the main window of the application and all other widgets are children of this root widget.

Widgets communicate with each other by sending events. For example, when a button is clicked, it sends a click event to its parent widget, which can then react to this event. This makes it easy to write programs that are composed of many different widgets that interact with each other.

## Creating the game screen

Now that you understand a bit better what Tkinter is and how it works, let's create the game screen. 

Clean up the code you previously had in your `main.py` file. Now let's start by importing the `tkinter` library:

```python
import tkinter as tk
```

Now we can create a window by defining a class that inherits from the `tk.Tk` class. Let's call it `GameScreen`:

```python
class GameScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PyRPG")
        self.geometry("1200x800")
```

To run the game, we need to create an instance of the `GameScreen` class. At the very bottom of the file, add the following code:

```python
game_screen = GameScreen()
game_screen.mainloop()
```

If you run it now, you should see a window with the title "PyRPG" and a size of 1200x800. The screen is empty but we will start filling it soon.

Coming back to the `GameScreen` class, we will visualize the different panels that we will use to visualize the map, the stats, the inventory, etc. For that, add a method `create_layout()` that will create the different panels and place them in the window.

```python
class GameScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PyRPG")
        self.geometry("1200x800")

        # Create main layout
        self.create_layout()
        
    def create_layout(self):
        """Create the main UI layout"""
        main_container = tk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Define a grid 2x3 (2 rows and 3 columns)
        main_container.columnconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=2)
        main_container.columnconfigure(2, weight=1)
        main_container.rowconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)
        
        # Left top panel (Stats)
        left_top_panel = tk.Frame(main_container, bg='green')
        left_top_panel.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        
        # Center top panel (Canvas)
        center_top_panel = tk.Frame(main_container, bg = 'black')
        center_top_panel.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        
        # Right top panel (Diary)
        right_top_panel = tk.Frame(main_container, bg='lightyellow')
        right_top_panel.grid(row=0, column=2, sticky='nsew', padx=5, pady=5)

        # Left bottom panel (Inventory/Quests)
        left_bottom_panel = tk.Frame(main_container, bg='red')
        left_bottom_panel.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)

        # Center bottom panel (Controls)
        center_bottom_panel = tk.Frame(main_container, bg = 'white')
        center_bottom_panel.grid(row=1, column=1, columnspan=2, sticky='nsew', padx=5, pady=5)
```


Now if you run the code, you should see the main window with the different panels, colored in different colors. If you don't see them, check again the code above and make sure you didn't miss anything.


