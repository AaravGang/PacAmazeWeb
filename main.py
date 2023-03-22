# MAZE CREATOR USING RANDOMISED DFS AND BACKTRACKING
# PATH GENERATION USING DFS AND BFS (ANY ONE)
import asyncio
import random  # FOR RANDOMISING THE MAZE
import time  # FOR KEEPING TRACK OF HOW MUCH TIME IT TAKES TO GENERATE THE MAZE
from queue import (
    LifoQueue as lifo,
    Queue as fifo,
)  # LIFO- USED FOR BACKTRACKING & DFS, AND FIFO- USED FOR BFS

import pygame  # USE PYGAME TO CREATE THE  GUI


pygame.init()
infoObject = pygame.display.Info()

pygame.font.init()

# mouse related vars
minSwipe = 30

# GLOBAL VARIABLES RELATED TO DRAWING THE MAZE
LENGTH, BREADTH = (
    (800, 800,)
    if infoObject.current_w > 800 and infoObject.current_h > 800
    else (infoObject.current_w, infoObject.current_h)
)

HEIGHT_BUFFER = 50  # make some space for buttons and score


rows = 15  # Number of rows = Number of cols
WIDTH = int((BREADTH - HEIGHT_BUFFER) / rows)
cols = int(LENGTH / WIDTH)

WIDTH_BUFFER = (LENGTH - cols * WIDTH) // 2


wallwidth = min(WIDTH // 10, 8)  # WIDTH OF EVERY WALL
pointRadius = min(WIDTH // 10, 8)

animate_generation = False
FPS = 10

# COLORS
KHAKI = (240, 230, 140)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
LIGHTBLUE = (200, 202, 255)
LIGHTGREEN = (20, 246, 211)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)
BROWN = (150, 94, 0)

# IMAGES
playerR = pygame.transform.scale(
    pygame.image.load("static/pacman.png"), (WIDTH // 2, WIDTH // 2)
)
playerU = pygame.transform.rotate(playerR, 90)
playerL = pygame.transform.flip(playerR, True, False)
playerD = pygame.transform.rotate(playerL, 90)

chaserImg = pygame.transform.scale(
    pygame.image.load("static/chaser.png"), (WIDTH // 2, WIDTH // 2)
)

scoreFont = pygame.font.Font("freesansbold.ttf", 25)

pause_img = pygame.transform.scale(
    pygame.image.load("static/pause.png"), (min(WIDTH, 50), min(WIDTH, 50))
)
play_img = pygame.transform.scale(
    pygame.image.load("static/play.png"), (min(WIDTH, 50), min(WIDTH, 50))
)
restart_img = pygame.transform.scale(
    pygame.image.load("static/restart.png"), (min(WIDTH, 50), min(WIDTH, 50))
)


button_style = {
    "call_on_release": True,
    "hover_color": LIGHTGREEN,
    "clicked_color": GREY,
    "click_sound": None,
    "hover_sound": None,
    "image": None,
}

pause_play_button_style = button_style.copy()
pause_play_button_style["image"] = pause_img

restart_button_style = button_style.copy()
restart_button_style["image"] = restart_img


# A FUNCTION TO CHECK IF THE USER WANTS TO QUIT PYGAME.
def CheckQuit():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print("Quit via user interruption")
            pygame.quit()
            quit()


# path finding - bfs is ideal for maze.
def bfs(start_cell, end_cell, grid):
    # CREATE A QUEUE TO SEARCH THROUGH THE MAZE 'BREADTH FIRST'
    Q = fifo()
    searched = []
    # STEP 1. MAKE THE START CELL SEARCHED AND PUSH IT TO THE QUEUE
    searched.append(start_cell)
    Q.put(start_cell)
    # CREATE A HASH-MAP TO KEEP TRACK OF WHERE EACH CELL COMES FROM ( ROOT OF EACH CELL ), AND ALL THE SEARCHED CELLS
    track = {}
    # KEEP SEARCHING UNTIL A PATH IS FOUND
    while True:
        CheckQuit()  # CHECK IF THE USER WANTS TO QUIT PYGAME
        # STEP 2
        # POP A CELL FROM THE QUEUE AND ASSIGN IT TO ROOT
        root = Q.get()
        # IF ROOT IS THE END CELL, PATH HAS BEEN FOUND
        if root == end_cell:
            # BACKTRACK THE PATH FROM THE END CELL TO THE START CELL USING THE HASH-MAP
            while track[root] != start_cell:
                CheckQuit()  # CHECK IF THE USER WANTS TO QUIT PYGAME

                # UPDATE ROOT TO BE THE ROOT OF THE CURRENT ROOT CELL
                root = track[root]
            # ANNOUNCE THE COMPLETION OF PATH
            return root

        # IF ROOT HAS ANY NEIGHBOURS, MAKE THEM ALL SEARCHED IF THEY HAVEN'T ALREADY BEEN AND PUSH THEM TO THE QUEUE
        neighbours = root.get_unsearched_neighbour(grid, searched)
        if neighbours:
            for n in neighbours:
                searched.append(n)
                track[n] = root
                Q.put(n)


# random colored chaser
def rand_chaser(image, color):
    image = image.copy()
    colorImage = pygame.Surface(image.get_size()).convert_alpha()
    colorImage.fill(color)
    image.blit(colorImage, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return image


# Class Cell. Every element in the grid is a Cell
class Cell:
    def __init__(self, row, col, width_buffer=0, height_buffer=0):
        self.row = row  # ROW NUMBER
        self.col = col  # COLUMN NUMBER
        self.y = row * WIDTH + height_buffer  # POSITION X COORDINATE
        self.x = col * WIDTH + width_buffer  # POSITION Y COORDINATE

        self.visited = False  # IS IT VISITED OR NOT, USED WHILE MAZE MAKING
        self.searched = False  # IS IT SEARCHED OR NOT, USED WHILE PATH FINDING
        self.start = False  # IS IT THE START CELL
        self.end = False  # IS IT THE END CELL
        self.ispath = False  # DOES THIS CELL COME IN THE PATH
        self.blank = False
        # RIGHT, LEFT, TOP AND BOTTOM WALLS. CHANGE TO False TO REMOVE THEM
        self.right = True
        self.left = True
        self.top = True
        self.bottom = True

        # COLORS USED FOR DRAWING THE CELL,HIGHLIGHTING IT AND DRAWING ITS WALLS
        self.color = KHAKI
        self.highlight_color = ORANGE
        self.line_color = TURQUOISE

        # is this cell the player or the chaser?
        self.playerHost = False
        self.chaserHost = False
        self.point = True
        self.chaserImg = None

    def reinit(self):
        self.visited = False  # IS IT VISITED OR NOT, USED WHILE MAZE MAKING
        self.searched = False  # IS IT SEARCHED OR NOT, USED WHILE PATH FINDING
        self.start = False  # IS IT THE START CELL
        self.end = False  # IS IT THE END CELL
        self.ispath = False  # DOES THIS CELL COME IN THE PATH
        self.blank = False
        # RIGHT, LEFT, TOP AND BOTTOM WALLS. CHANGE TO False TO REMOVE THEM
        self.right = True
        self.left = True
        self.top = True
        self.bottom = True

        # COLORS USED FOR DRAWING THE CELL,HIGHLIGHTING IT AND DRAWING ITS WALLS
        self.color = KHAKI
        self.highlight_color = ORANGE
        self.line_color = TURQUOISE

        self.playerHost = False
        self.chaserHost = False
        self.point = True
        self.chaserImg = None

    # THIS FUNCTION CHECKS ALL UNVISITED NEIGHBOURS OF A CELL AND RETURNS A RANDOM ONE IF IT DOES
    def get_neighbour(self, grid):
        neighbours = (
            []
        )  # A LIST NEIGHBOURS. TO TEMPORARILY STORE ALL NEIGHBOURS OF A GIVEN CELL

        # THIS PART IS FOR THE MAZE MAKING...HERE THE NEIGHBOURS OF A GIVEN CELL ARE THOSE CELLS WHICH SURROUND IT (TOP,BOTTOM,LEFT,RIGHT)
        # AND ARE NOT YET VISITED
        # WALLS IN BETWEEN NEIGHBOURS ARE NOT CONSIDERED
        # IF THE GIVEN CELL IS NOT THE IN FIRST ROW AND HAS A NON VISITED NEIGHBOUR ABOVE IT, APPEND IT TO NEIGHBOURS
        if (
            0 < self.row
            and not grid[self.row - 1][self.col].visited
            and not grid[self.row - 1][self.col].blank
        ):
            neighbours.append(grid[self.row - 1][self.col])  # top

        # IF THE GIVEN CELL IS NOT THE IN LAST ROW AND HAS A NON VISITED NEIGHBOUR BELOW IT, APPEND IT TO NEIGHBOURS
        if (
            rows - 1 > self.row
            and not grid[self.row + 1][self.col].visited
            and not grid[self.row + 1][self.col].blank
        ):
            neighbours.append(grid[self.row + 1][self.col])  # bottom

        # IF THE GIVEN CELL IS NOT THE IN FIRST COLUMN AND HAS A NON VISITED NEIGHBOUR TO THE LEFT OF IT, APPEND IT TO NEIGHBOURS
        if (
            0 < self.col
            and not grid[self.row][self.col - 1].visited
            and not grid[self.row][self.col - 1].blank
        ):
            neighbours.append(grid[self.row][self.col - 1])  # left

        # IF THE GIVEN CELL IS NOT THE IN LAST COLUMN AND HAS A NON VISITED NEIGHBOUR TO THE RIGHT OF IT, APPEND IT TO NEIGHBOURS
        if (
            cols - 1 > self.col
            and not grid[self.row][self.col + 1].visited
            and not grid[self.row][self.col + 1].blank
        ):
            neighbours.append(grid[self.row][self.col + 1])  # right

        # IF THERE ARE ANY NEIGHBOURS FOR A GIVEN CELL, THEN RETURN A RANDOM ONE, TO RANDOMISE THE FORMATION OF THE MAZE
        if len(neighbours) > 0:
            return neighbours[random.randint(0, len(neighbours) - 1)]
        # IF THERE ARE NO NEIGHBOURS THAT ARE UNVISITED RETURN FALSE
        return False

    # get all unsearched neighbors for path finding
    def get_unsearched_neighbour(self, grid, searched):
        neighbours = (
            []
        )  # A LIST NEIGHBOURS. TO TEMPORARILY STORE ALL NEIGHBOURS OF A GIVEN CELL

        # THIS PART IS FOR THE PATH FINDING...HERE THE NEIGHBOURS OF A CELL ARE THOSE THAT SURROUND IT
        # AND ARE NOT YET SEARCHED
        # AND THERE MUST BE NO WALL BETWEEN THE TWO NEIGHBOURS

        # IF THERE IS A RIGHT NEIGHBOUR THAT SATISFIES THE CONDITIONS APPEND IT
        if not self.right and grid[self.row][self.col + 1] not in searched:
            neighbours.append(grid[self.row][self.col + 1])  # right

        # IF THERE IS A BOTTOM NEIGHBOUR THAT SATISFIES THE CONDITIONS APPEND IT
        if not self.bottom and grid[self.row + 1][self.col] not in searched:
            neighbours.append(grid[self.row + 1][self.col])  # bottom

        # IF THERE IS A LEFT NEIGHBOUR THAT SATISFIES THE CONDITIONS APPEND IT
        if not self.left and grid[self.row][self.col - 1] not in searched:
            neighbours.append(grid[self.row][self.col - 1])  # left

        # IF THERE IS A TOP NEIGHBOUR THAT SATISFIES THE CONDITIONS APPEND IT
        if not self.top and grid[self.row - 1][self.col] not in searched:
            neighbours.append(grid[self.row - 1][self.col])  # top

        if len(neighbours) > 0:
            return neighbours

        return False

    # CHANGE THE COLOR OF THE END CELL
    def make_end(self):
        self.color = LIGHTBLUE

    # CHANGE THE COLOR OF THE START CELL
    def make_start(self):
        self.color = BROWN

    # CHANGE THE COLOR OF VISITED CELLS,WHEN MAZE IS COMPLETED ALL CELLS BECOME VISITED
    def make_visited(self):
        if not self.end and not self.start:
            self.color = BLACK

    # CHANGE THE COLOR OF THOSE CELLS THAT COME IN THE PATH FROM START TO END
    def make_path(self):
        if not self.end and not self.start:
            self.color = PURPLE

    # make it a chaser
    def make_chaser(self, img):
        self.chaserHost = True
        self.chaserImg = img

    # make player
    def make_player(self, player_img):
        self.playerHost = True
        self.playerImg = (
            player_img  # start the player facing right (if this call if the player)
        )

    # HIGHLIGHT ANY CELL FOR DEBUGGING
    def highlight(self, win):
        pygame.draw.rect(win, self.highlight_color, (self.x, self.y, WIDTH, WIDTH), 0)
        pygame.display.flip()

    # logic to move player or chaser
    def move(self, win, grid, player=None, swipe=-1):

        if self.playerHost and self.chaserHost:
            return {"defeat": True}  # game over

        # logic for moving player
        elif self.playerHost:
            score_inc = 0
            if self.point:
                self.point = False
                score_inc += 1
                self.show(win)
                pygame.display.update()

            new_player = self
            keys = pygame.key.get_pressed()

            if (keys[pygame.K_RIGHT] or swipe == 1) and not self.right:
                self.playerHost = False
                self.show(win)

                new_player = grid[self.row][self.col + 1]
                new_player.make_player(player_img=playerR)
                new_player.show(win)

                pygame.display.update()

            elif (keys[pygame.K_LEFT] or swipe == 2) and not self.left:
                self.playerHost = False
                self.show(win)

                new_player = grid[self.row][self.col - 1]
                new_player.make_player(player_img=playerL)
                new_player.show(win)

                pygame.display.update()

            elif (keys[pygame.K_DOWN] or swipe == 3) and not self.bottom:
                self.playerHost = False
                self.show(win)

                new_player = grid[self.row + 1][self.col]
                new_player.make_player(player_img=playerD)
                new_player.show(win)

                pygame.display.update()

            elif (keys[pygame.K_UP] or swipe == 4) and not self.top:
                self.playerHost = False
                self.show(win)

                new_player = grid[self.row - 1][self.col]
                new_player.make_player(player_img=playerU)
                new_player.show(win)

                pygame.display.update()

            return {"player": new_player, "score_gained": score_inc}

        # logic for moving chaser
        elif self.chaserHost:
            new_chaser = bfs(self, player, grid)

            # dont want both chasers to merge
            if not new_chaser.chaserHost:
                self.chaserHost = False
                new_chaser.make_chaser(self.chaserImg)
                self.chaserImg = None
                self.show(win)
                new_chaser.show(win)
                pygame.display.update()

                return {"chaser": new_chaser}
            return {"chaser": self}

    # THIS FUNCTION SHOWS THE CELL ON PYGAME WINDOW
    def show(self, win):
        # DRAW A RECTANGLE WITH THE DIMENSIONS OF THE CELL, TO COLOR IT
        pygame.draw.rect(win, self.color, (self.x, self.y, WIDTH, WIDTH), 0)

        # DRAW RIGHT, LEFT, TOP, BOTTOM WALLS
        if self.right:  # RIGHT
            pygame.draw.line(
                win,
                self.line_color,
                (self.x + WIDTH, self.y),
                (self.x + WIDTH, self.y + WIDTH),
                width=wallwidth,
            )
        if self.left:  # LEFT
            pygame.draw.line(
                win,
                self.line_color,
                (self.x, self.y),
                (self.x, self.y + WIDTH),
                width=wallwidth,
            )
        if self.top:  # TOP
            pygame.draw.line(
                win,
                self.line_color,
                (self.x, self.y),
                (self.x + WIDTH, self.y),
                width=wallwidth,
            )
        if self.bottom:  # BOTTOM
            pygame.draw.line(
                win,
                self.line_color,
                (self.x, self.y + WIDTH),
                (self.x + WIDTH, self.y + WIDTH),
                width=wallwidth,
            )

        # draw appropriate images
        if self.point:
            pygame.draw.circle(
                win, KHAKI, (self.x + WIDTH // 2, self.y + WIDTH // 2), pointRadius
            )
        if self.playerHost:
            win.blit(self.playerImg, (self.x + WIDTH // 4, self.y + WIDTH // 4))
        if self.chaserHost:
            win.blit(self.chaserImg, (self.x + WIDTH // 4, self.y + WIDTH // 4))


# Simple button class
class Button(object):
    def __init__(self, rect, color, function, **kwargs):
        self.rect = pygame.Rect(rect)
        self.color = color
        self.function = function
        self.clicked = False
        self.hovered = False
        self.process_kwargs(kwargs)

    def process_kwargs(self, kwargs):
        """Various optional customization you can change by passing kwargs."""
        settings = {
            "call_on_release": True,
            "hover_color": None,
            "clicked_color": None,
            "click_sound": None,
            "hover_sound": None,
            "image": None,
            "clicked_image": None,
        }
        for kwarg in kwargs:
            if kwarg in settings:
                settings[kwarg] = kwargs[kwarg]
            else:
                raise AttributeError("Button has no keyword: {}".format(kwarg))
        self.__dict__.update(settings)

    def check_event(self, event):
        """The button needs to be passed events from your program event loop."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.on_click(event)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            return self.on_release(event)

    def on_click(self, event):

        if self.rect.collidepoint(event.pos):
            self.clicked = True
            if not self.call_on_release:
                return self.function()

    def on_release(self, event):
        if self.clicked and self.call_on_release:
            self.clicked = False
            return self.function()
        self.clicked = False

    def check_hover(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if not self.hovered:
                self.hovered = True
                if self.hover_sound:
                    self.hover_sound.play()
        else:
            self.hovered = False

    def update(self, surface):
        """Update needs to be called every frame in the main loop."""
        color = self.color
        self.check_hover()
        if self.clicked and self.clicked_color:
            color = self.clicked_color

        elif self.hovered and self.hover_color:
            color = self.hover_color

        surface.fill(color, self.rect.inflate(-4, -4))

        if self.image:
            surface.blit(self.image, self.rect)


WIN = pygame.display.set_mode((LENGTH, BREADTH))
clock = pygame.time.Clock()


highscore = 0

# CREATES THE GRID FULL OF CELLS. GRID IS 2D
def setup(create=False, grid=None):
    if create:
        grid = []
        for row in range(rows):
            grid.append([])
            for col in range(cols):
                grid[row].append(
                    Cell(
                        row, col, width_buffer=WIDTH_BUFFER, height_buffer=HEIGHT_BUFFER
                    )
                )
        return grid

    else:
        for row in grid:
            for cell in row:
                cell.reinit()


GRID = setup(create=True)  # THE ENTIRE GRID/MAZE STORED IN  A 2D ARRAY
start = GRID[0][0]
end = GRID[-1][-1]


# change highscore
def change_highscore(s):
    global highscore
    highscore = s


# empty off some space in the middle where ghosts live
def make_den(size=2):
    for i in range(rows // 2 - 1, rows // 2 + rows % 2 + 1):
        for j in range(cols // 2 - 1, cols // 2 + cols % 2 + 1):
            GRID[i][j].blank = True


# FUNCTION TO REMOVE A WALL BETWEEN THE CURRENT AND THE NEXT CELL
def removeWall(curr, next):
    # r IS THE CURRENT ROW - NEXT ROW AND c IS THE CURRENT COLUMN - NEXT COLUMN
    r, c = curr.row - next.row, curr.col - next.col
    # IF c IS 1 WE KNOW THE NEXT CELL IS THE TO THE LEFT OF THE CURRENT CELL
    if c == 1:
        curr.left = False
        next.right = False
    # IF c IS -1 WE KNOW THE NEXT CELL IS THE TO THE RIGHT OF THE CURRENT CELL
    if c == -1:
        next.left = False
        curr.right = False
    # IF r IS 1 WE KNOW THE CURRENT CELL IS BELOW THE NEXT CELL
    if r == 1:
        next.bottom = False
        curr.top = False
    # IF r IS -1 WE KNOW THE CURRENT CELL IS ABOVE THE NEXT CELL
    if r == -1:
        curr.bottom = False
        next.top = False

    # SHOW THE UPDATED VERSIONS OF THE CURRENT AND NEXT CELL
    if animate_generation:
        curr.show(WIN)
        next.show(WIN)
        pygame.display.flip()


# THE ALGORITHM FOR CREATING THE MAZE
def maze_algorithm():
    all_visited = False
    paths = {}  # CREATE A DICTIONARY TO STORE ALL THE ROOT CELLS OF EVERY VISITED CELL

    # STARTING THE TIMER FOR MAZE MAKING
    start_time = time.time()

    # ---- STEP 1 MAZE MAKER ---- #
    # MAKE THE START CELL FOR MAZE MAKING (THE CELL TO BEGIN MAKING THE MAZE FROM)
    # MAKE THE CURRENT CELL THE START CELL
    # MAKE IT VISITED
    start = GRID[0][0]
    current = start
    current.visited = True
    current.make_visited()

    # INITIALISE THE STACK FOR BACKTRACKING ( WHEN THERE ARE NO NEIGHBOURS FOR A CELL, BACKTRACK TO A CELL WITH NEIGHBOURS )
    stack = lifo()

    # --- STEP 2--- #
    # WHILE THERE ARE UNVISITED CELLS
    while not all_visited:
        CheckQuit()  # CHECK IF THE USER WANTS TO QUIT PYGAME

        next = current.get_neighbour(
            GRID
        )  # STEP 2.1, A RANDOM UNVISITED NEIGHBOUR. VALUE IS FALSE IF THERE ARE NONE
        if (
            next
        ):  # CONDITION OF STEP 2.1. IF THERE ARE ANY UNVISITED NEIGHBOURS THEN DO THE FOLLOWING
            stack.put(current)  # STEP 2.1.2... PUSH THE CURRENT CELL TO THE STACK
            removeWall(
                current, next
            )  # STEP 2.1.3... REMOVE THE WALL BETWEEN THE CURRENT AND THE NEXT CELL
            # STEP 2.1.4... MARK THE CHOSEN CELL AS VISITED AND MAKE IT THE CURRENT CELL
            next.visited = True
            next.make_visited()
            paths[
                next
            ] = current  # BEFORE MAKING NEXT CURRENT MAKE CURRENT THE ROOT OF THE NEXT CELL, TO HELP IN PATH FINDING
            current = next

        elif (
            stack.qsize() > 0
        ):  # STEP 2.2... IF THERE ARE NO UNVISITED NEIGHBOURS AND THE STACK SIZE IS NOT ZERO
            current = (
                stack.get()
            )  # STEP 2.2.1. POP A CELL FROM THE STACK AND MAKE IT THE CURRENT CELL

        # SHOW THE UPDATED CURRENT CELL
        if animate_generation:
            current.show(WIN)
            pygame.display.flip()

        # ---- STEP 2 DONE ---- ALGORITHM IS COMPLETE ----

        # IF ALL CELLS ARE VISITED, ANNOUNCE THE COMPLETION OF MAZE TO BE ABLE TO CONTINUE WITH THE PATH FINDING
        if stack.qsize() == 0:
            all_visited = True
            end_time = time.time()  # END THE TIMER
            # PRINT THE TIME TAKE TO FIND THE PATH
            print(f"Time taken to create the maze : {end_time - start_time}")

            # SAVE AN IMAGE OF THE MAZE
            # pygame.image.save(WIN, 'maze.png')


# show all the cells
def draw_grid():
    WIN.fill(BLACK)
    for i in range(rows):
        for j in range(cols):
            GRID[i][j].show(WIN)

    # pygame.draw.rect(WIN,TURQUOISE,(GRID[0][0].x,GRID[0][0].y,cols*WIDTH,rows*WIDTH),width=wallwidth)

    # blit_pic(centerPic, (WIDTH * (cols // 4) + wallwidth // 2), (WIDTH * (rows // 4)) + wallwidth // 2)
    write_text(
        scoreFont,
        TURQUOISE,
        f"High Score: {highscore}",
        LENGTH - max(100, scoreFont.size(f"High Score: {highscore}")[0] + 10),
        10,
        True,
    )

    pygame.display.update()


def write_text(font, color, text, x, y, fill=True, center=False):
    text = font.render(text, True, color)
    textRect = text.get_rect()

    if center:
        textRect.center = (x, y)
    else:
        textRect.topleft = (x, y)
    if fill:
        WIN.fill(BLACK, textRect)
    WIN.blit(text, textRect)
    pygame.display.flip()


# function to randomly remove a few walls to make it easy.
def make_easy(difficulty=25):  # simplicity: 25 %
    for i in range(1, rows - 1):
        for j in range(1, cols - 1):
            if not GRID[i][j].blank:
                # 1 in 4 chance to remove each wall
                removeProbability = [random.randint(0, 3) for _ in range(4)][
                    : int(4 * (100 - difficulty) / 100)
                ]
                if (
                    GRID[i][j].right
                    and 0 in removeProbability
                    and not GRID[i][j + 1].blank
                ):
                    removeWall(GRID[i][j], GRID[i][j + 1])
                if (
                    GRID[i][j].left
                    and 0 in removeProbability
                    and not GRID[i][j - 1].blank
                ):
                    removeWall(GRID[i][j], GRID[i][j - 1])
                if (
                    GRID[i][j].top
                    and 0 in removeProbability
                    and not GRID[i - 1][j].blank
                ):
                    removeWall(GRID[i][j], GRID[i - 1][j])
                if (
                    GRID[i][j].bottom
                    and 0 in removeProbability
                    and not GRID[i + 1][j].blank
                ):
                    removeWall(GRID[i][j], GRID[i + 1][j])


def blit_pic(pic, x, y):
    WIN.blit(pic, (x, y))
    pygame.display.update()


# initialise all vars
def restart(level=1):
    setup(create=False, grid=GRID)
    # make_den()

    player = GRID[0][0]
    player.make_player(player_img=playerR)

    chasers = []

    free_spots = sum(
        [
            list(filter(lambda spot: not spot.blank, row[cols // 2 :]))
            for row in GRID[rows // 2 :]
        ],
        [],
    )

    while len(chasers) < level:
        chaser_temp = random.choice(free_spots)
        free_spots.remove(chaser_temp)
        chaser_temp.make_chaser(
            rand_chaser(
                chaserImg,
                (
                    random.randint(128, 255),
                    random.randint(128, 255),
                    random.randint(128, 255),
                ),
            )
        )
        chasers.append(chaser_temp)

    draw_grid()

    return (
        player,
        chasers,
        level,
    )


# Function to detect swipes
# -1 is that it was not detected as a swipe or click
# It will return 1 , 2 for horizontal swipe
# If the swipe is vertical will return 3, 4
# If it was a click it will return 0
def getSwipeType(rel):
    x, y = rel if rel else pygame.mouse.get_rel()
    if abs(x) <= minSwipe:
        if y > minSwipe // 2:
            return 3
        elif y < -minSwipe // 2:
            return 4
    elif abs(y) <= minSwipe:
        if x > minSwipe // 2:
            return 1
        elif x < -minSwipe // 2:
            return 2

    return -1


# creates maze and then starts game
async def main(player, chasers, level):
    run = True  # WHILE THIS IS TRUE THE MAIN LOOP WILL RUN

    # DRAW THE GRID
    draw_grid()
    pygame.display.set_caption("Creating Maze...")
    print("Creating Maze...")

    # CREATE THE MAZE
    maze_algorithm()

    make_easy(min(100, 75))  # randomly remove a few walls

    draw_grid()

    pygame.display.set_caption("Hit space to start game.")
    print("Maze Created...Hit space to start game.")
    maze_created = True

    # THE MAIN GUI LOOP
    while run:
        for event in pygame.event.get():
            # IF THE USER HITS THE CROSS BUTTON . CLOSE THE WINDOW
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
            # IF THE USER PRESSES ANY KEY PROCEED TO THE FOLLOWING
            if event.type == pygame.KEYDOWN or pygame.MOUSEBUTTONUP:
                if maze_created:  # and event.key == pygame.K_SPACE:
                    run = False
                    break

        await asyncio.sleep(0)
    await game(player, chasers, level)


# all the game logic
async def game(player, chasers, level):
    run = True

    count = 0
    score = 0

    game_over = False
    defeat = False

    pause_play = Button(
        pygame.Rect(
            LENGTH // 2 - min(WIDTH, 50),
            (HEIGHT_BUFFER - min(WIDTH, 50)) / 2,
            min(WIDTH, 50),
            min(WIDTH, 50),
        ),
        BLACK,
        lambda: True,
        **pause_play_button_style,
    )
    paused = False

    restart_button = Button(
        pygame.Rect(
            LENGTH // 2 + min(WIDTH, 50),
            (HEIGHT_BUFFER - min(WIDTH, 50)) / 2,
            min(WIDTH, 50),
            min(WIDTH, 50),
        ),
        BLACK,
        lambda: True,
        **restart_button_style,
    )
    score = 0

    pygame.display.set_caption(f"Level: {len(chasers)}")
    print("Game started.")
    swipe = 0

    while run:
        clock.tick(FPS)
        await asyncio.sleep(0)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                print("Quit via user interruption")
                pygame.quit()
                quit()

            if e.type == pygame.MOUSEMOTION:
                if e.touch:
                    s = getSwipeType(e.rel)
                    if s > 0:
                        swipe = s

            if e.type == pygame.KEYDOWN:
                swipe = 0

            if pause_play.check_event(e):
                paused = not paused
                pause_play.image = play_img if paused else pause_img

            if restart_button.check_event(e):
                return await main(*restart(level))

        pause_play.update(WIN)
        restart_button.update(WIN)

        pygame.display.update()

        if paused:
            continue

        if player:
            payload = player.move(WIN, GRID, swipe=swipe)
            count += 1

            defeat = payload.get("defeat")
            player = payload.get("player")
            score += (
                payload.get("score_gained") if payload.get("score_gained") else 0
            ) * level

            write_text(
                scoreFont, YELLOW, f"Score: {score}", 10, 10, True,
            )
            if score > highscore:
                change_highscore(score)
            write_text(
                scoreFont,
                TURQUOISE,
                f"High Score: {highscore}",
                LENGTH - max(100, scoreFont.size(f"High Score: {highscore}")[0] + 10),
                10,
                True,
            )

        if game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RETURN] or pygame.mouse.get_pressed()[0]:
                print("LEVEL:", level)
                return await main(*restart(level))

        elif score >= (rows * cols) * level:
            write_text(
                pygame.font.Font("freesansbold.ttf", 100),
                PURPLE,
                "You Have Won!",
                LENGTH // 2,
                BREADTH // 2,
                False,
                True,
            )

            pygame.display.set_caption("Hit Enter to Restart.")
            print("Game Over. Hit Enter to Restart.")

            level += 1

            game_over = True

        elif defeat:
            write_text(
                pygame.font.Font("freesansbold.ttf", 100),
                PURPLE,
                "Game Over!",
                LENGTH // 2,
                BREADTH // 2,
                False,
                True,
            )

            pygame.display.set_caption("Hit Enter to Restart.")
            print("Game Over. Hit Enter to Restart.")

            game_over = True

        elif count % 10 == 0:
            for ind, c in enumerate(chasers):
                new_chaser = c.move(WIN, GRID, player).get("chaser")
                if new_chaser:
                    chasers[ind] = new_chaser
            count = 0


if __name__ == "__main__":
    asyncio.run(main(*restart()))
