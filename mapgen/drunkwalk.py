import random

NO_INTERSECTION = 0.0
BASIC_INTERSECTION = 0.75
FULL_INTERSECTION = 1.0
UNLIMITED_STEPS = -1

TILE_EMPTY = 0
TILE_FLOOR = 1
TILE_WALL = 2

class DrunkWalk():
    """
    Generates a map out of a random walk
    """
    
    def __init__(self, seed, area_size = (100, 100), intersection_allowance = BASIC_INTERSECTION, max_steps = UNLIMITED_STEPS):
        self.rnd = random.Random(x=seed)

        self.walk_map = []

        for i in range(area_size[1]):
            self.walk_map.append([TILE_EMPTY for x in range(area_size[0])])

        self.generate_floor(max_steps = max_steps, intersection_allowance = intersection_allowance)

        self.generate_walls()

    def generate_floor(self, max_steps, intersection_allowance):
        can_walk = True
        pos_y = len(self.walk_map)//2
        pos_x = len(self.walk_map[pos_y])//2
        possible_directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        while (max_steps == UNLIMITED_STEPS or max_steps > 0) and can_walk:
            check_directions = []+possible_directions
            can_walk = False

            while (len(check_directions) > 0):

                # get random direction and remove from choices
                test_direction = self.rnd.choice(check_directions)
                check_directions.remove(test_direction)

                # check if we are out of bounds
                if pos_y + test_direction[1] < 0 or pos_y + test_direction[1] >= len(self.walk_map) or pos_x + test_direction[0] < 0 or pos_x + test_direction[0] >= len(self.walk_map[pos_y + test_direction[1]]):
                    continue

                # walk if empty or intersection roll is ok
                if (self.walk_map[pos_y+test_direction[1]][pos_x+test_direction[0]] == TILE_EMPTY) or (intersection_allowance != NO_INTERSECTION and self.rnd.random() <= intersection_allowance):
                    pos_x += test_direction[0]
                    pos_y += test_direction[1]
                    self.walk_map[pos_y][pos_x] = TILE_FLOOR
                    can_walk = True
                    break

            if max_steps != UNLIMITED_STEPS:
                max_steps -= 1

    def get_pos(self, x, y):
        """
        Returns tile data or 0 if out of bounds
        """
        
        if y < 0 or y >= len(self.walk_map) or x < 0 or x >= len(self.walk_map[y]):
            return TILE_EMPTY
        
        return self.walk_map[y][x]

    def get_pos_inner(self, x, y):
        """
        Returns true if pos is 1 (drunkwalk path)
        Cheap way to check for wall positions for mark_walls
        """

        return self.get_pos(x, y) == TILE_FLOOR

    def generate_walls(self):
        for y in range(len(self.walk_map)):
            for x in range(len(self.walk_map[y])):
                if self.get_pos(x, y) == 0:
                    if (self.get_pos_inner(x-1, y) or self.get_pos_inner(x+1, y) or self.get_pos_inner(x, y-1) or self.get_pos_inner(x, y+1) or
                        self.get_pos_inner(x-1, y-1) or self.get_pos_inner(x+1, y-1) or self.get_pos_inner(x-1, y-1) or self.get_pos_inner(x-1, y+1) or 
                        self.get_pos_inner(x-1, y+1) or self.get_pos_inner(x+1, y+1) or self.get_pos_inner(x+1, y-1) or self.get_pos_inner(x+1, y+1)):

                        self.walk_map[y][x] = TILE_WALL



if __name__ == '__main__':
    import matplotlib.pyplot as plt
    mapgen = DrunkWalk(32, area_size=(200,200))

    # for fun we now add another floor generation to it
    mapgen.generate_floor(max_steps=UNLIMITED_STEPS, intersection_allowance=0.82)
    mapgen.generate_walls()

    plt.style.use('_mpl-gallery-nogrid')

    # plot
    fig, ax = plt.subplots()

    ax.imshow(mapgen.walk_map)

    plt.show()