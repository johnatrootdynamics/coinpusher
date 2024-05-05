import socketio
import time

# Create a Socket.IO client instance
sio = socketio.Client(logger=True, engineio_logger=True)  # Logging is optional but helpful for debugging

# Define event handlers
@sio.event
def connect():
    print("Connected to the server.")
    sio.emit('my event', {'data': 'Client connected'})  # Example of sending data to the server

@sio.event
def message(data):
    print('Received data:', data)
@sio.event
def update_machine():
    sio.emit('update_machine', {'data': {'machine_id': '1', 'machine_status': '2'}})
@sio.event
def disconnect():
    print("Disconnected from the server.")

# Connect to the Flask-SocketIO server
try:
    sio.connect('http://coinpusheronline.root-dynamics.com')
    time.sleep(2)
    sio.update_machine()
    sio.disconnect()
except socketio.exceptions.ConnectionError as e:
    print("Connection failed:", e)