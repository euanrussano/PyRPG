from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from tilemap.tilemap import Tilemap, TilemapLoader
from .world import Location, World, WorldFactory
if TYPE_CHECKING:
    from main import GameScreen

from .hero import Hero


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
        self.hero: Hero = Hero("John")
        self.view = view
        self.world = WorldFactory().create()
        loc = self.world.get_location(0, 0)
        assert loc is not None
        self.current_location: Location = loc

    def start(self):
        self.view.update_hero_stats(self.hero)
        self.view.render(self.current_location, self.hero)
        
    def move_hero(self, dx: int, dy: int):
        if self.hero is None:
            return
        # can only move by one tile
        if abs(dx) > 1 or abs(dy) > 1:
            return
        # do not allow diagonal movement
        if abs(dx) + abs(dy) != 1:
            return
        
        # "predict" new position for checking
        new_x = self.hero.x + dx
        new_y = self.hero.y + dy
        
        # try and trigger event if there is one
        self.try_trigger_event(new_x, new_y)

        if new_x < 0 or new_x >= self.current_location.tilemap.width:
            self._try_change_location(dx, dy)
            return
        elif new_y < 0 or new_y >= self.current_location.tilemap.height:
            self._try_change_location(dx, dy)
            return
        
        if self.current_location.tilemap.is_blocked(new_x, new_y):
            return
        
        self.hero.x += dx
        self.hero.y += dy
        
        self.view.render(self.current_location, self.hero)

    def move_down(self, event):
        self.move_hero(0, -1)
        

    def move_up(self, event):
        self.move_hero(0, 1)
        
    def move_left(self, event):
        self.move_hero(-1, 0)
        
    def move_right(self, event):
        self.move_hero(1, 0)

    def _try_change_location(self, dx: int, dy: int) -> None:
        location = self.current_location
        hero = self.hero

        new_global_x = location.x + dx
        new_global_y = location.y + dy

        new_location = self.world.get_location(new_global_x, new_global_y)
        if new_location is None:
            return

        self.current_location = new_location

        tilemap = new_location.tilemap

        if dx != 0:
            hero.x = 0 if dx > 0 else tilemap.width - 1
        if dy != 0:
            hero.y = 0 if dy > 0 else tilemap.height - 1

        self.view.render(new_location, hero)

    def try_trigger_event(self, x: int, y: int):
        tilemap = self.current_location.tilemap
        event_tile = tilemap.get_event_tile(x, y)
        if event_tile.has_event():
            event_tile.trigger(self)

    def add_message(self, msg: str):
        # TODO()
        pass

    
