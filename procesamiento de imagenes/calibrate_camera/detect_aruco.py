import cv2
from cv2 import aruco
import numpy as np

# dictionary to specify type of the marker
marker_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_1000)

# detect the marker
param_markers = aruco.DetectorParameters()
cap = cv2.VideoCapture(0)

path = "procesamiento de imagenes/calibrate_camera"

calib_data_path = "/calibration.npz"

calib_data = np.load(f"{path}{calib_data_path}")
print(calib_data.files)

cam_mat = calib_data["mtx"]
dist_coef = calib_data["dist"]
r_vectors = calib_data["rvecs"]
t_vectors = calib_data["tvecs"]
errors = calib_data["mean_error"]

print(cam_mat)
print(dist_coef)
print(r_vectors)
print(t_vectors)
print(errors)


#point = [x,y]
point1 = [0,0]
point2 = [0,0]
point3 = [0,0]
point4 = [0,0]

dist1 = 0

MARKER_SIZE = 4  # centimettros
w, h = 600, 400
points_destino = np.array([[0, 0], [w, 0], [w, h], [0, h]], np.float32)

def distance_cm(px_distance):
    return (px_distance * MARKER_SIZE) / 1000.0

def work_zone(frame,w,h):
    matriz_perspective = cv2.getPerspectiveTransform(points_copy, points_destino)
    img_perspective = cv2.warpPerspective(frame, matriz_perspective, (w,h))
    return img_perspective

def px_to_cm(w_px,h_px):
    w_cm = w_px*4.9/w
    h_cm = h_px*9.9/h
    
    return w_cm, h_cm

while True:
    points = np.array([point1,point2,point3,point4], dtype=np.int32)
    points_copy = np.float32(points)
    points = points.reshape((-1, 1, 2))
    
    
    ret, frame = cap.read()
    if not ret:
        break
    
    gray_frame = cv2.cv2tColor(frame, cv2.COLOR_BGR2GRAY)
    marker_corners, marker_IDs, reject = aruco.detectMarkers(
        gray_frame, marker_dict, parameters=param_markers
    )
    # getting conrners of markers
    if marker_corners:
        rVec, tVec, _ = aruco.estimatePoseSingleMarkers(
            marker_corners, MARKER_SIZE, cam_mat, dist_coef
        )
        total_markers = range(0, marker_IDs.size)
        for ids, corners in zip(marker_IDs, marker_corners):
            cv2.polylines(frame, [corners.astype(np.int32)], True, (0,255, 255), 1, cv2.LINE_AA)            
            corners = corners.reshape(4, 2)
            corners = corners.astype(int)
            top_right = corners[0].ravel()    
            #print(top_right)
            top_left = corners[1].ravel()
            bottom_right = corners[2].ravel()
            bottom_left = corners[3].ravel()
            #cv2.circle(frame, top_right, 6, (0, 255, 0), -1)
            #cv2.circle(frame, corners[1], 6, (255, 0, 0), -1)
            #cv2.circle(frame, corners[2], 6, (255, 255, 0), -1)
            #cv2.circle(frame, corners[3], 6, (255, 0, 255), -1)
            #print(corners[0], "  ", corners[1], "  ", corners[2], "  ", corners[3] )
            cv2.putText(
                frame,
                f"id: {ids[0]}",
                top_right,
                cv2.FONT_HERSHEY_PLAIN,
                1.3,
                (200, 100, 0),
                2,
                cv2.LINE_AA,
            )
            if ids[0] == 0:
                cv2.circle(frame, top_left, 3, (0, 255, 0), -1)   
                point1 = top_left
                
            if ids[0] == 1:
                cv2.circle(frame, top_right, 3, (0, 255, 0), -1)
                point2 = top_right
                
            if ids[0] == 2:
                cv2.circle(frame, bottom_right, 3, (0, 255, 0), -1)
                point4 = bottom_right
                
            if ids[0] == 3:
                cv2.circle(frame, bottom_left, 3, (0, 255, 0), -1)
                point3 = bottom_left
                
            cv2.polylines(frame, [points], True, (0, 255, 0), 1)
            zone = work_zone(frame,w,h)
            if zone is not None:
                                    
                cx = int(w/2)
                cy = int(h/2)
                cx_cm, cy_cm = px_to_cm(cx,cy)
                cx_cm = round(cx_cm,2)
                cy_cm = round(cy_cm,2)
                cv2.circle(zone, (cx, cy), 5, (255, 0, 0), -1, cv2.LINE_AA)
                cv2.putText(zone, f"({cx_cm},{cy_cm})", (cx+5, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                gray = cv2.cv2tColor(zone, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                cv2.imshow("thresh", thresh)
                cv2.imshow("zone", zone)

            

    cv2.imshow("frame", frame)
    key = cv2.waitKey(1)
    if key == ord("q"):
        break
cap.release()
cv2.destroyAllWindows()
