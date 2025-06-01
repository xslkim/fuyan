import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw

# STEP 2: Create an FaceLandmarker object.
base_options = python.BaseOptions(model_asset_path='face_landmarker_v2_with_blendshapes.task')
options = vision.FaceLandmarkerOptions(base_options=base_options,
                                       output_face_blendshapes=True,
                                       output_facial_transformation_matrixes=True,
                                       num_faces=1)
detector = vision.FaceLandmarker.create_from_options(options)


def draw_landmarks_on_image(rgb_image, detection_result):
  face_landmarks_list = detection_result.face_landmarks

  draw = ImageDraw.Draw(rgb_image)
  width = rgb_image.width
  height = rgb_image.height

  for idx in range(len(face_landmarks_list)):
    face_landmarks = face_landmarks_list[idx]
    for i in range(len(face_landmarks)):
      x = face_landmarks[i].x * width
      y = face_landmarks[i].y * height
      point_size = 2
      draw.ellipse([(x, y), (x+point_size, y+point_size)], fill='yellow')

    # Draw the face landmarks.
    # face_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
    # face_landmarks_proto.landmark.extend([
      # landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in face_landmarks
    # ])

    # solutions.drawing_utils.draw_landmarks(
    #     image=annotated_image,
    #     landmark_list=face_landmarks_proto,
    #     connections=mp.solutions.face_mesh.FACEMESH_TESSELATION,
    #     landmark_drawing_spec=None,
    #     connection_drawing_spec=mp.solutions.drawing_styles
    #     .get_default_face_mesh_tesselation_style())
    # solutions.drawing_utils.draw_landmarks(
    #     image=annotated_image,
    #     landmark_list=face_landmarks_proto,
    #     connections=mp.solutions.face_mesh.FACEMESH_CONTOURS,
    #     landmark_drawing_spec=None,
    #     connection_drawing_spec=mp.solutions.drawing_styles
    #     .get_default_face_mesh_contours_style())
    # solutions.drawing_utils.draw_landmarks(
    #     image=annotated_image,
    #     landmark_list=face_landmarks_proto,
    #     connections=mp.solutions.face_mesh.FACEMESH_IRISES,
    #       landmark_drawing_spec=None,
          # connection_drawing_spec=mp.solutions.drawing_styles
          # .get_default_face_mesh_iris_connections_style())

  # return annotated_image
  return rgb_image


def dectedAndDraw(img, path):
  
    # STEP 3: Load the input image.
    mp_image = mp.Image.create_from_file(path)

    # STEP 4: Detect face landmarks from the input image.
    detection_result = detector.detect(mp_image)

    out_img = draw_landmarks_on_image(img, detection_result)
    return out_img

def face(img, path):
  
    # STEP 3: Load the input image.
    mp_image = mp.Image.create_from_file(path)

    # STEP 4: Detect face landmarks from the input image.
    detection_result = detector.detect(mp_image)

    out_img = draw_landmarks_on_image(img, detection_result)
    return out_img
