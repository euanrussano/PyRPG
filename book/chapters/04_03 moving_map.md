# 4.3 - Moving around the map

- Separate the `Tileset` from the `Spritesheet`. A tileset holds tiles that can be reused throughout the game. A spritesheet holds the cropped images from the PNG file.
- Add a property `walkable` to the `Tile` class. This will be used to determine if a tile is walkable or not.
- Now when trying to move the hero, we need to check if the tile is walkable. If it is, we can move the hero. otherwise, we can't.