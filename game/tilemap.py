from typing import List


class TilemapFactory:
    def create_tilemap(self, filename: str) -> 'Tilemap':
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