from math import floor

# X East, Y South, Z Deeper
# Classic start position 25, 13, 1 - consider random inn/tavern/etc.
# Scale / Zoom Dungeon
# Teleport to any start position possibility
# Storing items in Inn?
# More than sword for weapon - creature weaknesses to weapons
# Support for beyond 1 distance away sight.
"""
  let
    fx = toFloat p.x
    fy = toFloat p.y
    fz = toFloat p.z
    q = fx * xo + fy * yo + fz * zo + (fx + xo) * (fy + yo) * (fz + zo)
    h = floor (frac q * 4694)
    hi = h `div` 256
    ft = if hi == 0 || hi > 5 then 0 else floor (frac (10 * q) * 15) + 1
  in
    {top = if p.y == 1 then WALL else decodeBoundary h,
     left = if p.x == 1 then WALL else decodeBoundary (h `div` 4),
     feature = decodeFeature ft}
"""


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
            15: 'Fountain',
            16: 'SOLIDS', }
        # Consider future extension of procedural features, magic mirror, eternal flame
        # Real time override with game state tracking of override occurrence
        self.boundaries = {
            0: None,
            1: None,
            2: 'Door',
            3: 'Wall',
            4: 'Solid', }
        self.tracker = 'init'
        self.proc_gen = (1.6915, 1.4278, 1.2462)

    def position_bits(self, x: int, y: int, z: int) -> int:
        #  http://elm-telengard.blogspot.com
        fx, fy, fz = float(x), float(y), float(z)
        (xo, yo, zo) = self.proc_gen
        # q = (x * xo) + (y * yo) + (z * zo) + ((x + xo) * (y + yo) * (z + zo))
        q = (fx * xo) + (fy * yo) + (fz * zo) + ((fx + xo) * (fy + yo) * (fz + zo))
        # f = (q % 1) * 10000
        # # eight_bit = q << 8
        # res = int(f // 1)
        # res *= 4694
        f = frac(q)
        res = floor(f * 4694)
        self.tracker = 'position_bits' + str(q) + str(f) + str(res)
        return res

    def position_features(self, x: int, y: int, z: int):
        if x < 1 or x > self.max_height or y < 1 or y > self.max_height:
            ft = 16  # Solid
            return ft, self.features[ft]
        q = self.position_bits(x, y, z)
        hi = q // 256
        if hi == 0 or hi > 5:
            ft = 0
        else:
            ft = floor(frac(10 * q) * 15) + 1  # Feature determination - possibly easier with 8 bit shift
        # b = bin(q)[2:7]
        # bin_array = bin(q)[2 - (13 - len(bin(q)[0:6])):]  # Features 5 bits 12 - 8
        # b = bin_array[2:7]
        # ft = int(b, 2)
        ft = ft % 16
        if ft in self.features.keys():
            return ft, self.features[ft]
        else:
            return ft, None

    def position_north(self, x: int, y: int, z: int):  # check 2 bits 1 and 0
        if x < 1 or x > self.max_height or y < 1 or y > self.max_height:
            b = 4  # Solid
            return b, self.boundary_lookup(b)
        if x == 1 or x == self.max_height:
            b = 3  # Wall
            return b, self.boundary_lookup(b)
        q = self.position_bits(x, y, z)
        # bin_array = bin(q)[2 - (13 - len(bin(q)[2:])):]
        # north = bin_array[0:1]
        # b = floor(frac(10 * q) * 5) + 1
        # north = bin(q)[13:]
        north = bin(q)[-2:]
        b = int(north, 2)
        # b = b % 4
        return b, self.boundary_lookup(b)

    def position_west(self, x: int, y: int, z: int):  # check 2 bits 3 and 2
        # consider wrap or larger size as well logic
        if x < 1 or x > self.max_height or y < 1 or y > self.max_height:
            b = 4  # Solid
            return b, self.boundary_lookup(b)
        if y == 1 or y == self.max_height:
            b = 3  # Wall
            return b, self.boundary_lookup(b)
        q = self.position_bits(x, y, z)
        # bin_array = bin(q)[2 - (13 - len(bin(q)[2:])):]
        # west = bin_array[2:3]
        # west = bin(q)[10:12]
        west = bin(q)[-4:-2]
        # b = floor(frac(10 * q) * 5) + 1
        b = int(west, 2)
        # b = q // 4
        b = b % 4
        return b, self.boundary_lookup(b)

    def boundary_lookup(self, b):
        if b in self.boundaries.keys():
            return b, self.boundaries[b]
        else:
            return b, None

    def grid_around(self, x: int, y: int, z: int, distance=1) -> [[]]:
        p, q, grid = 0, 0, [[] for _ in range((2 * distance) + 1)]
        for i in range(x - distance, x + 1 + distance):
            for j in range(y - distance, y + 1 + distance):
                grid[p] += [(
                    self.position_north(i, j, z),
                    self.position_west(i, j, z),
                    self.position_features(i, j, z),
                    (i, j, z)
                )]
            p += 1
        grid += [[self.position_features(x, y, z - 1), (x, y, z - 1)]]  # above feature for inns/stairs, etc
        print(x, y, z, grid[-1])
        return grid

    def print_horizontal(self, boundary, width=3):
        self.tracker = self.__module__ + str(width) + str(boundary)
        if boundary == 2:  # Door
            return 'X'+(width - 2)*'-'+'X'
        if boundary == 3:  # Wall
            return width * 'X'
        if boundary == 4:  # Wall
            return width * '8'
        return ' ' * width

    def print_vertical(self, boundary, width=3):
        self.tracker = self.__module__ + str(width) + str(boundary)
        if boundary == 2:  # Door
            return 'X'+((width - 2) * '\n')+'X'
        if boundary == 3:  # Wall
            return width * 'X\n'
        if boundary == 4:  # Wall
            return width * '8\n'
        return '\n'*width

    def print_feature(self, feature, width=3):
        self.tracker = self.__module__ + str(width) + str(feature)
        if feature in self.features:
            return ' ' + self.features[feature][:width - 2] + ' '
        return ' ' * width

    def print_grid_around(self, pos, width=7):
        print(pos)
        distance = 1
        user_loc = self.grid_around(*pos, distance=distance)
        for r in user_loc:
            # print(r)
            if len(r) != 2:
                for c in r:
                    print(self.print_horizontal(c[0][0], width=width), end='')
                print('   ||')
                for c in r:
                    print(self.print_feature(c[2][0], width=width), end='')
                print('   ||')
            else:
                s = 'Above' + str(r)
                wide = 3 + ((2 * distance) + 1) * width
                left = wide - len(s)
                left //= 2
                ends = ' ' * left
                s = ends + s + ends
                print(s, end='||\n')
# def frac(x: float, precision: int = 10) -> int:
#     return floor((x % 1) * precision)
# frac r = r - toFloat (floor r)


def frac(x: float) -> float:
    return x - float(floor(x))


"""
Using ANSI escape sequence, where ESC[y;xH moves curser to row y, col x:
print("\033[6;3HHello")
"""


def main():
    # feature check test
    d = Dungeon()
    # positions = [(24, 14, 1), (1, 1, 1), (1, 200, 1), (25, 16, 1), (25, 13, 1), (13, 25, 1)]
    # for p in positions:
    #     print(*p, d.position_features(*p))

    # print(d.position_features(25, 16, 1))  # Throne
    # print(d.position_features(24, 14, 1))  # GMC
    # print(d.position_features(25, 13, 1))  # Above Stairs to inn

    # print(d.position_north(25, 13, 1))
    # print(d.position_west(25, 13, 1))

    # print(d.grid_around(1, 1, 1))
    # print(d.grid_around(1, 200, 1))

    print('\nConfirm Procedural Generation Match to Original\n')
    # pos = [(1, 1, 1), (1, 200, 1), (25, 13, 1), (13, 25, 1)]
    pos = [(25, 13, 1)]
    for p in pos:
        d.print_grid_around(p)

    print(frac(45.123))


if __name__ == '__main__':
    main()
