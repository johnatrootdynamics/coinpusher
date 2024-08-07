import socketio
import cv2
import base64
import time
import signal
import sys
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)  # Use BCM GPIO numbering
GPIO.setwarnings(False)



def send_video():


    
    cap = cv2.VideoCapture('/dev/video0')  # 0 is typically the default camera

    if not cap.isOpened():
        print("Error: Could not open video device")
        return
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture image")
            break

        # Encode the frame in JPEG format
        _, buffer = cv2.imencode('.jpg', frame)
        jpg_as_text = base64.b64encode(buffer).decode('utf-8')

        # Send the frame to the servers
        sio.emit('video_frame', jpg_as_text, namespace='/machine')

        # To simulate a real-time streaming delay
        #sio.sleep(0.1)

    cap.release()

GPIO.setup(17, GPIO.OUT)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)

def turn_off_gpio(pin):

    # Set up the pin as an output
    GPIO.setup(pin, GPIO.OUT)
    
    # Set the pin to LOW
    GPIO.output(pin, GPIO.LOW)
    #print(f"GPIO {pin} set to LOW")


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
    sio.emit('subtract_token', {'machine_id': '1'}, namespace='/machine')

@sio.event
def status_updated(data):
    print("DB updated")

@sio.event
def disconnect():
    print("Disconnected from the server.")
    sio.emit('disconnect', {'machine_id': '1', 'machine_status': '2'})

def signal_handler(sig, frame):
    print('Disconnecting...')
    if sio.connected:
        sio.disconnect()
    sys.exit(0)


def setup_gpio():
    GPIO.setmode(GPIO.BCM)  # Use BCM GPIO numbering
    GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Set GPIO 21 as input
    GPIO.setup(5, GPIO.OUT)  # Set GPIO 17 as output for the relay
    GPIO.setup(5, GPIO.LOW)  # Set GPIO 17 as output for the relay

@sio.event(namespace='/machine')
def webclient_status(data):
    global user_id
    user_id = data['user_id']
    return user_id

@sio.event(namespace='/machine')
def play_tokens(data):
    tokens = int(data['plays_added'])  # Ensure the tokens are handled as an integer
    token_clicks = tokens // 5  # Use integer division to determine how many times to activate the relay

    GPIO.setmode(GPIO.BCM)  # Set the GPIO numbering system to BCM
    GPIO.setup(17, GPIO.OUT)  # Setup GPIO 17 as an output for the relay

    try:
        for _ in range(token_clicks):
            GPIO.output(17, GPIO.HIGH)  # Turn on the relay
            time.sleep(0.1)  # Relay is on for 0.1 seconds
            GPIO.output(17, GPIO.LOW)  # Turn off the relay
            time.sleep(0.1)  # Wait for 0.1 seconds before potentially turning it on again
    finally:
        GPIO.cleanup(17) 







def main():
    setup_gpio()
    count = 0  # Initialize the counter to 0
    
    try:
        while True:

            if GPIO.input(21) == GPIO.HIGH:
                GPIO.output(5, GPIO.LOW)  # Turn on relay
                count += 1  # Increment count when relay is on
                #print("Relay ON, Count:", count)
                time.sleep(.1)
                GPIO.output(5, GPIO.HIGH)
            else:
                
                if count > 0:  # Only print when there was a previous count
                    print("Final count before relay off:", count)
                    sio.emit('update_tickets', {'machine_id': '1', 'tickets': count, 'user_id': '1'}, namespace='/machine')
                  # Turn off relay
                count = 0  # Reset count when relay is off
                #print("Relay OFF")
            time.sleep(0.1)  # Sleep for 100 milliseconds

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
        send_video()
        main()
        sio.wait()
except socketio.exceptions.ConnectionError as e:
    print("Failed to connect to the server:", e)