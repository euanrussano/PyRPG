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
    
