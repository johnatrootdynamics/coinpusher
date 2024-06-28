import cv2

cap = cv2.VideoCapture('/dev/video0', cv2.CAP_MSMF)

if not cap.isOpened():
    print("Error: Could not open video device")
else:
    ret, frame = cap.read()
    if ret:
        cv2.imwrite('test.jpg', frame)
        print("Image captured and saved as test.jpg")
    else:
        print("Error: Could not read frame")

cap.release()
