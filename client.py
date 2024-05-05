import websocket
import json
import time
from threading import Thread

def on_message(ws, message):
    print(f"Received message from server: {message}")
    # Here you can add code to handle incoming messages, like commands to actuate machinery

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws):
    print("Connection Closed")

def on_open(ws):
    def run(*args):
        while True:
            # Send updates periodically or based on events
            data = {'status': 'OK', 'msg': 'Heartbeat from Raspberry Pi'}
            ws.send(json.dumps(data))
            time.sleep(10)  # Example: send data every 10 seconds
    Thread(target=run).start()

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws_app = websocket.WebSocketApp("ws://coinpusheronline.root-dynamics.com/",
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close,
                                    on_open=on_open)
    ws_app.run_forever()