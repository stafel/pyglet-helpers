#!/usr/bin/env python3
#
# pygsty: usefull stuff for pyglet
# Copyright (C) 2023 Rafael Stauffer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import pyglet
from pyglet import math
from pyglet.gl import Config

__doc__ = """
Pannable and zoomable window
"""


class PanZoomWindow(pyglet.window.Window):
    """
    Pannable and zoomable window

    Use method _draw_pan_zoom for all ingame objects
    Use method _draw_static for static menus

    Mouse wheel to zoom (method on_mouse_scroll)
    Press and move middle mouse to drag (method on_mouse_drag)
    """

    def __init__(self, width, height, zoom_in_factor=1.2, *args, **kwargs):
        conf = Config(sample_buffers=1, samples=4, depth_size=16, double_buffer=True)
        super().__init__(width=width, height=height, config=conf, *args, **kwargs)

        self.zoom_in_factor = zoom_in_factor
        self.zoom_out_factor = 1 / self.zoom_in_factor

        # Initialize camera values
        self.left = 0
        self.right = self.width
        self.bottom = 0
        self.top = self.height
        self.zoom_level = 1
        self.zoomed_width = self.width
        self.zoomed_height = self.height

    def _draw_pan_zoom(self):
        """
        Use to draw what must be panned and zoomed
        """

        pass

    def _draw_static(self):
        """
        Use to draw what remains static afterwards like a hud gui
        """

        pass

    def on_draw(self):
        """
        Clears screen, draws dynamic first then static on top
        """

        self.clear()

        self.projection = math.Mat4.orthogonal_projection(
            self.left, self.right, self.bottom, self.top, 1, -1
        )

        self._draw_pan_zoom()

        self.projection = math.Mat4.orthogonal_projection(
            0, self.width, 0, self.height, 1, -1
        )

        self._draw_static()

    def screen_pos_to_world_pos(self, screen_x, screen_y):
        """
        Converts screen coordinates to panned zoomed world coordinates
        """

        screen_x = screen_x / self.width
        screen_y = screen_y / self.height

        world_x = self.left + screen_x * self.zoomed_width
        world_y = self.bottom + screen_y * self.zoomed_height
        return (world_x, world_y)

    def on_resize(self, width, height):
        """
        Called on a window resize
        """

        pass

    def _drag_camera(self, dx, dy):
        """
        Move camera backwards (a dragging motion) relative to zoom level
        """

        self.left -= dx * self.zoom_level
        self.right -= dx * self.zoom_level
        self.bottom -= dy * self.zoom_level
        self.top -= dy * self.zoom_level

    def focus(self, x, y):
        """
        Focuses camera onto absolute point
        """

        half_width = self.width // 2
        half_height = self.height // 2

        self.left = x - half_width
        self.right = x + half_width
        self.bottom = y - half_height
        self.top = y + half_height

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        """
        Middle mouse drag: window drag
        """

        if buttons == pyglet.window.mouse.MIDDLE:
            self._drag_camera(dx, dy)

    def _zoom_camera(self, x, y, dx, dy):
        # Get scale factor
        f = self.zoom_in_factor if dy > 0 else self.zoom_out_factor if dy < 0 else 1
        # If zoom_level is in the proper range
        if 0.2 < self.zoom_level * f < 5:
            self.zoom_level *= f

            mouse_x = x / self.width
            mouse_y = y / self.height

            mouse_x_in_world = self.left + mouse_x * self.zoomed_width
            mouse_y_in_world = self.bottom + mouse_y * self.zoomed_height

            self.zoomed_width *= f
            self.zoomed_height *= f

            self.left = mouse_x_in_world - mouse_x * self.zoomed_width
            self.right = mouse_x_in_world + (1 - mouse_x) * self.zoomed_width
            self.bottom = mouse_y_in_world - mouse_y * self.zoomed_height
            self.top = mouse_y_in_world + (1 - mouse_y) * self.zoomed_height

    def on_mouse_scroll(self, x, y, dx, dy):
        """
        Zoom in and out
        """

        self._zoom_camera(x, y, dx, dy)


if __name__ == "__main__":

    class TestWindow(PanZoomWindow):
        def __init__(self, width, height, zoom_in_factor=1.2, *args, **kwargs):
            super().__init__(width, height, zoom_in_factor, *args, **kwargs)

            self.zoomed_batch = pyglet.graphics.Batch()
            self.zoomed_icon = pyglet.shapes.Circle(
                300, 300, 100, color=(255, 0, 0), batch=self.zoomed_batch
            )
            self.zoomed_text = pyglet.text.Label(
                "Zoom",
                font_name="Times New Roman",
                font_size=36,
                x=250,
                y=150,
                batch=self.zoomed_batch,
            )

            self.static_batch = pyglet.graphics.Batch()
            self.static_icon = pyglet.shapes.Rectangle(
                500, 300, 100, 100, color=(0, 0, 255), batch=self.static_batch
            )
            self.static_text = pyglet.text.Label(
                "Static",
                font_name="Times New Roman",
                font_size=36,
                x=490,
                y=250,
                batch=self.static_batch,
            )

        def _draw_pan_zoom(self):
            self.zoomed_batch.draw()

        def _draw_static(self):
            self.static_batch.draw()

    test_window = TestWindow(800, 600, vsync=False)
    pyglet.app.run()
