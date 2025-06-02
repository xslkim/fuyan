import os
from volcenginesdkarkruntime import Ark

# 请确保您已将 API Key 存储在环境变量 ARK_API_KEY 中
# 初始化Ark客户端，从环境变量中读取您的API Key
client = Ark(
    # 此为默认路径，您可根据业务所在地域进行配置
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    # 从环境变量中获取您的 API Key。此为默认方式，您可根据需要进行修改
    # api_key=os.environ.get("ARK_API_KEY"),
    api_key='14fc0280-fc65-462d-ac2d-50178c0212e3'
)

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
                    {"type": "text", "text": "告诉我图片中人物的以下特征，只要答案，面部年龄 脸型 嘴型 眼袋 眼型 鼻型 法令纹 人中 眉形 直得分 曲得分 直曲总分（直得分-曲得分） 大量感得分 小量感得分 量感总分（大量感得分-小量感得） 面部立体度（总分十分）"},
                ],
            }
        ],
        
    )

    # text = '面部年龄:30-40岁\n脸型:圆脸\n嘴型:薄唇\n眼袋:无\n眼型:圆眼\n鼻型:直鼻\n法令纹:无\n人中:中等\n眉形:直眉\n直得分:7\n曲得分:3\n直曲总分:4\n大量感得分:5\n小量感得分:5\n量感总分:0\n面部立体度:6'
    text = response.choices[0].message.content
    result = {}

    try:
        lines = text.split('\n')
        for line in lines:
            key, value = line.split(':')
            key = key.strip()
            value = value.strip()
            
            # 尝试转换为整数（如果是得分类的字段）
            if key.endswith('得分') or key.endswith('总分') or key == '面部立体度':
                try:
                    value = int(value)
                except ValueError:
                    pass
            
            result[key] = value
    except:
        print(f'Error {text}')

    return result
    