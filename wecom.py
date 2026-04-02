"""企业微信应用推送模块"""
import datetime
import time
import requests
import config

# access_token 缓存
_token_cache = {"token": "", "expires_at": 0}


def _get_access_token() -> str:
    """获取企业微信 access_token（自动缓存，2小时有效）"""
    now = time.time()
    if _token_cache["token"] and _token_cache["expires_at"] > now + 60:
        return _token_cache["token"]

    url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
    params = {
        "corpid": config.WECOM_CORP_ID,
        "corpsecret": config.WECOM_CORP_SECRET,
    }
    resp = requests.get(url, params=params, timeout=10)
    data = resp.json()

    if data.get("errcode") != 0:
        raise RuntimeError(f"获取 access_token 失败: {data}")

    _token_cache["token"] = data["access_token"]
    _token_cache["expires_at"] = now + data.get("expires_in", 7200)
    return _token_cache["token"]


def _send_markdown(title: str, content: str) -> bool:
    """通过企业微信应用发送 Markdown 消息"""
    if not config.WECOM_CORP_ID or not config.WECOM_CORP_SECRET:
        print("[企业微信] 未配置 CorpID/Secret，跳过推送")
        return False

    try:
        token = _get_access_token()
    except Exception as e:
        print(f"[企业微信] 获取 token 失败: {e}")
        return False

    url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={token}"
    payload = {
        "touser": config.WECOM_TO_USER,
        "msgtype": "markdown",
        "agentid": int(config.WECOM_AGENT_ID),
        "markdown": {
            "content": content,
        },
    }

    try:
        resp = requests.post(url, json=payload, timeout=10)
        result = resp.json()
        if result.get("errcode") == 0:
            print(f"[企业微信] 推送成功: {title}")
            return True
        else:
            print(f"[企业微信] 推送失败: {result}")
            return False
    except Exception as e:
        print(f"[企业微信] 推送异常: {e}")
        return False


def _direction_icon(direction: str) -> str:
    if direction == "利好":
        return "🔴"
    elif direction == "利空":
        return "🟢"
    return "⚪"


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

    # 企业微信 Markdown 格式
    md = f"# 📈 财经{period} | {date_str}（{weekday}）\n"

    if a_stock:
        md += "\n## 🇨🇳 A股关注\n"
        for i, n in enumerate(a_stock[:8], 1):
            icon = _direction_icon(n.get("direction", "中性"))
            direction = n.get("direction", "中性")
            summary = n.get("summary", n.get("title", ""))
            sectors = n.get("sectors", "")
            score = n.get("score", 0)
            md += f"> {i}. {icon} **[{direction}]** {summary}\n> → {sectors} | <font color=\"warning\">{score}/10</font>\n"

    if us_stock:
        md += "\n## 🇺🇸 美股/全球\n"
        for i, n in enumerate(us_stock[:5], 1):
            icon = _direction_icon(n.get("direction", "中性"))
            direction = n.get("direction", "中性")
            summary = n.get("summary", n.get("title", ""))
            sectors = n.get("sectors", "")
            score = n.get("score", 0)
            md += f"> {i}. {icon} **[{direction}]** {summary}\n> → {sectors} | <font color=\"warning\">{score}/10</font>\n"

    if political:
        md += "\n## 🏛 政治热点\n"
        for i, n in enumerate(political[:3], 1):
            summary = n.get("summary", n.get("title", ""))
            sectors = n.get("sectors", "")
            score = n.get("score", 0)
            md += f"> {i}. {summary}\n> → {sectors} | <font color=\"warning\">{score}/10</font>\n"

    md += "\n---\n🤖 stock-news-bot 自动生成 | 数据仅供参考，不构成投资建议"

    return _send_markdown(title, md)


def send_breaking_news(news: dict) -> bool:
    """发送突发快讯"""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    direction = news.get("direction", "中性")
    icon = _direction_icon(direction)

    title = f"突发 | {news.get('summary', news.get('title', ''))[:30]}"

    color = "warning" if direction == "利好" else ("info" if direction == "利空" else "comment")

    md = f"""# ⚡ 突发快讯 | {now}

**{news.get('summary', news.get('title', ''))}**

> 影响评分：<font color=\"warning\">{news.get('score', 0)}/10</font>
> 方向：{icon} <font color=\"{color}\">{direction}</font>
> 重点板块：{news.get('sectors', '')}
> 来源：{news.get('source', '')}

---
🤖 stock-news-bot 自动推送 | 不构成投资建议"""

    return _send_markdown(title, md)
