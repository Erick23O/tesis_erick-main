import cv2


def obtener_camaras_conectadas():
    camaras_conectadas = []
    for i in range(10):  # Probamos hasta 10 dispositivos
        cap = cv2.VideoCapture(i)
        if not cap.isOpened():
            break
        else:
            camaras_conectadas.append(i)
        cap.release()
    return camaras_conectadas


if __name__ == "__main__":
    camaras = obtener_camaras_conectadas()
    print("Cámaras conectadas:", camaras)
