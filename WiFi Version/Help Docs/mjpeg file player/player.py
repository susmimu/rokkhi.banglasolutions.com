import cv2

cap = cv2.VideoCapture('image_2.mjpeg')

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imshow('MJPEG Player', frame)
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
