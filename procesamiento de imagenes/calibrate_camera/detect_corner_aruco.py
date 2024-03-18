import cv2
def detect_aruco_markers(cap):
    aruco_dict = cv2.aruco.Dictionary(cv2.aruco.DICT_4X4_50, _markerSize=50)
    aruco_params = cv2.aruco.DetectorParameters()

    while True:
        ret, frame = cap.read()

        corners, ids, rejected = cv2.aruco.ArucoDetector(aruco_dict,aruco_params).detectMarkers(frame)

        if corners is not None:
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)

        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1)
        if key == ord("q"):
            break


if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    detect_aruco_markers(cap)

##import cv2
##import cv2.aruco as aruco
##
### Cargar la imagen
##image_path = "procesamiento de imagenes/calibrate_camera/images/aruco1.jpg"
##frame = cv2.imread(image_path)
##
### Convertir la imagen a escala de grises
##gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
##
### Definir el diccionario ArUco
##aruco_dict = aruco.Dictionary(aruco.DICT_4X4_100,_markerSize=100)
##
### Configurar el detector ArUco
##parameters = aruco.DetectorParameters()
##
### Detectar marcadores ArUco
##corners, ids, rejectedImgPoints = aruco.ArucoDetector(aruco_dict, parameters).detectMarkers(gray)
##
### Dibujar los resultados en la imagen
##frame = aruco.drawDetectedMarkers(frame, corners, ids)
##
### Mostrar la imagen con los marcadores detectados
##cv2.imshow('ArUco Marker Detection', frame)
##cv2.waitKey(0)
##cv2.destroyAllWindows()
