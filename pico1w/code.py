print("Hello World!")
# SPDX-FileCopyrightText: 2024 Justin Myers for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense

import os
import time
import microcontroller
import socketpool
#import struct
import adafruit_requests
import wifi
import board
import busio
import pwmio
#import adafruit_mcp4725
import digitalio
from analogio import AnalogIn


import adafruit_connection_manager
from adafruit_httpserver import Server, Request, JSONResponse
import adafruit_ntp
#import adafruit_pca9685


#led = digitalio.DigitalInOut(board.GP17)
#led.direction = digitalio.Direction.OUTPUT

#analog_in = AnalogIn(board.GP26)

TEXT_URL = "http://wifitest.adafruit.com/testwifi/index.html"

wifi_ssid = "redacted"
wifi_password = "redacted"
radio = wifi.radio


while not radio.connected:
    radio.connect(wifi_ssid, wifi_password) 

# get the pool and ssl_context from the helpers:
pool = adafruit_connection_manager.get_radio_socketpool(radio)
#ntp = adafruit_ntp.NTP(pool, tz_offset=0, cache_seconds=3600)
server = Server(pool, debug=True)

# (Optional) Allow cross-origin requests.
#server.headers = {
#    "Access-Control-Allow-Origin": "*",
#}

#ssl_context = adafruit_connection_manager.get_radio_ssl_context(radio)

    

# get request session
#requests = adafruit_requests.Session(pool, ssl_context)
connection_manager = adafruit_connection_manager.get_connection_manager(pool)


pins = {'0' : board.GP14, '1' : board.GP15}

@server.route("/pwm_set") 
def gpio_set(request: Request):
    """
    Parses GPIO set for PWM and digital IO
    """

    #while True:
    #    try:
    pwmio.PWMOut(pins[request.query_params["pin"]], duty_cycle=int(request.query_params["value"]))
    #    except ValueError:
    #        abc="opps somebody cranky, try again"
    #    else:
    #        break


    data = {
        "GPinPWM": request.query_params["pin"],
        "GPinPWMvalue": request.query_params["value"], 

    }

    return JSONResponse(request, data)



server.serve_forever(str(wifi.radio.ipv4_address))



