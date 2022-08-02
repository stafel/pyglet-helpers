import pyglet
from pyglet.gl import *

class PanZoomWindow(pyglet.window.Window):
    def __init__(self, width, height, zoom_in_factor=1.2, *args, **kwargs):
        conf = Config(sample_buffers=1, samples=4, depth_size=16, double_buffer=True)
        super().__init__(width=width, height=height, config=conf, *args, **kwargs)

        self.zoom_in_factor = zoom_in_factor
        self.zoom_out_factor = 1/self.zoom_in_factor

        #Initialize camera values
        self.left   = 0
        self.right  = self.width
        self.bottom = 0
        self.top    = self.height
        self.zoom_level = 1
        self.zoomed_width  = self.width
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
        
        # Initialize Projection matrix
        glMatrixMode( GL_PROJECTION )
        glLoadIdentity()

        # Initialize Modelview matrix
        glMatrixMode( GL_MODELVIEW )
        glLoadIdentity()
        # Save the default modelview matrix
        glPushMatrix()

        # Clear window with ClearColor
        glClear( GL_COLOR_BUFFER_BIT )

        # Set orthographic projection matrix
        glOrtho( self.left, self.right, self.bottom, self.top, 1, -1 )

        self._draw_pan_zoom()

        # Remove default modelview matrix
        glPopMatrix()

        # Initialize Projection matrix
        glMatrixMode( GL_PROJECTION )
        glLoadIdentity()

        # Initialize Modelview matrix
        glMatrixMode( GL_MODELVIEW )
        glLoadIdentity()
        # Save the default modelview matrix
        glPushMatrix()

        glOrtho( 0, self.width, 0, self.height, 1, -1 )

        self._draw_static()

        glPopMatrix()

    def screen_pos_to_world_pos(self, screen_x, screen_y):
        screen_x = screen_x/self.width
        screen_y = screen_y/self.height

        world_x = self.left   + screen_x*self.zoomed_width
        world_y = self.bottom + screen_y*self.zoomed_height
        return (world_x, world_y)

    def _init_gl(self, width, height):
        # Set clear color
        glClearColor(0/255, 0/255, 0/255, 0/255)

        # Set antialiasing
        glEnable( GL_LINE_SMOOTH )
        glEnable( GL_POLYGON_SMOOTH )
        glHint( GL_LINE_SMOOTH_HINT, GL_NICEST )

        # Set alpha blending
        glEnable( GL_BLEND )
        glBlendFunc( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA )

        # Set viewport
        glViewport( 0, 0, width, height )

    def on_resize(self, width, height):
        # Initialize OpenGL context
        self._init_gl(width, height)

    def _drag_camera(self, dx, dy):
        # Move camera
        self.left   -= dx*self.zoom_level
        self.right  -= dx*self.zoom_level
        self.bottom -= dy*self.zoom_level
        self.top    -= dy*self.zoom_level

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if buttons == pyglet.window.mouse.MIDDLE:
            self._drag_camera(dx, dy)

    def _zoom_camera(self, x, y, dx, dy):
        # Get scale factor
        f = self.zoom_in_factor if dy > 0 else self.zoom_out_factor if dy < 0 else 1
        # If zoom_level is in the proper range
        if .2 < self.zoom_level*f < 5:

            self.zoom_level *= f

            mouse_x = x/self.width
            mouse_y = y/self.height

            mouse_x_in_world = self.left   + mouse_x*self.zoomed_width
            mouse_y_in_world = self.bottom + mouse_y*self.zoomed_height

            self.zoomed_width  *= f
            self.zoomed_height *= f

            self.left   = mouse_x_in_world - mouse_x*self.zoomed_width
            self.right  = mouse_x_in_world + (1 - mouse_x)*self.zoomed_width
            self.bottom = mouse_y_in_world - mouse_y*self.zoomed_height
            self.top    = mouse_y_in_world + (1 - mouse_y)*self.zoomed_height

    def on_mouse_scroll(self, x, y, dx, dy):
        self._zoom_camera(x, y, dx, dy)

if __name__ == '__main__':


    class TestWindow(PanZoomWindow):
        def __init__(self, width, height, zoom_in_factor=1.2, *args, **kwargs):
            super().__init__(width, height, zoom_in_factor, *args, **kwargs)

            self.zoomed_batch = pyglet.graphics.Batch()
            self.zoomed_icon = pyglet.shapes.Circle(300, 300, 100, color=(255, 0, 0), batch=self.zoomed_batch)
            self.zoomed_text = pyglet.text.Label('Zoom', font_name='Times New Roman', font_size=36, x=250, y=150, batch=self.zoomed_batch)

            self.static_batch = pyglet.graphics.Batch()
            self.static_icon = pyglet.shapes.Rectangle(500, 300, 100, 100, color=(0, 0, 255), batch=self.static_batch)
            self.static_text = pyglet.text.Label('Static', font_name='Times New Roman', font_size=36, x=490, y=250, batch=self.static_batch)

        def _draw_pan_zoom(self):
            self.zoomed_batch.draw()

        def _draw_static(self):
            self.static_batch.draw()

    test_window = TestWindow(800, 600)
    pyglet.app.run()