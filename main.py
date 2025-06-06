import datetime
import time

import numpy as np
import pyautogui

from queens_solver import queens_solver


def main():
    """
    Main function to run the queens game solver

    In this function you should change the Queens linkedin game box coordinates. 
    You can check what coordinates are appropiated in you screen by running the script mouse_info.py.
    """
    # Wait for 3 seconds to switch to the game window
    time.sleep(3)

    # Queens start button
    x_start = 1332
    y_start = 814
    # Click on the start button
    pyautogui.click(x_start, y_start)

    # Wait for the game to load
    time.sleep(1)

    # Queens box parameter
    # CHANGE BY YOUR COORDINATES
    top_left_x = 708    # Top left x coordinate
    top_left_y = 342    # Top left y coordinate
    
    bottom_right_x = 1192   # Botton right x coordinate
    # bottom_right_y = 827  # Botton right y coordinate

    # Queens box with
    box_width = bottom_right_x - top_left_x 

    # Screenshot of the Queens box
    date = datetime.datetime.now()
    screenshot = pyautogui.screenshot(f"Data/queens_{date.year}_{date.month}_{date.day}.png")

    # Determine the number of colors (Crowns to use) in the current game
    diff_colors = 1
    previous_color = (0, 0, 0)  # White color as initial since there are no white color in the game
    y = top_left_y + 15         # Row of pixels to check the color

    for x in range(top_left_x + 10, bottom_right_x - 10):
        current_color = screenshot.getpixel((x, y))
        if current_color != previous_color:
            diff_colors += 1
        previous_color = current_color

    # Number of crowns in the current game
    n_crown = diff_colors // 2
    print(f"Number of colors: {n_crown}")

    # Sub-boxes values
    each_box_width = box_width // n_crown 
    middle_box = each_box_width // 2

    queens_color_matrix = np.zeros((n_crown, n_crown))  # Initialize queens matrix

    # Obtain matrix of colors
    for i in range(n_crown):
        for j in range(n_crown):
            color = screenshot.getpixel((top_left_x + middle_box + j*each_box_width,
                                    top_left_y + middle_box + i*each_box_width))
            queens_color_matrix[i,j] = np.round(0.299*color[0] + 0.587*color[1] + 0.114*color[2], 2)

    unique_colors = np.unique(queens_color_matrix)
    if len(unique_colors) != n_crown:
        raise ValueError(f"Expected {n_crown} unique values but found {len(unique_colors)}")

    value_to_index = {val: idx for idx, val in enumerate(unique_colors)}
    indexed_matrix = np.vectorize(lambda x: value_to_index[x])(queens_color_matrix)

    print(indexed_matrix)   # Show the color matrix in terminal

    matrix_sol, _ = queens_solver(indexed_matrix+1) # Solve the game

    # Put crowns in solution
    for i in range(n_crown):
        for j in range(n_crown):
            if matrix_sol[i, j] == 1:
                pyautogui.click(
                    top_left_x + middle_box + j*each_box_width,
                    top_left_y + middle_box + i*each_box_width, 
                    clicks=2
                    )

if __name__ == "__main__":
    main()  