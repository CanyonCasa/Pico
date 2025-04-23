JSON over UDP for Pico...

A simple example of passing JSON from PC to Pico

PC
    pc_2_pico_udp_test.py       -   script to send test messages to Pico

Pico code
    code.py
    settings.toml               - wifi settings
    lib
        definition.py           - my library to convert dict to class object for simpler dot notation. i.e. test.data vs test["data"]
    
Node-red Demo
    pico_udp_node-red_demo.json - A demo flow to do same thing as PC script

Sample outputs below...


Sample output from PC terminal...

PS C:\data\python> python pc_2_pico_udp_test.py   
1170651.765 sending to 192.168.0.77:5005 message: b'{"pin": 0, "pwm": 0}\n'
  Received message [21]=>{"pin": 0, "pwm": 0} from 192.168.0.77:5005
1170653.781 sending to 192.168.0.77:5005 message: b'{"pin": 1, "pwm": 16384}\n'
  Received message [25]=>{"pin": 1, "pwm": 16384} from 192.168.0.77:5005
1170655.781 sending to 192.168.0.77:5005 message: b'{"pin": 0, "pwm": 24576}\n'
  Received message [25]=>{"pin": 0, "pwm": 24576} from 192.168.0.77:5005
1170657.781 sending to 192.168.0.77:5005 message: b'{"pin": 1, "pwm": 36864}\n'

Corresponding sample Pico output...
.......................................Received message from 192.168.0.179:5005 => {'pin': 0, 'pwm': 0}
PWM request for pwm[0] set to 0/65536
Sent message b'{"pin": 0, "pwm": 0}\n' to 192.168.0.179:5005
....................Received message from 192.168.0.179:5005 => {'pin': 1, 'pwm': 16384}
PWM request for pwm[1] set to 16384/65536
Sent message b'{"pin": 1, "pwm": 16384}\n' to 192.168.0.179:5005
....................Received message from 192.168.0.179:5005 => {'pin': 0, 'pwm': 24576}
PWM request for pwm[0] set to 24576/65536
Sent message b'{"pin": 0, "pwm": 24576}\n' to 192.168.0.179:5005
....................Received message from 192.168.0.179:5005 => {'pin': 1, 'pwm': 36864}
PWM request for pwm[1] set to 36864/65536
Sent message b'{"pin": 1, "pwm": 36864}\n' to 192.168.0.179:5005
................................................................


Node-red UDP demo flow debug window...

4/7/2025, 12:58:08 PMnode: sent
msg.payload : string[18]
"{"pin":1,"pwm":0}↵"
4/7/2025, 12:58:08 PMnode: received
msg.payload : Object
{ pin: 1, pwm: 0 }
4/7/2025, 12:58:11 PMnode: sent
msg.payload : string[22]
"{"pin":1,"pwm":16384}↵"
4/7/2025, 12:58:11 PMnode: received
msg.payload : Object
{ pin: 1, pwm: 16384 }
4/7/2025, 12:58:14 PMnode: sent
msg.payload : string[22]
"{"pin":0,"pwm":24576}↵"
4/7/2025, 12:58:15 PMnode: received
msg.payload : Object
{ pin: 0, pwm: 24576 }
4/7/2025, 12:58:17 PMnode: sent
msg.payload : string[22]
"{"pin":1,"pwm":36864}↵"
4/7/2025, 12:58:18 PMnode: received
msg.payload : Object
{ pin: 1, pwm: 36864 }
4/7/2025, 12:58:20 PMnode: sent
msg.payload : string[22]
"{"pin":1,"pwm":53248}↵"
4/7/2025, 12:58:21 PMnode: received
msg.payload : Object
{ pin: 1, pwm: 53248 }


Corresponding Pico response...

..............Received message from 192.168.0.179:5005 => {'pin': 1, 'pwm': 0}
PWM request for pwm[1] set to 0/65536
Sent message b'{"pin": 1, "pwm": 0}\n' to 192.168.0.179:5005
..............................Received message from 192.168.0.179:5005 => {'pin': 1, 'pwm': 16384}
PWM request for pwm[1] set to 16384/65536
Sent message b'{"pin": 1, "pwm": 16384}\n' to 192.168.0.179:5005
..............................Received message from 192.168.0.179:5005 => {'pin': 0, 'pwm': 24576}
PWM request for pwm[0] set to 24576/65536
Sent message b'{"pin": 0, "pwm": 24576}\n' to 192.168.0.179:5005
..............................Received message from 192.168.0.179:5005 => {'pin': 1, 'pwm': 36864}
PWM request for pwm[1] set to 36864/65536
Sent message b'{"pin": 1, "pwm": 36864}\n' to 192.168.0.179:5005
..............................Received message from 192.168.0.179:5005 => {'pin': 1, 'pwm': 53248}
PWM request for pwm[1] set to 53248/65536
Sent message b'{"pin": 1, "pwm": 53248}\n' to 192.168.0.179:5005
.....................