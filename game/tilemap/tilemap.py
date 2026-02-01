from abc import ABC, abstractmethod
from typing import List
import random

from core.itemdefinition import ItemRepository
from tilemap.event import ChangeTileEvent, CompositeEvent, MapEvent, GiveGoldEvent, ShowMessageEvent, AddItemEvent, \
    IfEvent, HasItemCondition, DeactivateEvent, RemoveItemEvent, RandomMovementStrategy, MovementStrategy

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

class ForestTilemapFactory(TilemapFactory):
    def create(self, place_random_chests:bool = False, place_sign:bool = False, place_key:bool = False) -> 'Tilemap':
        
        random.seed(1)

        width = 10
        height = 10
        tileset: Tileset = get_tileset()
        tiles = []
        events = []
        for i in range(width):    
            row = []
            for j in range(height):
                id = TileID.EMPTY
                if random.random() < 0.3:
                    id = random.choice(TREES)
                elif place_random_chests:
                    if random.random() < 0.1:
                        gold_amount = random.randint(1, 3)
                        event = CompositeEvent([
                            ShowMessageEvent("You found a chest!"),
                            GiveGoldEvent(gold_amount),
                            ShowMessageEvent(f"You got {gold_amount} gold"),
                            ChangeTileEvent(tileset.get_tile(TileID.EMPTY)),
                        ])
                        map_event = MapEvent(i, j, tileset.get_tile(TileID.CHEST_CLOSED))
                        map_event.set_event(event)
                        events.append(map_event)
                elif place_sign:
                    if random.random() < 0.1:
                        map_event = MapEvent(i, j)
                        map_event.run_once = False
                        map_event.tile = tileset.get_tile(TileID.SIGN)
                        event = ShowMessageEvent("You found a sign!")
                        map_event.set_event(event)
                        events.append(map_event)
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
                    map_event = MapEvent(x, y)
                    map_event.tile = tileset.get_tile(TileID.KEY)
                    event = CompositeEvent([
                        ShowMessageEvent("You found a key!"),
                        ChangeTileEvent(tileset.get_tile(TileID.EMPTY)),
                        AddItemEvent(ItemRepository.get_instance().find_by_id(TileID.KEY))
                    ])
                    map_event.set_event(event)
                    events.append(map_event)
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
            for _ in range(10):
                id = TileID.EMPTY
                row.append(tileset.get_tile(id))
            tiles.append(row)
        
        # create 4 buildings
        self.create_building(tiles, events, 2, 2, 4, 4, door_type=DoorType.SIMPLE)
        self.create_building(tiles, events, 7, 2, 3, 3, door_type=DoorType.LOCKED)
        self.create_building(tiles, events, 2, 7, 3, 3)
        self.create_building(tiles, events, 7, 7, 3, 3)

        # create john the greeter
        folk = self.create_folk(1, 1, tile_id=TileID.FOLK_1, greet="Hey I'm John. Nice day btw...", movement = RandomMovementStrategy())
        events.append(folk)
        
    
        return Tilemap(tiles, events)
    
    def create_building(self, tiles: List[List['Tile']], events: List['MapEvent'], x: int, y: int, width: int, height: int, door_type: DoorType = DoorType.CLOSED):
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
            map_event = MapEvent(x+1, y)
            map_event.tile = tileset.get_tile(TileID.BUILDING_DOOR_CLOSED)
            event = CompositeEvent([
                ChangeTileEvent(tileset.get_tile(TileID.BUILDING_DOOR_OPEN)),
                ShowMessageEvent("You opened the door")
            ])
            map_event.set_event(event)
            events.append(map_event)
        elif door_type == DoorType.CLOSED:
            id = TileID.BUILDING_DOOR_CLOSED
            tiles[x+1][y] = tileset.get_tile(id)
        elif door_type == DoorType.OPEN:
            id = TileID.BUILDING_DOOR_OPEN
            tiles[x + 1][y] = tileset.get_tile(id)
        elif door_type == DoorType.LOCKED:
            tiles[x + 1][y] = tileset.get_tile(TileID.EMPTY)
            map_event = MapEvent(x+1, y)
            map_event.tile = tileset.get_tile(TileID.BUILDING_DOOR_CLOSED)
            event = IfEvent(
                condition=HasItemCondition(TileID.KEY),
                then_event=CompositeEvent([
                    RemoveItemEvent(TileID.KEY),
                    ShowMessageEvent("You unlocked the door."),
                    ChangeTileEvent(tileset.get_tile(TileID.BUILDING_DOOR_OPEN)),
                    DeactivateEvent()
                ]),
                else_event=ShowMessageEvent("The door is locked.")
            )

            map_event.set_event(event)
            map_event.run_once = False
            events.append(map_event)
        
        # Window on the bottom wall if there's room
        if x+2 < x+width:
            tiles[x+2][y] = tileset.get_tile(TileID.BUILDING_WINDOW)

    def create_folk(self, x: int, y: int, tile_id: TileID, greet: str, movement: MovementStrategy) -> MapEvent:
        map_event = MapEvent(x, y)
        map_event.tile = get_tileset().get_tile(tile_id)
        map_event.run_once = False
        event = ShowMessageEvent(greet)
        map_event.set_event(event)
        map_event.movement = movement
        return map_event


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
    def __init__(self, tiles: List[List[Tile]], events: List[MapEvent] = ()):
        self.tiles = tiles
        self.width = len(tiles)
        self.height = len(tiles[0])

        self.events = events

    def has_tile(self, x: int, y: int):
        return x >= 0 and x < self.width and y >= 0 and y < self.height

    def get_tile(self, x: int, y: int):
        if not self.has_tile(x, y): 
            return Tile(TileID.EMPTY)
        return self.tiles[x][y]
    
    def get_map_event(self, x: int, y: int) -> MapEvent | None:
        if not self.has_tile(x, y): 
            return None
        map_event = next((map_event for map_event in self.events if map_event.x == x and map_event.y == y), None)
        return map_event
    
    def is_blocked(self, new_x: int, new_y: int):
        if not self.has_tile(new_x, new_y): 
            return True
        if not self.get_tile(new_x, new_y).is_walkable: 
            return True
        map_event = self.get_map_event(new_x, new_y)
        if map_event and not map_event.is_walkable:
            return True
        return False