# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT

import board
from circuitpython_uplot.plot import Plot
from circuitpython_uplot.pie import Pie


# Setting up the display
display = board.DISPLAY

plot = Plot(0, 0, display.width, display.height)

# Setting up tick parameters
plot.axs_params(axstype="box")
a = [5, 2, 7, 3]

Pie(plot, a)

# Plotting and showing the plot
display.root_group = plot
