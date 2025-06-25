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

def parse_face_json_data(data_str):
    print(f'原始字符串 {data_str}')
    # 去除多余的标记和换行符
    json_str_clean = data_str.strip('```json\n').strip('```').strip()

    try:
        # 转换为Python字典
        data = json.loads(json_str_clean)
        if '面部年龄' in data:
            s = data['面部年龄']
            data['年龄'] = s
        elif '年龄' in data:
            s = data['年龄']
        s = s.replace('岁', '')
        parts = s.split('-')
        start_age = int(parts[0])
        end_age = int(parts[1])
        data['start_age'] = start_age
        data['end_age'] = end_age
    except:
        print('转换年龄出错')

    if '瞳距' in data:
        try:
            if '毫米' in data['瞳距']:
                data['瞳距'] = data['瞳距'].replace('毫米', '')
            pd = int(data['瞳距'])
        except:
            pd = 62
        data['瞳距'] = pd
    else:
        pd = 62
        data['瞳距'] = pd

    return data

def parse_cloth_json_data(data_str):
    print(f'衣服原始字符串 {data_str}')
    # 去除多余的标记和换行符
    json_str_clean = data_str.strip('```json\n').strip('```').strip()

    # 转换为Python字典
    data = json.loads(json_str_clean)
    return data
    
def GetClothDesc(img_url):
    response = client.chat.completions.create(
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
                    {"type": "text", "text": "告诉我图片中服装的以下特征，只要答案，格式为json字符串，颜色四季型（春季型/夏季型/秋季型/冬季型，可以多选）适合年龄范围 直得分 曲得分 直曲总分（直得分-曲得分） 大量感得分 小量感得分 量感总分（大量感得分-小量感得）立体度（就是与面部风格立体度高的人的适配程度，总分十分）适合体型（H型/​X型/A型/O型/T型，可以多选）​​适合场景（职业/商务、休闲/日常、场合社交） 特点（显高、显瘦、显气场、 显腰线 、显腿长、显胸大、显胸小）以及10个最能概括衣服特征的标签"},
                ],
            }
        ],
    )

    text = response.choices[0].message.content
    result = {}

    try:
        result = parse_cloth_json_data(text)
    except:
        print(f'Error {text}')

    return result

def checkKey(key, bak_key, data, bak_value):
    if key in data:
        print(f'{key}:{data[key]}')
    else:
        if bak_key != None:
            if any(bak_key in key for key in data):
                matching_keys = [key for key in data if bak_key in key]
                print(f'bak_key {key}:{data[matching_keys[0]]}')
                data[key] = data[matching_keys[0]]
            else:
                print(f'bak_value {key}:{bak_value}')
                data[key] = bak_value
        else:
            print(f'bak_value {key}:{bak_value}')
            data[key] = bak_value
        

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
                    {"type": "text", "text": "告诉我图片中人物的以下特征，只要答案，格式为json字符串，图片是否有人脸（有人/没人） 用9个字以内概括图片三庭五眼的特征（答案要有三庭五眼四个字） 面部年龄（给出区间年龄）鼻长（鼻长适中/长鼻/短鼻） 脸型 嘴型 眼袋（答案要有眼袋两个个字） 眼型 鼻型 眼皮（双眼皮/单眼皮） 法令纹（有法令纹/无法令纹） 人中（答案要有人中两个字） 眉形 瞳色（答案要有瞳色两个字） 脖长（脖长适中/脖子短/脖子长） 肤色（粉一白/粉二白/粉三白/黄一白/黄二白/黄黑皮）直得分 曲得分 直曲总分（直得分-曲得分） 大量感得分 小量感得分 量感总分（大量感得分-小量感得） 面部立体度（总分十分）瞳距（毫米）对比度（对比度较强/对比度适中/对比度较弱）鼻子立体度（立体度高/立体度适中/立体度低）色相（中间表示0,最大值分别是-5和5，负数表示偏冷，正数表示偏暖）亮度（中间表示0,最大值分别是-5和5；负数表示暗沉，正数表示白皙）色度（中间表示0,最大值分别是-5和5；负数表示饱和度低，正数表示鲜艳）面部颜色对比度（10分制）四季色彩季型（净春型/暖春型/浅春型/浅夏型/冷夏型/柔夏型/柔秋型/暖秋型/深秋型/净冬型/冷冬型/深冬型）"},
                ],
            }
        ],
        
    )

    text = response.choices[0].message.content
    result = {}
    try:
        result = parse_face_json_data(text)
    except:
        print('parse_face_json_data exception')

    try:
        checkKey('图片是否有人', '是否有人', result, "没人")
        checkKey('三庭五眼特征', '三庭五眼', result, "适中")
        checkKey('年龄', None, result, "25-35")
        checkKey('脸型', None, result, "适中")
        checkKey('嘴型', None, result, "适中")
        checkKey('眼袋', None, result, "适中")
        checkKey('眼型', None, result, "适中")
        checkKey('鼻型', None, result, "适中")
        checkKey('眼皮', None, result, "适中")
        checkKey('法令纹', None, result, "适中")
        checkKey('人中', None, result, "适中")
        checkKey('眉形', None, result, "适中")
        checkKey('瞳色', None, result, "黑色")
        checkKey('脖长', None, result, "适中")
        checkKey('肤色', None, result, "白")
        checkKey('直得分', None, result, 7)
        checkKey('曲得分', None, result, 3)
        checkKey('直曲总分', None, result, 4)
        checkKey('大量感得分', '大量感', result, 6)
        checkKey('小量感得分', '小量感', result, 4)
        checkKey('量感总分', '量感', result, 2)
        checkKey('面部立体度', '量立体度', result, 8)
        checkKey('start_age', None, result, 25)
        checkKey('end_age', None, result, 35)
        checkKey('四季色彩季型', None, result, '暖春型')
        checkKey('面部颜色对比度', None, result, 6)
        result['动静得分'] = result['面部颜色对比度'] + result['面部立体度']
    except:
        print(f'Error {text}')

    return result

def GetFacePoint(detection_result, width, height):
    data = []
    face_landmarks_list = detection_result.face_landmarks
    if len(face_landmarks_list) == 0:
        return None
    
    face_landmarks = face_landmarks_list[0]
    for i in range(len(face_landmarks)):
      x = face_landmarks[i].x * width
      y = face_landmarks[i].y * height
      z = face_landmarks[i].z
      data.append({'id':i, 'x':round(x, 2), 'y':round(y, 2), 'z':round(z, 2)})
    
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
    final_data = {}
    final_data['face_figure'] = fire_ret
    page1 = {}
    p = GetFacePoint(mp_ret, width, height)
    if p == None:
        final_data['是否有标记点'] = '没有'
        return final_data
    else:
        final_data['是否有标记点'] = '有'
    final_data['raw_point'] = p
    pd = fire_ret['瞳距']
    p0 = p[34]
    p1 = p[130]
    p2 = p[133]
    p3 = p[362]
    p4 = p[359]
    p5 = p[356]
    page1['line_x_array'] = [p0['x'], p1['x'], p2['x'], p3['x'], p4['x'], p5['x']]
    tongju_pixel = distance(p[468]['x'], p[468]['y'], p[473]['x'], p[473]['y'])
    pd_cm = pd/10
    d0 = (p1['x'] - p0['x'])*(pd_cm)/tongju_pixel
    d1 = (p2['x'] - p1['x'])*(pd_cm)/tongju_pixel
    d2 = (p3['x'] - p2['x'])*(pd_cm)/tongju_pixel
    d3 = (p4['x'] - p3['x'])*(pd_cm)/tongju_pixel
    d4 = (p5['x'] - p4['x'])*(pd_cm)/tongju_pixel
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
    bi_jian = p[4]
    angel = calculate_angle((left_eye['x'], left_eye['y']),
                            (bi_jian['x'], bi_jian['y']),
                            (right_eye['x'], right_eye['y']))
    page3['left_eye'] = left_eye
    page3['right_eye'] = right_eye
    page3['bi_jian'] = bi_jian
    page3['angle'] = angel
    final_data['page3'] = page3

    return final_data
    