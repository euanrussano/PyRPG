from abc import ABC, abstractmethod
from typing import List
import random

from core.itemdefinition import ItemRepository
from tilemap.event import ChangeTileEvent, CompositeEvent, EventTile, GiveGoldEvent, ShowMessageEvent, AddItemEvent, \
    IfEvent, HasItemCondition, DeactivateEvent

from .tile_ids import TREES, TileID
from .tileset import Tile, Tileset, get_tileset

class TilemapFactory(ABC):
    @abstractmethod
    def create(self) -> 'Tilemap':
        pass

    @staticmethod
    def create_empty_tiles(width: int, height: int) -> List[List['Tile']]:
        tileset: Tileset = get_tileset()
        tiles = []
        for _ in range(width):    
            row = []
            for _ in range(height):
                row.append(tileset.get_tile(TileID.EMPTY))
            tiles.append(row)
        return tiles

    @staticmethod
    def create_empty_events(width: int, height: int) -> List[List['EventTile']]:
        events = []
        for _ in range(width):    
            row = []
            for _ in range(height):
                row.append(EventTile())
            events.append(row)
        return events

class ForestTilemapFactory(TilemapFactory):
    def create(self, place_random_chests:bool = False, place_sign:bool = False, place_key:bool = False) -> 'Tilemap':
        
        random.seed(1)

        width = 10
        height = 10
        tileset: Tileset = get_tileset()
        tiles = []
        events = TilemapFactory.create_empty_events(width, height)
        for i in range(width):    
            row = []
            for j in range(height):
                id = TileID.EMPTY
                if random.random() < 0.3:
                    id = random.choice(TREES)
                elif place_random_chests:
                    if random.random() < 0.1:
                        gold_amount = random.randint(1, 3)
                        events[i][j].tile = tileset.get_tile(TileID.CHEST_CLOSED)
                        event = CompositeEvent([
                            ShowMessageEvent("You found a chest!"),
                            GiveGoldEvent(gold_amount),
                            ShowMessageEvent(f"You got {gold_amount} gold"),
                            ChangeTileEvent(tileset.get_tile(TileID.EMPTY)),
                        ])  
                        events[i][j].set_event(event)
                elif place_sign:
                    if random.random() < 0.1:
                        events[i][j].run_once = False
                        events[i][j].tile = tileset.get_tile(TileID.SIGN)
                        event = ShowMessageEvent("You found a sign!")
                        events[i][j].set_event(event)
                        # only place max one sign
                        place_sign = False
                
                row.append(tileset.get_tile(id))
            tiles.append(row)

        if place_key:
            is_key_placed = False
            max_tries = 100
            trial = 0
            while not is_key_placed:
                trial += 1
                if trial > max_tries:
                    break
                x = random.randint(0, width-1)
                y = random.randint(0, height-1)
                if tiles[x][y].id == TileID.EMPTY:
                    events[x][y].tile = tileset.get_tile(TileID.KEY)
                    event = CompositeEvent([
                        ShowMessageEvent("You found a key!"),
                        ChangeTileEvent(tileset.get_tile(TileID.EMPTY)),
                        AddItemEvent(ItemRepository.get_instance().find_by_id(TileID.KEY))
                    ])
                    events[x][y].set_event(event)
                    is_key_placed = True
        return Tilemap(tiles, events)

from enum import Enum, auto

class DoorType(Enum):
    OPEN = auto()        # open passage
    CLOSED = auto()      # closed passage
    SIMPLE = auto()      # opens by bumping
    LOCKED = auto()      # needs a key

class TownTilemapFactory(TilemapFactory):
    def create(self) -> 'Tilemap':
        tileset: Tileset = get_tileset()
        tiles = []
        events = []
        for _ in range(10):    
            row = []
            event_row = []
            for _ in range(10):
                id = TileID.EMPTY
                row.append(tileset.get_tile(id))
                event_row.append(EventTile())
            tiles.append(row)
            events.append(event_row)
        
        # create 4 buildings
        self.create_building(tiles, events, 2, 2, 4, 4, door_type=DoorType.SIMPLE)
        self.create_building(tiles, events, 7, 2, 3, 3, door_type=DoorType.LOCKED)
        self.create_building(tiles, events, 2, 7, 3, 3)
        self.create_building(tiles, events, 7, 7, 3, 3)
        
    
        return Tilemap(tiles, events)
    
    def create_building(self, tiles: List[List['Tile']], events: List[List['EventTile']], x: int, y: int, width: int, height: int, door_type: DoorType = DoorType.CLOSED):
        """
        Create a building with y-axis pointing up
        (x, y) is the bottom-left corner of the building
        """
        tileset: Tileset = get_tileset()
        # 4 corners (bottom-left, bottom-right, top-left, top-right)
        tiles[x][y] = tileset.get_tile(TileID.BUILDING_CORNER_BL)  # Bottom-left
        tiles[x+width-1][y] = tileset.get_tile(TileID.BUILDING_CORNER_BR)  # Bottom-right
        tiles[x][y+height-1] = tileset.get_tile(TileID.BUILDING_CORNER_TL)  # Top-left
        tiles[x+width-1][y+height-1] = tileset.get_tile(TileID.BUILDING_CORNER_TR)  # Top-right
        
        # Vertical walls (left and right)
        for i in range(y+1, y+height-1):
            tiles[x][i] = tileset.get_tile(TileID.BUILDING_WALL_LEFT)
            tiles[x+width-1][i] = tileset.get_tile(TileID.BUILDING_WALL_RIGHT)
        
        # Horizontal walls (bottom and top)
        for i in range(x+1, x+width-1):
            tiles[i][y] = tileset.get_tile(TileID.BUILDING_WALL_HORIZONTAL)  # Bottom wall
            tiles[i][y+height-1] = tileset.get_tile(TileID.BUILDING_WALL_HORIZONTAL)  # Top wall

        # Door on the bottom wall
        if door_type == DoorType.SIMPLE:
            tiles[x+1][y] = tileset.get_tile(TileID.EMPTY)
            events[x+1][y].tile = tileset.get_tile(TileID.BUILDING_DOOR_CLOSED)
            event = CompositeEvent([
                ChangeTileEvent(tileset.get_tile(TileID.BUILDING_DOOR_OPEN)),
                ShowMessageEvent("You opened the door")
            ])
            events[x+1][y].set_event(event)
        elif door_type == DoorType.CLOSED:
            id = TileID.BUILDING_DOOR_CLOSED
            tiles[x+1][y] = tileset.get_tile(id)
        elif door_type == DoorType.OPEN:
            id = TileID.BUILDING_DOOR_OPEN
            tiles[x + 1][y] = tileset.get_tile(id)
        elif door_type == DoorType.LOCKED:
            tiles[x + 1][y] = tileset.get_tile(TileID.EMPTY)
            events[x + 1][y].tile = tileset.get_tile(TileID.BUILDING_DOOR_CLOSED)
            event = IfEvent(
                condition=HasItemCondition(TileID.KEY),
                then_event=CompositeEvent([
                    ShowMessageEvent("You unlocked the door."),
                    ChangeTileEvent(tileset.get_tile(TileID.BUILDING_DOOR_OPEN)),
                    DeactivateEvent()
                ]),
                else_event=ShowMessageEvent("The door is locked.")
            )

            events[x+1][y].set_event(event)
            events[x+1][y].run_once = False
        
        # Window on the bottom wall if there's room
        if x+2 < x+width:
            tiles[x+2][y] = tileset.get_tile(TileID.BUILDING_WINDOW)
        
        

class TilemapLoader:
    def load(self, filename: str) -> 'Tilemap':
        tiles = []
        tileset = get_tileset()
        with open(filename, 'r') as f:
            for line in f:
                row = []
                for c in line.split(","):
                    id = TileID(int(c))
                    row.append(tileset.get_tile(id))
                tiles.append(row)
        return Tilemap(tiles)

class Tilemap:
    def __init__(self, tiles: List[List[Tile]], events: List[List[EventTile]] | None = None):
        self.tiles = tiles
        self.width = len(tiles)
        self.height = len(tiles[0])

        if events is None:
            self.events = [[EventTile() for _ in range(self.height)] for _ in range(self.width)]
        else:
            assert(len(events) == self.width and len(events[0]) == self.height)
            self.events = events

    def has_tile(self, x: int, y: int):
        return x >= 0 and x < self.width and y >= 0 and y < self.height

    def get_tile(self, x: int, y: int):
        if not self.has_tile(x, y): 
            return Tile(TileID.EMPTY)
        return self.tiles[x][y]
    
    def get_event_tile(self, x: int, y: int):
        if not self.has_tile(x, y): 
            return EventTile()
        return self.events[x][y]
    
    def is_blocked(self, new_x: int, new_y: int):
        if not self.has_tile(new_x, new_y): 
            return True
        if not self.get_tile(new_x, new_y).is_walkable: 
            return True
        if not self.events[new_x][new_y].is_walkable:
            return True
        return False