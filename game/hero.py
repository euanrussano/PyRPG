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