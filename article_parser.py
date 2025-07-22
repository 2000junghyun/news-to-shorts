import json
import os
import requests
from bs4 import BeautifulSoup
from utils.cleaner import clean_article_text  # 정제 함수는 utils/cleaner.py에 구현

# 경로 및 파일명 설정
ARTICLES_META_FILE = "articles_YYYYMMDD.json"   # 날짜별로 자동 생성된 메타데이터 파일명
PARSED_OUTPUT_DIR = "data/parsed"
OUTPUT_FILE = os.path.join(PARSED_OUTPUT_DIR, "articles_full_YYYYMMDD.json")

def load_article_metadata(meta_file: str) -> list:
    """기사 메타데이터(JSON) 파일을 로드"""
    with open(meta_file, "r", encoding="utf-8") as f:
        return json.load(f)

def fetch_article_html(url: str) -> str:
    """기사 링크에 접속해 HTML 소스를 반환"""
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.text

def extract_main_text(html: str) -> str:
    """BeautifulSoup으로 본문 추출"""
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

def parse_and_save_articles(meta_file: str, output_file: str):
    """전체 기사 본문 파싱 → JSON 저장"""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    articles = load_article_metadata(meta_file)
    parsed_articles = []

    for item in articles:
        url = item["link"]
        try:
            html = fetch_article_html(url)
            raw_text = extract_main_text(html)
            cleaned_text = clean_article_text(raw_text)  # 광고/잡음 제거 (utils.cleaner)
            parsed_articles.append({
                "title": item["title"],
                "link": url,
                "published": item["published"],
                "body": cleaned_text
            })
            print(f"[OK] {item['title']}")
        except Exception as e:
            print(f"[FAIL] {item['title']}: {str(e)}")
            continue

    # 결과 저장
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(parsed_articles, f, indent=2, ensure_ascii=False)
    print(f"\n[RESULT] Parsed {len(parsed_articles)} articles. Saved to {output_file}")

if __name__ == "__main__":
    parse_and_save_articles(ARTICLES_META_FILE, OUTPUT_FILE)
