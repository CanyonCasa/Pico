# SPDX-FileCopyrightText: © 2024 Gustavo Diaz <contact@gusdiaz.dev>
#
# SPDX-License-Identifier: MIT

# Websockets client for CircuitPython
# Forked from: https://github.com/danni/uwebsockets

# Pins: UART TX: GP16, RX: GP17; fix: GP15; en: GP14; pps: GP0 

import os
import wifi
import time
import json
import cpwebsockets.client


NETWORKS = os.getenv('NETWORKS')
WIFI_CREDS = [tuple(creds.split(NETWORKS[0])) for creds in NETWORKS[1:].split(f"{NETWORKS[0]}{NETWORKS[0]}")]
active_wifi = None
# Wi-Fi credentials
print(NETWORKS,WIFI_CREDS)

def connect_to_wifi():
    print("Connecting to Wi-Fi...")
    index = 0
    while (not wifi.radio.connected):
        try:
            ssid, passphrase = WIFI_CREDS[index]
            wifi.radio.connect(ssid,passphrase)
            print(f"Connected to Wi-Fi network: {ssid}")
            active_wifi = ssid
            print(f"IP Address: {wifi.radio.ipv4_address} on network {ssid}")
            return
        except Exception as e:
            print(f"Failed to connect to Wi-Fi: {ssid}", e)
            index = (index+1) % len(NETWORKS)

def main():
    if not wifi.radio.connected: connect_to_wifi()

    # WebSocket connection
    try:
        print("Connecting to WebSocket server...")
        #websocket = cpwebsockets.client.connect("wss://ws.postman-echo.com/raw", wifi.radio)
        websocket = cpwebsockets.client.connect("wss://sedillocanyon.net/howl?topics=echo&name=gps", wifi.radio)
        print("Connected!", dir(websocket))
        
        # Send and receive a message
        #mesg = "The quick brown fox jumps over the lazy dog"
        mesg = json.dumps({"topic": "echo", "payload": "The quick brown fox jumps over the lazy dog"})
        websocket.send(mesg + "\r\n")
        resp = websocket.recv()
        print("Received:", resp)
        assert(mesg + "\r\n" == resp)
        
        # Close the WebSocket
        websocket.close()
        print("WebSocket connection closed.")
    except Exception as e:
        print("An error occurred:", e)

# Run the program
while True:
    main()
    time.sleep(5)
