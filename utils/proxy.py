import os
import requests
from flask import Flask, request

app = Flask(__name__)

PROXY_URL = os.environ.get('http_proxy')  # set your proxy URL here

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    url = f'https://api.openai.com/v1/chat/completions/{path}'
    headers = {
        'Authorization': request.headers.get('Authorization'),
        'Content-Type': 'application/json',
        'Host': 'api.openai.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive'
    }
    data = request.get_data()
    response = requests.request(
        method=request.method,
        url=url,
        headers=headers,
        data=data,
        proxies={'http': PROXY_URL, 'https': PROXY_URL} if PROXY_URL else None,
        timeout=360
    )
    return response.content, response.status_code, response.headers.items()

if __name__ == '__main__':
    app.run(port=5000)
