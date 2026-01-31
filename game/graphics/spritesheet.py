from PIL import Image, ImageTk

class Spritesheet:
    def __init__(self, filename, size: int):
        self.size = size
        self.filename = filename
        self.sprite_size = 8
        self.sprites = []
        self.create_sprites()

    def create_sprites(self):
        img: Image.Image = Image.open("assets/tileset.png")
        n_cols  = img.width // self.sprite_size
        n_rows = img.height // self.sprite_size
        self.tiles = []
        for j in range(n_rows):
            for i in range(n_cols):
                sprite = img.crop((i*self.sprite_size, j*self.sprite_size, (i+1)*self.sprite_size, (j+1)*self.sprite_size))
                sprite = sprite.resize((self.size, self.size))
                sprite_photo = ImageTk.PhotoImage(sprite)
                self.sprites.append(sprite_photo)
        img.close()

    def get_sprite(self, index):
        return self.sprites[index]