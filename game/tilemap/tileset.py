from typing import Dict, Optional

from .tile_ids import TileID

class Tile:
    def __init__(self, id: int, is_walkable: bool = True):
        self.id = id
        self.is_walkable = is_walkable

class Tileset:
    _instance: Optional['Tileset'] = None
    
    def __init__(self):
        if Tileset._instance is not None:
            raise RuntimeError("Tileset is a singleton. Use Tileset.get_instance()")
        
        self.tiles: Dict[TileID, Tile] = {}
        self.create_tiles()

    @classmethod
    def get_instance(cls) -> 'Tileset':
        """Get the singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def create_tiles(self):
        """Register all tiles with their metadata"""
        tiles_data = [
            # Special
            (TileID.EMPTY, True),
            
            # Trees (non-walkable)
            (TileID.TREE_1, False),
            (TileID.TREE_2, False),
            (TileID.TREE_3, False),
            (TileID.COCONUT_TREE, False),
            
            # Folks (non-walkable - can't walk through people)
            (TileID.FOLK_1, False),
            (TileID.FOLK_2, False),
            (TileID.FOLK_3, False),
            (TileID.FOLK_4, False),
            (TileID.FOLK_5, False),
            (TileID.FOLK_6, False),
            (TileID.FOLK_7, False),
            
            # Building components (non-walkable - solid walls)
            (TileID.BUILDING_CORNER_TL, False),
            (TileID.BUILDING_CORNER_TR, False),
            (TileID.BUILDING_CORNER_BL, False),
            (TileID.BUILDING_CORNER_BR, False),
            (TileID.BUILDING_WALL_LEFT, False),
            (TileID.BUILDING_WALL_RIGHT, False),
            (TileID.BUILDING_WALL_HORIZONTAL, False),
            (TileID.BUILDING_DOOR_CLOSED, False),
            (TileID.BUILDING_DOOR_OPEN, True),  # Can walk through open door
            (TileID.BUILDING_WINDOW, False),
            
            # Furniture (non-walkable)
            (TileID.FURNITURE_TABLE_ROUND, False),
            (TileID.FURNITURE_TABLE_SQUARE, False),
            (TileID.FURNITURE_BENCH, False),
            (TileID.FURNITURE_BED, False),
            
            # Chest (non-walkable)
            (TileID.CHEST_CLOSED, False),
        ]
        
        for tile_id, walkable in tiles_data:
            self.tiles[tile_id] = Tile(tile_id, walkable)

    def get_tile(self, tile_id: TileID) -> Tile:
        """Get tile by its ID"""
        if tile_id not in self.tiles:
            # Return empty tile as fallback
            return self.tiles.get(TileID.EMPTY, Tile(TileID.EMPTY, True))
        return self.tiles[tile_id]

# Create the singleton instance at module load
_tileset_instance = Tileset.get_instance()

# Provide a simple function to access it
def get_tileset() -> Tileset:
    """Get the global tileset instance"""
    return _tileset_instance