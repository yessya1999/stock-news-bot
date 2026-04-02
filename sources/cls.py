"""财联社电报 - A股实时快讯"""
import time
import requests
from config import REQUEST_TIMEOUT, MAX_NEWS_PER_SOURCE


def fetch_cls() -> list[dict]:
    """抓取财联社电报快讯"""
    news_list = []
    try:
        # 财联社电报 API
        url = "https://www.cls.cn/nodeapi/telegraphList"
        params = {
            "app": "CailianpressWeb",
            "os": "web",
            "sv": "7.7.5",
            "rn": str(MAX_NEWS_PER_SOURCE),
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.cls.cn/",
            "Accept": "application/json, text/plain, */*",
        }
        resp = requests.get(url, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()

        rolls = data.get("data", {}).get("roll_data", [])
        for item in rolls:
            content = item.get("content", "").strip()
            if not content:
                continue
            title = item.get("title", "") or content[:60]
            ctime = item.get("ctime", 0)
            pub_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(ctime)) if ctime else ""

            news_list.append({
                "title": title,
                "content": content,
                "source": "财联社",
                "url": f"https://www.cls.cn/detail/{item.get('id', '')}",
                "pub_time": pub_time,
            })
    except Exception as e:
        print(f"[财联社] 抓取失败: {e}")
    return news_list
