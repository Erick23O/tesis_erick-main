import flet as ft
import cv2
import serial as sr
import serial.tools.list_ports
import math
import threading
from cv2 import aruco
import numpy as np


from camera import Camera


# dictionary to specify type of the marker
marker_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_1000)

# detect the marker
param_markers = aruco.DetectorParameters()
num_camera = 1
cap = cv2.VideoCapture(num_camera)

path = "procesamiento de imagenes/calibrate_camera"

calib_data_path = "/calibration.npz"

calib_data = np.load(f"{path}{calib_data_path}")
# print(calib_data.files)
cam_mat = calib_data["mtx"]
dist_coef = calib_data["dist"]
r_vectors = calib_data["rvecs"]
t_vectors = calib_data["tvecs"]
errors = calib_data["mean_error"]
MARKER_SIZE = 4  # centimettros

cap.set(cv2.CAP_PROP_FPS, 30)
width_camera = int(cap.get(3))
height_camera = int(cap.get(4))

width_camera = int(width_camera/1.1)
height_camera = int(height_camera/1.1)

port = sr.Serial()


def obtener_puertos_COM():
    puertos_COM = []
    puertos_disponibles = serial.tools.list_ports.comports()
    for puerto in puertos_disponibles:
        if puerto.device.startswith('COM'):
            puertos_COM.append(puerto.device)
        

    return puertos_COM



def cam():
    # point = [x,y]
    point1 = [0, 0]
    point2 = [0, 0]
    point3 = [0, 0]
    point4 = [0, 0]
    while True:
        points = np.array([point1, point2, point3, point4], dtype=np.int32)
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
        cv2.imshow("frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


t = threading.Thread(target=cam)
t.start()

camera = Camera()

page = ft.Page


def main(page: page):

    page.title = "Scara and Vision"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = ft.colors.GREY
    page.scroll = "adaptive"
    page.theme_mode = "light"

    def cinetica_inversa(x, y):
        # Longitudes de los eslabones
        longitud_eslabon1 = 12.0
        longitud_eslabon2 = 12.0
        # Calculamos la distancia desde el origen al punto (x, y)
        distancia = math.sqrt(x**2 + y**2)

        # Calculamos el ángulo theta2 usando la ley de los cosenos
        cos_theta2 = (distancia**2-longitud_eslabon1**2 - longitud_eslabon2 **
                      2) / (2 * longitud_eslabon1 * longitud_eslabon2)
        theta2 = math.acos(cos_theta2)

        # Calculamos el ángulo theta1 usando trigonometría básica
        # Usamos la función atan2 para obtener el ángulo correcto en el rango completo [-pi, pi]
        theta1 = math.atan2(x, y) - math.atan2((longitud_eslabon2 * math.sin(theta2)),
                                               (longitud_eslabon1 + longitud_eslabon2 * math.cos(theta2)))

        # Convertimos los ángulos de radianes a grados
        theta1_grados = math.degrees(theta1)
        theta2_grados = math.degrees(theta2)

        return theta1_grados, theta2_grados

    def angle_to_step_m1(angle):
        return int(angle * (7600 / 360))

    def angle_to_step_m2(angle):
        return int(angle * (10800 / 360))  # antes 5400

    def button_clicked(event):

        if event.control.value:

            animate_camera.content = section_with_camera if animate_camera.content == section_without_camera else section_without_camera
            animate_camera.update()
            # switch_camera.update()

        else:
            animate_camera.content = section_without_camera
            animate_camera.update()
            # if cap.isOpened():
            #    cap.release()

        page.update()

    def radiogroup_changed(event):
        if event.control.value == "manual":

            buttons_auto.controls[0].disabled = True
            buttons_manual.controls[0].controls[0].disabled = False
            buttons_manual.controls[0].controls[1].disabled = False
            buttons_manual.controls[1].controls[0].disabled = False
            buttons_manual.controls[1].controls[1].disabled = False
            buttons_manual.controls[2].disabled = False

            page.update()
        if event.control.value == "auto":

            buttons_auto.controls[0].disabled = False
            buttons_manual.controls[0].controls[0].disabled = True
            buttons_manual.controls[0].controls[1].disabled = True
            buttons_manual.controls[1].controls[0].disabled = True
            buttons_manual.controls[1].controls[1].disabled = True
            buttons_manual.controls[2].disabled = True

            page.update()

    def close_dlg(event):
        alert.open = False
        page.update()

    def send_manual(event):
        x1 = float(textField_X1.value)
        y1 = float(textField_Y1.value)
        x2 = float(textField_X2.value)
        y2 = float(textField_Y2.value)
        # print(f"X: {x}, Y: {y}")
        try:
            
            # Calcular la cinemática inversa
            global port
            theta1_pos1, theta2_pos1 = cinetica_inversa(x1, y1)
            theta1_pos2, theta2_pos2 = cinetica_inversa(x2, y2)
            print(theta1_pos1, theta2_pos1)
            data = str(angle_to_step_m1(theta1_pos1)) + "," + str(angle_to_step_m2(theta2_pos1)) + \
                ","+str(angle_to_step_m1(theta1_pos2))+"," + \
                str(angle_to_step_m2(theta2_pos2))
            port.write(data.encode('utf-8') + b'\n')
            # port.flush()
            print(data)

        except:
            # port.write(f"X{x}Y{y}".encode())
            page.dialog = alert

            alert.open = True
            page.update()

    def send_auto(event):
        # clase = camera.get_clase()

        x2 = 10.0
        y2 = 12.0

        x4 = 16.0
        y4 = 12.0

        puntos_auto = camera.get_centros()

        print(f"Los centros son: {puntos_auto}")

        clase = puntos_auto[0][2]

        if clase == "laser":

            x1 = puntos_auto[0][0]
            y1 = puntos_auto[0][1]
            x3 = puntos_auto[1][0]
            y3 = puntos_auto[1][1]
        elif clase == "3d":
            x1 = puntos_auto[1][0]
            y1 = puntos_auto[1][1]
            x3 = puntos_auto[0][0]
            y3 = puntos_auto[0][1]

        print(f"Los centroides son: {x1}, {y1}, {x3}, {y3}")
        try:
            global port
            # Calcular la cinemática inversa
            theta1_pos1, theta2_pos1 = cinetica_inversa(x1, y1)
            theta1_pos2, theta2_pos2 = cinetica_inversa(x2, y2)
            theta1_pos3, theta2_pos3 = cinetica_inversa(x3, y3)
            theta1_pos4, theta2_pos4 = cinetica_inversa(x4, y4)
            data_auto = str(angle_to_step_m1(theta1_pos1)) + "," + str(angle_to_step_m2(theta2_pos1)) + ","+str(angle_to_step_m1(theta1_pos2))+"," + str(angle_to_step_m2(theta2_pos2)) + \
                ","+str(angle_to_step_m1(theta1_pos3))+","+str(angle_to_step_m2(theta2_pos3)) + \
                ","+str(angle_to_step_m1(theta1_pos4))+"," + \
                str(angle_to_step_m2(theta2_pos4))
            port.write(data_auto.encode('utf-8') + b'\t')
            # port.flush()
            print(data_auto)
        except:
            # port.write(f"X{x}Y{y}".encode())
            page.dialog = alert

            alert.open = True
            page.update()
    
    def get_options_com():
        options = []
        for i in range(len(obtener_puertos_COM())):
            options.append(ft.dropdown.Option(obtener_puertos_COM()[i]))
        page.update()
        return options

    def select_port(event):
        port_name = drop_button.value
        try:
           global port
           port = sr.Serial(port=port_name, baudrate=9600)
           print("Conectado")
        except:
           print("Error al conectar con el puerto")
        
        page.update()
    
  

    def go_home(event):
        try:
            global port
            port.write(b'\r')
            # port.flush()
            print("Reseteando...")
        except:
            print("Falló la comunicación")
            page.update()

    section_without_camera = ft.Container(

        content=ft.Icon(name=ft.icons.CAMERA, size=300),
        width=width_camera,
        height=height_camera,
        bgcolor=ft.colors.BLUE_400,
        border_radius=ft.border_radius.all(20),
    )

    section_with_camera = ft.Container(
        content=Camera(),
        width=width_camera,
        height=height_camera,
        border_radius=ft.border_radius.all(20),

    )

    switch_camera = ft.Switch(
        label="Activar Cámara", value=False, on_change=button_clicked)

    animate_camera = ft.AnimatedSwitcher(
        section_without_camera,
        transition=ft.AnimatedSwitcherTransition.SCALE,
        duration=200,
        reverse_duration=100,
        switch_in_curve=ft.AnimationCurve.BOUNCE_OUT,
        switch_out_curve=ft.AnimationCurve.BOUNCE_IN,
    )

    radio_buttons = ft.RadioGroup(
        content=ft.Column(
            controls=[
                ft.Radio(value="manual", label="Manual"),
                ft.Radio(value="auto", label="Automático"),
            ]
        ),
        on_change=radiogroup_changed,
    )

    button_enviar_manual = ft.ElevatedButton(
        text="Enviar",
        disabled=True,
        on_click=send_manual,
    )
    button_enviar_auto = ft.ElevatedButton(
        text="Enviar",
        disabled=True,
        on_click=send_auto,
    )

    buttons_auto = ft.Column(
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            button_enviar_auto,

        ]
    )

    button_reset = ft.ElevatedButton(
        text="Home",
        on_click=go_home
    )

    textField_X1 = ft.TextField(label="X1", disabled=True, width=100)
    textField_X2 = ft.TextField(label="X2", disabled=True, width=100)
    textField_Y1 = ft.TextField(label="Y1", disabled=True, width=100)
    textField_Y2 = ft.TextField(label="Y2", disabled=True, width=100)

    alert = ft.AlertDialog(
        modal=True,
        title=ft.Text("Fuera de Rango"),
        content=ft.Text("Ingrese valores válidos..."),
        actions=[
            ft.TextButton("Salir", on_click=close_dlg),

        ],
        actions_alignment=ft.MainAxisAlignment.END
    )
    buttons_manual = ft.Column(
        # width=30,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    textField_X1,
                    textField_X2,
                ],
            ),
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    textField_Y1,
                    textField_Y2,
                ]
            ),


            button_enviar_manual,
        ]

    )

    drop_button = ft.Dropdown(
        on_change=select_port,
        options=get_options_com(),
        label="COM",
        hint_text="Seleccione el puerto...",
        width=200,
    )

    
    page.add(

        ft.Container(
            margin=ft.margin.all(5),
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Image(
                                src="../assets/logo_espe.png",
                                height=80
                            ),
                            ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Text(
                                        "PROYECTO DE INTEGRACIÓN CURRICULAR", color="black", ),
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        controls=[
                                            ft.Text("AUTOR:\t",
                                                    color="black"),
                                            ft.Column(
                                                controls=[
                                                    ft.Text(
                                                        "- Erick Mauricio Oña Muilema", color="black"),
                                                ]
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                            ft.Image(
                                src="../assets/logo_mecatronica_sin_fondo.png",
                                height=140,
                                width=140,
                            ),
                        ]
                    ),

                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,

                        controls=[

                            animate_camera,
                            ft.Container(width=50),
                            ft.Column(
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    drop_button,
                                    radio_buttons,
                                    ft.Row(
                                        controls=[
                                            ft.Container(
                                                alignment=ft.alignment.center,
                                                padding=10,
                                                width=325,
                                                height=250,
                                                bgcolor=ft.colors.WHITE24,
                                                border_radius=ft.border_radius.all(
                                                    20),
                                                content=ft.Column(
                                                    controls=[
                                                        ft.Text(
                                                            "Ingrese valores entre -24 y 24 para cada eje."),
                                                        buttons_manual
                                                    ]
                                                )
                                            ),
                                            ft.Container(
                                                padding=10,
                                                width=325,
                                                height=250,
                                                bgcolor=ft.colors.WHITE24,
                                                border_radius=ft.border_radius.all(
                                                    20),
                                                content=ft.Column(
                                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                    controls=[
                                                        ft.Container(
                                                            bgcolor=ft.colors.WHITE,
                                                            padding=ft.padding.all(
                                                                10),
                                                            border_radius=ft.border_radius.all(
                                                                20),
                                                            content=ft.Image(
                                                                src="../assets/scara.gif",
                                                                height=150,
                                                                width=150,
                                                            ),
                                                        ),
                                                        buttons_auto,
                                                    ]
                                                ),
                                            ),
                                        ]
                                    ),
                                    button_reset

                                ]
                            ),


                            # ft.Container(width=200),



                        ]
                    ),
                    switch_camera,
                ]
            )
        )
    )


if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
    cap.release()
    cv2.destroyAllWindows()
