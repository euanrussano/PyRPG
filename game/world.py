from tilemap import Tilemap, ForestTilemapFactory, TownTilemapFactory


class Location:
    def __init__(self, name:str, x: int, y: int, tilemap: Tilemap):
        self.name = name
        self.x = x
        self.y = y
        self.tilemap = tilemap

class World:
    def __init__(self):
        self.locations = []

    def add_location(self, location: Location):
        for existing_location in self.locations:
            if existing_location.x == location.x and existing_location.y == location.y:
                raise ValueError(f"Location {location.x}, {location.y} already exists in the world.")
        self.locations.append(location)

    def get_location(self, x: int, y: int) -> Location | None:
        for location in self.locations:
            if location.x == x and location.y == y:
                return location
        return None
    
    def get_location_by_id(self, id: int) -> Location | None:
        if id < 0 or id >= len(self.locations):
            return None
        return self.locations[id]
    
    @staticmethod
    def create() -> 'World':
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

        