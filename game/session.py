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
        self.hero = None
        self.view = view

    def start(self):
        self.hero = Hero("John")
        