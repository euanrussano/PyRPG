from typing import List, Optional


# ItemDefinition is a class that represents a TYPE of item in the game
class ItemDefinition:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def __str__(self) -> str:
        return self.name

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

    def find_by_name(self, name: str) -> ItemDefinition | None:
        for item in self.items:
            if item.name == name:
                return item
        return None

    def add_item(self, item: ItemDefinition) -> None:
        self.items.append(item)

    def load_data(self) -> None:
        self.items = [
            ItemDefinitionBuilder().name("Key").description("A key to open a door").build(),
            ItemDefinitionBuilder().name("Ring").description("Nice jewelry...").build(),
        ]
        print(f"{type(self)}: Loaded item data")

class ItemDefinitionBuilder:
    def __init__(self) -> None:
        self.__name: str = ""
        self.__description: str = ""

    def name(self, name: str) -> 'ItemDefinitionBuilder':
        self.__name = name
        return self

    def description(self, description: str) -> 'ItemDefinitionBuilder':
        self.__description = description
        return self

    def build(self) -> ItemDefinition:
        return ItemDefinition(self.__name, self.__description)



