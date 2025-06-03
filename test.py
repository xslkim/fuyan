import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
from FaceArk import GetFinalData
from FaceArk import GetFacePoint
from FaceArk import GetDetector

def GetServerIP():
   return '47.95.20.1' 

# STEP 2: Create an FaceLandmarker object.





def draw_landmarks_on_image(rgb_image, path):
  detection_result = GetDetector(path)
  point_data = GetFacePoint(detection_result, rgb_image.width, rgb_image.height)

  draw = ImageDraw.Draw(rgb_image)
  for p in point_data:
    point_size = 2
    x = p['x']
    y = p['y']
    draw.ellipse([(x, y), (x+point_size, y+point_size)], fill='yellow')


  # return annotated_image
  return rgb_image



def find_x_coordinate(x1, y1, slope, y_target):
    if y1 == y_target:
        return x1
    x = x1 + (y_target - y1) / slope
    return (x, y_target)

def drawVerticalLine(draw, x, height):
   draw.line((x, 20, x, height-20),fill='green', width=2)

def draw_line_on_image(img, final_data):
  width = img.width
  height = img.height
  draw = ImageDraw.Draw(img)

  page1 = final_data['page1']
  line_x_array = page1['line_x_array']
  for x in line_x_array:
    drawVerticalLine(draw, x, height)

  return img


def face(path):
    img = Image.open(path)
    detection_result = GetDetector(path)
    data = {}
    data['point_array'] = GetFacePoint(detection_result, img.width, img.height)
    return data
