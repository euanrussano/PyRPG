from abc import ABC, abstractmethod
from typing import List
import random

class TilemapFactory(ABC):
    @abstractmethod
    def create(self) -> 'Tilemap':
        pass

class ForestTilemapFactory(TilemapFactory):
    def create(self) -> 'Tilemap':
        tiles = []
        for _ in range(10):    
            row = []
            for _ in range(10):
                id = -1
                if random.random() < 0.3:
                    id = random.choice([84, 85, 86])
                row.append(Tile(id))
            tiles.append(row)
        return Tilemap(tiles)

class TownTilemapFactory(TilemapFactory):
    def create(self) -> 'Tilemap':
        tiles = []
        for _ in range(10):    
            row = []
            for _ in range(10):
                id = -1
                row.append(Tile(id))
            tiles.append(row)
        
        # create 4 buildings
        self.create_building(tiles, 2, 2, 4, 4)
        self.create_building(tiles, 7, 2, 3, 3)
        self.create_building(tiles, 2, 7, 3, 3)
        self.create_building(tiles, 7, 7, 3, 3)
        
    
        return Tilemap(tiles)
    
    def create_building(self, tiles: List[List['Tile']], x: int, y: int, width: int, height: int):
        # 4 corners
        tiles[x][y].id = 32
        tiles[x+width-1][y].id = 35
        tiles[x][y+height-1].id = 0
        tiles[x+width-1][y+height-1].id = 3
        # 2 horizontal edges
        for i in range(y+1, y+height-1):
            tiles[x][i].id = 16
            tiles[x+width-1][i].id = 19
        # # 2 vertical edges
        for i in range(x+1, x+width-1):
            tiles[i][y].id = 1
            tiles[i][y+height-1].id = 1

        # # door
        tiles[x+1][y].id = 2
        # # window if not at the edge
        if x+2 < width:
            tiles[x+2][y].id = 33
        
        

class TilemapLoader:
    def load(self, filename: str) -> 'Tilemap':
        tiles = []
        with open(filename, 'r') as f:
            for line in f:
                row = []
                for c in line.split(","):
                    row.append(Tile(int(c)))
                tiles.append(row)
        return Tilemap(tiles)
    
class Tile:
    def __init__(self, id: int):
        self.id = id

class Tilemap:
    def __init__(self, tiles: List[List[Tile]]):
        self.tiles = tiles
        self.width = len(tiles)
        self.height = len(tiles[0])

    def get_tile(self, x: int, y: int):
        return self.tiles[x][y]