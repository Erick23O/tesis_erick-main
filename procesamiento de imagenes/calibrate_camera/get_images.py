import cv2

cap = cv2.VideoCapture(0)
path = "procesamiento de imagenes\calibrate_camera\images"
count = 0


while True:
    ret, frame = cap.read()
    cv2.imshow("frame", frame)
    key = cv2.waitKey(100)
    if key == ord('s'):
        count += 1
        cv2.imwrite(f"{path}/image_{count}.jpg", frame)
        print("Saved")
    if key == ord('q'):
        print("Saved...")
        break
    
    
cap.release()
cv2.destroyAllWindows()

