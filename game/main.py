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

if __name__ == "__main__":
    view = GameScreen()
    view.mainloop()
        
    
    