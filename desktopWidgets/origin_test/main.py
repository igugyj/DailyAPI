import requests
import json

api_dict = {
    "bilibili": "/bilibili",
    "tieba": "/tieba",
    "zhihu": "/zhihu",
    "weibo": "/weibo",
}

for key, value in api_dict.items():
    url = "http://127.0.0.1:6688" + value
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        with open(key + ".json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
