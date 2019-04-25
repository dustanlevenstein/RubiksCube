# Colors
WHITE  = '#FFFFFF'
YELLOW = '#FFFF00'
BLUE   = '#0000FF'
GREEN  = '#00FF00'
RED    = '#FF0000'
ORANGE = '#FFAA00'
COLORS = set((WHITE, YELLOW, BLUE, GREEN, RED, ORANGE))

# Sides
BACK  = 'Back'
LEFT  = 'Left'
TOP   = 'Top'
RIGHT = 'Right'
FRONT = 'Front'
DOWN  = 'Down'
SIDES = set((BACK, LEFT, TOP, RIGHT, FRONT, DOWN))
ZERO_REFERENCES = (FRONT, RIGHT, TOP)

# Dimensions
X = DEPTH = (FRONT, BACK)
Y = HORIZONTAL = (RIGHT, LEFT)
Z = VERTICAL = (TOP, DOWN)
DIMENSIONS = set((DEPTH, HORIZONTAL, VERTICAL))

OPPOSITE = {
    FRONT:BACK, BACK:FRONT,
    RIGHT:LEFT, LEFT:RIGHT,
    TOP:DOWN, DOWN:TOP
    }

REFERENTIAL_PLANE = {
    BACK  : (2, 1),
    LEFT  : (0, 2),
    TOP   : (0, 1),
    RIGHT : (2, 0),
    FRONT : (1, 2),
    DOWN  : (1, 0)
    }

CROSS_PRODUCT = {
    (BACK,  LEFT)  : TOP,
    (BACK,  RIGHT) : DOWN,
    (BACK,  TOP)   : RIGHT,
    (BACK,  DOWN)  : LEFT,
    (FRONT, LEFT)  : DOWN,
    (FRONT, RIGHT) : TOP,
    (FRONT, TOP)   : LEFT,
    (FRONT, DOWN)  : RIGHT,
    (LEFT,  BACK)  : DOWN,
    (LEFT,  FRONT) : TOP,
    (LEFT,  TOP)   : BACK,
    (LEFT,  DOWN)  : FRONT,
    (RIGHT, BACK)  : TOP,
    (RIGHT, FRONT) : DOWN,
    (RIGHT, TOP)   : FRONT,
    (RIGHT, DOWN)  : BACK,
    (TOP,   BACK)  : LEFT,
    (TOP,   FRONT) : RIGHT,
    (TOP,   LEFT)  : FRONT,
    (TOP,   RIGHT) : BACK,
    (DOWN,  BACK)  : RIGHT,
    (DOWN,  FRONT) : LEFT,
    (DOWN,  LEFT)  : BACK,
    (DOWN,  RIGHT) : FRONT
    }

def _swap(tpl):
    '''Swaps a 2-tuple'''
    return tpl[1], tpl[0]
def _turn(xy_position, cube_size):
    shift = cube_size/2.0 - .5
    x, y = xy_position[0] - shift, xy_position[1] - shift
    nx, ny = (y + shift, -x + shift)
    return int(nx), int(ny)
class Cubelet(object):
    def __init__(self, parent, position=None, colors_sides=None):
        self._parent = parent
        self._cube_size = parent._size
        if position is None:
            return
        self._colors_sides = colors_sides
        self._update_sides_colors()
        self._position = tuple(position)
        assert len(self._position) == 3 # 3 dimensions
        self._validate_cs()
    def _update_sides_colors(self):
        sc = {}
        for i, v in self._colors_sides.items():
            sc[v] = i
        self._sides_colors = sc
    def _validate_cs(self):
        for color, side in self._colors_sides.items():
            assert color in COLORS
            assert side in SIDES
    def turn(self, side, amt):
        for i in range(amt):
            # Move the piece
            position = list(self._position)
            Xrefdim, Yrefdim = REFERENTIAL_PLANE[side] # referential dimension
            X_ref, Y_ref = position[Xrefdim], position[Yrefdim]
            X_ref, Y_ref = _turn((X_ref, Y_ref), self._cube_size)
            position[Xrefdim], position[Yrefdim] = X_ref, Y_ref
            self._position = tuple(position)
            # Rotate the piece
            for color, square_side in self._colors_sides.items():
                if side == square_side or OPPOSITE[side] == square_side:
                    continue
                self._colors_sides[color] = CROSS_PRODUCT[(square_side, side)]
            self._update_sides_colors()
    def raw_data(self):
        return self._cube_size, self._position, self._colors_sides
    def __str__(self):
        return "Cubelet(%s)"%(str(self._colors_sides))
    __repr__ = __str__
    def load(self, data):
        self._cube_size, self._position, self._colors_sides = data
        self._update_sides_colors()

class Cube(object):
    def __init__(self, size):
        self._size = size
        cublets = []
        for x in range(size):
            c_x = []
            cublets.append(c_x)
            for y in range(size):
                c_y = []
                c_x.append(c_y)
                for z in range(size):
                    colors_sides = {}
                    if x == 0:      colors_sides[ORANGE] = BACK
                    if x == size-1: colors_sides[RED   ] = FRONT
                    if y == 0:      colors_sides[GREEN ] = LEFT
                    if y == size-1: colors_sides[BLUE  ] = RIGHT
                    if z == 0:      colors_sides[YELLOW] = DOWN
                    if z == size-1: colors_sides[WHITE ] = TOP
                    c_y.append(Cubelet(self, (x, y, z), colors_sides))
        self._set_cublets(cublets)
        self._record = []
        self._saved_solutions = {}
    def _set_cublets(self, new_cublets):
        self._cublets = tuple(tuple(tuple(c for c in y)
                                            for y in x)
                                            for x in new_cublets)
    def _rearrange(self):
        old_cublets = self._cublets
        size = self._size
        new_cublets = [[[0 for a in range(size)]
                           for b in range(size)]
                           for c in range(size)]
        for x in range(size):
            for y in range(size):
                for z in range(size):
                    cublet = old_cublets[x][y][z]
                    xn, yn, zn = cublet._position
                    if new_cublets[xn][yn][zn] != 0:
                        raise EnvironmentError(
                            "unexpected duplicated position.")
                    new_cublets[xn][yn][zn] = cublet
        self._set_cublets(new_cublets)
    def _extract(self, dimension, level):
        """
        Extracts a side or slice of the cube (slices are between and parallel
        to the sides)
        """
        size = self._size
        all_cublets = self._cublets
        if dimension == X:
            return [all_cublets[level][y][z] for y in range(size)
                                             for z in range(size)]
        if dimension == Y:
            return [all_cublets[x][level][z] for x in range(size)
                                             for z in range(size)]
        if dimension == Z:
            return [all_cublets[x][y][level] for x in range(size)
                                             for y in range(size)]
        raise ValueError("arg dimension is not a dimension")
    def _turn(self, dimension, level, side_ref, amt):
        """Turns 'off the record'"""
        size = self._size
        all_cublets = self._cublets
        pieces = self._extract(dimension, level)
        for piece in pieces: piece.turn(side_ref, amt)
        self._rearrange()
    def turn(self, dimension, level, side_ref, amt):
        self._turn(dimension, level, side_ref, amt)
        self._record.append((dimension, level, side_ref, amt))
    def undo(self, turns = 1):
        for i in range(turns):
            dimension, level, side_ref, amt = self._record[-1]
            self.turn(dimension, level, OPPOSITE[side_ref], amt)
            self._record.pop(-1)
            self._record.pop(-1)
    def solved(self):
        sides_colors = {}
        for side in self._cublets:
            for row in side:
                for piece in row:
                    piece_cs = piece._colors_sides
                    x, y, z = piece._position
                    for color, side in piece_cs.items():
                        if side in sides_colors:
                            if sides_colors[side] != color:
                                return False
                        else:
                            sides_colors[side] = color
        return True
    def _solution(self, _level = 1, _levels = 5, _prev_dimension = None,
       _levels_tried = frozenset()):
        # print str(_level) + (' '*_level) + 'r'
        if _level == 1: print _levels
        size = self._size
        half, is_odd_cube = divmod(size, 2)
        flag = False
        if self.solved():
            return []
        if _level > _levels: return None
        for dimension in DIMENSIONS:
            side_ref = dimension[1]
            for cube_level in range(size):
                if dimension == _prev_dimension:
                    # Don't turn the same slice multiple times
                    if cube_level in _levels_tried:
                        continue
                    # Don't turn more than half of the pieces
                    # in a dimension in an even-numbered cube.
                    if (not is_odd_cube) and len(_levels_tried) >= half:
                        continue
                for amt in range(1,4):
                    self._turn(dimension, cube_level, side_ref, 1)
                    if flag: continue
                    # print (' ' * _level) + str((dimension, cube_level, side_ref, amt))
                    if _level <= _levels:
                        solution = 'DNE' #= self._saved_solutions.get(
                            #(self._cublets, _levels-_level), 'DNE')
                        if solution == 'DNE':
                            levels_tried = frozenset((cube_level,))
                            if dimension == _prev_dimension:
                                levels_tried = _levels_tried.union(levels_tried)
                            solution = self._solution(_level+1, _levels,
                              dimension, levels_tried)
                            #if (_levels - _level) < 2:
                                #self._saved_solutions[
                                  #(self._cublets,_levels-_level)] = solution
                        if solution is not None:
                            solution.append((dimension, cube_level, side_ref, amt))
                            flag = True
                self._turn(dimension, cube_level, side_ref, 1)
                if flag: return solution
        return None
    def solution(self, levels = 1, max_levels = None):
        while True:
            if max_levels is not None and levels > max_levels: break
            solution = self._solution(1, levels)
            if solution is not None: return solution
            levels += 1
        return None
    def solve(self, levels = 1):
        solution = self.solution(levels)
        for step in solution:
            self.turn(*step)
    def __str__(self):
        return str(self._cublets)
        str_list = []
        size = self._size
        for side in (TOP, LEFT, FRONT, RIGHT, DOWN, BACK):
            # Find the dimension & level
            for dimension in DIMENSIONS:
                if side in dimension: break
            else: raise EnvironmentError("dimension not found")
            if side == dimension[0]: level = size-1
            elif side == dimension[1]: level = 0
            else: raise EnvironmentError("level not found")
            # Extract pieces and add to string list in order.
            pieces = self._extract(dimension, level)
    def perform_random_turn(self):
        import random
        dimensions = list(DIMENSIONS)
        dim = random.choice(dimensions)
        level = random.randrange(self._size)
        side_ref = dim[0]
        amt = random.randrange(1, 4)
        self.turn(dim, level, side_ref, amt)

    def raw_data(self):
        return self._size, tuple(tuple(tuple(c.raw_data() \
                                             for c in y)
                                             for y in x)
                                             for x in self._cublets)
    def load(self, data):
        size, cublets = data
        self._size = size
        new_cublets = []
        for x in cublets:
            c_x = []
            new_cublets.append(c_x)
            for y in x:
                c_y = []
                c_x.append(c_y)
                for cublet_data in y:
                    cub = Cubelet(self)
                    cub.load(cublet_data)
                    c_y.append(cub)
        self._set_cublets(new_cublets)

def test():
    cube1 = Cube(5)
    cube2 = Cube(6)
    cube1.load(cube2.raw_data())

if __name__ == '__main__' and isinstance(__import__('sys').stdout, file):
    import code
    code.interact(local=globals())
