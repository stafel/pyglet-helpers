import random
import math

class ChargeGen():
    """
    Generates a map out of positive and negative charges
    """
    
    def __init__(self, seed, area_size = (1000, 1000), number_of_positive_charges = 10, number_of_negative_charges = 5, cutoff_multiplier = 1.0):
        rnd = random.Random(x=seed)

        # get average charge str
        self.charge_strength = (area_size[0] + area_size[1]) / 2 / math.sqrt(number_of_positive_charges + number_of_negative_charges)

        # define charge positions
        self.charges = []
        for i in range(number_of_positive_charges + number_of_negative_charges):
            self.charges.append(
                    (
                        rnd.randint(0, area_size[0]),
                        rnd.randint(0, area_size[1]),
                        (1 if i < number_of_positive_charges else -1)
                    )
                )

        # check total charge of each point
        self.charge_map = []
        for y in range(area_size[1]):
            charge_slice = []
            for x in range(area_size[0]):
                charge_slice.append(self.get_total_charge_of_point(point=(x, y)))
            self.charge_map.append(charge_slice)

        # define average for cutoff
        self.cutoff = 0
        for y in range(area_size[1]):
            for x in range(area_size[0]):
                self.cutoff += self.charge_map[y][x]
        self.cutoff /= (area_size[0] * area_size[1])

        self.cutoff *= cutoff_multiplier # cutoff modified from avg

        # cutoff map
        for y in range(area_size[1]):
            for x in range(area_size[0]):
                if self.charge_map[y][x] < self.cutoff:
                    self.charge_map[y][x] = 0
                #else: # harmonize positive charges too
                #    self.charge_map[y][x] = 50
        
        # mark negative charges for debugging
        #for i in range(number_of_negative_charges):
        #    charge = self.charges[i + number_of_positive_charges]
        #    self.charge_map[charge[1]][charge[0]] = -50

        # TODO tidy up map by deleting small landmasses

    def get_total_charge_of_point(self, point):
        total_charge = 0
        for charge in self.charges:
            #distance_x = abs(point[0] - charge[0])
            #distance_y = abs(point[1] - charge[1])

            distance_x = point[0] - charge[0]
            distance_y = point[1] - charge[1]
            distance = math.sqrt(math.pow(distance_x, 2) + math.pow(distance_y, 2))

            charge_percentage = self.charge_strength

            if distance != 0:
                charge_percentage = self.charge_strength / distance

            total_charge += charge[2] * charge_percentage

        return total_charge


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    cgen = ChargeGen(0, area_size=(500,500), number_of_positive_charges=300, number_of_negative_charges=100, cutoff_multiplier=1.15)

    plt.style.use('_mpl-gallery-nogrid')

    # plot
    fig, ax = plt.subplots()

    ax.imshow(cgen.charge_map)

    plt.show()