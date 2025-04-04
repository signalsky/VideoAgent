import requests

# 定义API的URL
url = "http://127.0.0.1:3141/trans_vedio"

headers = {
    "Content-Type": "application/json"
}


def test_trans_vedio():
    # 定义请求体，确保参数名和类型正确
    data = {
        "youtube_url": "https://www.youtube.com/watch?v=imJI8OwpLt8"
    }

    # 发送POST请求
    response = requests.post(url, json=data, headers=headers)

    # 打印响应状态码和内容
    print(f"Status Code: {response.status_code}")
    print(f"Response Content: {response.json()}")
        

if __name__ == "__main__":
    test_trans_vedio()
    