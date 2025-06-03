import os
import json
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from volcenginesdkarkruntime import Ark
import math

base_options = python.BaseOptions(model_asset_path='face_landmarker_v2_with_blendshapes.task')
options = vision.FaceLandmarkerOptions(base_options=base_options,
                                       output_face_blendshapes=True,
                                       output_facial_transformation_matrixes=True,
                                       num_faces=1)
detector = vision.FaceLandmarker.create_from_options(options)

# 请确保您已将 API Key 存储在环境变量 ARK_API_KEY 中
# 初始化Ark客户端，从环境变量中读取您的API Key
client = Ark(
    # 此为默认路径，您可根据业务所在地域进行配置
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    # 从环境变量中获取您的 API Key。此为默认方式，您可根据需要进行修改
    # api_key=os.environ.get("ARK_API_KEY"),
    api_key='14fc0280-fc65-462d-ac2d-50178c0212e3'
)

def parse_facial_data(data_str):
    print(f'原始字符串 {data_str}')
    # 去除多余的标记和换行符
    json_str_clean = data_str.strip('```json\n').strip('```').strip()

    # 转换为Python字典
    data = json.loads(json_str_clean)
    return data
    


def GetPicDesc(img_url):
    response = client.chat.completions.create(
        # 指定您创建的方舟推理接入点 ID，此处已帮您修改为您的推理接入点 ID
        model="doubao-1.5-vision-pro-250328",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": img_url
                        },
                    },
                    {"type": "text", "text": "告诉我图片中人物的以下特征，只要答案，格式为json字符串，用9个字以内概括图片三庭五眼的特征 面部年龄（给出区间年龄） 脸型 嘴型 眼袋 眼型 鼻型 法令纹（有法令纹/无法令纹） 人中（答案要有人中两个字） 眉形 瞳孔颜色（答案要有瞳色两个字） 肤色（粉一白/粉二白/粉三白/黄一白/黄二白/黄黑皮）直得分 曲得分 直曲总分（直得分-曲得分） 大量感得分 小量感得分 量感总分（大量感得分-小量感得） 面部立体度（总分十分）瞳距（毫米）"},
                ],
            }
        ],
        
    )

    text = response.choices[0].message.content
    result = {}

    try:
        result = parse_facial_data(text)
    except:
        print(f'Error {text}')

    return result

def GetFacePoint(detection_result, width, height):
    data = []
    face_landmarks_list = detection_result.face_landmarks
    face_landmarks = face_landmarks_list[0]
    for i in range(len(face_landmarks)):
      x = face_landmarks[i].x * width
      y = face_landmarks[i].y * height
      data.append({'id':i, 'x':round(x, 2), 'y':round(y, 2)})
    
    return data


def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def GetDetector(path):
    mp_image = mp.Image.create_from_file(path)
    mp_ret = detector.detect(mp_image)
    return mp_ret

def GetFinalData(fire_ret, save_path, width, height):
    mp_ret = GetDetector(save_path)
    if fire_ret['瞳距'] != None:
        pd = int(fire_ret['瞳距'])
    else:
        pd = 62
        fire_ret['瞳距'] = pd

    final_data = {}
    final_data['face_figure'] = fire_ret
    page1 = {}
    point_data = GetFacePoint(mp_ret, width, height)
    p0 = point_data[34]
    p1 = point_data[33]
    p2 = point_data[133]
    p3 = point_data[362]
    p4 = point_data[263]
    p5 = point_data[356]
    page1['line_x_array'] = [p0['x'], p1['x'], p2['x'], p3['x'], p4['x'], p5['x']]
    tongju = distance(point_data[468]['x'], point_data[468]['y'], point_data[473]['y'], point_data[473]['y'])
    d0 = (p1['x'] - p0['x'])*(pd/10)/tongju
    d1 = (p2['x'] - p1['x'])*(pd/10)/tongju
    d2 = (p3['x'] - p2['x'])*(pd/10)/tongju
    d3 = (p4['x'] - p3['x'])*(pd/10)/tongju
    d4 = (p5['x'] - p4['x'])*(pd/10)/tongju
    page1['line_distance_array'] = [d0, d1, d2, d3, d4]
    final_data['page1'] = page1
    return final_data
    