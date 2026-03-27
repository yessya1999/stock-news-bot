"""PushPlus 微信推送模块"""
import datetime
import requests
import config


def _send(title: str, content: str, template: str = "html") -> bool:
    """发送 PushPlus 消息"""
    if not config.PUSHPLUS_TOKEN:
        print("[PushPlus] 未配置 Token，跳过推送")
        return False

    payload = {
        "token": config.PUSHPLUS_TOKEN,
        "title": title,
        "content": content,
        "template": template,
    }
    try:
        resp = requests.post(config.PUSHPLUS_URL, json=payload, timeout=10)
        result = resp.json()
        if result.get("code") == 200:
            print(f"[PushPlus] 推送成功: {title}")
            return True
        else:
            print(f"[PushPlus] 推送失败: {result}")
            return False
    except Exception as e:
        print(f"[PushPlus] 推送异常: {e}")
        return False


def _direction_color(direction: str) -> str:
    """影响方向的颜色"""
    if direction == "利好":
        return "#e74c3c"  # 红色
    elif direction == "利空":
        return "#27ae60"  # 绿色
    return "#7f8c8d"  # 灰色


def _direction_emoji(direction: str) -> str:
    if direction == "利好":
        return "&#x1F534;"  # 红圈
    elif direction == "利空":
        return "&#x1F7E2;"  # 绿圈
    return "&#x26AA;"  # 白圈


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

    # 按评分排序
    a_stock.sort(key=lambda x: x.get("score", 0), reverse=True)
    us_stock.sort(key=lambda x: x.get("score", 0), reverse=True)

    html = f"""
<h2 style="color:#2c3e50;border-bottom:2px solid #3498db;padding-bottom:8px;">
    &#x1F4C8; 财经{period} | {date_str}（{weekday}）
</h2>
"""

    if a_stock:
        html += '<h3 style="color:#e74c3c;">&#x1F1E8;&#x1F1F3; A股关注</h3>'
        for i, n in enumerate(a_stock[:8], 1):
            color = _direction_color(n.get("direction", "中性"))
            emoji = _direction_emoji(n.get("direction", "中性"))
            html += f"""
<p style="margin:6px 0;">
    {i}. {emoji} <b style="color:{color};">[{n.get('direction','中性')}]</b>
    {n.get('summary', n.get('title',''))}
    <span style="color:#95a5a6;">&#x2192; {n.get('sectors','')}</span>
    <b style="color:#e67e22;"> | {n.get('score',0)}/10</b>
</p>"""

    if us_stock:
        html += '<h3 style="color:#2980b9;">&#x1F1FA;&#x1F1F8; 美股/全球</h3>'
        for i, n in enumerate(us_stock[:5], 1):
            color = _direction_color(n.get("direction", "中性"))
            emoji = _direction_emoji(n.get("direction", "中性"))
            html += f"""
<p style="margin:6px 0;">
    {i}. {emoji} <b style="color:{color};">[{n.get('direction','中性')}]</b>
    {n.get('summary', n.get('title',''))}
    <span style="color:#95a5a6;">&#x2192; {n.get('sectors','')}</span>
    <b style="color:#e67e22;"> | {n.get('score',0)}/10</b>
</p>"""

    if political:
        html += '<h3 style="color:#8e44ad;">&#x1F3DB; 政治热点</h3>'
        for i, n in enumerate(political[:3], 1):
            html += f"""
<p style="margin:6px 0;">
    {i}. {n.get('summary', n.get('title',''))}
    <span style="color:#95a5a6;">&#x2192; {n.get('sectors','')}</span>
    <b style="color:#e67e22;"> | {n.get('score',0)}/10</b>
</p>"""

    html += f"""
<hr style="border:none;border-top:1px solid #bdc3c7;margin:12px 0;">
<p style="color:#95a5a6;font-size:12px;">
    &#x1F916; 由 stock-news-bot 自动生成 | 数据仅供参考，不构成投资建议
</p>"""

    return _send(title, html)


def send_breaking_news(news: dict) -> bool:
    """发送突发快讯"""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    direction = news.get("direction", "中性")
    color = _direction_color(direction)

    title = f"突发 | {news.get('summary', news.get('title', ''))[:30]}"

    html = f"""
<div style="border-left:4px solid {color};padding:10px;background:#fdf2e9;">
    <h2 style="color:{color};margin:0 0 8px 0;">
        &#x26A1; 突发快讯 | {now}
    </h2>
    <p style="font-size:16px;font-weight:bold;margin:8px 0;">
        {news.get('summary', news.get('title', ''))}
    </p>
    <p style="margin:6px 0;">
        影响评分：<b style="color:#e67e22;">{news.get('score', 0)}/10</b> |
        <b style="color:{color};">{direction}</b> |
        重点板块：{news.get('sectors', '')}
    </p>
    <p style="margin:6px 0;color:#7f8c8d;">
        来源：{news.get('source', '')}
    </p>
</div>
<p style="color:#95a5a6;font-size:12px;margin-top:8px;">
    &#x1F916; stock-news-bot 自动推送 | 不构成投资建议
</p>"""

    return _send(title, html)
