import cv2

# Set video capture device (0 is usually the default camera)
cap = cv2.VideoCapture(0)

# Set the frame width and height
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)

# Set the codec to MJPEG
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'MJPG')
out = cv2.VideoWriter('outputcode.avi', fourcc, 30.0, (800, 600))

# Record for 5 seconds
num_frames = int(30 * 25)  # 20 fps * 5 seconds

for _ in range(num_frames):
    ret, frame = cap.read()
    if ret:
        out.write(frame)
    else:
        break

# Release everything
cap.release()
out.release()
cv2.destroyAllWindows()
