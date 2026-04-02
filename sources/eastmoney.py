"""东方财富快讯 - A股盘中要闻、龙虎榜、资金流向"""
import time
import requests
from config import REQUEST_HEADERS, REQUEST_TIMEOUT, MAX_NEWS_PER_SOURCE


def fetch_eastmoney() -> list[dict]:
    """抓取东方财富快讯"""
    news_list = []
    try:
        url = "https://np-listapi.eastmoney.com/comm/web/getNewsByColumns"
        params = {
            "column": "74",
            "pageSize": str(MAX_NEWS_PER_SOURCE),
            "pageIndex": "1",
            "client": "web",
            "biz": "web_724",
            "req_trace": str(int(time.time() * 1000)),
        }
        resp = requests.get(url, params=params, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()

        items = (data.get("data") or {}).get("list", []) or []
        for item in items:
            title = item.get("title", "").strip()
            if not title:
                # 有些快讯没 title，用 summary
                title = item.get("summary", "").strip()
            if not title:
                continue
            content = item.get("summary", "") or item.get("digest", "") or title
            show_time = item.get("showTime", "") or item.get("showtime", "")

            news_list.append({
                "title": title,
                "content": content,
                "source": "东方财富",
                "url": item.get("uniqueUrl", "") or item.get("url", ""),
                "pub_time": show_time,
            })
    except Exception as e:
        print(f"[东方财富] 抓取失败: {e}")
    return news_list
