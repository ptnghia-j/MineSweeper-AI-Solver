#
# Remake of the classic Minesweeper game
#

import datetime
import random
import pygame
import sys

sys.path.append('../')

#import sleep module
from time import sleep


class MineSweeper:
    """
    Classic MineSweeper remake 
    Game can be played by a human player, and AI player
    
    AI player has 3 level of mastery: 
        logicPlayer (play easy and intermediate well),
        ProbabilityPlayer (play intermediate and expert well), 
        and ANNPlayer (play expert and custom mode well as the data it is trained on grows)


    Beginner: 9x9, 10 bombs
    Intermediate: 16x16, 40 bombs
    Expert: 30x16, 99 bombs

    Custom: user defined

    !!! NOTE:
    A tile is described as tile[y][x], with y being the row and x being the column 
    as x being the horizontal axis and y being the vertical axis

    80 x 45 , 742 mines

    !!! When adjust the size of the game, also adjust the number of mines accordingly
    mine density in easy mode: 12.345%
    mine density in intermediate mode: 15.625%
    mine density in expert mode: 20.625%
    """
    
    

    def __init__(self, width=80, height=45, bomb_count=742):
        self.width = width
        self.height = height
        self.bomb_count = bomb_count

        # ALGORITHM
        self.grid = None
        self.clicked_grid = [
            [False for x in range(self.width)] for y in range(self.height)
        ]
        self.first_click = True
        self.game_failed = False
        self.game_won = False
        self.bomb_left = self.bomb_count
        self.timer = 0
        self.start_time = None

        # UI/PYGAME
        self.margin = 10
        self.top_bar = 32
        self.tile_size = 16
        self.border = 1
        self.face_size = 26
        self.window_width = self.width * self.tile_size + self.margin * 2
        self.window_height = self.height * self.tile_size + self.margin * 3 + self.top_bar
        
        self.window_size = (self.window_width, self.window_height)
        self.window = pygame.display.set_mode(self.window_size, 0, 0)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Minesweeper")
        self.image_folder = "../img/"
        pygame.display.set_icon(pygame.image.load(self.image_folder + "ico.png"))

        # IMAGES
        self.undiscovered_tile = self.image_folder + "undiscovered_tile.png"
        self.discovered_tile = self.image_folder + "discovered_tile.png"
        self.flag = self.image_folder + "flag.png"
        self.bomb = self.image_folder + "bomb.png"
        self.flaged_bomb = self.image_folder + "flaged_bomb.png"
        self.exploded_bomb = self.image_folder + "bomb_exploded.png"
        self.question = self.image_folder + "question.png"
        self.background = self.image_folder + "background.png"
        # tile numbers
        self.number_image_folder = self.image_folder + "tiles/"
        self.number = [0 for x in range(11)]
        for x in range(len(self.number)):
            self.number[x] = self.number_image_folder + str(x) + ".png"
        # face images
        self.face_image_folder = self.image_folder + "faces/"
        self.face_happy = self.face_image_folder + "happy.png"
        self.face_death = self.face_image_folder + "death.png"
        self.face_cool = self.face_image_folder + "cool.png"
        # timer/flag counter images
        self.counter_image_folder = self.image_folder + "counter/"
        self.counter = [0 for x in range(11)]
        for x in range(len(self.counter)):
            self.counter[x] = self.counter_image_folder + str(x) + ".png"

        # COLORS
        self.background_color = (180, 180, 180)

    def game_loop(self):
        """
        Game loop with different actions based on user input type
        (right-left click) and click position (top-bar/grid)
        """
        pygame.init()
        self.init_display()
        while True:
            pygame.display.update()
            self.clock.tick(60)

            self.human_play()
                    
            self.update_timer()
      
    def human_play(self, end = False):
        """
        Human play mode
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_action(event)
            
            

    def mouse_action(self, event):
        """
        When a click is registered on the window
        """
        clicked_register = False
        pos = pygame.mouse.get_pos()

        # if the click is on the grid
        if (
            self.margin < pos[0] < self.window_width - self.margin
            and self.margin * 2 + self.top_bar
            < pos[1]
            < self.window_height - self.margin
            and self.game_failed is False
            and self.game_won is False
        ):
            self.grid_click(event.button, pos)
            clicked_register = True

        # if the click is on the face
        elif (
            self.window_width / 2 - self.face_size / 2
            < pos[0]
            < self.window_width / 2 - self.face_size / 2 + self.face_size
            and self.margin + self.top_bar / 2 - self.face_size / 2
            < pos[1]
            < self.margin + self.top_bar / 2 - self.face_size / 2 + self.face_size
        ):
            self.face_click()
            clicked_register = True

        self.display_top_bar()
        return clicked_register

    def grid_click(self, button, pos):
        """
        When a click is registered on the grid
        """
        y = int((pos[1] - self.margin * 2 - self.top_bar) / self.tile_size)
        x = int((pos[0] - self.margin) / self.tile_size)

        # left click
        if button == 1:
            self.click_register(x, y)
            if self.game_failed is False:
                self.display_tiles()

        # right click
        elif button == 3:
            self.right_click_register(x, y)

        self.win_test()

    def face_click(self):
        """
        When a click is registered on the face restart the game
        """
        self.__init__(
            width=self.width, height=self.height, bomb_count=self.bomb_count,
        )
        self.game_loop()


    def init_display(self):
        """
        Initialize the display by updating background, tiles and top bar
        """
        self.display_background()
        self.display_tiles()
        self.display_top_bar()

    def display_background(self):
        """
        Update the background image
        """
        self.window.blit(pygame.image.load(self.background), (0, 0))

    def display_face(self):
        """
        Update the face on the top bar
        """
        if self.game_failed:
            face = self.face_death
        elif self.game_won:
            face = self.face_cool
        else:
            face = self.face_happy

        self.window.blit(
            pygame.image.load(face),
            (
                self.window_width / 2 - self.face_size / 2,
                self.margin + self.top_bar / 2 - self.face_size / 2,
            ),
        )

    def display_bomb_counter(self):
        """
        Update the bomb counter
        """
        count = "000" + str(self.bomb_left)
        for x in range(3):
            number = count[-(3 - x)]
            if number == "-":
                number = 10
            self.display_counter_digit(
                self.margin + 6 + 13 * x, self.margin + 4, number
            )

    def display_timer_counter(self):
        """
        Update the timer displayed
        """
        count = "000" + str(self.timer)
        for x in range(3):
            self.display_counter_digit(
                self.window_width - (self.margin + 6 + 13 * (3 - x)),
                self.margin + 4,
                count[-(3 - x)],
            )

    def display_counter_digit(self, x, y, digit):
        """
        Update a single digit of either the bomb counter or the timer
        """
        self.window.blit(pygame.image.load(self.counter[int(digit)]), (x, y))

    def display_top_bar(self):
        """
        Update the top bar, with timer, bomb counter and face
        """
        # reset the top bar
        self.window.fill(
            self.background_color,
            pygame.Rect(
                (
                    (self.margin, self.margin),
                    (self.window_width - self.margin * 2, self.top_bar),
                )
            ),
        )

        self.display_face()
        self.display_bomb_counter()
        self.display_timer_counter()

    def update_timer(self):
        """
        Update the timer displayed to the player
        """
        if (
            self.start_time is not None
            and self.game_failed is False
            and self.game_won is False
        ):
            self.timer = int(
                (datetime.datetime.now() - self.start_time).total_seconds()
            )
        self.display_timer_counter()

    def tile_position(self, x, y):
        """
        convert a grid position into gui position of a tile
        """
        gui_x = self.margin + self.tile_size * x
        gui_y = self.margin * 2 + self.tile_size * y + self.top_bar
        return gui_x, gui_y

    def display_tiles(self):
        """
        Update the display of every tiles on the grid
        """
        for x in range(self.width):
            for y in range(self.height):
                self.display_one_tile(x, y)

    def display_one_tile(self, x, y):
        """
        Update the display of a single tile on the grid
        """
        if self.clicked_grid[y][x] is True:
            if isinstance(self.grid[y][x], int):
                # number tile
                self.window.blit(
                    pygame.image.load(self.number[self.grid[y][x]]),
                    self.tile_position(x, y),
                )

            else:
                # empty tile
                self.window.blit(
                    pygame.image.load(self.discovered_tile), self.tile_position(x, y)
                )

        elif self.clicked_grid[y][x] == "F":
            # flagged tile
            self.window.blit(pygame.image.load(self.flag), self.tile_position(x, y))

        elif self.clicked_grid[y][x] == "?":
            # question tile
            self.window.blit(
                pygame.image.load(self.question), self.tile_position(x, y)
            )

        else:
            # undiscovered tile
            self.window.blit(
                pygame.image.load(self.undiscovered_tile), self.tile_position(x, y)
            )

    def show_bombs(self, exploded_x, exploded_y):
        """
        At the end of the game every bombs are shown to the player
        """
        for x in range(self.width):
            for y in range(self.height):
                if self.grid[y][x] == "*":
                    if self.clicked_grid[y][x] == "F" or self.clicked_grid[y][x] == "?":
                        self.window.blit(
                            pygame.image.load(self.flaged_bomb),
                            self.tile_position(x, y),
                        )
                    else:
                        self.window.blit(
                            pygame.image.load(self.bomb), self.tile_position(x, y)
                        )

        self.window.blit(
            pygame.image.load(self.exploded_bomb),
            self.tile_position(exploded_x, exploded_y),
        )

    def click_register(self, x, y):
        """
        When a user left click on the tile at position x, y
        """
        # Bombs are placed after the first click, preventing the
        # player from clicking on a bomb at first click
        if self.first_click:
            self.first_click = False
            self.generate_grid()
            while self.grid[y][x] != " ":
                self.generate_grid()
            self.start_time = datetime.datetime.now()

        if self.clicked_grid[y][x] is False:
            
            self.clicked_grid[y][x] = True
            if self.grid[y][x] == "*":
                self.game_failed = True
                self.show_bombs(x, y)
            elif self.grid[y][x] == " ":
                self.discover_tiles(x, y)

    def right_click_register(self, x, y):
        """
        When a user right click on the tile at position x, y
        """
        if self.clicked_grid[y][x] == "F":
            self.clicked_grid[y][x] = "?"
            self.bomb_left += 1
        elif self.clicked_grid[y][x] == "?":
            self.clicked_grid[y][x] = False
        elif self.clicked_grid[y][x] is False:
            self.clicked_grid[y][x] = "F"
            self.bomb_left -= 1
        self.display_one_tile(x, y)

    def discover_tiles(self, x, y):
        """
        Will pass on all 8 adjacent tiles and
        if they are either number or empty it will be recursive
        """
        for n in range(-1, 2):
            for m in range(-1, 2):
                u = x + m
                v = y + n
                if 0 <= v <= (self.height - 1) and 0 <= u <= (self.width - 1):
                    if self.grid[v][u] == " " or isinstance(self.grid[v][u], int):
                        self.click_register(u, v)

    def win_test(self):
        """
        Test if player has won the game or not
        and update self.game_won
        """
        if self.grid is not None:
            for x in range(self.width):
                for y in range(self.height):
                    if (
                        (self.grid[y][x] == "*" and self.clicked_grid[y][x] != "F")
                        or (self.clicked_grid[y][x] == "F" and self.grid[y][x] != "*")
                        or (self.clicked_grid[y][x] is False and self.grid[y][x] != "*")
                    ):
                        return
            self.game_won = True

    def generate_grid(self):
        """
        Generate a random grid filled with bomb and with numbers
        """
        self.grid = [[" " for x in range(self.width)] for y in range(self.height)]
        self.place_bombs()
        self.attribute_value()

    def place_bombs(self):
        """
        Randomly place bombs on the grid
        """
        bomb_count = 0
        while bomb_count != self.bomb_count:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if self.grid[y][x] != "*":
                self.grid[y][x] = "*"
                bomb_count += 1

    def attribute_value(self):
        """
        Place numbers on the grid based on the number of bomb in
        the 8 adjacent tiles
        """
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                if self.grid[y][x] != "*":
                    c = 0
                    for n in range(-1, 2):
                        for m in range(-1, 2):
                            u = x + m
                            v = y + n
                            if (
                                0 <= u and u <= (self.width - 1)
                                and
                                0 <= v and v <= (self.height - 1) 
                            ):
                                if self.grid[v][u] == "*":
                                    c += 1
                    if c > 0:
                        self.grid[y][x] = c
                    else:
                        self.grid[y][x] = " "


if __name__ == "__main__":
    
    session = MineSweeper()
    session.game_loop()
