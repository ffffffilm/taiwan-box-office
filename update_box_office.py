import json
import os
from datetime import datetime

def update_box_office():
    # 1. 取得執行當下的正確日期
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 2. 這裡可以加入自動校正清單 (解決你說的國別錯誤問題)
    # 以後只要在這裡增加片名，機器人就會自動正名，不用去改 JSON
    CORRECT_DATA = {
        "雙囍": {"country": "中華民國", "type": "國片"},
        "其他國片A": {"country": "中華民國", "type": "國片"}
    }

    # 模擬抓取到的原始數據 (未來可替換為爬蟲程式碼)
    raw_movie_title = "雙囍" 
    
    # 3. 自動判定邏輯
    movie_info = CORRECT_DATA.get(raw_movie_title, {"country": "未知", "type": "其他"})

    new_data = {
        "date": today,
        "total_movies": "52", # 這裡之後可以改成爬蟲抓到的數量
        "top_movie": raw_movie_title,
        "country": movie_info["country"],
        "market_trend": f"目前熱門：{raw_movie_title} ({movie_info['type']})，數據已自動校正。"
    }

    # 4. 存檔並推送
    file_path = 'data/index.json'
    os.makedirs('data', exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    update_box_office()