import requests
from bs4 import BeautifulSoup
import json
import time
import argparse
from datetime import date, datetime, timedelta
from pathlib import Path

DATA_DIR = Path("data")
DAILY_DIR = DATA_DIR / "daily"
WEEKLY_DIR = DATA_DIR / "weekly"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

MOVIEARENA_BASE = "https://moviearenatw.com"


def ensure_dirs():
    DAILY_DIR.mkdir(parents=True, exist_ok=True)
    WEEKLY_DIR.mkdir(parents=True, exist_ok=True)


def save_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("  OK:" + str(path))


def load_json(path):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def parse_delta(s):
    s = s.strip().replace("–", "").replace("-", "").replace("%", "")
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def compute_summary(films):
    if not films:
        return {}
    total_seats = sum(f["seats"] for f in films)
    total_att = sum(f["attendance"] for f in films)
    avg_rate = round(total_att / total_seats * 100, 2) if total_seats else 0
    return {
        "total_films": len(films),
        "total_seats": total_seats,
        "total_attendance": total_att,
        "avg_rate": avg_rate,
        "top_film": films[0]["title"] if films else None,
        "top_rate": films[0]["rate"] if films else None,
    }


def parse_table(html, target_date):
    soup = BeautifulSoup(html, "html.parser")
    films = []
    table = soup.find("table")
    if not table:
        print("  找不到表格")
        return {}
    rows = table.find_all("tr")
    for row in rows[1:]:
        cols = [td.get_text(strip=True) for td in row.find_all("td")]
        if len(cols) < 6:
            continue
        try:
            film = {
                "rank": int(cols[0]),
                "title": cols[1],
                "seats": int(cols[2].replace(",", "")),
                "attendance": int(cols[3].replace(",", "")),
                "rate": float(cols[4]),
                "d_minus_1": parse_delta(cols[5]),
                "d_minus_7": parse_delta(cols[6]) if len(cols) > 6 else None,
            }
            films.append(film)
        except Exception:
            continue
    return {
        "date": target_date.isoformat(),
        "source": "MovieArena",
        "films": films,
        "summary": compute_summary(films),
    }


def scrape_daily(target_date):
    date_str = target_date.strftime("%Y-%m-%d")
    out_path = DAILY_DIR / f"{date_str}.json"
    if out_path.exists():
        print(f"  {date_str} 已有資料，跳過")
        return load_json(out_path)
    print(f"正在爬取：{date_str}")
    encoded = requests.utils.quote(f"電影上座率日表-{date_str}", safe="")
    url = f"{MOVIEARENA_BASE}/{encoded}/"
    print(f"  網址：{url}")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        print(f"  失敗：{e}")
        return None
    data = parse_table(resp.text, target_date)
    if data and data.get("films"):
        save_json(out_path, data)
        return data
    print("  無資料")
    return None


def update_index():
    daily_files = sorted(DAILY_DIR.glob("*.json"), reverse=True)
    index = {
        "updated_at": datetime.now().isoformat(),
        "daily": {
            "latest": daily_files[0].stem if daily_files else None,
            "count": len(daily_files),
            "files": [f.stem for f in daily_files[:30]],
        }
    }
    if daily_files:
        latest = load_json(daily_files[0])
        index["latest_summary"] = latest.get("summary", {})
        index["latest_date"] = latest.get("date", "")
    save_json(DATA_DIR / "index.json", index)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str)
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()
    ensure_dirs()
    if args.all:
        dates = [date.today() - timedelta(days=i) for i in range(30)]
        print(f"開始爬取最近 {len(dates)} 天...")
    elif args.date:
        dates = [datetime.strptime(args.date, "%Y-%m-%d").date()]
    else:
        dates = [date.today()]
    success = 0
    for d in dates:
        result = scrape_daily(d)
        if result:
            success += 1
        time.sleep(2)
    update_index()
    print(f"完成！成功 {success}/{len(dates)} 天")


if __name__ == "__main__":
    main()
