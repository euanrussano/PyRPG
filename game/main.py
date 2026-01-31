import tkinter as tk
from typing import List
from PIL import Image, ImageTk

from session import GameSession, IGameSession
from tilemap import Tile, TilemapFactory
from tileset import Tileset
import config

class GameScreen(tk.Tk):
    def __init__(self, viewport_width=10, viewport_height=10):
        super().__init__()
        self.title("PyRPG")
        self.geometry("1200x800")
        self.viewport = (viewport_width, viewport_height)

        self.hero_sprite = None
        self.tile_size = 64  # Default tile size, will be recalculated after layout

        # Create main layout
        self.create_layout()

        # Force the window to update and calculate actual sizes
        self.update_idletasks()
        
        # Now calculate the actual tile size based on rendered canvas
        self.calculate_tile_size()

        # Create tileset
        self.tileset = Tileset(self.tile_size)        

        # Load sprites (now tile_size has a proper value)
        self.load_hero_sprite()

        self.session: IGameSession = GameSession(self)

        # Bind key events
        self.bind("<Up>", self.session.move_up)
        self.bind("<Down>", self.session.move_down)
        self.bind("<Left>", self.session.move_left)
        self.bind("<Right>", self.session.move_right)

        self.session.start()

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

    def load_hero_sprite(self):
        self.hero_photo = self.tileset.get_tile(config.hero_sprite)
    
    def update_hero_position(self, world_x: int, world_y: int):
        """Update hero sprite position"""
        x = world_x * self.tile_size
        y = world_y * self.tile_size
        
        if self.hero_sprite:
            self.canvas.delete(self.hero_sprite)
        self.hero_sprite = self.canvas.create_image(x, y, image=self.hero_photo, anchor='nw')
        

    def update_hero_stats(self, name: str, level: int, xp: int, gold: int, energy: int):
        self.hero_name_label.config(text=f"{name}")
        self.hero_level_label.config(text=f"{level}")
        self.hero_xp_label.config(text=f"{xp}")
        self.hero_gold_label.config(text=f"{gold}")
        self.hero_energy_label.config(text=f"{energy}")

    def update_tilemap(self, width: int, height: int, tiles: List[List[Tile]]):
        self.canvas.delete(tk.ALL)
        for x in range(width):
            for y in range(height):
                tile = tiles[x][y]
                if tile.id == -1:
                    continue
                tile_img = self.tileset.get_tile(tile.id)
                self.canvas.create_image(x * self.tile_size, y * self.tile_size, image=tile_img, anchor='nw')
        
    def create_layout(self):
        """Create the main UI layout"""
        main_container = tk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Define a grid 2x3 (2 rows and 3 columns)
        main_container.columnconfigure(0, weight=10, minsize=200)
        main_container.columnconfigure(1, weight=15, minsize=200)
        main_container.columnconfigure(2, weight=10, minsize=200)
        main_container.rowconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)
        
        # Left top panel (Stats)
        left_top_panel = tk.Frame(main_container, bg='green')
        left_top_panel.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        
        # Center top panel (Canvas)
        center_top_panel = tk.Frame(main_container, bg='black')
        center_top_panel.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        
        # Right top panel (Diary)
        right_top_panel = tk.Frame(main_container, bg='lightyellow')
        right_top_panel.grid(row=0, column=2, sticky='nsew', padx=5, pady=5)

        # Left bottom panel (Inventory/Quests)
        left_bottom_panel = tk.Frame(main_container, bg='red')
        left_bottom_panel.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)

        # Center bottom panel (Controls)
        center_bottom_panel = tk.Frame(main_container, bg='white')
        center_bottom_panel.grid(row=1, column=1, columnspan=2, sticky='nsew', padx=5, pady=5)

        self.create_center_top_panel(center_top_panel)
        self.create_left_top_panel(left_top_panel)
        # self.create_right_top_panel(right_top_panel)
        # self.create_left_bottom_panel(left_bottom_panel)
        # self.create_center_bottom_panel(center_bottom_panel)

    def create_left_top_panel(self, parent):
        # Configure parent
        parent.configure(bg='green')
    
        # Create a common style config
        label_config = {'bg': 'green', 'anchor': 'w'}
        grid_config = {'padx': 5, 'pady': 5, 'sticky': 'w'}
        # hero stats widgets
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
        self.hero_gold_label.grid(row=3, column=1, padx=5, pady=5,sticky='w')
        
        tk.Label(parent, text="Energy: ", **label_config).grid(row=4, column=0, **grid_config)
        self.hero_energy_label = tk.Label(parent, text="<energy here>", **label_config)
        self.hero_energy_label.grid(row=4, column=1, **grid_config)

    def create_center_top_panel(self, parent):
        # Give the canvas a reasonable initial size
        self.canvas = tk.Canvas(parent, bg='black', highlightthickness=2, 
                               highlightbackground='black')
        self.canvas.pack(fill=tk.BOTH, expand=True, pady=10)

if __name__ == "__main__":
    view = GameScreen()
    view.mainloop()

    