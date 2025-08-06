import requests

# 定义请求地址
url = "http://43.143.205.217:5000/cloth_url"

# 定义请求参数（JSON 格式）
data = {
    # "url": "http://43.143.205.217/imgs/girl1.jpg"
    "url": "https://oss.yz.zglvling.com/20250626164450518582485.jpg"
}

# 发送 POST 请求
response = requests.post(url, json=data)

# 打印响应结果
print("状态码:", response.status_code)
print("响应内容:", response.text)