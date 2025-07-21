import requests
import xml.etree.ElementTree as ET

rss_url = "https://finance.yahoo.com/news/rssindex"

# 봇 요청 차단 우회를 위해 User-Agent 설정
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36"
}

try:
    response = requests.get(rss_url, headers=headers)
    response.raise_for_status()
    response.encoding = 'utf-8'

    if not response.text.strip().startswith("<?xml") and "<rss" not in response.text:
        print("[ERROR] 응답이 XML 형식이 아닙니다.")
        print("응답 내용 앞부분:", response.text[:200])
    else:
        try:
            root = ET.fromstring(response.text)
            for item in root.findall(".//item"):
                title = item.findtext("title")
                link = item.findtext("link")
                pubDate = item.findtext("pubDate")
                print(f"Title: {title}")
                print(f"Link: {link}")
                print(f"Published: {pubDate}")
                print("-" * 80)
        except ET.ParseError as e:
            print("[ERROR] XML 파싱 실패:", str(e))
            print("응답 내용 앞부분:", response.text[:300])
except requests.RequestException as e:
    print("[ERROR] HTTP 요청 실패:", str(e))