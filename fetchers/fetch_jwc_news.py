"""
抓取西南交通大学教务网新闻列表；不可达时写入空数据，让整份简报继续生成。
"""
import json
import random
import re
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup


def fetch_jwc_news():
    time.sleep(random.uniform(1, 3))
    url = "https://jwc.swjtu.edu.cn/vatuu/WebAction?setAction=newsList"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }

    resp = requests.get(url, headers=headers, timeout=10)
    resp.encoding = resp.apparent_encoding
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    results = []
    news_links = soup.find_all("a", href=lambda h: h and "newsDetail" in h)
    for link in news_links:
        title = link.get_text(strip=True)
        if not title or len(title) < 4:
            continue
        href = link["href"]
        full_url = href if href.startswith("http") else "https://jwc.swjtu.edu.cn" + href
        container = link.find_parent(["div", "li", "dd"]) or link.parent
        container_text = container.get_text(" ", strip=True) if container else ""
        date_match = re.search(r"\d{4}-\d{2}-\d{2}", container_text)
        results.append({
            "title": title,
            "date": date_match.group() if date_match else "",
            "url": full_url,
        })

    seen = set()
    return [item for item in results if not (item["title"] in seen or seen.add(item["title"]))]


def save_news(news, warning=None):
    output = {
        "fetched_at": datetime.now().isoformat(),
        "source": "jwc_swjtu",
        "items": news,
    }
    if warning:
        output["warning"] = warning
    with open("jwc_news.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    try:
        news = fetch_jwc_news()
        print(f"抓取到 {len(news)} 条教务网通知")
        save_news(news)
    except requests.RequestException as e:
        print(f"⚠️ 教务网暂时无法访问，跳过本次教务通知：{e}")
        news = []
        save_news(news, "教务网暂时无法访问，本次简报未包含教务通知")

    print(f"已保存到 jwc_news.json（共 {len(news)} 条）")
