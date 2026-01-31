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