from typing import List, Tuple
import pyglet

class Tilemap():
    def __init__(self, base_image_path: str, tile_dimension: Tuple[int, int], map_data: List[List[int]], batch: pyglet.graphics.Batch):
        self.load_tile_texture(base_image_path=base_image_path, tile_dimension=tile_dimension)
        self.set_map_data(map_data)
        self.generate_drawables(batch=batch)

    def load_tile_texture(self, base_image_path: str, tile_dimension: Tuple[int, int]):
        self._base_image = pyglet.image.load(base_image_path)
        self._tile_dimension = tile_dimension

        columns = self._base_image.width//tile_dimension[0]
        rows = self._base_image.height//tile_dimension[1]

        self._image_sequence = pyglet.image.ImageGrid(self._base_image, columns, rows)

    def set_map_data(self, map_data):
        self._map_data = map_data

    def generate_drawables(self, batch: pyglet.graphics.Batch):
        self._sprites = []

        for y in range(len(self._map_data)):
            for x in range(len(self._map_data[y])):
                if self._map_data[y][x] >= 0 and self._map_data[y][x] < len(self._image_sequence):
                    self._sprites.append(pyglet.sprite.Sprite(self._image_sequence[self._map_data[y][x]], x=x*self._tile_dimension[0], y=y*self._tile_dimension[1], batch=batch))

if __name__ == '__main__':
    import os.path
    import random
    from pan_zoom_window import PanZoomWindow
    from mapgen.drunkwalk import DrunkWalk

    class TestWindow(PanZoomWindow):
        def __init__(self, width, height, zoom_in_factor=1.2, *args, **kwargs):
            super().__init__(width, height, zoom_in_factor, *args, **kwargs)

            self.zoomed_batch = pyglet.graphics.Batch()
            self.tilemap = Tilemap(os.path.join('res', 'test', 'floortileset.png'), (32, 32), self.beautify_mapdata(DrunkWalk(32, area_size=(200,200)).walk_map), self.zoomed_batch)

            self.static_batch = pyglet.graphics.Batch()
            self.static_icon = pyglet.sprite.Sprite(self.tilemap._base_image, batch=self.static_batch)

            self.focus(100*32, 100*32)

        def beautify_mapdata(self, map_data):
            for y in range(len(map_data)):
                for x in range(len(map_data[y])):
                    match map_data[y][x]:
                        case 0:
                            map_data[y][x] = -1
                        case 1:
                            match random.randint(1, 6):
                                case 1 | 2:
                                    map_data[y][x] = 1
                                case 3:
                                    map_data[y][x] = 0
                                case 4 | 5:
                                    map_data[y][x] = 2
                                case 6:
                                    map_data[y][x] = 5
                        case 2:
                            map_data[y][x] = 16

            return map_data

        def _draw_pan_zoom(self):
            self.zoomed_batch.draw()

        def _draw_static(self):
            self.static_batch.draw()

    test_window = TestWindow(800, 600, vsync=False)
    pyglet.app.run()