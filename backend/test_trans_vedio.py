import requests

# 定义API的URL
baseUrl = "http://104.171.203.178:3141"   # 104.171.203.178

headers = {
    "Content-Type": "application/json"
}


def test_trans_vedio(download):
    # 定义请求体，确保参数名和类型正确
    data = {
        "youtube_url": "https://www.youtube.com/watch?v=uy8mOp84KzU"
    }

    # 发送POST请求
    response = requests.post(baseUrl+"/trans_vedio", json=data, headers=headers)
    # 打印响应状态码和内容
    print(f"Status Code: {response.status_code}")
    print(f"Response Content: {response.json()}")
    # 下载
    if download:
        response = response.json()
        download_url = baseUrl + response['file_link']
        response = requests.get(download_url, stream=True)
        response.raise_for_status()

        with open("GAoR9ji8D6A.mp4", 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)   
        

if __name__ == "__main__":
    test_trans_vedio()
    