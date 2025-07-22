import os
import re
import json
import requests
from bs4 import BeautifulSoup
# from utils.cleaner import clean_article_text

DATE="20250720"
ARTICLES_META_FILE = os.path.join("data", "fatchedNews", f"articles_{DATE}.json")
PARSED_OUTPUT_DIR = os.path.join("data", "parsed")
OUTPUT_DIR = os.path.join(PARSED_OUTPUT_DIR, f"articles_full_{DATE}")

def parse_articles(meta_file: str, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    articles = load_article_metadata(meta_file)

    for item in articles:
        url = item["link"]
        try:
            html = fetch_article_html(url)
            raw_text = extract_main_text(html)
            # cleaned_text = clean_article_text(raw_text)  # 광고/잡음 제거

            # 파일명: 기사 제목에서 특수문자/공백 제거 후 저장
            safe_title = re.sub(r'[^a-zA-Z0-9_\-]', '_', item["title"])[:50]
            file_name = f"{safe_title}.json"
            file_path = os.path.join(output_dir, file_name)

            article_data = {
                "title": item["title"],
                "link": url,
                "published": item["published"],
                "body": raw_text
            }
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(article_data, f, indent=2, ensure_ascii=False)

            print(f"[OK] Saved: {file_name}")
        except Exception as e:
            print(f"[FAIL] {item['title']}: {str(e)}")
            continue

    print(f"\n[RESULT] Parsed and saved {len(articles)} articles to directory {output_dir}")


# 기사 메타데이터(JSON) 파일을 로드
def load_article_metadata(meta_file: str) -> list:
    with open(meta_file, "r", encoding="utf-8") as f:
        return json.load(f)


# 기사 링크에 접속해 HTML 소스를 반환
def fetch_article_html(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.text


# BeautifulSoup으로 본문 추출
def extract_main_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    # Yahoo Finance 기사 본문의 주된 클래스 구조 (변경 가능성 있음)
    candidates = [
        {"name": "div", "attrs": {"class": "caas-body"}},
        {"name": "div", "attrs": {"class": "article-body"}},
    ]
    for candidate in candidates:
        tag = soup.find(candidate["name"], candidate["attrs"])
        if tag:
            return tag.get_text(separator="\n", strip=True)
    # 못 찾았을 경우, fallback: 전체 텍스트
    return soup.get_text(separator="\n", strip=True)



if __name__ == "__main__":
    parse_articles(ARTICLES_META_FILE, OUTPUT_DIR)