from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from tilemap.tile_ids import TileID
from tilemap.tilemap import Tilemap, TilemapLoader
from .itemdefinition import ItemDefinition, ItemInstance
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

    @abstractmethod
    def update(self, delta: int):
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

    def update(self, delta: int):
        for map_event in self.current_location.tilemap.events:
            dx, dy = map_event.update(delta)
            nx = map_event.x + dx
            ny = map_event.y + dy

            if nx < 0 or nx >= self.current_location.tilemap.width:
                dx = 0
            elif ny < 0 or ny >= self.current_location.tilemap.height:
                dy = 0

            if self.current_location.tilemap.is_blocked(nx, ny):
                dx = 0
                dy = 0

            # do not move if hero is adjacent to current position
            if self.hero.x in range(map_event.x-1, map_event.x+2) and self.hero.y in range(map_event.y-1, map_event.y+2):
                dx = 0
                dy = 0
                
            # do not move if hero overlaps
            if self.hero.x in range(nx-1, nx+2) and self.hero.y in range(ny-1, ny+2):
                dx = 0
                dy = 0


            map_event.x += dx
            map_event.y += dy

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
        map_event = tilemap.get_map_event(x, y)
        if not map_event: return

        if map_event.has_event():
            map_event.trigger(self)

            self.view.render(self.current_location, self.hero)

    def add_message(self, msg: str):
        self.hero.add_diary_entry(msg)
        self.view.update_diary(self.hero)

    def add_gold(self, amount: int):
        self.hero.add_gold(amount)
        self.view.update_hero_stats(self.hero)

    def add_item(self, item: ItemDefinition):
        item_instance = ItemInstance(item)
        self.hero.add_item(item_instance)
        self.view.update_inventory(self.hero)

    def remove_item(self, item_id: TileID):
        self.hero.remove_item(item_id)
        self.view.update_inventory(self.hero)

    
