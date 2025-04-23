# The MIT License (MIT)
#
# Copyright (c) 2018 Dave Astels
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
A gaunlet running game using the dotstar wing and the joy wing.
"""

from time import sleep
from random import randint

import board
import busio
import dotstar_featherwing
import Adafruit_seesaw

i2c = busio.I2C(board.SCL, board.SDA)
ss = Adafruit_seesaw.Seesaw(i2c)
wing = dotstar_featherwing.DotstarFeatherwing(board.D13, board.D11, 0.1)

black = 0x000000
wall = 0x200800           # must not have any blue, must have red
pellet = 0x000040               # must have blue
player = 0x00FF00

numbers = {
    ' ': [0,  0,  0],
    '0': [30, 33, 30],
    '1': [34, 63, 32],
    '2': [50, 41, 38],
    '3': [33, 37, 26],
    '4': [ 7,  4, 63],
    '5': [23, 37, 25],
    '6': [30, 41, 25],
    '7': [49,  9,  7],
    '8': [26, 37, 26],
    '9': [38, 41, 30],
}

row = (wall, wall, wall, wall,
       wall, wall, wall, wall,
       black, black, black, black, black,
       wall, wall, wall, wall,
       wall, wall, wall, wall)


def run():
    """Play the game."""

    player_x = 6
    score = 0
    steps = 0
    step_delay = 0.15
    offset = 4

    for _ in range(wing.rows):
        wing.shift_into_top(row, offset)
    wing.show()


    while True:
        # remove player sprite
        wing.set_color(3, player_x, black)

        # shift/advance the track
        offset = min(max(0, offset + randint(-1, 1)), 9)
        wing.shift_into_top(row, offset)

        # Maybe add a pellet
        if randint(1, 20) == 1:
            wing.set_color(0, randint(8, 12) - offset, pellet)

        # Adjust player position
        joy_x = ss.analog_read(3)
        if joy_x < 256 and player_x > 0:
            player_x -= 1
        elif joy_x > 768 and player_x < 11:
            player_x += 1

        # Check for collisions
        r, _, b = wing.get_color(3, player_x)
        if b:
            score += 1
        elif r:
            return steps, score

        # Show player sprite
        wing.set_color(3, player_x, player)

        # Update some things and sleep a bit
        wing.show()
        steps += 1
        if steps % 25 == 0:
            score += 1
        if steps % 100 == 0:
            step_delay *= 0.9
        sleep(step_delay)

while True:
    result = run()
    # got here because of a crash, so report score and restart
    wing.shift_in_string(numbers, '{:03d}'.format(result[1]), 0x101010)
    sleep(5)
