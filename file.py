import cv2
import mediapipe as mp
import numpy as np
import pygame

#Inicializar pygame para sonido
pygame.mixer.init()
sonido_alerta = pygame.mixer.Sound("alerta.flac")

# Parámetros
EAR_UMBRAL = 0.21
UMBRAL_FRAMES = 15
contador_cerrado = 0
alerta_sonando = False

#Función para calcular EAR
def calcular_ear(ojos):
    A = np.linalg.norm(ojos[1] - ojos[5])
    B = np.linalg.norm(ojos[2] - ojos[4])
    C = np.linalg.norm(ojos[0] - ojos[3])
    ear = (A + B) / (2.0 * C)
    return ear

# --- Inicializar Mediapipe y video ---
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1)
mp_drawing = mp.solutions.drawing_utils

#Puntos del ojo derecho e izquierdo (indices de mediapipe)
ojo_izq = [362, 385, 387, 263, 373, 380]
ojo_der = [33, 160, 158, 133, 153, 144]
#Los números son los puntos/coordenadas para calibrar ambos ojos dependiendo
# de la posición (izquierda o derecha)

# Cargar video
cam = cv2.VideoCapture("Sujeto_Prueba.mp4")
#Sirve para subir el video ya que no se cuenta con webcam en el laboratorio#

while True:
    ret, frame = cam.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultado = face_mesh.process(frame_rgb)

    if resultado.multi_face_landmarks:
        for rostro in resultado.multi_face_landmarks:
            h, w, _ = frame.shape

            # Extraer puntos de los ojos
            puntos = []
            for i in ojo_izq + ojo_der:
                x = int(rostro.landmark[i].x * w)
                y = int(rostro.landmark[i].y * h)
                puntos.append((x, y))
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

            # Calcular EAR para ambos ojos
            puntos_ojos = np.array(puntos)
            ear_izq = calcular_ear(puntos_ojos[0:6])
            ear_der = calcular_ear(puntos_ojos[6:12])
            ear_promedio = (ear_izq + ear_der) / 2.0

            if ear_promedio < EAR_UMBRAL:
                contador_cerrado += 1
            else:
                contador_cerrado = 0
                alerta_sonando = False
                pygame.mixer.stop()

            if contador_cerrado >= UMBRAL_FRAMES:
                cv2.putText(frame, "ALERTA DE FATIGA!", (50, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
                if not alerta_sonando:
                    sonido_alerta.play(loops=-1)
                    alerta_sonando = True

    cv2.imshow("Detector de Fatiga - Mediapipe", frame)
    if cv2.waitKey(30) & 0xFF == 27:
        break

cam.release()
cv2.destroyAllWindows()
pygame.mixer.quit()
