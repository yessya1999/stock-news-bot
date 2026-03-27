"""华尔街见闻 - 全球宏观、美联储、中美经济"""
import time
import requests
from config import REQUEST_TIMEOUT, MAX_NEWS_PER_SOURCE


def fetch_wallstreetcn() -> list[dict]:
    """抓取华尔街见闻快讯"""
    news_list = []
    try:
        url = "https://api-one-wscn.awtmt.com/apiv1/content/lives"
        params = {
            "channel": "global-channel",
            "limit": str(MAX_NEWS_PER_SOURCE),
        }
        headers = {"Accept": "application/json"}
        resp = requests.get(url, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()

        items = data.get("data", {}).get("items", [])
        for item in items:
            content = item.get("content_text", "").strip()
            if not content:
                content = item.get("title", "").strip()
            if not content:
                continue
            title = item.get("title", "") or content[:60]
            display_time = item.get("display_time", 0)
            pub_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(display_time)) if display_time else ""

            news_list.append({
                "title": title,
                "content": content,
                "source": "华尔街见闻",
                "url": f"https://wallstreetcn.com/live/{item.get('id', '')}",
                "pub_time": pub_time,
            })
    except Exception as e:
        print(f"[华尔街见闻] 抓取失败: {e}")
    return news_list
