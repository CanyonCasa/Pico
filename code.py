# polling server test...

import board
import pwmio
import json
import wifi
import socketpool
import time
from definition import Definition

def my_send(sock, udp):
    udp.msg = json.dumps(udp.data)
    udp.bx = bytes( udp.msg + '\n', 'utf-8')
    sock.sendto(udp.bx,(udp.peer[0],udp.port))

def my_receive(sock, udp):
    udp.msg = None
    udp.data = None
    try:
        size, addr = sock.recvfrom_into(udp.buf)
    except OSError as e:
        return ''
    udp.peer = addr
    udp.stream += udp.buf[:size].decode('utf-8') # assume a string, so convert from bytearray
    if '\n' in udp.stream:
        udp.msg, udp.stream = udp.stream.split('\n',1)
        try:
            udp.data = json.loads(udp.msg)
        except:
            udp.data = None
    return udp

def gpio_pwm(pwmio, rqst):
    """
    Parses GPIO set for PWM and digital IO
    """
    pin = int(rqst["pin"])
    dc = int(rqst["pwm"])
    print(f"PWM request for pwm[{pin}] set to {dc}/65536")
    try:
        pwmio[pin].duty_cycle = dc
    except ValueError:
        rqst.error = 500
        rqst.msg = "PWM Set Fail!"

    return rqst


# main code...

# define pwm instances
pwm = [ pwmio.PWMOut(board.GP14), pwmio.PWMOut(board.GP15)]

# wifi autoconnect using settings.toml
print(f"my IP addr: {wifi.radio.ipv4_address}")

# udp parameters and socket setup
bufsize = 128
udp = Definition({
    "host": str(wifi.radio.ipv4_address),   # my LAN IP as a string
    "port": 5005,                           # chosen UDP port to use, should be 1024-65000
    "peer": (None,None),                    # holds peer (addr,port)
    "bufsize": bufsize,                     # defines buffer size
    "buf": bytearray(bufsize),              # stores our incoming packet
    "stream": '',                           # holds input text stream
    "msg": '',                              # hold last complete message
    "data": {},                             # JSON data extracted from msg
    "bx": None
})
pool = socketpool.SocketPool(wifi.radio)
sock = pool.socket(pool.AF_INET, pool.SOCK_DGRAM)   # UDP socket
sock.bind((udp.host, udp.port))                     # listen to host:port
sock.setblocking(False)                             # important!

print('waiting for messages...')
stream = ''
while True:
    try:
        # receive data or None ...
        my_receive(sock, udp)
        # process request...
        if udp.data:
            print(f"Received message from {udp.peer[0]}:{udp.peer[1]} => {udp.data}")
            udp.data = gpio_pwm(pwm, udp.data) # using same data field for send/receive
            # handle the response...
            my_send(sock, udp)
            print(f"Sent message {udp.bx} to {udp.peer[0]}:{udp.port}")
        # do other useful things here...
        print('.',end="")   # diagnostic to show loop is repeating
        time.sleep(0.1)     # slow loop for visualization
    except OSError as error:
        print(error)
        continue
