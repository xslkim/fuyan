import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw

def GetServerIP():
   return '47.95.20.1' 

# STEP 2: Create an FaceLandmarker object.
base_options = python.BaseOptions(model_asset_path='face_landmarker_v2_with_blendshapes.task')
options = vision.FaceLandmarkerOptions(base_options=base_options,
                                       output_face_blendshapes=True,
                                       output_facial_transformation_matrixes=True,
                                       num_faces=1)
detector = vision.FaceLandmarker.create_from_options(options)

def GetFacePoint(detection_result, width, height):
    data = []
    face_landmarks_list = detection_result.face_landmarks
    face_landmarks = face_landmarks_list[0]
    for i in range(len(face_landmarks)):
      x = face_landmarks[i].x * width
      y = face_landmarks[i].y * height
      data.append({'id':i, 'x':round(x, 2), 'y':round(y, 2)})
    
    return data


def draw_landmarks_on_image(rgb_image, detection_result):
  point_data = GetFacePoint(detection_result, rgb_image.width, rgb_image.height)

  draw = ImageDraw.Draw(rgb_image)
  for p in point_data:
    point_size = 2
    x = p['x']
    y = p['y']
    draw.ellipse([(x, y), (x+point_size, y+point_size)], fill='yellow')


  # return annotated_image
  return rgb_image




def dectedAndDraw(img, path):
    # STEP 3: Load the input image.
    mp_image = mp.Image.create_from_file(path)

    # STEP 4: Detect face landmarks from the input image.
    detection_result = detector.detect(mp_image)

    out_img = draw_landmarks_on_image(img, detection_result)
    return out_img

def find_x_coordinate(x1, y1, slope, y_target):
    if y1 == y_target:
        return x1
    x = x1 + (y_target - y1) / slope
    return (x, y_target)

def drawVerticalLine(draw, x, height):
   draw.line((x, 20, x, height-20),fill='green', width=2)

def draw_line_on_image(rgb_image, detection_result):
  width = rgb_image.width
  height = rgb_image.height
  point_data = GetFacePoint(detection_result, width, height)
  draw = ImageDraw.Draw(rgb_image)
  p0 = point_data[34]
  p1 = point_data[33]
  p2 = point_data[133]
  p3 = point_data[362]
  p4 = point_data[263]
  p5 = point_data[356]
  drawVerticalLine(draw, p0['x'], height)
  drawVerticalLine(draw, p1['x'], height)
  drawVerticalLine(draw, p2['x'], height)
  drawVerticalLine(draw, p3['x'], height)
  drawVerticalLine(draw, p4['x'], height)
  drawVerticalLine(draw, p5['x'], height)
  return rgb_image




  # meixin = point_data[9]
  # xiaba = point_data[200]
  # if(meixin.x == xiaba.x):
  #    print(a)
  # else:
  #    slope = (xiaba.y - meixin.y) / (xiaba.x - meixin.y)

  

def dectedAndDrawLine(img, path):
  
    # STEP 3: Load the input image.
    mp_image = mp.Image.create_from_file(path)

    # STEP 4: Detect face landmarks from the input image.
    detection_result = detector.detect(mp_image)

    out_img = draw_line_on_image(img, detection_result)
    return out_img

def face(path):
    img = Image.open(path)

    # STEP 3: Load the input image.
    mp_image = mp.Image.create_from_file(path)

    # STEP 4: Detect face landmarks from the input image.
    detection_result = detector.detect(mp_image)
    data = {}
    data['point_array'] = GetFacePoint(detection_result, img.width, img.height)
    
      
    return data
