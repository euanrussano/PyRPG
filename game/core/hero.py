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

    @property
    def diary(self):
        return self.__diary

    def add_diary_entry(self, entry):
        self.__diary.append(entry)

    def add_gold(self, amount):
        self.gold += amount