from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from tilemap import Tilemap, TilemapLoader
from world import Location, World
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

    @abstractmethod
    def change_location(self, loc_id: int):
        pass

class GameSession(IGameSession):
    def __init__(self, view: GameScreen) -> None:
        super().__init__()
        self.hero: Hero | None = None
        self.view = view
        self.world = World.create()
        loc = self.world.get_location(0, 0)
        assert loc is not None
        self.current_location: Location = loc

    def start(self):
        tilemap = self.current_location.tilemap
        self.view.update_tilemap(tilemap.width, tilemap.height, tilemap.tiles)
        
        self.hero = Hero("John")
        self.view.update_hero_position(self.hero.x, self.hero.y)
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
        
        self.view.render()

    def move_down(self, event):
        self.move_hero(0, 1)
        

    def move_up(self, event):
        self.move_hero(0, -1)
        
    def move_left(self, event):
        self.move_hero(-1, 0)
        
    def move_right(self, event):
        self.move_hero(1, 0)

    def change_location(self, loc_id: int):
        loc = self.world.get_location_by_id(loc_id)
        if loc is None:
            return
        self.current_location = loc
        self.view.render(self.current_location, self.hero)
    
