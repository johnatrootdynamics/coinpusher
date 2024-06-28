import cv2
import base64
import socketio

# Initialize Socket.IO client
sio = socketio.Client()

@sio.event
def connect():
    print("Connected to server")

@sio.event
def disconnect():
    print("Disconnected from server")

def send_video():
    cap = cv2.VideoCapture(0)  # 0 is typically the default camera

    if not cap.isOpened():
        print("Error: Could not open video device")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture image")
            break

        # Encode the frame in JPEG format
        _, buffer = cv2.imencode('.jpg', frame)
        jpg_as_text = base64.b64encode(buffer).decode('utf-8')

        # Send the frame to the server
        sio.emit('video_frame', jpg_as_text, namespace='/machine')

        # To simulate a real-time streaming delay
        sio.sleep(0.1)

    cap.release()

if __name__ == '__main__':
    sio.connect('http://coinpusheronline.root-dynamics.com', namespaces=['/machine'])
    send_video()
    sio.wait()
