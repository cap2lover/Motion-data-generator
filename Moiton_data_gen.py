import pygame as pg

import pyautogui  # get the size of the screen
from scipy.special import binom  # for Bernstein polynomial

# 1366x768 -> 1920x1200
# WIDTH, HEIGHT = pyautogui.size()
WIDTH = 1920
HEIGHT = 1200
# WIDTH = 1366
# HEIGHT = 768
WIN = pg.display.set_mode((WIDTH, HEIGHT))
K: float = HEIGHT / 1200

input_boxes = []


BLOCK: int = int((100 * K) - (100 * K) % 2)


colors: dict = {
    "fill": "#212122",
    "rect": "#3F3D43",
    "header": "#151515",
    "area": "#282828",
    "grid_main_line": "#8a8996",
    "grid_sub_line": "#4e4e59",
    "main_dot": "#3e702c",
    "middle_dot": "#6f964d",
    "start_button": "#2e601c",
    "pause_button": "#2f560d",
    "moving_dot": "#fb4943",
    "line": "#f6e2c5",
    "text": "#000000",
    "input": "#2F2D33",
    "back": "#0f360d"
}

# ---------------------------------------------------------------------------- drawing simple items
def draw_grid():
    WIN.fill(colors["fill"])

    end_x = 15 * BLOCK
    end_y = 10 * BLOCK

    pg.draw.rect(WIN, colors["area"], (BLOCK, BLOCK, end_x - BLOCK, end_y - BLOCK))

    draw_axis_numbers()
    count_x = 0
    count_y = 0

    for j in range(BLOCK, 10 * BLOCK + 1, int(BLOCK / 2)):  # horizontal lines
        if count_x % 2 == 0:
            color = colors["grid_main_line"]
        else:
            color = colors["grid_sub_line"]
        pg.draw.line(WIN, color, (BLOCK, j), (end_x, j))
        count_x += 1

    for m in range(BLOCK, 15 * BLOCK + 1, int(BLOCK / 2)):  # vertical lines
        if count_y % 2 == 0:
            color = colors["grid_main_line"]
        else:
            color = colors["grid_sub_line"]
        pg.draw.line(WIN, color, (m, BLOCK), (m, end_y))
        count_y += 1


def draw_button(label: str, color: str, x: int, y: int, width, height, size):
    pg.draw.rect(WIN, color, (x, y, width, height), int(height / 2), 10)
    blit_text(label, x + int(width / 2), y + int(height / 2), size, True, True, "xy")


def draw_curve_dots(coord_list: list):
    for k in range(0, len(coord_list) - 1, 2):
        if k == 0 or k == len(coord_list) - 2:
            color = colors["main_dot"]
        else:
            color = colors["middle_dot"]
        pg.draw.circle(WIN, color, (coord_list[k] / 100 * BLOCK + BLOCK, coord_list[k + 1] / 100 * BLOCK + BLOCK),
                       10 * K)


def draw_axis_numbers():
    count = 0
    for step in range(BLOCK, 16 * BLOCK, BLOCK):
        blit_text(str(count), step, BLOCK - int(5 * K), 15, False, True, "x")
        count += 100
    count = 100
    for step in range(2 * BLOCK, 11 * BLOCK, BLOCK):
        blit_text(str(count), BLOCK - int(10 * K), step, 15, False, True, "y")
        count += 100


def blit_text(string: str, x: int, y: int, size: int, bold=False, change=False, change_coord="", text_color=""):
    font = pg.font.SysFont("Arial", int(size * K), bold=True) if bold else pg.font.SysFont("Arial", int(size * K))
    color = colors["red"] if text_color == "red" else colors["line"]

    text = font.render(string, True, color)

    if change:
        x -= text.get_width()
        y -= text.get_height()
        if "x" in change_coord:
            x += text.get_width() / 2
        if "y" in change_coord:
            y += text.get_height() / 2

    WIN.blit(text, (x, y))


def draw_input_box(points: int, active_box: int, coord_list: list):
    input_boxes.clear()

    for i in range(1, points + 1):
        pg.draw.line(WIN, colors["header"], (BLOCK, 2 * BLOCK + BLOCK * i + int((HEIGHT - 4 * BLOCK) / 10)),
                     (BLOCK + (WIDTH - BLOCK) / 5 * 3 - 1, 2 * BLOCK + BLOCK * i + int((HEIGHT - 4 * BLOCK) / 10)), 2)
        blit_text(str(i + 1), int(1.2 * BLOCK), 2 * BLOCK + i * BLOCK, 30, bold=True)
        blit_text("X:", int(2.9 * BLOCK), 2 * BLOCK + i * BLOCK + int(0.1 * BLOCK), 50)
        blit_text("Y:", int(7.4 * BLOCK), 2 * BLOCK + i * BLOCK+ int(0.1 * BLOCK), 50)

        color_x = colors["start_button"] if active_box == i * 2 - 1 else colors["input"]
        color_y = colors["start_button"] if active_box == i * 2 else colors["input"]

        pg.draw.rect(WIN, color_x, (int(3.5 * BLOCK), 2 * BLOCK + i * BLOCK, 2 * BLOCK, BLOCK - int(25 * K)))
        pg.draw.rect(WIN, color_y, (8 * BLOCK, 2 * BLOCK + i * BLOCK, 2 * BLOCK, BLOCK - int(25 * K)))
        input_boxes.extend((int(3.5 * BLOCK), 2 * BLOCK + i * BLOCK, 8 * BLOCK, 2 * BLOCK + i * BLOCK))
        blit_text(str(coord_list[2 * i - 2]), int(3.5 * BLOCK), 2 * BLOCK + i * BLOCK, 70)
        blit_text(str(coord_list[2 * i - 1]), 8 * BLOCK, 2 * BLOCK + i * BLOCK, 70)
# ---------------------------------------------------------------------------- drawing simple items


def draw_bezier_curve(line_coord_x: list, line_coord_y: list):
    for index in range(0, len(line_coord_x)):
        x = line_coord_x[index] / 100 * BLOCK + BLOCK
        y = line_coord_y[index] / 100 * BLOCK + BLOCK
        pg.draw.circle(WIN, colors["line"], (x, y), 1)


def calculate_polynomial(line_coord_x: list, line_coord_y: list, time: float, coord_list: list) -> tuple[int, int]:
    # split coordinate list into separate x and y coordinate lists
    x_coordinates = coord_list[::2]
    y_coordinates = coord_list[1::2]

    n = int(len(x_coordinates))
    x = y = 0

    for j in range(0, n):
        polynomial = binom(n - 1, j) * (1 - time) ** (n - 1 - j) * (time ** j)
        x += x_coordinates[j] * polynomial
        y += y_coordinates[j] * polynomial

    line_coord_x.append(x)
    line_coord_y.append(y)

    return x, y


def main_menu(points: int, active_box: int, coord_list: list):
    WIN.fill(colors["fill"])

    # title
    blit_text("Beziér algorithm", int(WIDTH / 2), BLOCK, 60, True, True, "x")
    blit_text("for moving 2D objects", int(WIDTH / 2), int(160 * K), 50, False, True, "x")

    # main rect
    pg.draw.rect(WIN, colors["rect"], (BLOCK, 2 * BLOCK, (WIDTH - BLOCK) / 5 * 3, HEIGHT - 3 * BLOCK),
                 int((WIDTH - 2 * BLOCK) / 5 * 3), 10)
    pg.draw.rect(WIN, colors["header"], (BLOCK, 2 * BLOCK, (WIDTH - BLOCK) / 5 * 3, int((HEIGHT - 4 * BLOCK) / 10)), 0,
                 0, 10, 10)

    # START button
    draw_button("START", colors["start_button"], int(2 * BLOCK + (WIDTH - 2 * BLOCK) / 5 * 3 + 50), 2 * BLOCK,
                WIDTH - (WIDTH - 2 * BLOCK) / 5 * 3 - 3 * BLOCK - 100, (HEIGHT - 4 * BLOCK) / 4, 100)

    # instructions
    blit_text("Press ESC to quit", int(2 * BLOCK + (WIDTH - 2 * BLOCK) / 5 * 3 + 50
              + (WIDTH - (WIDTH - 2 * BLOCK) / 5 * 3 - 3 * BLOCK - 100) / 2),
              int(2 * BLOCK + (HEIGHT - 4 * BLOCK) / 4 + int(40 * K)), 20, True, True, "x")

    # rect title & add/remove points buttons
    blit_text("Point coordinates:", int(1.2 * BLOCK), int(2.2 * BLOCK), 40)
    blit_text("+", int(0.5 * BLOCK + (WIDTH - BLOCK) / 5 * 3), 2 * BLOCK, 60)
    blit_text("-", int(0.5 * BLOCK + (WIDTH - BLOCK) / 5 * 3 - 50 * K), 2 * BLOCK, 70)

    draw_input_box(points, active_box, coord_list)


def curve_window(time: float, move_point: bool, line_coord_x: list, line_coord_y: list, coord_list: list, x_coordinates: list, y_coordinates: list):
    draw_grid()
    draw_bezier_curve(line_coord_x, line_coord_y)

    # start/pause button
    if not move_point:
        text = "START"
        color = colors["start_button"]
    else:
        text = "PAUSE"
        color = colors["pause_button"]
    draw_button(text, color, int(15 * BLOCK + (WIDTH - 15 * BLOCK - BLOCK * 3) / 2), BLOCK, 3 * BLOCK, BLOCK, 60)
    draw_button("back to menu", colors["back"], int(15 * BLOCK + (WIDTH - 15 * BLOCK - BLOCK * 3) / 2),
                2 * BLOCK + int(25 * K), 3 * BLOCK, BLOCK, 40)

    draw_curve_dots(coord_list)

    x, y = calculate_polynomial(line_coord_x, line_coord_y, time, coord_list)
    pg.draw.circle(WIN, colors["moving_dot"], (x / 100 * BLOCK + BLOCK, y / 100 * BLOCK + BLOCK), int(10 * K))

    # instructions
    blit_text("Press SPACE to start/pause", int(15 * BLOCK + (WIDTH - 18 * BLOCK) / 2), 9 * BLOCK, 20, True)
    blit_text("Press ESC to quit", int(15 * BLOCK + (WIDTH - 18 * BLOCK) / 2), 9 * BLOCK + int(30 * K), 20, True)


def main():
    run: bool = True
    time: float = 0
    menu: bool = True
    move_point: bool = False
    points: int = 3
    active_box: int = -1
    user_text: str = ""
    coord_list = [0] * points * 2
    line_coord_x: list[int] = []
    line_coord_y: list[int] = []
    x_coordinates: list = []
    y_coordinates: list = []

    pg.init()
    pg.display.set_caption("Beziér curve")

    while run:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    run = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    move_point = not move_point
                    if time > 1:
                        time = 0
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse = pg.mouse.get_pos()
                if menu:
                    # START button in the main menu
                    if 2 * BLOCK + (WIDTH - 2 * BLOCK) / 5 * 3 + 50 <= mouse[0] <= \
                            (2 * BLOCK + (WIDTH - 2 * BLOCK) / 5 * 3 + 50) + \
                            (WIDTH - (WIDTH - 2 * BLOCK) / 5 * 3 - 3 * BLOCK - 100) and 2 * BLOCK <= mouse[1] <= \
                            (7 * BLOCK) + (int((HEIGHT - 4 * BLOCK) / 4)):
                        menu = False

                        # fill the list with line coordinate values
                        while time <= 1:
                            calculate_polynomial(line_coord_x, line_coord_y, time, coord_list)
                            time += 0.001
                        time = 0

                    # + button in the main menu
                    elif BLOCK <= mouse[1] <= 2 * BLOCK + int((HEIGHT - 4 * BLOCK) / 10) and BLOCK + \
                            (WIDTH - BLOCK) / 5 * 3 - int((HEIGHT - 4 * BLOCK) / 10) <= mouse[0] <= \
                            BLOCK + (WIDTH - BLOCK) / 5 * 3:
                        if points < 7:
                            points += 1
                            active_box = -1
                            coord_list.extend((0,0))

                    # - button in the main menu
                    elif BLOCK <= mouse[1] <= 2 * BLOCK + int((HEIGHT - 4 * BLOCK) / 10) and BLOCK + \
                            (WIDTH - BLOCK) / 5 * 3 - int((HEIGHT - 4 * BLOCK) / 10) - int(20 * K) <= mouse[0] <= \
                            BLOCK + (WIDTH - BLOCK) / 5 * 3:
                        if points > 3:
                            points -= 1
                            active_box = -1
                            del coord_list[-2:]


                    # point coordinates input boxes in main menu
                    for i in range(0, int(len(input_boxes)), 2):
                        if input_boxes[i] <= mouse[0] <= input_boxes[i] + 2 * BLOCK and \
                            input_boxes[i + 1] <= mouse[1] <= input_boxes[i + 1] + BLOCK - int(25 * K):
                            active_box = int(i/2 + 1)
                            user_text = ""

                else:
                    # BACK TO MENU button in curve window
                    if 15 * BLOCK + (WIDTH - 15 * BLOCK - BLOCK * 3) / 2 <= mouse[0] <= \
                            (15 * BLOCK + (WIDTH - 15 * BLOCK - BLOCK * 3) / 2) + 3 * BLOCK and \
                            2 * BLOCK + int(25 * K) <= mouse[1] <= 2 * BLOCK + int(25 * K) + BLOCK:
                        menu = True
                        coord_list = [0] * points * 2
                        line_coord_y.clear()
                        line_coord_x.clear()

                    # START button in curve window
                    if int(1550 * K) <= mouse[0] <= int(1850 * K) and BLOCK <= mouse[1] <= 2 * BLOCK:
                        move_point = not move_point
                        if time > 1:
                            time = 0

            if active_box != -1:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_BACKSPACE:
                        user_text = user_text[:-1]
                        if len(user_text) == 0:
                            user_text = "0"
                    else:
                        user_text += event.unicode

                    if user_text.isnumeric():
                        if active_box % 2 == 1:
                            if 0 <= int(user_text) <= 1400:
                                coord_list[active_box - 1] = int(user_text)
                            else:
                                user_text = "0"
                        else:
                            if 0 <= int(user_text) <= 900:
                                coord_list[active_box - 1] = int(user_text)
                            else:
                                user_text = "0"
                    else:
                        user_text = "0"

        if time > 1:
            move_point = False

        if menu:
            main_menu(points, active_box, coord_list)
        else:
            curve_window(time, move_point, line_coord_x, line_coord_y, coord_list, x_coordinates, y_coordinates)

        if move_point:
            time += 0.01

        pg.display.update()
    pg.quit()
    quit()


if __name__ == "__main__":
    main()