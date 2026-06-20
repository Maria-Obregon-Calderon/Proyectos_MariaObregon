**Instalar las siguientes librerías en el bash de anaconda o en el cmd de Windows:

- cv2 (OpenCV)
versión: 4.5.5.64
- MediaPipe
Versión: 0.10.5
- Numpy
Versión: 1.23.5
- Pygame
Versión: 2.1.0

De la siguiente manera:

pip install opencv-python 4.5.5.64
pip install mediapipe 0.10.5
pip install numpy 1.23.5
pip install pygame 2.1.0


**Utilizar este código con Python 3.9 ya que las versiones de las librerías son compatibles con esta versión

Archivos que no pueden ser subidos debido al tamaño:

shape_predictor_68_face_landmarks:
Es un modelo preentrenado que se utiliza en visión por computadora con el fin de detectar y
mapear 68 puntos del rostro humano en específico. Por lo tanto, es necesario para este proyecto
ya que trackea los ojos.
