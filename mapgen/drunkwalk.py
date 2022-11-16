import random

NO_INTERSECTION = 0.0
FULL_INTERSECTION = 1.0
UNLIMITED_STEPS = -1

class DrunkWalk():
    """
    Generates a map out of a random walk
    """
    
    def __init__(self, seed, area_size = (100, 100), intersection_allowance = NO_INTERSECTION, max_steps = UNLIMITED_STEPS):
        rnd = random.Random(x=seed)

        self.walk_map = []

        for i in range(area_size[1]):
            self.walk_map.append([0 for x in range(area_size[0])])

        can_walk = True
        pos_x = area_size[0]//2
        pos_y = area_size[1]//2
        possible_directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        while (max_steps == UNLIMITED_STEPS or max_steps > 0) and can_walk:
            check_directions = []+possible_directions
            can_walk = False

            while (len(check_directions) > 0):

                # get random direction and remove from choices
                test_direction = rnd.choice(check_directions)
                check_directions.remove(test_direction)

                # check if we are out of bounds
                if pos_x + test_direction[0] < 0 or pos_x + test_direction[0] >= area_size[0] or pos_y + test_direction[1] < 0 or pos_y + test_direction[1] >= area_size[1]:
                    continue

                # walk if empty or intersection roll is ok
                if (self.walk_map[pos_y+test_direction[1]][pos_x+test_direction[0]] == 0) or (intersection_allowance != NO_INTERSECTION and rnd.random() <= intersection_allowance):
                    pos_x += test_direction[0]
                    pos_y += test_direction[1]
                    self.walk_map[pos_y][pos_x] = 1
                    can_walk = True
                    break

            if max_steps != UNLIMITED_STEPS:
                max_steps -= 1

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    mapgen = DrunkWalk(1, area_size=(200,200), intersection_allowance=0.8)

    plt.style.use('_mpl-gallery-nogrid')

    # plot
    fig, ax = plt.subplots()

    ax.imshow(mapgen.walk_map)

    plt.show()