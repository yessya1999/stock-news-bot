"""Server酱微信推送模块"""
import datetime
import requests
import config


def _send(title: str, desp: str) -> bool:
    """通过 Server酱 发送消息（支持 Markdown）"""
    if not config.SERVERCHAN_SENDKEY:
        print("[Server酱] 未配置 SendKey，跳过推送")
        return False

    url = f"https://sctapi.ftqq.com/{config.SERVERCHAN_SENDKEY}.send"
    payload = {
        "title": title[:32],
        "desp": desp,
    }

    try:
        resp = requests.post(url, data=payload, timeout=10)
        result = resp.json()
        if result.get("code") == 0:
            print(f"[Server酱] 推送成功: {title}")
            return True
        else:
            print(f"[Server酱] 推送失败: {result}")
            return False
    except Exception as e:
        print(f"[Server酱] 推送异常: {e}")
        return False


def _direction_icon(direction: str) -> str:
    if direction == "利好":
        return "🔴"
    elif direction == "利空":
        return "🟢"
    return "⚪"


def _format_news_item(idx: int, n: dict) -> str:
    """格式化单条新闻"""
    icon = _direction_icon(n.get("direction", "中性"))
    direction = n.get("direction", "中性")
    summary = n.get("summary", n.get("title", ""))
    analysis = n.get("analysis", "")
    sectors = n.get("sectors", "")
    score = n.get("score", 0)
    source = n.get("source", "")

    item = f"### {idx}. {icon} [{direction}] {summary}\n"
    if analysis:
        item += f"> 💡 {analysis}\n"
    item += f"> 📊 影响板块：{sectors} | 评分：**{score}/10** | 来源：{source}\n\n"
    return item


def send_daily_digest(analyzed_news: list[dict], period: str = "早报") -> bool:
    """发送定时摘要"""
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    weekday = weekdays[now.weekday()]

    title = f"财经{period} | {date_str}（{weekday}）"

    # 按市场分组
    a_stock = [n for n in analyzed_news if n.get("market") in ("A股", "两者")]
    us_stock = [n for n in analyzed_news if n.get("market") in ("美股", "两者")]
    political = [n for n in analyzed_news if n.get("source") in ("新华社", "中国政府网", "央行")]

    a_stock.sort(key=lambda x: x.get("score", 0), reverse=True)
    us_stock.sort(key=lambda x: x.get("score", 0), reverse=True)

    md = f"# 📈 财经{period} | {date_str}（{weekday}）\n"

    if a_stock:
        md += "\n## 🇨🇳 A股关注\n"
        for i, n in enumerate(a_stock[:6], 1):
            md += _format_news_item(i, n)

    if us_stock:
        md += "\n## 🇺🇸 美股/全球\n"
        for i, n in enumerate(us_stock[:4], 1):
            md += _format_news_item(i, n)

    if political:
        md += "\n## 🏛 政治热点\n"
        for i, n in enumerate(political[:3], 1):
            md += _format_news_item(i, n)

    md += "\n---\n🤖 stock-news-bot 自动生成 | 数据仅供参考，不构成投资建议"

    return _send(title, md)


def send_breaking_news(news: dict) -> bool:
    """发送突发快讯"""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    direction = news.get("direction", "中性")
    icon = _direction_icon(direction)

    title = f"⚡突发 | {news.get('summary', news.get('title', ''))[:20]}"

    md = f"""# ⚡ 突发快讯 | {now}

**{news.get('summary', news.get('title', ''))}**

- 影响评分：**{news.get('score', 0)}/10**
- 方向：{icon} **{direction}**
- 重点板块：{news.get('sectors', '')}
- 来源：{news.get('source', '')}

---
🤖 stock-news-bot 自动推送 | 不构成投资建议"""

    return _send(title, md)
