# Rui Santos & Sara Santos - Random Nerd Tutorials
# Complete project details at https://RandomNerdTutorials.com/raspberry-pi-pico-w-asynchronous-web-server-micropython/

# Import necessary modules
import network
import asyncio
import socket
import time
from machine import ADC #for temp sensor
from machine import Pin, PWM

# Wi-Fi credentials
ssid = 'redacted'
password = 'redacted'

# Initialize variables
duty_step = 2047
frequency = 5000

# Internal temperature sensor is connected to ADC channel 4
temp_sensor = ADC(4)

def read_internal_temperature():
    # Read the raw ADC value
    adc_value = temp_sensor.read_u16()

    # Convert ADC value to voltage
    voltage = adc_value * (3.3 / 65535.0)

    # Temperature calculation based on sensor characteristics
    temperature_celsius = 27 - (voltage - 0.706) / 0.001721

    return int( temperature_celsius * 10 ) / 10 #one decimal place to right



# HTML template for the webpage
def webpage( pinNum, pwmNum):
    temperatureC = read_internal_temperature()
    html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Pico Web Server</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
        </head>
        <body>
            <h1>Raspberry Pi Pico Web Server</h1>
            <h2>Led Control</h2>
            <form action="http://10.30.30.20/pin_20_pwm_65535">
                <input type="submit" value="Light on" />
            </form>
            <br>
            <form action="http://10.30.30.20/pin_20_pwm_00000">
                <input type="submit" value="Light off" />
            </form>
            <p>Pin Number: {pinNum}</p>
            <p>Pwm Number: {pwmNum}</p>
            <p>Pico Temp: {temperatureC}</p>
        </body>
        </html>
        """
    return str(html)

# Init Wi-Fi Interface
def init_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    # Connect to your network
    wlan.connect(ssid, password)
    # Wait for Wi-Fi connection
    connection_timeout = 10
    while connection_timeout > 0:
        print(wlan.status())
        if wlan.status() >= 3:
            break
        connection_timeout -= 1
        print('Waiting for Wi-Fi connection...')
        time.sleep(1)
    # Check if connection is successful
    if wlan.status() != 3:
        print('Failed to connect to Wi-Fi')
        return False
    else:
        print('Connection successful!')
        network_info = wlan.ifconfig()
        print('IP address:', network_info[0])
        return True

# Asynchronous functio to handle client's requests
async def handle_client(reader, writer):
    global state
    
    #print("Client connected")
    request_line = await reader.readline()
    
    # Skip HTTP request headers
    while await reader.readline() != b"\r\n":
        pass

    request = str(request_line, 'utf-8').split()[1]
    if request.find("favicon") == -1:
        print('Client Connected. Request:', request_line)
        requestLen = len(request)
        pinLoc = request.find("pin_")
        pinNumber="invalid"
        pwmNumber="invalid"
              
        # Process the request and update variables
        # example: http://10.30.30.20/pin_20_pwm_65535?
        if request.find("/pin_") >= 0:
            if pinLoc >= 0:
                pwmLoc = request.find("pwm_")
                if pwmLoc >= 0:
                    pinNumber = request[pinLoc+4:pwmLoc-1]
                    pwmNumber = request[pwmLoc+4:requestLen-1]
                    led_blink = Pin(int(pinNumber), Pin.OUT)
                    led_pwm = PWM(led_blink)
                    led_pwm.freq (frequency)
                    led_pwm.duty_u16(int(pwmNumber))

        # Generate HTML response
        response = webpage(pinNumber, pwmNumber)  

        # Send the HTTP response and close the connection
        writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        writer.write(response)
        await writer.drain()
        await writer.wait_closed()
        print('Client Disconnected: HTTP/1.0 200 OK  Content-type: text/html')
    
async def blink_led():
    while True:
      for duty_cycle in range(0, 65536, duty_step):
        led_pwm.duty_u16(duty_cycle)
        await asyncio.sleep(0.05)
        
      # Decrease the duty cycle gradually
      for duty_cycle in range(65536, 0, -duty_step):
        led_pwm.duty_u16(duty_cycle)
        await asyncio.sleep(0.05)
        #led_blink.toggle()  # Toggle LED state
        #await asyncio.sleep(0.5)  # Blink interval

async def main():    
    if not init_wifi(ssid, password):
        print('Exiting program.')
        return
    
    # Start the server and run the event loop
    print('Setting up server')
    server = asyncio.start_server(handle_client, "0.0.0.0", 80)
    asyncio.create_task(server)
    #asyncio.create_task(blink_led())
    
    while True:
        # Add other tasks that you might need to do in the loop
        await asyncio.sleep(100)
        print('This message will be printed every 100 seconds')
        

# Create an Event Loop
loop = asyncio.get_event_loop()
# Create a task to run the main function
loop.create_task(main())

try:
    # Run the event loop indefinitely
    loop.run_forever()
except Exception as e:
    print('Error occurred: ', e)
except KeyboardInterrupt:
    print('Program Interrupted by the user')
