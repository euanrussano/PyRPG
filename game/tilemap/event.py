from abc import ABC, abstractmethod
from typing import List, Optional

from core.itemdefinition import ItemDefinition
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
        

class GiveGoldEvent(Event):
    def __init__(self, amount: int):
        super().__init__()
        self.amount = amount

    def trigger(self, session):
        session.add_gold(self.amount)

class AddItemEvent:
    def __init__(self, item: ItemDefinition):
        super().__init__()
        self.item = item

    def trigger(self, session):
        session.add_item(self.item)

class DeactivateEvent(Event):
    def __init__(self):
        super().__init__()

    def trigger(self, session):
        if self.owner:
            self.owner.is_active = False

class Condition(ABC):
    @abstractmethod
    def is_met(self, session) -> bool:
        pass

from tilemap.tile_ids import TileID

class HasItemCondition(Condition):
    def __init__(self, item_id: TileID):
        self.item_id = item_id

    def is_met(self, session) -> bool:
        for item in session.hero.inventory:
            if item.item_definition.id == self.item_id:
                return True
        return False

class IfEvent(Event):
    def __init__(
        self,
        condition: Condition,
        then_event: Event,
        else_event: Event | None = None
    ):
        super().__init__()
        self.condition = condition
        self.then_event = then_event
        self.else_event = else_event

    def trigger(self, session):
        # ensure child events know who owns the tile
        self.then_event.owner = self.owner
        if self.else_event:
            self.else_event.owner = self.owner

        if self.condition.is_met(session):
            self.then_event.trigger(session)
        elif self.else_event is not None:
            self.else_event.trigger(session)


class EventTile:
    def __init__(self, tile: Optional[Tile] = None, event: Optional[Event] = None, run_once:bool=True):
        self.tile = tile
        self.__event = None
        self.run_once = run_once
        self.is_active = True

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
        if not self.is_active: return

        if self.__event is not None:
            self.__event.trigger(session)

        # for now events run once
        if self.run_once:
            self.__event = None