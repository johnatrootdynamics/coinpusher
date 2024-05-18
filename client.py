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


# Create a Socket.IO client instance
sio = socketio.Client(logger=True, engineio_logger=True)  # Logging is optional but helpful for debugging

# Define event handlers
@sio.event
def connect():
    print("Connected to the server.")
    sio.emit('update_machine', {'machine_id':'1', 'machine_status':'1'})  # Example of sending data to the server

@sio.event()
def message(data):
    print('Received data from server:', data)

@sio.event
def update_machine_info():
    sio.emit('update_machine', {'machine_id': '1', 'machine_status': '1'})
@sio.event
def update_machine_info2():
    sio.emit('update_machine', {'machine_id': '1', 'machine_status': '3'})

@sio.event(namespace='/machine')
def button_push(data):
    LR = data['action']
    if (LR == "left"):
        GPIO.setup(23, GPIO.OUT)
        GPIO.output(23, GPIO.HIGH)
        time.sleep(.1)
        GPIO.output(23, GPIO.LOW)
        print("left button pushed")
    if (LR == "right"):
        GPIO.setup(24, GPIO.OUT)
        GPIO.output(24, GPIO.HIGH)
        time.sleep(.1)
        GPIO.output(24, GPIO.LOW)
        print("right Button pushed")

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


def setup_gpio():
    GPIO.setmode(GPIO.BCM)  # Use BCM GPIO numbering
    GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Set GPIO 21 as input
    GPIO.setup(5, GPIO.OUT)  # Set GPIO 17 as output for the relay

def main():
    setup_gpio()
    count = 0  # Initialize the counter to 0

    try:
        while True:
            if GPIO.input(21) == GPIO.HIGH:
                GPIO.output(5, GPIO.HIGH)  # Turn on relay
                count += 1  # Increment count when relay is on
                print("Relay ON, Count:", count)
                time.sleep(.1)
                GPIO.output(5, GPIO.LOW)
            else:
                if count > 0:  # Only print when there was a previous count
                    print("Final count before relay off:", count)
                    sio.emit('update_tickets', {'machine_id': '1', 'tickets': count}, namespace='/machine')
                  # Turn off relay
                count = 0  # Reset count when relay is off
                print("Relay OFF")
            time.sleep(0.05)  # Sleep for 100 milliseconds

    except KeyboardInterrupt:
        print("Program terminated by user")
    finally:
        GPIO.cleanup()  # Ensure GPIOs are reset on exit














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
    while True:
        sio.connect('http://coinpusheronline.root-dynamics.com', namespaces=["/machine"])
        # Bind the signal handler to handle SIGINT (CTRL+C)
        signal.signal(signal.SIGINT, signal_handler)
        main()
        sio.wait()
except socketio.exceptions.ConnectionError as e:
    print("Failed to connect to the server:", e)