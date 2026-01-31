from abc import ABC, abstractmethod
from typing import List, Optional

from tilemap.tileset import Tile

class Event(ABC):
    def __init__(self):
        self.owner: Optional['EventTile'] = None
    @abstractmethod
    def trigger(self, session):
        pass


class CompositeEvent(Event):
    def __init__(self, events: List[Event]):
        super().__init__()
        self.events = events
        # TODO(set owner eariler setter)

    def trigger(self, session):
        for event in self.events:
            event.owner = self.owner
            event.trigger(session)


class ShowMessageEvent(Event):
    def __init__(self, message: str):
        super().__init__()
        self.message = message

    def trigger(self, session):
        session.add_message(self.message)


class ChangeTileEvent(Event):
    def __init__(self, tile: Tile):
        super().__init__()
        self.tile = tile

    def trigger(self, session):
        if self.owner :
            self.owner.tile = self.tile
        


class EventTile:
    def __init__(self, tile: Optional[Tile] = None, event: Optional[Event] = None):
        self.tile = tile
        self.__event = None

        if event is not None:
            self.set_event(event)

    @property
    def is_walkable(self):
        if self.tile is None:
            return True
        return self.tile.is_walkable
    
    def set_event(self, event: Event):
        self.__event = event
        self.__event.owner = self

    def has_event(self):
        return self.__event is not None
    
    def trigger(self, session):
        if self.__event is not None:
            self.__event.trigger(session)

        # for now events run once
        self.__event = None