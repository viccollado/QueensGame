import pyautogui
import numpy as np
from queens_solver import queens_solver
import time
import datetime


def main():

    # Wait for 3 seconds to switch to the game window
    time.sleep(3)

    # Start button
    x_start = 1332
    y_start = 814
    # Click on the start button
    pyautogui.click(x_start, y_start)

    # Wait for the game to load
    time.sleep(0.5)

    # Parameters of the board
    top_left_x = 708 # 708  Final 1192
    top_left_y = 342    # 342 Final 827
    bottom_right_x = 1192 # 1194 Final 1687
    # bottom_right_y = 827 # 829 Final 1322
    box_width = bottom_right_x - top_left_x  # Width of the box in pixels

    # box_width = 485     # Assume the box are squared
    date = datetime.datetime.now()
    screenshot = pyautogui.screenshot(f"Data/queens_{date.year}_{date.month}_{date.day}.png")

    diff_colors = 1
    previous_color = (0, 0, 0)
    y = top_left_y + 15

    for x in range(top_left_x + 10, bottom_right_x - 10):
        current_color = screenshot.getpixel((x, y))
        if current_color != previous_color:
            diff_colors += 1
        previous_color = current_color

    n_box = diff_colors // 2
    print(f"Number of colors: {n_box}")

    # n_box = int(input("Enter the number of boxes (default is 8): ") or 8)


    # Derived values
    each_box_width = box_width // n_box 
    middle_box = each_box_width // 2

    queens_color_matrix = np.zeros((n_box, n_box))

    for i in range(n_box):
        for j in range(n_box):
            color = screenshot.getpixel((top_left_x + middle_box + j*each_box_width,
                                    top_left_y + middle_box + i*each_box_width))
            queens_color_matrix[i,j] = np.round(0.299*color[0] + 0.587*color[1] + 0.114*color[2], 2)

    unique_colors = np.unique(queens_color_matrix)
    print(len(unique_colors))
    if len(unique_colors) != n_box:
        raise Warning(f"Expected {n_box} unique values but found {len(unique_colors)}")

    value_to_index = {val: idx for idx, val in enumerate(unique_colors)}
    indexed_matrix = np.vectorize(lambda x: value_to_index[x])(queens_color_matrix)

    print(indexed_matrix)

    matrix_sol, _ = queens_solver(indexed_matrix+1)

    for i in range(n_box):
        for j in range(n_box):
            if matrix_sol[i, j] == 1:

                # Convert to int in case of float values
                pyautogui.click(
                    top_left_x + middle_box + j*each_box_width,
                    top_left_y + middle_box + i*each_box_width, 
                    clicks=2
                    )

if __name__ == "__main__":
    main()  