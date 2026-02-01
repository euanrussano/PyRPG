# tile_ids.py
from enum import IntEnum

class TileID(IntEnum):
    EMPTY = -1
    
    # Trees
    TREE_1 = 84
    TREE_2 = 85
    TREE_3 = 86
    COCONUT_TREE = 87

    # Folks
    FOLK_1 = 4
    FOLK_2 = 5
    FOLK_3 = 6
    FOLK_4 = 7
    FOLK_5 = 8
    FOLK_6 = 14
    FOLK_7 = 15
    
    # Building
    BUILDING_CORNER_TL = 0
    BUILDING_CORNER_TR = 3
    BUILDING_CORNER_BL = 32
    BUILDING_CORNER_BR = 35
    BUILDING_WALL_LEFT = 16
    BUILDING_WALL_RIGHT = 19
    BUILDING_WALL_HORIZONTAL = 1
    BUILDING_DOOR_CLOSED = 36
    BUILDING_DOOR_OPEN = 37
    BUILDING_WINDOW = 33

    # Furniture
    FURNITURE_TABLE_ROUND = 54
    FURNITURE_TABLE_SQUARE = 55
    FURNITURE_BENCH = 56
    FURNITURE_BED = 62

    CHEST_CLOSED = 57
    SIGN = 31
    KEY = 90
    RING = 89
    

# Helper groups
TREES = [TileID.TREE_1, TileID.TREE_2, TileID.TREE_3]