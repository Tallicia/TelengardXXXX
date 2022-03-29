from math import floor

# Classic start position 25, 13, 1 - consider random inn/tavern/etc
# Teleport to any start position possibility
# Storing items in Inn?
# More than sword for weapon - creature weaknesses to weapons

class Dungeon:
    def __init__(self):
        self.max_width = 200
        self.max_height = 200
        self.max_depth = 50
        self.features = {
            1: 'Elevator',
            2: 'Pit',
            3: 'Teleporter',
            4: 'Stairway down',
            5: 'Altar',
            6: 'Fountain',
            7: 'Gray misty cube',
            8: 'Throne',
            9: 'Small box with buttons',
            10: 'Elevator',
            11: 'Pit',
            12: 'Teleporter',
            13: 'Stairway down',
            14: 'Altar',
            15: 'Fountain', }
        # Consider future extension of procedural features, magic mirror, eternal flame
        # Real time override with game state tracking of override occurrence

        self.boundaries = {
            0: None,
            1: None,
            2: 'Door',
            3: 'Wall', }

    def position_bits(self, x: int, y: int, z: int) -> int:
        #  http://elm-telengard.blogspot.com
        xo, yo, zo = 1.6915, 1.4278, 1.2462
        q = (x * xo) + (y * yo) + (z * zo) + ((x + xo) * (y + yo) * (z + zo))
        # f = (q % 1) * 10000
        # # eight_bitf = q << 8
        # res = int(f // 1)
        # res *= 4694
        f = frac(q)
        res = floor(f * 4694)
        return res

    def position_features(self, x: int, y: int, z: int) -> str:
        q = self.position_bits(x, y, z)
        hi = q // 256
        if hi == 0 or hi > 5:
            ft = 0
        else:
            ft = floor(frac(10 * q) * 15) + 1  # this might be easier with 8 bit shift
            # ft = floor(frac(10 * q) * 15) + 1  # Feature determination
        # b = bin(q)[2:7]
        # bin_array = bin(q)[2 - (13 - len(bin(q)[0:6])):]  # Features 5 bits 12 - 8
        # b = bin_array[2:7]
        # ft = int(b, 2)
        if ft in self.features.keys():
            return self.features[ft]
        else:
            return None

    def position_north(self, x: int, y: int, z: int) -> str:  # check 2 bits 1 and 0
        if y == 1 or y == self.max_height + 1:
            return 'Wall'
        q = self.position_bits(x, y, z)
        # bin_array = bin(q)[2 - (13 - len(bin(q)[2:])):]
        # north = bin_array[0:1]
        # b = floor(frac(10 * q) * 5) + 1
        # north = bin(q)[13:]
        north = bin(q)[-2:]
        b = int(north, 2)
        # return self.boundaries[b]
        if b in self.boundaries.keys():
            return self.boundaries[b]
        else:
            return None

    def position_west(self, x: int, y: int, z: int) -> str:  # check 2 bits 3 and 2
        # consider wrap or larger size as well logic
        if x == 1 or x == self.max_width + 1:
            return 'Wall'
        q = self.position_bits(x, y, z)
        # bin_array = bin(q)[2 - (13 - len(bin(q)[2:])):]
        # west = bin_array[2:3]
        # west = bin(q)[10:12]
        west = bin(q)[-4:-2]
        # b = floor(frac(10 * q) * 5) + 1
        b = int(west, 2)
        # b = q // 4
        if b in self.boundaries.keys():
            return self.boundaries[b]
        else:
            return None

    def grid_around(self, x: int, y: int, z: int) -> [[]]:
        p, q, grid = 0, 0, [[] for _ in range(3)]
        for i in range(x-1, x+2):
            for j in range(y - 1, y + 2):
                if 0 < i < self.max_width and 0 < j < self.max_height:
                    grid[p] += [(
                        self.position_north(i, j, z),
                        self.position_west(i, j, z),
                        self.position_features(i, j, z)
                    )]
            p += 1
        grid += [self.position_features(x, y, z + 1)]
        return grid


# def frac(x: float, precision: int = 10) -> int:
#     return floor((x % 1) * precision)
#frac r = r - toFloat (floor r)
def frac(x: float) -> int:
    return x - float(floor(x))


def main():
    # feature check test
    d = Dungeon()
    positions = [(25, 13, 1), (25, 16, 1), (24, 14, 1), ]
    for p in positions:
        print(p[0], p[1], p[2], d.position_features(p[0], p[1], p[2]))

    # print(d.position_features(25, 16, 1))  # Throne
    # print(d.position_features(24, 14, 1))  # GMC
    # print(d.position_features(25, 13, 1))  # Above Stairs to inn

    # print(d.position_north(25, 13, 1))
    # print(d.position_west(25, 13, 1))

    # print(d.grid_around(1, 1, 1))
    # print(d.grid_around(1, 200, 1))
    x = 1
    for r in d.grid_around(25, 13, 1):
        for c in r:
            print('N-', c[0], 'W-', c[1], 'F-', c[2], end='::')
            if x % 3 == 0:
                print()
            x += 1
        x = 1


if __name__ == '__main__':
    main()
