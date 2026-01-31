from abc import ABC
from typing import Optional

from tilemap.tileset import Tile

class Event(ABC):
    pass

class EventTile:
    def __init__(self, tile: Optional[Tile] = None, event: Optional[Event] = None):
        self.event = event
        self.tile = tile

    @property
    def is_walkable(self):
        if self.tile is None:
            return True
        print("here")
        return self.tile.is_walkable