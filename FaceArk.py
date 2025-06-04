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
    s = data['面部年龄']
    s = s.replace('岁', '')
    parts = s.split('-')
    start_age = int(parts[0])
    end_age = int(parts[1])
    data['start_age'] = start_age
    data['end_age'] = end_age
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
                    {"type": "text", "text": "告诉我图片中人物的以下特征，只要答案，格式为json字符串，用9个字以内概括图片三庭五眼的特征 面部年龄（给出区间年龄） 脸型 嘴型 眼袋 眼型 鼻型 眼皮（双眼皮/单眼皮） 法令纹（有法令纹/无法令纹） 人中（答案要有人中两个字） 眉形 瞳孔颜色（答案要有瞳色两个字） 肤色（粉一白/粉二白/粉三白/黄一白/黄二白/黄黑皮）直得分 曲得分 直曲总分（直得分-曲得分） 大量感得分 小量感得分 量感总分（大量感得分-小量感得） 面部立体度（总分十分）瞳距（毫米）"},
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

def angle(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    angle_rad = math.atan2(dy, dx)
    angle_deg = math.degrees(angle_rad)
    return angle_deg

def calculate_angle(A, B, C):
    """
    使用atan2方法计算角度
    """
    # 创建向量BA和BC
    BA = (A[0] - B[0], A[1] - B[1])
    BC = (C[0] - B[0], C[1] - B[1])
    
    # 计算两个向量的角度
    angle_BA = math.atan2(BA[1], BA[0])
    angle_BC = math.atan2(BC[1], BC[0])
    
    # 计算角度差
    angle = math.degrees(angle_BC - angle_BA)
    
    # 规范化角度到0-360度
    angle = angle % 360
    
    # 取较小的角度（如果大于180度，取360-angle）
    if angle > 180:
        angle = 360 - angle
    
    return angle

def GetDetector(path):
    mp_image = mp.Image.create_from_file(path)
    mp_ret = detector.detect(mp_image)
    return mp_ret

def GetFinalData(fire_ret, save_path, width, height):
    mp_ret = GetDetector(save_path)
    if fire_ret['瞳距'] != None:
        try:
            if '毫米' in fire_ret['瞳距']:
                fire_ret['瞳距'] = fire_ret['瞳距'].replace('毫米', '')
            pd = int(fire_ret['瞳距'])
        except:
            pd = 62
        fire_ret['瞳距'] = pd
    else:
        pd = 62
        fire_ret['瞳距'] = pd

    final_data = {}
    final_data['face_figure'] = fire_ret
    page1 = {}
    p = GetFacePoint(mp_ret, width, height)
    p0 = p[34]
    p1 = p[130]
    p2 = p[133]
    p3 = p[362]
    p4 = p[359]
    p5 = p[356]
    page1['line_x_array'] = [p0['x'], p1['x'], p2['x'], p3['x'], p4['x'], p5['x']]
    tongju = distance(p[468]['x'], p[468]['y'], p[473]['y'], p[473]['y'])
    d0 = (p1['x'] - p0['x'])*(pd/10)/tongju
    d1 = (p2['x'] - p1['x'])*(pd/10)/tongju
    d2 = (p3['x'] - p2['x'])*(pd/10)/tongju
    d3 = (p4['x'] - p3['x'])*(pd/10)/tongju
    d4 = (p5['x'] - p4['x'])*(pd/10)/tongju
    page1['line_distance_array'] = [d0, d1, d2, d3, d4]
    final_data['page1'] = page1

    page2 = {}
    right_eye = {}
    right_eye['height'] = distance(p[470]['x'], p[470]['y'], p[23]['y'], p[23]['y'])
    right_eye['width'] =  distance(p[130]['x'], p[130]['y'], p[133]['y'], p[133]['y'])
    right_eye['top'] = p[470]
    right_eye['bottom'] = p[23]
    right_eye['right'] = p[130]
    right_eye['left'] = p[133]
    page2['right_eye'] = right_eye

    left_eye = {}
    left_eye['height'] = distance(p[475]['x'], p[475]['y'], p[253]['y'], p[253]['y'])
    left_eye['width'] =  distance(p[362]['x'], p[362]['y'], p[359]['y'], p[359]['y'])
    left_eye['top'] = p[475]
    left_eye['bottom'] = p[253]
    left_eye['right'] = p[362]
    left_eye['left'] = p[359]
    page2['left_eye'] = left_eye

    right_eyebrow = {}
    right_eyebrow['angle'] = angle(p[55]['x'], p[55]['x'], p[52]['x'], p[52]['x'])
    right_eyebrow['distance'] = distance(p[66]['x'], p[66]['y'], p[158]['y'], p[158]['y'])
    page2['right_eyebrow'] = right_eyebrow

    left_eyebrow = {}
    left_eyebrow['angle'] = angle(p[285]['x'], p[285]['x'], p[282]['x'], p[282]['x'])
    left_eyebrow['distance'] = distance(p[295]['x'], p[295]['y'], p[385]['y'], p[385]['y'])
    page2['left_eyebrow'] = left_eyebrow
    final_data['page2'] = page2

    page3 = {}
    left_eye = p[473]
    right_eye = p[468]
    ren_zhong = p[164]
    angel = calculate_angle((left_eye['x'], left_eye['y']),
                            (ren_zhong['x'], ren_zhong['y']),
                            (right_eye['x'], right_eye['y']))
    page3['left_eye'] = left_eye
    page3['right_eye'] = right_eye
    page3['ren_zhong'] = ren_zhong
    page3['angle'] = angel
    final_data['page3'] = page3

    return final_data
    