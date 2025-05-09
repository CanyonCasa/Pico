# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya, DJDevon
#
# SPDX-License-Identifier: MIT

import board
from circuitpython_uplot.plot import Plot, color
from circuitpython_uplot.bar import Bar

# Setting up the display
display = board.DISPLAY

# Configuring display dimensions
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 320

# Defining the plot
plot = Plot(
    0,
    0,
    DISPLAY_WIDTH,
    DISPLAY_HEIGHT,
    background_color=color.BLACK,
    padding=10,
    box_color=color.BLACK,
)

# Dummy data to plot
activities_latest_heart_value = [55, 20, 25, 30, 35, 10]
a = ["a", "b", "c", "d", "e", "f"]

# Creating the Bar Plot
Bar(
    plot,
    a,
    activities_latest_heart_value,
    0xFF1000,
    True,
    color_palette=[0xFF1000, 0x00FF00, 0x0000FF, 0xFFFF00, 0x00FFFF, 0x123456],
)

# Showing the plot
display.root_group = plot
