import requests
import xml.etree.ElementTree as ET
import hashlib
import json
import os
from datetime import datetime

RSS_URL = "https://finance.yahoo.com/news/rssindex"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}
SEEN_HASHES_FILE = "seen_hashes.json"

# 🧠 기사 링크 기반으로 고유 해시 생성
def hash_article(link: str) -> str:
    return hashlib.sha256(link.encode("utf-8")).hexdigest()

# 🧠 기존 수집한 해시 불러오기
def load_seen_hashes() -> set:
    if os.path.exists(SEEN_HASHES_FILE):
        with open(SEEN_HASHES_FILE, "r") as f:
            return set(json.load(f))
    return set()

# 🧠 새로운 해시 저장
def save_seen_hashes(hashes: set):
    with open(SEEN_HASHES_FILE, "w") as f:
        json.dump(list(hashes), f, indent=2)

# 🧠 기사 리스트 JSON 파일로 저장
def save_articles_to_json(articles: list):
    today = datetime.now().strftime("%Y%m%d")
    file_name = f"articles_{today}.json"
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
    print(f"[OK] Saved {len(articles)} articles to {file_name}")

# 🧠 RSS로부터 기사 수집
def fetch_rss_articles() -> list:
    try:
        response = requests.get(RSS_URL, headers=HEADERS)
        response.raise_for_status()
        response.encoding = "utf-8"
        root = ET.fromstring(response.text)

        articles = []
        for item in root.findall(".//item"):
            title = item.findtext("title")
            link = item.findtext("link")
            pub_date = item.findtext("pubDate")

            articles.append({
                "title": title,
                "link": link,
                "published": pub_date
            })
        return articles

    except requests.RequestException as e:
        print("[ERROR] HTTP 요청 실패:", str(e))
    except ET.ParseError as e:
        print("[ERROR] XML 파싱 실패:", str(e))
    return []

# 🧠 중복을 제거한 새 기사만 필터링
def filter_new_articles(articles: list, seen_hashes: set) -> tuple:
    new_articles = []
    new_hashes = set()

    for article in articles:
        article_hash = hash_article(article["link"])
        if article_hash in seen_hashes:
            continue
        new_articles.append(article)
        new_hashes.add(article_hash)

    return new_articles, new_hashes

# 🧠 전체 흐름 제어
def main():
    seen_hashes = load_seen_hashes()
    articles = fetch_rss_articles()

    if not articles:
        print("[INFO] No articles found or RSS fetch failed.")
        return

    new_articles, new_hashes = filter_new_articles(articles, seen_hashes)

    if new_articles:
        for a in new_articles:
            print(f"Title: {a['title']}")
            print(f"Link: {a['link']}")
            print(f"Published: {a['published']}")
            print("-" * 80)

        save_articles_to_json(new_articles)
        save_seen_hashes(seen_hashes.union(new_hashes))
    else:
        print("[INFO] No new articles to save.")

# 🔁 실행 진입점
if __name__ == "__main__":
    main()