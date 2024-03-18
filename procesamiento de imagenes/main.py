import cv2
from cv2 import aruco
import numpy as np

# dictionary to specify type of the marker
marker_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_1000)

# detect the marker
param_markers = aruco.DetectorParameters()

# Dirección IP de la cámara y puerto
ip_address = '192.168.1.120'
port = '4747'

# URL de la transmisión de video de la cámara IP
#url = f'http://{ip_address}:{port}/video'

# Captura de video desde la cámara IP
#cap = cv2.VideoCapture(url)
cap = cv2.VideoCapture(1)

path = "procesamiento de imagenes/calibrate_camera"

calib_data_path = "/calibration.npz"

calib_data = np.load(f"{path}{calib_data_path}")
#print(calib_data.files)
cam_mat = calib_data["mtx"]
dist_coef = calib_data["dist"]
r_vectors = calib_data["rvecs"]
t_vectors = calib_data["tvecs"]
errors = calib_data["mean_error"]

# point = [x,y]
point1 = [0, 0]
point2 = [0, 0]
point3 = [0, 0]
point4 = [0, 0]


MARKER_SIZE = 4  # centimettros
w, h = 600, 400
points_destino = np.array([[0, 0], [w, 0], [w, h], [0, h]], np.float32)

###########
kernel = np.ones((3, 3), np.uint8)


red_bajo_1 = np.array([0, 100, 100], np.uint8)
red_alto_1 = np.array([8, 255, 255], np.uint8)

red_bajo_2 = np.array([150, 100, 100], np.uint8)
red_alto_2 = np.array([179, 255, 255], np.uint8)

blue_bajo = np.array([96, 80, 100], np.uint8)
blue_alto = np.array([145, 255, 255], np.uint8)

green_bajo = np.array([38, 80, 100], np.uint8)
green_alto = np.array([95, 255, 255], np.uint8)

laser_bajo = np.array([12, 55, 100], np.uint8)
laser_alto = np.array([36, 255, 255], np.uint8)

white_bajo = np.array([0, 0, 180], np.uint8)
white_alto = np.array([180, 30, 255], np.uint8)

min_area = 1000
max_area = 4000


def px_to_cm(w_px, h_px):
    w_cm = (w_px*68/w) - 34
    h_cm = 35 - (h_px*35/h)

    return w_cm, h_cm


def get_contour_and_show_centroid(img, contours, text, color):
    for c in contours:
        area = cv2.contourArea(c)
        if area > min_area and area < max_area:
            Moment = cv2.moments(c)
            if Moment['m00'] == 0:
                Moment['m00'] = 1
            cx = int(Moment['m10']/Moment['m00'])
            cy = int(Moment['m01']/Moment['m00'])
            cx_cm, cy_cm = px_to_cm(cx, cy)
            cx_cm = round(cx_cm, 2)
            cy_cm = round(cy_cm, 2)
            cv2.circle(img, (cx, cy), 3, (0, 255, 255), -1)
            cv2.putText(img, f"{cx_cm},{cy_cm}", (cx+5, cy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(img, (x-10, y-10),
                          (x+10 + w, y+10 + h), color, 1)
            cv2.putText(img, text, (x, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

######




def work_zone(frame, w, h):
    matriz_perspective = cv2.getPerspectiveTransform(
        points_copy, points_destino)
    img_perspective = cv2.warpPerspective(frame, matriz_perspective, (w, h))
    return img_perspective




while True:
    points = np.array([point1, point2, point3, point4], dtype=np.int32)
    points_copy = np.float32(points)
    points = points.reshape((-1, 1, 2))

    ret, frame = cap.read()
    if not ret:
        break

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
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
            cv2.polylines(frame, [corners.astype(np.int32)],
                          True, (0, 255, 255), 1, cv2.LINE_AA)
            corners = corners.reshape(4, 2)
            corners = corners.astype(int)
            top_right = corners[0].ravel()        
            top_left = corners[1].ravel()
            bottom_right = corners[2].ravel()
            bottom_left = corners[3].ravel()

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
            zone = work_zone(frame, w, h)
            if zone is not None:                
                hsv = cv2.cvtColor(zone, cv2.COLOR_BGR2HSV)    
                red_1 = cv2.inRange(hsv, red_bajo_1, red_alto_1)
                red_2 = cv2.inRange(hsv, red_bajo_2, red_alto_2)
                red_color = red_1 + red_2
                blue_color = cv2.inRange(hsv, blue_bajo, blue_alto)
                green_color = cv2.inRange(hsv, green_bajo, green_alto)
                laser = cv2.inRange(hsv, laser_bajo, laser_alto)
                white = cv2.inRange(hsv, white_bajo, white_alto)
                laser_closing = cv2.morphologyEx(laser, cv2.MORPH_CLOSE, kernel)
                red_closing = cv2.morphologyEx(red_color, cv2.MORPH_CLOSE, kernel)
                blue_closing = cv2.morphologyEx(blue_color, cv2.MORPH_CLOSE, kernel)
                green_closing = cv2.morphologyEx(green_color, cv2.MORPH_CLOSE, kernel)
                white_closing = cv2.morphologyEx(white, cv2.MORPH_CLOSE, kernel)
                contours_red, _ = cv2.findContours(red_closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                contours_blue, _ = cv2.findContours(blue_closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                contours_green, _ = cv2.findContours(green_closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                contours_laser, _ = cv2.findContours(laser_closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                contours_white, _  = cv2.findContours(white_closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                get_contour_and_show_centroid(zone, contours_red, "3D R", (0, 0, 255))
                get_contour_and_show_centroid(zone, contours_blue, "3D B",(255,0,0))
                get_contour_and_show_centroid(zone, contours_green, "3D G",(0,255,0))
                get_contour_and_show_centroid(zone, contours_laser, "Laser",(0,255,255))
                get_contour_and_show_centroid(zone, contours_white, "3D W",(255,255,255))

                cv2.imshow('White', white_closing)
                cv2.imshow('Laser', laser_closing)
                cv2.imshow('Rojo', red_closing)
                cv2.imshow('Azul', blue_closing)
                cv2.imshow('Verde', green_closing)                
                cv2.imshow("zone", zone)

    cv2.imshow("frame", frame)
    key = cv2.waitKey(1)
    if key == ord("q"):
        break
cap.release()
cv2.destroyAllWindows()
