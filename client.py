import socketio
import time
import signal
import sys

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
    time.sleep(2)
    update_machine_info()
    sio.wait()
    signal.signal(signal.SIGINT, signal_handler)
    sio.wait()
except socketio.exceptions.ConnectionError as e:
    print("Failed to connect to the server:", e)