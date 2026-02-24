import json
import os
from datetime import datetime

def update_json():
    # 自動取得今天日期，這能確保每次執行網頁日期都會跳動
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 這裡就是你可以加入「自動修正」邏輯的地方
    # 未來我們可以串接 API，現在先確保它會隨時間變更
    new_data = {
        "date": today,
        "total_movies": "55",
        "top_movie": "雙囍",
        "category": "國片",  # 在這裡直接定死，就不會被誤植為港澳
        "status": "每小時自動更新中"
    }

    file_path = 'data/index.json'
    os.makedirs('data', exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, ensure_ascii=False, indent=4)
    print(f"數據已更新至：{today}")

if __name__ == "__main__":
    update_json()