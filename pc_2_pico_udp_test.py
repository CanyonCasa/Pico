# PC (Windows) Pico UDP test code...

import json, random, time, socket

udp_pico = "192.168.0.77"  # LAN IP of receiver
udp_host = "192.168.0.179"
udp_port = 5005
udp_bufsize = 128
udp_buffer = bytearray(udp_bufsize)  # stores our incoming packet

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.bind((udp_host, udp_port))                     # listen to host:port

sock.setblocking(False)
#sock.setblocking(True) # alternative blocking IO with timeout
#sock.settimeout(0.01)

pin = 0
pwm = 0
stream = ''
while True:
    msg = json.dumps({ "pin": pin, "pwm": pwm })
    udp_message = bytes( msg + '\n', 'utf-8')
    print(time.monotonic(), f"sending to {udp_pico}:{udp_port} message:", udp_message)
    sock.sendto(udp_message, (udp_pico,udp_port))
    time.sleep(2)   # just to slow loop for observation
    pwm = (pwm + random.randint(1,4)*4096) % 65536
    pin = random.randint(0,1)
    # receive response...
    try:
        size, addr = sock.recvfrom_into(udp_buffer)
        stream += udp_buffer[:size].decode('utf-8') # assume a string, so convert from bytearray
        if '\n' in stream:
            msg, stream = stream.split('\n',1)
        else:
            msg = ''
        # process msg...
        if msg:
            print(f"  Received message [{size}]=>{msg} from {addr[0]}:{addr[1]}")
    except OSError as err:
        print(f"ERROR: {err}")
        pass
