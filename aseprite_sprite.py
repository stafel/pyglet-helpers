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
import json

__doc__ = """
AsepriteSprite for easy usage of aseprite exports
"""


class AsepriteSprite(pyglet.sprite.Sprite):
    """Reads animation data from aseprite json export

    Good export parameters for Aseprite:
    Layout: Sheet type Packed with Merge duplicates
    Sprite: Split by Layers and Tags
    Borders: with "Trim sprite" and "By grid" for best result
    Output: Set item filename to: {layer}_{tag}_{frame}
    Json name and Png name must match

    Non looping tags can be indicated with a frame duration of 1ms on last frame
    But there must be a looping animation at the end of the animation shedule stack
    Reaching a non looping animation without a follow up causes issues in pyglet
    """

    def __init__(
        self,
        image_path,
        json_path,
        pos_x,
        pos_y,
        draw_batch,
        start_animation=None,
        start_layer=None,
        center_images_x=True,
        center_images_y=True,
    ):
        # wrong centering can lead to jittering
        self.center_images_x = center_images_x
        self.center_images_y = center_images_y

        self.spritesheet_image = pyglet.resource.image(image_path)

        self.animation_sequences = (
            {}
        )  # holds animation data itself accessed with {layer}_{animation}
        self.available_animations = []  # available animations of this sprite
        self.available_layers = []  # available layers of this sprite

        json_data = None
        with open(json_path, "r") as json_file:
            json_data = json.loads(json_file.read())

        # aseprite can split the export into layers, check if we have some available
        for layer_data in json_data["meta"]["layers"]:
            if not layer_data["name"] in self.available_layers:
                self.available_layers.append(layer_data["name"])
        if (
            len(self.available_layers) < 1
        ):  # we found no layer info, assume the user left everything on default
            self.available_layers.append("Layer")

        individual_frame_data = {}
        if (
            type(json_data["frames"]) == dict
        ):  # if it is a dict this was exported with the Hash setting, else with List setting
            individual_frame_data = self._load_frame_hash(json_data["frames"])
        else:
            individual_frame_data = self._load_frame_list(json_data["frames"])

        for animation_data in json_data["meta"]["frameTags"]:
            direction = animation_data["direction"]

            for layer in self.available_layers:
                frames_to_add = []

                animation_sequence_name = f"{layer}_{animation_data['name']}"

                for image_id in range(
                    int(animation_data["from"]), int(animation_data["to"]) + 1
                ):
                    correctedimage_id = image_id - int(
                        animation_data["from"]
                    )  # aseprite id is the index in the list and not the index in the animation itself

                    image_id_str = (
                        f"{layer}_{animation_data['name']}_{correctedimage_id}"
                    )

                    image_duration = (
                        float(individual_frame_data[image_id_str]["duration"]) / 1000.0
                    )  # ms to seconds
                    if (
                        image_duration < 0.002
                    ):  # if duration is one millisecond we assume its none and make the animation nonlooping
                        image_duration = None

                    frames_to_add.append(
                        pyglet.image.AnimationFrame(
                            individual_frame_data[image_id_str]["region"],
                            duration=image_duration,
                        )
                    )

                if direction == "reverse":
                    frames_to_add.reverse()
                elif direction == "pingpong":
                    frames_to_add = frames_to_add + frames_to_add.reverse()

                self.animation_sequences[
                    animation_sequence_name
                ] = pyglet.image.Animation(frames=frames_to_add)

                if not animation_data["name"] in self.available_animations:
                    self.available_animations.append(animation_data["name"])

        if not start_animation:
            start_animation = self.available_animations[0]

        if not start_layer:
            start_layer = self.available_layers[0]

        self.current_layer = start_layer
        self.current_animation = start_animation

        self.sheduled_animations = []
        super().__init__(
            self.animation_sequences[
                self._get_animation_sequence_name(
                    self.current_layer, self.current_animation
                )
            ],
            x=pos_x,
            y=pos_y,
            batch=draw_batch,
        )
        self.push_handlers(on_animation_end=self._load_next_animation)

    def _load_frame(self, image_meta_data):
        """this cuts a region for a single frame from the aseprite meta frame data"""

        image_data = image_meta_data["frame"]

        recalculated_y = (
            self.spritesheet_image.height - image_data["y"] - image_data["h"]
        )

        converted_region_data = {
            "region": self.spritesheet_image.get_region(
                x=image_data["x"],
                y=recalculated_y,
                width=image_data["w"],
                height=image_data["h"],
            ),
            "duration": image_meta_data["duration"],
        }

        if self.center_images_x:
            converted_region_data["region"].anchor_x = (
                converted_region_data["region"].width // 2
            )
        if self.center_images_y:
            converted_region_data["region"].anchor_y = (
                converted_region_data["region"].height // 2
            )

        return converted_region_data

    def _load_frame_list(self, frame_meta_list):
        """
        converts the aseprite frames list into a dict with imageRegions
        """

        individual_images = {}
        for image_data_meta in frame_meta_list:
            image_key_str = image_data_meta["filename"]
            individual_images[image_key_str] = self._load_frame(image_data_meta)

        return individual_images

    def _load_frame_hash(self, frame_meta_hash_dict):
        """
        converts the aseprite frames hash dict into a dict with imageRegions
        """

        individual_images = {}
        for image_data_metaKey in frame_meta_hash_dict:
            image_key_str = image_data_metaKey
            individual_images[image_key_str] = self._load_frame(
                frame_meta_hash_dict[image_data_metaKey]
            )

        return individual_images

    def shedule_animation(self, animation_name, layer_name=None):
        """
        Add animation to queue to be played at free moment
        """

        if (
            not self.current_animation
        ):  # we currently have no animation, shedule immediatly
            self.set_animation(layer_name=layer_name, animation_name=animation_name)
        else:
            self.sheduled_animations.append((layer_name, animation_name))

    def _load_next_animation(self):
        if len(self.sheduled_animations) > 0:
            layer_name, animation_name = self.sheduled_animations.pop(0)

            if not layer_name:
                layer_name = self.current_layer

            self.set_animation(layer_name=layer_name, animation_name=animation_name)
        else:
            if self.current_animation:
                if (
                    not self.animation_sequences[
                        self._get_animation_sequence_name(
                            self.current_layer, self.current_animation
                        )
                    ]
                    .frames[-1]
                    .duration
                ):  # we stopped the last animation and have no backup ready
                    raise NotImplementedError(
                        f"Animation '{self.current_layer}_{self.current_animation}' is not looping, shedule another one before the first one stops"
                    )

    def _get_animation_sequence_name(self, layer_name, animation_name):
        return f"{layer_name}_{animation_name}"

    def set_animation(self, animation_name=None, layer_name=None, force_reset=False):
        """
        Set animation imidiatly

        force_reset: if True resets animation back to first frame even if it was already loaded
        """

        if not layer_name:
            layer_name = self.current_layer

        if not animation_name:
            animation_name = self.current_animation

        if (
            force_reset
            or self.current_animation != animation_name
            or self.current_layer != layer_name
        ):
            self.image = self.animation_sequences[
                self._get_animation_sequence_name(layer_name, animation_name)
            ]
            self.current_animation = animation_name
            self.current_layer = layer_name

    def get_position(self):
        """
        Position (x, y) of the sprite
        """

        x = self.position[0]
        y = self.position[1]

        if self.center_images_x:
            x -= self.width // 2

        if self.center_images_y:
            y -= self.height // 2

        return (x, y)

    def get_size(self):
        """
        Size (width, height) of the sprite
        """

        return (self.width, self.height)

    def get_midpoint(self):
        """
        Midpoint (x, y) of the sprite
        Will be inaccurate if center_images_x or center_images_y is True
        """

        pos = self.get_position()
        size = self.get_size()

        return (pos[0] + size[0] // 2, pos[1] + size[1] // 2)

    def move(self, deltaX, deltaY):
        """
        Move sprite deltaX and deltaY units
        """
        
        self.update(x=self.position[0] + deltaX, y=self.position[1] + deltaY)

    def set_position(self, pos_x, pos_y):
        """
        Sets sprite postion to (pos_x, pos_y)
        """

        self.update(x=pos_x, y=pos_y)

    def set_batch(self, batch):
        """
        Sets batch
        """

        self.batch = batch

    def get_aabb(self):
        """
        Axis aligned bounding box
        (min_x, min_y, max_x, max_y)
        """

        x, y = self.get_position()
        w, h = self.get_size()
        return (x, y, x + w, y + h)


if __name__ == "__main__":
    window = pyglet.window.Window(600, 300)
    batch = pyglet.graphics.Batch()
    test_token = AsepriteSprite(
        "res/test/token.png",
        "res/test/token.json",
        300,
        160,
        batch,
        start_animation="idle",
    )

    @window.event
    def on_draw():
        window.clear()
        batch.draw()

    @window.event
    def on_key_press(symbol, modifiers):
        if symbol == pyglet.window.key.ENTER:
            test_token.set_animation("derp")
            test_token.shedule_animation("idle")

    pyglet.app.run()
