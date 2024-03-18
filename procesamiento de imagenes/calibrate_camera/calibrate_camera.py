import numpy as np
import cv2
import glob

path = "procesamiento de imagenes/calibrate_camera"
count = 0
# Tamaño del tablero de ajedrez (número de esquinas en el tablero)
chessboard_size = (6, 4)

# Arreglos para almacenar puntos de objeto y puntos de imagen de todas las imágenes
objpoints = []  # Puntos 3D del mundo real
imgpoints = []  # Puntos 2D en la imagen

# Listar todas las imágenes de tablero de ajedrez en la carpeta
images = glob.glob(f'{path}/images/*.jpg')

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Buscar esquinas del tablero de ajedrez
    ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)

    # Si se encuentran las esquinas, agregar puntos de objeto y puntos de imagen
    if ret:
        objpoints.append(
            np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32))
        objpoints[-1][:, :2] = np.mgrid[0:chessboard_size[0],
                                        0:chessboard_size[1]].T.reshape(-1, 2)
        imgpoints.append(corners)

        # Dibujar y mostrar las esquinas en la imagen (opcional)
        cv2.drawChessboardCorners(img, chessboard_size, corners, ret)
        cv2.imshow('Chessboard Corners', img)
        if count == 0:
            cv2.imwrite(f'{path}/images/image_calibrated.jpg', img)
        count += 1
        cv2.waitKey(500)

cv2.destroyAllWindows()


# Calibrar la cámara usando los puntos de objeto e imagen
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
    objpoints, imgpoints, gray.shape[::-1], None, None)

print("Camera matrix: ")
print(mtx)

print("Distortion coefficients: ")
print(dist)

# Calcular el error de calibración
mean_error = 0
list_error = []

for i in range(len(objpoints)):
    imgpoints2, _ = cv2.projectPoints(
        objpoints[i], rvecs[i], tvecs[i], mtx, dist)
    error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
    list_error.append(error)
    mean_error += error

mean_error /= len(objpoints)





print("Error de calibración: ", mean_error)
# Guardar los parámetros de calibración para su uso posterior
np.savez(f'{path}/calibration.npz', mtx=mtx, dist=dist, rvecs=rvecs, tvecs=tvecs, mean_error = mean_error)

print("Calibration complete!")


# Cargar la imagen de ejemplo
img_example = cv2.imread(f'{path}/images/image_10.jpg')

# Corregir distorsiones en la imagen de ejemplo
undistorted = cv2.undistort(img_example, mtx, dist, None, mtx)

# Mostrar las imágenes original y corregida
cv2.imshow('Original Image', img_example)
cv2.imshow('Undistorted Image', undistorted)
cv2.waitKey(0)
cv2.destroyAllWindows()
