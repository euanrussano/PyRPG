from tilemap.tilemap import Tilemap, ForestTilemapFactory, TownTilemapFactory


class Location:
    def __init__(self, name:str, x: int, y: int, tilemap: Tilemap):
        self.name = name
        self.x = x
        self.y = y
        self.tilemap = tilemap

class LocationNotFoundError(Exception):
    def __init__(self, x: int, y: int):
        super().__init__(f"Location ({x}, {y}) does not exist in the world.")
        self.x = x
        self.y = y

class World:
    def __init__(self):
        self.locations = []

    def add_location(self, location: Location):
        for existing_location in self.locations:
            if existing_location.x == location.x and existing_location.y == location.y:
                raise ValueError(f"Location {location.x}, {location.y} already exists in the world.")
        self.locations.append(location)

    def has_location(self, x: int, y: int) -> bool:
        for location in self.locations:
            if location.x == x and location.y == y:
                return True
        return False

    def get_location(self, x: int, y: int) -> Location:
        if not self.has_location(x, y):
            raise LocationNotFoundError(x, y)
        for location in self.locations:
            if location.x == x and location.y == y:
                return location
        raise LocationNotFoundError(x, y)

class WorldFactory:
    def create(self) -> World:
        world = World()
        forestFactory = ForestTilemapFactory()
        townFactory = TownTilemapFactory()
        # forest
        forest = Location("Forest", 0, -1, forestFactory.create())
        town = Location("Town",0, 0, townFactory.create())
        farm = Location("Farm", 1, 0, forestFactory.create())
        world.add_location(forest)
        world.add_location(town)
        world.add_location(farm)
        return world
        