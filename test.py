import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import matplotlib.pyplot as plt

# STEP 2: Create an FaceLandmarker object.
base_options = python.BaseOptions(model_asset_path='C:/fuyan/face_landmarker_v2_with_blendshapes.task')
options = vision.FaceLandmarkerOptions(base_options=base_options,
                                       output_face_blendshapes=True,
                                       output_facial_transformation_matrixes=True,
                                       num_faces=1)
detector = vision.FaceLandmarker.create_from_options(options)


def draw_landmarks_on_image(rgb_image, detection_result):
  face_landmarks_list = detection_result.face_landmarks
  # annotated_image = np.copy(rgb_image)

  from PIL import Image, ImageDraw

  # 打开图像
# image = Image.open('image.jpg')  # 替换为你的图片路径

  # 创建一个 Draw 对象
  draw = ImageDraw.Draw(rgb_image)

  # 画一条红线 (RGB格式)
  # 参数：起点坐标, 终点坐标, 颜色(R,G,B), 线宽
  # draw.line([(50, 50), (200, 200)], fill=(255, 0, 0), width=2)

  # 显示图像
  # image.show()

  # 保存图像
  # image.save('image_with_line_pil.jpg')
  # Loop through the detected faces to visualize.
  for idx in range(len(face_landmarks_list)):
    face_landmarks = face_landmarks_list[idx]
    for i in range(len(face_landmarks)):
       x = face_landmarks[i].x * 320
       y = face_landmarks[i].y * 480
       draw.point((x, y))

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


def dectedAndDraw(srcImg, path):
  
    # STEP 3: Load the input image.
    image = mp.Image.create_from_file(path)

    # STEP 4: Detect face landmarks from the input image.
    detection_result = detector.detect(image)

    out_img = draw_landmarks_on_image(srcImg, detection_result)
    return out_img
