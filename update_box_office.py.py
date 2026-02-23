import json
import os
from datetime import datetime

# 這個程式碼會幫你產生今天的日期和模擬數據
def fetch_data():
    today = datetime.now().strftime("%Y-%m-%d")
    data = {
        "date": today,
        "total_movies": "45",
        "occupancy": "30.5%",
        "daily_viewers": "45,000",
        "top_movie": "最新熱門電影",
        "market_trend": "自動化更新測試：數據已成功同步。"
    }
    return data

def update_json():
    os.makedirs('data', exist_ok=True)
    new_data = fetch_data()
    with open('data/index.json', 'w', encoding='utf-8') as f:
        json.dump(new_data, f, ensure_ascii=False, indent=4)
    print(f"成功更新數據日期：{new_data['date']}")

if __name__ == "__main__":
    update_json()