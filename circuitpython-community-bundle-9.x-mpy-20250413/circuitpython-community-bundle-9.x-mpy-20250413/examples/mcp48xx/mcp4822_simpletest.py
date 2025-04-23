# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2024 Steffen Kreutz
#
# SPDX-License-Identifier: Unlicense

import board
import busio
from digitalio import DigitalInOut
import mcp48xx

# Initialize SPI bus.
spi = busio.SPI(board.GP6, board.GP7)
cs = DigitalInOut(board.GP5)

# Initialize MCP4822.
dac = mcp48xx.MCP4822(spi, cs)

# There are two channels which can be updated independently
dac.channel_a.value = 65535
dac.channel_b.value = 65535

# There are a three ways to set the DAC output, you can use any of these:
dac.channel_a.value = 65535  # Use the value property with a 16-bit number just like
# the AnalogOut class.  Note the MCP4822 is only a 12-bit
# DAC so quantization errors will occur.  The range of
# values is 0 (minimum/ground) to 65535 (maximum/Vout).

dac.channel_a.raw_value = 4095  # Use the raw_value property to directly read and write
# the 12-bit DAC value.  The range of values is
# 0 (minimum/ground) to 4095 (maximum/Vout).

dac.channel_a.normalized_value = 1.0  # Use the normalized_value property to set the
# output with a floating point value in the range
# 0 to 1.0 where 0 is minimum/ground and 1.0 is
# maximum/Vout.

# Main loop will go up and down through the range of DAC values forever.
while True:
    # Go up the 12-bit raw range.
    print("Going up 0-2.048V...")
    for i in range(4095):
        dac.channel_a.raw_value = i
        dac.channel_b.raw_value = i
    # Go back down the 12-bit raw range.
    print("Going down 2.048-0V...")
    for i in range(4095, -1, -1):
        dac.channel_a.raw_value = i
        dac.channel_b.raw_value = i
