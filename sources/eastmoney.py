"""东方财富快讯 - A股盘中要闻、龙虎榜、资金流向"""
import requests
from config import REQUEST_HEADERS, REQUEST_TIMEOUT, MAX_NEWS_PER_SOURCE


def fetch_eastmoney() -> list[dict]:
    """抓取东方财富快讯"""
    news_list = []
    try:
        # 东方财富财经快讯 API
        url = "https://np-listapi.eastmoney.com/comm/web/getNewsByColumns"
        params = {
            "columns": "74",  # 财经快讯
            "pageSize": str(MAX_NEWS_PER_SOURCE),
            "pageIndex": "1",
            "client": "web",
        }
        resp = requests.get(url, params=params, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()

        items = data.get("data", {}).get("list", []) or []
        for item in items:
            title = item.get("title", "").strip()
            if not title:
                continue
            content = item.get("digest", "") or item.get("content", "") or title

            news_list.append({
                "title": title,
                "content": content,
                "source": "东方财富",
                "url": item.get("url", "") or f"https://finance.eastmoney.com/a/{item.get('art_code', '')}.html",
                "pub_time": item.get("showtime", ""),
            })
    except Exception as e:
        print(f"[东方财富] 抓取失败: {e}")

    # 备用方案：直接抓取快讯页
    if not news_list:
        try:
            from bs4 import BeautifulSoup
            resp = requests.get(
                "https://kuaixun.eastmoney.com/",
                headers=REQUEST_HEADERS,
                timeout=REQUEST_TIMEOUT,
            )
            resp.encoding = "utf-8"
            soup = BeautifulSoup(resp.text, "lxml")
            for li in soup.select(".news_list li")[:MAX_NEWS_PER_SOURCE]:
                a_tag = li.select_one("a")
                if not a_tag:
                    continue
                news_list.append({
                    "title": a_tag.get_text(strip=True),
                    "content": a_tag.get_text(strip=True),
                    "source": "东方财富",
                    "url": a_tag.get("href", ""),
                    "pub_time": "",
                })
        except Exception:
            pass
    return news_list
