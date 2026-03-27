"""新浪财经要闻 - 国内财经综合"""
import requests
from bs4 import BeautifulSoup
from config import REQUEST_HEADERS, REQUEST_TIMEOUT, MAX_NEWS_PER_SOURCE


def fetch_sina_finance() -> list[dict]:
    """抓取新浪财经要闻"""
    news_list = []
    try:
        # 新浪财经滚动新闻 API
        url = "https://feed.mix.sina.com.cn/api/roll/get"
        params = {
            "pageid": "153",
            "lid": "2516",
            "k": "",
            "num": str(MAX_NEWS_PER_SOURCE),
            "page": "1",
        }
        resp = requests.get(url, params=params, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()

        items = data.get("result", {}).get("data", [])
        for item in items:
            title = item.get("title", "").strip()
            if not title:
                continue
            # 提取摘要
            intro = item.get("intro", "") or title
            pub_time = item.get("ctime", "")

            news_list.append({
                "title": title,
                "content": intro,
                "source": "新浪财经",
                "url": item.get("url", ""),
                "pub_time": pub_time,
            })
    except Exception as e:
        print(f"[新浪财经] 抓取失败: {e}")

    # 备用：RSS 方式
    if not news_list:
        try:
            import feedparser
            feed = feedparser.parse("https://finance.sina.com.cn/roll/index.d.html?cid=56588&page=1")
            for entry in feed.entries[:MAX_NEWS_PER_SOURCE]:
                news_list.append({
                    "title": entry.get("title", ""),
                    "content": entry.get("summary", entry.get("title", "")),
                    "source": "新浪财经",
                    "url": entry.get("link", ""),
                    "pub_time": entry.get("published", ""),
                })
        except Exception:
            pass
    return news_list
