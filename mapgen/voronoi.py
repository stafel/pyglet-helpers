import random

MAP_OUT_OF_BOUNDS = -1
MAP_EMPTY = 0

class Area():
    """
    Holds all voronoi cell area data
    """

    def __init__(self, id, origin_position):
        self.id = id
        self.origin_position = origin_position
        self.positions = []
        self.neighbours = []
        
    def get_positions(self):
        return self.positions

    def get_neighbours(self):
        return self.neighbours

    def get_origin(self):
        return self.origin_position

class Voronoi():
    """
    Generates a flat voronoi texture
    """

    def __init__(self, seed, number_of_seeds=10, map_size=(200, 200)):
        self.rnd = random.Random(seed)
        self.map_size = map_size
        self.number_of_seeds = number_of_seeds

        self.init_map()
        self.init_seeds()

    def init_map(self):
        self.map_data = []
        for y in range(self.map_size[1]):
            map_slice = []
            for x in range(self.map_size[0]):
                map_slice.append(0)
            self.map_data.append(map_slice)

    def init_seeds(self):
        self.areas = {}

        open_positions = []
        for i in range(self.number_of_seeds):
            seed_position = (self.rnd.randint(0, self.map_size[0]-1), self.rnd.randint(0, self.map_size[1]-1))
            open_positions.append((i+1, [seed_position]))

            self.areas[i+1] = Area(i+1, seed_position)

        while len(open_positions) > 0:
            new_checks = []
            for seed_id, positions in open_positions:

                new_positions = []

                for position in positions:

                    if self.map_data[position[1]][position[0]] == MAP_EMPTY: # position is free, we take it
                        self.map_data[position[1]][position[0]] = seed_id

                        self.areas[seed_id].positions.append((position[1],position[0]))

                        for y in range(-1, 2): # try to expand further
                            for x in range(-1, 2):

                                tot_x = x+position[0]
                                tot_y = y+position[1]

                                if tot_y < 0 or tot_y >= self.map_size[1] or tot_x < 0 or tot_x >= self.map_size[0]:
                                    continue
                                
                                if not (tot_x, tot_y) in new_positions:
                                    new_positions.append((tot_x, tot_y))
                    else:
                        # if we have no id reference to the neighbour already we add it now
                        if not self.map_data[position[1]][position[0]] in self.areas[seed_id].neighbours and self.map_data[position[1]][position[0]] != self.areas[seed_id].id:
                            self.areas[seed_id].neighbours.append(self.map_data[position[1]][position[0]])

                if len(new_positions) > 0:
                    new_checks.append((seed_id, new_positions))

            open_positions = new_checks

    def get_area_from_position(self, position) -> int:
        if position[1] < 0 or position[1] >= self.map_size[1] or position[0] < 0 or position[0] >= self.map_size[0]:
            return MAP_OUT_OF_BOUNDS
        return self.map_data[position[1]][position[0]]

    def get_positions_from_area(self, area_id):
        return self.areas.get(area_id, Area(-1, (-1, -1))).get_positions()

    def get_area(self, area_id):
        return self.areas.get(area_id, Area(-1, (-1, -1)))


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    v = Voronoi(seed=random.randint(0,1000))

    print(f"(100,100) is area {v.get_area_from_position((100,100))}")
    print(f"and has neighbours {v.get_area(v.get_area_from_position((100,100))).get_neighbours()}")

    fig, ax = plt.subplots()
    ax.imshow(v.map_data)

    for area_id in v.areas:
        ax.plot([v.areas[area_id].get_origin()[0]], [v.areas[area_id].get_origin()[1]], 'o', color='red')

    ax.plot([100], [100], 'x', color='yellow') # mark testposition

    plt.show()
