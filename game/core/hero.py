from typing import List

from core.itemdefinition import ItemInstance


class Hero:
    def __init__(self, name):
        self.name = name
        self.level = 1
        self.xp = 0
        self.gold = 0
        self.max_energy = 10
        self.energy = self.max_energy
        self.x = 5
        self.y = 5
        self.__diary = []
        self.__inventory: List[ItemInstance] = []

    @property
    def inventory(self):
        return self.__inventory

    @property
    def diary(self):
        return self.__diary

    def add_diary_entry(self, entry):
        self.__diary.append(entry)

    def add_gold(self, amount):
        self.gold += amount

    def add_item(self, item: ItemInstance):
        self.__inventory.append(item)