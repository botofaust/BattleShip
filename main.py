import random


BOARD_SIZE = 6
BOARD_RANGE = range(1, BOARD_SIZE + 1)
LEN_SHIPS = [3, 2, 2, 1, 1, 1, 1]
EMPTY_FIELD = "O"
SHIP_FIELD = "*"
CONTOUR_FIELD = "C"
MISS_FIELD = "M"
FIRE_FIELD = "F"
GRAPHICS = {EMPTY_FIELD: ".", SHIP_FIELD: "S", CONTOUR_FIELD: ".", MISS_FIELD: "T", FIRE_FIELD: "X"}


class BoardOutException(Exception):
    pass


class FieldNotEmptyException(Exception):
    pass


class GameOverException(Exception):
    pass


class Dot:
    def __init__(self, x, y):
        if x not in BOARD_RANGE or y not in BOARD_RANGE:
            raise BoardOutException()
        self.x_coord = x
        self.y_coord = y

    def __eq__(self, other):
        return self.x_coord == other.x and self.y_coord == other.y

    @property
    def x(self):
        return self.x_coord

    @x.setter
    def x(self, value):
        if value in BOARD_RANGE:
            self.x_coord = value
        else:
            raise BoardOutException()

    @property
    def y(self):
        return self.y_coord

    @y.setter
    def y(self, value):
        if value in range(1, BOARD_SIZE + 1):
            self.y_coord = value
        else:
            raise BoardOutException()


class Ship:
    def __init__(self, start_dot, end_dot):
        self.start_dot = start_dot
        self.end_dot = end_dot

    @property
    def length(self):
        return abs(self.start_dot.x - self.end_dot.x) + abs(self.start_dot.y - self.end_dot.y) + 1

    def is_hit(self, dot):
        result = False
        for ship_part in self.dots:
            if dot == ship_part:
                result = True
                break
        return result

    def dots(self):
        x_coords = (self.start_dot.x, self.end_dot.x)
        y_coords = (self.start_dot.y, self.end_dot.y)
        return [Dot(x, y) for x in range(min(x_coords), max(x_coords) + 1) for y in range(min(y_coords), max(y_coords) + 1)]


class Board:
    def __init__(self, hidden):
        self.game_net = [[EMPTY_FIELD for x in BOARD_RANGE] for y in BOARD_RANGE]
        self.hidden = hidden
        self.fires = 0
        self.ships_segments = 0

    def contour(self, ship):
        for x in range(max(1, ship.dots()[0].x - 1) - 1, min(BOARD_SIZE, ship.dots()[-1].x + 1)):
            for y in range(max(1, ship.dots()[0].y - 1) - 1, min(BOARD_SIZE, ship.dots()[-1].y + 1)):
                self.game_net[x][y] = CONTOUR_FIELD

    def possible_add(self, ship):
        result = True
        for dot in ship.dots():
            if self.game_net[dot.x - 1][dot.y - 1] != EMPTY_FIELD:
                result = False
                break
        return result

    def add_ship(self, ship):
        result = self.possible_add(ship)
        if result:
            self.contour(ship)
            for dot in ship.dots():
                self.game_net[dot.x - 1][dot.y - 1] = SHIP_FIELD
            self.ships_segments += ship.length
        return result

    def output(self):
        output_str = '  '
        for x in BOARD_RANGE:
            output_str += str(x) + '|'
        print(output_str)
        for x in BOARD_RANGE:
            output_str = str(x) + '|'
            for y in BOARD_RANGE:
                if self.hidden and self.game_net[x - 1][y - 1] == SHIP_FIELD:
                    output_str += GRAPHICS[EMPTY_FIELD] + '|'
                else:
                    output_str += GRAPHICS[self.game_net[x - 1][y - 1]] + '|'
            print(output_str)

    def generate(self):
        generated = False
        while not generated:
            self.__init__(self.hidden)
            counter = 0
            num_ships = 0
            while counter != 1000 and num_ships != len(LEN_SHIPS):
                counter += 1
                vert = random.random() < 0.5
                if vert:
                    start_dot = Dot(random.randint(1, BOARD_SIZE), random.randint(1, BOARD_SIZE - LEN_SHIPS[num_ships]))
                    end_dot = Dot(start_dot.x, start_dot.y + LEN_SHIPS[num_ships] - 1)
                else:
                    start_dot = Dot(random.randint(1, BOARD_SIZE - LEN_SHIPS[num_ships]), random.randint(1, BOARD_SIZE))
                    end_dot = Dot(start_dot.x + LEN_SHIPS[num_ships] - 1, start_dot.y)
                ship = Ship(start_dot, end_dot)
                if self.add_ship(ship):
                    num_ships += 1
            generated = counter < 1000
        for x in BOARD_RANGE:
            for y in BOARD_RANGE:
                if self.game_net[x - 1][y - 1] == CONTOUR_FIELD:
                    self.game_net[x - 1][y - 1] = EMPTY_FIELD

    def fire(self, dot):
        result = False
        field = self.game_net[dot.x - 1][dot.y - 1]
        if field != MISS_FIELD and field != FIRE_FIELD:
            if field == SHIP_FIELD:
                self.fires += 1
                result = True
            self.game_net[dot.x - 1][dot.y - 1] = MISS_FIELD if field == EMPTY_FIELD else FIRE_FIELD
        else:
            raise FieldNotEmptyException()
        if self.fires == self.ships_segments:
            raise GameOverException()
        return result


class Player:
    def __init__(self, is_human, board):
        self.is_human = is_human
        self.enemy_board = board

    def human_turn(self):
        result = False
        good_coords = False
        while not good_coords:
            try:
                coords = list(map(int, input('(row col)?').split()))
                x, y = coords[0], coords[1]
            except Exception:
                print('Incorrect input')
            else:
                try:
                    dot = Dot(coords[0], coords[1])
                except BoardOutException:
                    print('Bad coords')
                else:
                    try:
                        result = self.enemy_board.fire(dot)
                    except FieldNotEmptyException:
                        print('Repeated turn')
                    else:
                        good_coords = True
        return result

    def comp_turn(self):
        result = False
        good_coords = False
        while not good_coords:
            dot = Dot(random.randint(1, BOARD_SIZE), random.randint(1, BOARD_SIZE))
            try:
                result = self.enemy_board.fire(dot)
            except FieldNotEmptyException:
                pass
            else:
                good_coords = True
        return result

    def turn(self):
        if self.is_human:
            return self.human_turn()
        else:
            return self.comp_turn()


class Game:
    def __init__(self):
        self.human_board = Board(False)
        self.comp_board = Board(True)
        self.human = Player(True, self.comp_board)
        self.comp = Player(False, self.human_board)

    def print_boards(self):
        self.human_board.output()
        print('')
        self.comp_board.output()

    def start(self):
        self.human_board.generate()
        self.comp_board.generate()
        while True:
            self.print_boards()
            try:
                while self.human.turn():
                    self.print_boards()
            except GameOverException:
                print('Human win :(')
                return 'human'
            self.print_boards()
            try:
                while self.comp.turn():
                    self.print_boards()
            except GameOverException:
                print('Computer is always smarter')
                return 'comp'


game = Game()
game.start()
