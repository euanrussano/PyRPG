from typing import List, Optional

from tilemap.tile_ids import TileID
from tilemap.tileset import Tileset


# ItemDefinition is a class that represents a TYPE of item in the game
class ItemDefinition:
    def __init__(self, id: TileID, name: str, description: str):
        self.id = id
        self.name = name
        self.description = description

    def __str__(self) -> str:
        return self.name

# Represents an instance of an item
class ItemInstance:
    def __init__(self, item_definition: ItemDefinition):
        self.item_definition = item_definition

    @property
    def name(self) -> str:
        return self.item_definition.name

    @property
    def description(self) -> str:
        return self.item_definition.description

    def __str__(self) -> str:
        return str(self.item_definition)

class ItemRepository:
    _instance: Optional['ItemRepository'] = None

    def __init__(self) -> None:
        if ItemRepository._instance is not None:
            raise RuntimeError("ItemRepository is a singleton. Use ItemRepository.get_instance()")
        self.items: List[ItemDefinition] = []

    @classmethod
    def get_instance(cls) -> 'ItemRepository':
        """Get the singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def find_by_id(self, id: TileID) -> ItemDefinition | None:
        for item in self.items:
            if item.id == id:
                return item
        return None

    def add_item(self, item: ItemDefinition) -> None:
        self.items.append(item)

    def load_data(self) -> None:
        self.items = [
            ItemDefinitionBuilder().id(TileID.KEY).name("Key").description("A key to open a door").build(),
            ItemDefinitionBuilder().id(TileID.RING).name("Ring").description("Nice jewelry...").build(),
        ]
        print(f"{type(self)}: Loaded item data")

class ItemDefinitionBuilder:
    def __init__(self) -> None:
        self.__name: str = ""
        self.__description: str = ""
        self.__id: TileID = TileID.EMPTY

    def id(self, id: TileID) -> 'ItemDefinitionBuilder':
        self.__id = id
        return self

    def name(self, name: str) -> 'ItemDefinitionBuilder':
        self.__name = name
        return self

    def description(self, description: str) -> 'ItemDefinitionBuilder':
        self.__description = description
        return self

    def build(self) -> ItemDefinition:
        return ItemDefinition(self.__id, self.__name, self.__description)



