from abc import ABC, abstractmethod
from typing import List
import random

from .tile_ids import TREES, TileID
from .tileset import Tile, Tileset, get_tileset

class TilemapFactory(ABC):
    @abstractmethod
    def create(self) -> 'Tilemap':
        pass

class ForestTilemapFactory(TilemapFactory):
    def create(self) -> 'Tilemap':
        tileset: Tileset = get_tileset()
        tiles = []
        for _ in range(10):    
            row = []
            for _ in range(10):
                id = TileID.EMPTY
                if random.random() < 0.3:
                    id = random.choice(TREES)
                row.append(tileset.get_tile(id))
            tiles.append(row)
        return Tilemap(tiles)

class TownTilemapFactory(TilemapFactory):
    def create(self) -> 'Tilemap':
        tileset: Tileset = get_tileset()
        tiles = []
        for _ in range(10):    
            row = []
            for _ in range(10):
                id = TileID.EMPTY
                row.append(tileset.get_tile(id))
            tiles.append(row)
        
        # create 4 buildings
        self.create_building(tiles, 2, 2, 4, 4, True)
        self.create_building(tiles, 7, 2, 3, 3)
        self.create_building(tiles, 2, 7, 3, 3)
        self.create_building(tiles, 7, 7, 3, 3)
        
    
        return Tilemap(tiles)
    
    def create_building(self, tiles: List[List['Tile']], x: int, y: int, width: int, height: int, is_door_open:bool = False):
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
        id = TileID.BUILDING_DOOR_OPEN if is_door_open else TileID.BUILDING_DOOR_CLOSED
        tiles[x+1][y] = tileset.get_tile(id)
        
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
    def __init__(self, tiles: List[List[Tile]]):
        self.tiles = tiles
        self.width = len(tiles)
        self.height = len(tiles[0])

    def has_tile(self, x: int, y: int):
        return x >= 0 and x < self.width and y >= 0 and y < self.height

    def get_tile(self, x: int, y: int):
        if not self.has_tile(x, y): 
            return Tile(TileID.EMPTY)
        return self.tiles[x][y]
    
    def is_blocked(self, new_x: int, new_y: int):
        if not self.has_tile(new_x, new_y): 
            return True
        return not self.get_tile(new_x, new_y).is_walkable