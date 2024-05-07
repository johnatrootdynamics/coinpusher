import socketio
import time
import signal
import sys
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)  # Use BCM GPIO numbering
GPIO.setwarnings(False)



def turn_off_gpio(pin):

    # Set up the pin as an output
    GPIO.setup(pin, GPIO.OUT)
    
    # Set the pin to LOW
    GPIO.output(pin, GPIO.LOW)
    print(f"GPIO {pin} set to LOW")


def button_push(LR):
    if (LR == "left"):
        GPIO.setup("23", GPIO.OUT)
        GPIO.output("23", GPIO.HIGH)
        time.sleep(.1)
        GPIO.output("23", GPIO.LOW)
    if (LR == "right"):
        GPIO.setup("24", GPIO.OUT)
        GPIO.output("24", GPIO.HIGH)
        time.sleep(.1)
        GPIO.output("24", GPIO.LOW)







def joinroom():
    sio.emit('joinroom', {'machine_id': '1'})
    print("tryin to join room")

# Create a Socket.IO client instance
sio = socketio.Client(logger=True, engineio_logger=True)  # Logging is optional but helpful for debugging

# Define event handlers
@sio.event
def connect():
    print("Connected to the server.")
    sio.emit('session_data', {'machine_id':'1'})  # Example of sending data to the server

@sio.event
def message(data):
    print('Received data from server:', data)

@sio.event
def update_machine_info():
    sio.emit('update_machine', {'machine_id': '1', 'machine_status': '1'})
@sio.event
def update_machine_info2():
    sio.emit('update_machine', {'machine_id': '1', 'machine_status': '3'})

@sio.event
def button_push(data):
    print(data)

@sio.event
def status_updated(data):
    print("DB updated")

@sio.event
def disconnect():
    print("Disconnected from the server.")

def signal_handler(sig, frame):
    print('Disconnecting...')
    if sio.connected:
        sio.disconnect()
    sys.exit(0)

# Connect to the Flask-SocketIO server
# try:
#     sio.connect('http://coinpusheronline.root-dynamics.com')
#     time.sleep(2)
#     update_machine_info()
#     sio.wait()
#     sio.disconnect()
# except socketio.exceptions.ConnectionError as e:
#     print("Connection failed:", e)



try:
    sio.connect('http://coinpusheronline.root-dynamics.com')
    # Bind the signal handler to handle SIGINT (CTRL+C)
    signal.signal(signal.SIGINT, signal_handler)
    time.sleep(2)
    update_machine_info()
    time.sleep(2)
    joinroom()
    time.sleep(10)
    update_machine_info2()
    joinroom()
    sio.wait()
except socketio.exceptions.ConnectionError as e:
    print("Failed to connect to the server:", e)