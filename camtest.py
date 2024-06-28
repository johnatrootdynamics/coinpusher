import cv2
import asyncio
import websockets

async def send_video():
    uri = "ws://your_server_address:port"
    async with websockets.connect(uri) as websocket:
        cap = cv2.VideoCapture(0)

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
            jpg_as_text = buffer.tobytes()

            # Send the frame to the server
            await websocket.send(jpg_as_text)

            # To simulate a real-time streaming delay
            await asyncio.sleep(0.1)

        cap.release()

asyncio.get_event_loop().run_until_complete(send_video())