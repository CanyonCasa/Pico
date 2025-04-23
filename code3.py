# polling server test...

import board
import pwmio
import wifi
import socketpool
from adafruit_httpserver import Server, Request, JSONResponse, REQUEST_HANDLED_RESPONSE_SENT

pins = {'0' : board.GP14, '1' : board.GP15}
pwm = [ pwmio.PWMOut(board.GP14), pwmio.PWMOut(board.GP15)]

print(f"wifi: {dir(wifi.radio)}")

pool = socketpool.SocketPool(wifi.radio)
print(f"pool: {dir(pool)}")

server = Server(pool, debug=True)
print(f"server: {dir(server)}")

@server.route("/stop")
def stop():
    print("stopping server...")
    server.stop()

@server.route("/pwm_set") 
def gpio_set(request: Request):
    """
    Parses GPIO set for PWM and digital IO
    """
    pin = int(request.query_params["pin"])
    dc = int(request.query_params["value"])
    print(f"PWM request for pwm[{pin}] set to {dc}/65536")
    
    try:
        pwm[pin].duty_cycle = dc
        data = { "GPinPWM": pin, "GPinPWMvalue": dc }
    except ValueError:
        data = { "error": 500, "msg": "PWM Set Fail!" }

    return JSONResponse(request, data)

server.start(str(wifi.radio.ipv4_address))

while True:
    try:
        # do other useful things have
        request = server.poll()
        if request==REQUEST_HANDLED_RESPONSE_SENT:
            # optional post processing after response...
            pass
    except OSError as error:
        print(error)
        continue
