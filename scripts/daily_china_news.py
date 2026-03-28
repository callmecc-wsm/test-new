#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每晚抓取中文即时新闻 RSS，按简单启发式选出 3 条较「有意思」的条目并输出。

定时任务（cron，按中国时区每天 22:10）示例，请先 chmod +x 本脚本：

  crontab -e

  添加一行（把 /workspace 换成你本机仓库路径）：

  10 22 * * * TZ=Asia/Shanghai /usr/bin/python3 /workspace/scripts/daily_china_news.py >> /tmp/china_news.log 2>&1

可选环境变量：
  CHINA_NEWS_RSS   覆盖默认 RSS 地址
  SKIP_NOTIFY      若设为 1 则不发桌面通知（仅打印到终端）
"""

from __future__ import annotations

import email.utils
import os
import re
import subprocess
import sys
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Iterable

# 默认：中新网即时新闻 RSS（UTF-8，国内可访问性较好）
DEFAULT_RSS = "https://www.chinanews.com.cn/rss/scroll-news.xml"

# 明显负面/突发灾难类标题，降低「有意思」权重（仍可作为兜底，尽量不选）
NEGATIVE_PATTERNS = re.compile(
    r"着火|火灾|爆炸|地震|坍塌|车祸|遇难|死亡|枪击|袭击|塌方|泥石流|"
    r"事故|明火|受伤|失联|坠机|沉船|暴恐|抢劫|杀害"
)

# 偏「可读/有意思」的主题词（科技、文化、社会趣闻等），提高权重
POSITIVE_HINTS = re.compile(
    r"科技|AI|人工智能|机器人|创新|文化|非遗|民俗|铁路|隧道|航天|"
    r"发现|探秘|亮相|发布|出海|论坛|东西问|人物|春潮|消费|乡村|生态|"
    r"最美|超级工程|基因库|首发"
)

# 中新网 RSS 的 pubDate 示例: Sat, 28 Mar 2026 21:53:12 +0800
RFC2822_TZ = timezone(timedelta(hours=8))


@dataclass
class NewsItem:
    title: str
    link: str
    description: str
    pub_date: datetime | None

    def score(self) -> float:
        text = f"{self.title}\n{self.description}"
        s = 0.0
        if POSITIVE_HINTS.search(text):
            s += 3.0
        if NEGATIVE_PATTERNS.search(text):
            s -= 5.0
        # 描述稍长通常信息更丰富
        if len(self.description.strip()) > 80:
            s += 0.5
        return s


def _parse_pub_date(raw: str | None) -> datetime | None:
    if not raw:
        return None
    raw = raw.strip()
    try:
        tup = email.utils.parsedate_tz(raw)
        if tup is None:
            return None
        ts = email.utils.mktime_tz(tup)
        return datetime.fromtimestamp(ts, tz=timezone.utc)
    except Exception:
        return None


def _local_today_bounds() -> tuple[datetime, datetime]:
    """按 TZ 或本机本地时区，取「今天」0 点与次日 0 点（用于过滤「今天」的新闻）。"""
    tz_name = os.environ.get("TZ")
    if tz_name:
        # 简化：依赖系统时区数据库；无 tzdata 时退回固定东八区
        try:
            from zoneinfo import ZoneInfo

            tz = ZoneInfo(tz_name)
        except Exception:
            tz = RFC2822_TZ
    else:
        try:
            from zoneinfo import ZoneInfo

            tz = ZoneInfo("Asia/Shanghai")
        except Exception:
            tz = RFC2822_TZ
    now = datetime.now(tz)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    return start, end


def fetch_rss(url: str, timeout: int = 20) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "daily-china-news/1.0 (+https://github.com/)",
            "Accept": "application/rss+xml, application/xml, text/xml, */*",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def parse_items(xml_bytes: bytes) -> list[NewsItem]:
    root = ET.fromstring(xml_bytes)
    channel = root.find("channel")
    if channel is None:
        return []
    items: list[NewsItem] = []
    for el in channel.findall("item"):
        title = (el.findtext("title") or "").strip()
        link = (el.findtext("link") or "").strip()
        desc = (el.findtext("description") or "").strip()
        pub_raw = el.findtext("pubDate")
        items.append(
            NewsItem(
                title=title,
                link=link,
                description=desc,
                pub_date=_parse_pub_date(pub_raw),
            )
        )
    return items


def filter_today(items: Iterable[NewsItem]) -> list[NewsItem]:
    start, end = _local_today_bounds()
    out: list[NewsItem] = []
    for it in items:
        if it.pub_date is None:
            continue
        # 统一转为与 start 相同时区比较
        p = it.pub_date.astimezone(start.tzinfo)
        if start <= p < end:
            out.append(it)
    return out


def pick_top_three(items: list[NewsItem]) -> list[NewsItem]:
    if not items:
        return []
    # 分数高的优先；同分保持 RSS 原顺序（通常较新在前）
    scored = [(it.score(), i, it) for i, it in enumerate(items)]
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [t[2] for t in scored[:3]]


def format_block(items: list[NewsItem], header: str) -> str:
    lines = [header, ""]
    for i, it in enumerate(items, 1):
        lines.append(f"{i}. {it.title}")
        if it.link:
            lines.append(f"   {it.link}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def try_notify(title: str, body: str) -> None:
    if os.environ.get("SKIP_NOTIFY") == "1":
        return
    # Linux 桌面常见通知；无图形环境时静默跳过
    for cmd in (
        ["notify-send", title, body],
        ["osascript", "-e", f'display notification "{body}" with title "{title}"'],
    ):
        try:
            subprocess.run(cmd, check=False, capture_output=True, timeout=5)
            return
        except FileNotFoundError:
            continue
        except Exception:
            return


def main() -> int:
    url = os.environ.get("CHINA_NEWS_RSS", DEFAULT_RSS)
    try:
        raw = fetch_rss(url)
    except Exception as e:
        print(f"抓取 RSS 失败: {e}", file=sys.stderr)
        return 1

    try:
        all_items = parse_items(raw)
    except ET.ParseError as e:
        print(f"解析 XML 失败: {e}", file=sys.stderr)
        return 1

    today_items = filter_today(all_items)
    # 若「今天」尚无条目（例如刚过零点或源未更新），退回当日 RSS 内最新若干条再选
    pool = today_items if today_items else all_items[:30]
    picked = pick_top_three(pool)

    if not picked:
        print("未找到可用新闻条目。", file=sys.stderr)
        return 1

    today_str = date.today().isoformat()
    text = format_block(
        picked,
        f"【今日有意思的中国新闻 · {today_str}】（共 3 条，来源 RSS）",
    )
    print(text, end="")

    # 通知正文不宜过长，取标题列表
    body = "\n".join(f"{i}. {it.title}" for i, it in enumerate(picked, 1))
    try_notify("今日 3 条中国新闻", body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
