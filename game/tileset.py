from PIL import Image
from PIL import Image, ImageTk

class Tileset:
    def __init__(self, out_tile_size: int):
        self.tile_size = 8
        self.out_tile_size = out_tile_size
        self.tiles = [] 
        self.create_tiles()

    def create_tiles(self):
        tileset: Image.Image = Image.open("assets/tileset.png")
        n_cols  = tileset.width // self.tile_size
        n_rows = tileset.height // self.tile_size
        self.tiles = []
        for j in range(n_rows):
            for i in range(n_cols):
                tile = tileset.crop((i*self.tile_size, j*self.tile_size, (i+1)*self.tile_size, (j+1)*self.tile_size))
                tile = tile.resize((self.out_tile_size, self.out_tile_size))
                tile = ImageTk.PhotoImage(tile)
                self.tiles.append(tile)
        tileset.close()

    def get_tile(self, index):
        return self.tiles[index]






