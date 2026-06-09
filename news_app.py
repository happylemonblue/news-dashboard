#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║  📰 Daily Global News Digest v2.0 — Full-Featured Streamlit Dashboard   ║
║  Live RSS • 11 Regions • Keyword Alerts • Excel Export • Word Cloud     ║
║  Author: Lemon Leong (generated via Copilot)                            ║
║  Created: 2026-04-15                                                    ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import feedparser
import re
import io
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from dateutil import parser as dateparser
from collections import Counter

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ──────────────────────── Page Configuration ──────────────────────────────

st.set_page_config(
    page_title="📰 Daily News Digest",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────── Session State Init ──────────────────────────────

if "last_fetch_time" not in st.session_state:
    st.session_state.last_fetch_time = time.time()
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "smtp_server" not in st.session_state:
    st.session_state.smtp_server = "smtp.gmail.com"
if "smtp_port" not in st.session_state:
    st.session_state.smtp_port = 587
if "smtp_email" not in st.session_state:
    st.session_state.smtp_email = ""
if "smtp_password" not in st.session_state:
    st.session_state.smtp_password = ""
if "smtp_recipient" not in st.session_state:
    st.session_state.smtp_recipient = ""

# ──────────────────────── Configuration ───────────────────────────────────

DEFAULT_MAX_ARTICLES = 25
CACHE_TTL_SECONDS = 3600  # 1 hour

REGIONS = {
    "🇸🇬 Singapore": {
        "id": "singapore",
        "feeds": [
            {"url": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=6511", "source": "CNA", "country": "Singapore", "color": "#e67e22"},
            {"url": "https://www.straitstimes.com/news/singapore/rss.xml", "source": "The Straits Times", "country": "Singapore", "color": "#e74c3c"},
            {"url": "https://www.todayonline.com/feed", "source": "TODAY", "country": "Singapore", "color": "#8e44ad"},
        ],
    },
    "🇲🇾 Malaysia": {
        "id": "malaysia",
        "feeds": [
            {"url": "https://www.malaymail.com/feed/rss/malaysia", "source": "Malay Mail", "country": "Malaysia", "color": "#1abc9c"},
            {"url": "https://www.thestar.com.my/rss/News/Nation", "source": "The Star", "country": "Malaysia", "color": "#f1c40f"},
            {"url": "https://www.freemalaysiatoday.com/feed/", "source": "Free Malaysia Today", "country": "Malaysia", "color": "#2ecc71"},
        ],
    },
    "🌏 Other APAC": {
        "id": "otherapac",
        "feeds": [
            {"url": "https://www.aljazeera.com/xml/rss/all.xml", "source": "Al Jazeera", "country": "Asia-Pacific", "color": "#ff5722"},
            {"url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=19832390", "source": "CNBC Asia", "country": "Asia-Pacific", "color": "#f39c12"},
        ],
    },
    "🇭🇰 Hong Kong SAR": {
        "id": "hongkong",
        "feeds": [
            {"url": "https://rthk.hk/rthk/news/rss/e_expressnews_elocal.xml", "source": "RTHK", "country": "Hong Kong SAR", "color": "#3498db"},
            {"url": "https://www.thestandard.com.hk/newsfeed/latest/news.xml", "source": "The Standard", "country": "Hong Kong SAR", "color": "#00bcd4"},
            {"url": "https://www.scmp.com/rss/91/feed", "source": "SCMP", "country": "Hong Kong SAR", "color": "#ff9800"},
        ],
    },
    "🇹🇼 Taiwan": {
    "id": "taiwan",
    "feeds": [
        {"url": "https://www.taipeitimes.com/xml/index.rss", "source": "Taipei Times", "country": "Taiwan", "color": "#4caf50"},
        {"url": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=6311", "source": "CNA World", "country": "Taiwan", "color": "#8bc34a"},
        {"url": "https://feeds.feedburner.com/TheNewsLens", "source": "The News Lens", "country": "Taiwan", "color": "#26a69a"},
        ],
    },
    "🇺🇸 United States": {
        "id": "us",
        "feeds": [
            {"url": "https://feeds.npr.org/1001/rss.xml", "source": "NPR", "country": "United States", "color": "#5c6bc0"},
            {"url": "https://www.reutersagency.com/feed/?taxonomy=best-sectors&post_type=best", "source": "Reuters", "country": "United States", "color": "#ff6f00"},
            {"url": "https://feedx.net/rss/ap.xml", "source": "AP News", "country": "United States", "color": "#d32f2f"},
        ],
    },
    "🌐 Global": {
        "id": "global",
        "feeds": [
            {"url": "http://feeds.bbci.co.uk/news/world/rss.xml", "source": "BBC World", "country": "Global", "color": "#b71c1c"},
            {"url": "http://feeds.reuters.com/Reuters/worldNews", "source": "Reuters World", "country": "Global", "color": "#ff6f00"},
            {"url": "https://rss.dw.com/rdf/rss-en-all", "source": "DW", "country": "Global", "color": "#0288d1"},
        ],
    },
    "🇯🇵 Japan": {
        "id": "japan",
        "feeds": [
            {"url": "https://www3.nhk.or.jp/nhkworld/en/news/feeds/", "source": "NHK World", "country": "Japan", "color": "#e91e63"},
            {"url": "https://www.japantimes.co.jp/feed/", "source": "Japan Times", "country": "Japan", "color": "#9c27b0"},
        ],
    },
    "🇰🇷 Korea": {
        "id": "korea",
        "feeds": [
            {"url": "https://en.yna.co.kr/RSS/news.xml", "source": "Yonhap News", "country": "South Korea", "color": "#2196f3"},
            {"url": "http://www.koreaherald.com/common/rss_xml.php?ct=102", "source": "Korea Herald", "country": "South Korea", "color": "#00bcd4"},
        ],
    },
    "🇮🇳 India": {
        "id": "india",
        "feeds": [
            {"url": "https://feeds.feedburner.com/ndtvnews-top-stories", "source": "NDTV", "country": "India", "color": "#f44336"},
            {"url": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms", "source": "Times of India", "country": "India", "color": "#ff5722"},
        ],
    },
    "🇪🇺 Europe": {
        "id": "europe",
        "feeds": [
            {"url": "https://www.euronews.com/rss", "source": "Euronews", "country": "Europe", "color": "#1565c0"},
            {"url": "https://rss.dw.com/rdf/rss-en-eu", "source": "DW Europe", "country": "Europe", "color": "#0288d1"},
        ],
    },
}

# ──────────────────────── Data Model ──────────────────────────────────────

@dataclass
class Article:
    title: str
    summary: str
    link: str
    source: str
    country: str
    color: str
    region: str = ""
    published: str = ""
    published_dt: datetime = field(default_factory=lambda: datetime.min.replace(tzinfo=timezone.utc))
    thumbnail: str = ""

# ──────────────────────── RSS Fetching ────────────────────────────────────

@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def fetch_feed(feed_url: str) -> list[dict]:
    """Fetch and parse a single RSS feed. Cached for 1 hour."""
    try:
        feed = feedparser.parse(feed_url)
        if feed.bozo and not feed.entries:
            return []
        results = []
        for entry in feed.entries:
            # Extract thumbnail from various RSS formats
            thumb = ""
            # media:content
            media = entry.get("media_content", [])
            if media and isinstance(media, list):
                thumb = media[0].get("url", "")
            # media:thumbnail
            if not thumb:
                media_thumb = entry.get("media_thumbnail", [])
                if media_thumb and isinstance(media_thumb, list):
                    thumb = media_thumb[0].get("url", "")
            # enclosure
            if not thumb:
                enclosures = entry.get("enclosures", [])
                if enclosures:
                    for enc in enclosures:
                        if enc.get("type", "").startswith("image"):
                            thumb = enc.get("href", enc.get("url", ""))
                            break
            # og:image in summary (fallback)
            if not thumb:
                summary_html = entry.get("summary", "")
                img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', summary_html)
                if img_match:
                    thumb = img_match.group(1)

            results.append({
                "title": entry.get("title", "No title"),
                "summary": entry.get("summary", entry.get("description", "")),
                "link": entry.get("link", "#"),
                "published": entry.get("published", entry.get("updated", "")),
                "thumbnail": thumb,
            })
        return results
    except Exception:
        return []


def parse_published_date(date_str: str) -> datetime:
    if not date_str:
        return datetime.min.replace(tzinfo=timezone.utc)
    try:
        dt = dateparser.parse(date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return datetime.min.replace(tzinfo=timezone.utc)


def clean_summary(raw: str, max_len: int = 250) -> str:
    text = re.sub(r"<[^>]+>", "", raw)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    text = text.replace("&#8217;", "'").replace("&#8220;", '"').replace("&#8221;", '"')
    text = text.replace("&#39;", "'").replace("&quot;", '"')
    text = " ".join(text.split())
    if len(text) > max_len:
        text = text[:max_len].rsplit(" ", 1)[0] + "…"
    return text


def get_articles_for_region(region_name: str, max_articles: int) -> list[Article]:
    region = REGIONS[region_name]
    all_articles: list[Article] = []

    for feed_cfg in region["feeds"]:
        raw_entries = fetch_feed(feed_cfg["url"])
        for entry in raw_entries:
            pub_dt = parse_published_date(entry["published"])
            pub_display = ""
            if pub_dt != datetime.min.replace(tzinfo=timezone.utc):
                pub_display = pub_dt.strftime("%b %d, %Y %H:%M")

            all_articles.append(
                Article(
                    title=entry["title"],
                    summary=clean_summary(entry["summary"]),
                    link=entry["link"],
                    source=feed_cfg["source"],
                    country=feed_cfg["country"],
                    color=feed_cfg["color"],
                    region=region_name,
                    published=pub_display,
                    published_dt=pub_dt,
                    thumbnail=entry.get("thumbnail", ""),
                )
            )

    all_articles.sort(key=lambda a: a.published_dt, reverse=True)
    return all_articles[:max_articles]


def get_all_articles(selected_regions: list[str], max_articles: int) -> list[Article]:
    """Get articles across all selected regions."""
    all_arts = []
    for rname in selected_regions:
        all_arts.extend(get_articles_for_region(rname, max_articles))
    return all_arts

# ──────────────────────── Theme CSS ───────────────────────────────────────

def get_theme_css(dark: bool) -> str:
    if dark:
        return """
        <style>
            :root {
                --bg-primary: #0f1923;
                --bg-card: #162233;
                --bg-card-hover: #1a2a3f;
                --border: #1e3348;
                --text-primary: #e8eef4;
                --text-secondary: #8899aa;
                --text-muted: #556677;
                --accent: #1e90ff;
                --ticker-bg: #0d1520;
                --highlight-border: #ffd700;
                --highlight-bg: rgba(255, 215, 0, 0.06);
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(12px); }
                to { opacity: 1; transform: translateY(0); }
            }
            @keyframes ticker {
                0% { transform: translateX(100%); }
                100% { transform: translateX(-100%); }
            }
            .ticker-wrap {
                background: var(--ticker-bg);
                border: 1px solid var(--border);
                border-radius: 8px;
                overflow: hidden;
                padding: 10px 0;
                margin-bottom: 16px;
                position: relative;
            }
            .ticker-label {
                position: absolute;
                left: 0; top: 0; bottom: 0;
                background: #e74c3c;
                color: #fff;
                font-weight: 700;
                font-size: 0.78rem;
                padding: 10px 14px;
                z-index: 10;
                display: flex; align-items: center;
                letter-spacing: 0.5px;
            }
            .ticker-move {
                display: inline-block;
                white-space: nowrap;
                animation: ticker 60s linear infinite;
                padding-left: 140px;
            }
            .ticker-move a {
                color: var(--text-primary);
                text-decoration: none;
                font-size: 0.88rem;
                margin-right: 48px;
            }
            .ticker-move a:hover { color: var(--accent); }
            .news-card {
                background: var(--bg-card);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 16px 20px;
                margin-bottom: 12px;
                transition: all 0.2s ease;
                display: flex;
                gap: 16px;
                align-items: flex-start;
            }
            .news-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(30,144,255,0.1);
                border-color: rgba(30,144,255,0.3);
            }
            .news-card.highlighted {
                border-left: 4px solid var(--highlight-border) !important;
                background: var(--highlight-bg) !important;
            }
            .card-thumb {
                width: 120px;
                min-width: 120px;
                height: 80px;
                border-radius: 8px;
                object-fit: cover;
                background: #1a2a3f;
            }
            .card-body { flex: 1; }
            .card-title {
                font-size: 1.02rem;
                font-weight: 600;
                color: var(--text-primary);
                text-decoration: none;
                line-height: 1.45;
            }
            .card-title:hover { color: var(--accent); }
            .card-summary {
                font-size: 0.86rem;
                color: var(--text-secondary);
                margin: 6px 0 10px;
                line-height: 1.55;
            }
            .card-meta {
                display: flex;
                align-items: center;
                gap: 10px;
                flex-wrap: wrap;
            }
            .badge {
                display: inline-block;
                padding: 3px 10px;
                border-radius: 20px;
                font-size: 0.72rem;
                font-weight: 600;
                color: #fff;
            }
            .country-tag { font-size: 0.78rem; color: var(--text-muted); }
            .pub-time { font-size: 0.75rem; color: var(--text-muted); }
            .stTabs [data-baseweb="tab-list"] { gap: 4px; flex-wrap: wrap; }
            .stTabs [data-baseweb="tab"] { border-radius: 8px; padding: 8px 14px; font-size: 0.85rem; }
            section[data-testid="stSidebar"] { background: #0d1b2a; }
            .search-highlight { background: rgba(30,144,255,0.25); padding: 1px 3px; border-radius: 3px; }
            @media (max-width: 768px) {
                .card-thumb { width: 80px; min-width: 80px; height: 56px; }
                .news-card { gap: 10px; padding: 12px 14px; }
            }
        </style>
        """
    else:
        return """
        <style>
            :root {
                --bg-primary: #f5f7fa;
                --bg-card: #ffffff;
                --bg-card-hover: #f0f4f8;
                --border: #e2e8f0;
                --text-primary: #1a202c;
                --text-secondary: #4a5568;
                --text-muted: #718096;
                --accent: #2b6cb0;
                --ticker-bg: #edf2f7;
                --highlight-border: #d69e2e;
                --highlight-bg: rgba(214, 158, 46, 0.08);
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(12px); }
                to { opacity: 1; transform: translateY(0); }
            }
            @keyframes ticker {
                0% { transform: translateX(100%); }
                100% { transform: translateX(-100%); }
            }
            .ticker-wrap {
                background: var(--ticker-bg);
                border: 1px solid var(--border);
                border-radius: 8px;
                overflow: hidden;
                padding: 10px 0;
                margin-bottom: 16px;
                position: relative;
            }
            .ticker-label {
                position: absolute;
                left: 0; top: 0; bottom: 0;
                background: #e53e3e;
                color: #fff;
                font-weight: 700;
                font-size: 0.78rem;
                padding: 10px 14px;
                z-index: 10;
                display: flex; align-items: center;
                letter-spacing: 0.5px;
            }
            .ticker-move {
                display: inline-block;
                white-space: nowrap;
                animation: ticker 60s linear infinite;
                padding-left: 140px;
            }
            .ticker-move a {
                color: var(--text-primary);
                text-decoration: none;
                font-size: 0.88rem;
                margin-right: 48px;
            }
            .ticker-move a:hover { color: var(--accent); }
            .news-card {
                background: var(--bg-card);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 16px 20px;
                margin-bottom: 12px;
                transition: all 0.2s ease;
                display: flex;
                gap: 16px;
                align-items: flex-start;
                box-shadow: 0 1px 3px rgba(0,0,0,0.06);
            }
            .news-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0,0,0,0.08);
                border-color: var(--accent);
            }
            .news-card.highlighted {
                border-left: 4px solid var(--highlight-border) !important;
                background: var(--highlight-bg) !important;
            }
            .card-thumb {
                width: 120px;
                min-width: 120px;
                height: 80px;
                border-radius: 8px;
                object-fit: cover;
                background: #edf2f7;
            }
            .card-body { flex: 1; }
            .card-title {
                font-size: 1.02rem;
                font-weight: 600;
                color: var(--text-primary);
                text-decoration: none;
                line-height: 1.45;
            }
            .card-title:hover { color: var(--accent); }
            .card-summary {
                font-size: 0.86rem;
                color: var(--text-secondary);
                margin: 6px 0 10px;
                line-height: 1.55;
            }
            .card-meta {
                display: flex;
                align-items: center;
                gap: 10px;
                flex-wrap: wrap;
            }
            .badge {
                display: inline-block;
                padding: 3px 10px;
                border-radius: 20px;
                font-size: 0.72rem;
                font-weight: 600;
                color: #fff;
            }
            .country-tag { font-size: 0.78rem; color: var(--text-muted); }
            .pub-time { font-size: 0.75rem; color: var(--text-muted); }
            .stTabs [data-baseweb="tab-list"] { gap: 4px; flex-wrap: wrap; }
            .stTabs [data-baseweb="tab"] { border-radius: 8px; padding: 8px 14px; font-size: 0.85rem; }
            .search-highlight { background: rgba(43,108,176,0.2); padding: 1px 3px; border-radius: 3px; }
            @media (max-width: 768px) {
                .card-thumb { width: 80px; min-width: 80px; height: 56px; }
                .news-card { gap: 10px; padding: 12px 14px; }
            }
        </style>
        """

# ──────────────────────── Render Helpers ──────────────────────────────────

def highlight_text(text: str, keywords: list[str]) -> str:
    """Highlight matching keywords in text."""
    if not keywords:
        return text
    for kw in keywords:
        if kw.strip():
            pattern = re.compile(re.escape(kw.strip()), re.IGNORECASE)
            text = pattern.sub(f'<span class="search-highlight">{kw.strip()}</span>', text)
    return text


def render_card(article: Article, index: int, watch_keywords: list[str], search_keywords: list[str]):
    """Render a single article card."""
    is_highlighted = False
    if watch_keywords:
        combined_text = (article.title + " " + article.summary).lower()
        is_highlighted = any(kw.strip().lower() in combined_text for kw in watch_keywords if kw.strip())

    highlight_class = " highlighted" if is_highlighted else ""
    alert_icon = "⚠️ " if is_highlighted else ""

    # Highlight search keywords in title and summary
    all_highlight_kws = [k for k in (watch_keywords + search_keywords) if k.strip()]
    display_title = highlight_text(article.title, all_highlight_kws)
    display_summary = highlight_text(article.summary, all_highlight_kws)

    pub_html = ""
    if article.published:
        pub_html = f'<span class="pub-time">🕐 {article.published}</span>'

    # Thumbnail
    thumb_html = ""
    if article.thumbnail:
        thumb_html = f'<img class="card-thumb" src="{article.thumbnail}" alt="" onerror="this.style.display=\'none\'">'
    else:
        thumb_html = '<div class="card-thumb" style="display:flex;align-items:center;justify-content:center;font-size:1.8rem;color:var(--text-muted);">📰</div>'

    st.markdown(f"""
    <div class="news-card{highlight_class}" style="animation: fadeIn 0.35s ease {index * 0.05}s forwards; opacity:0;">
        {thumb_html}
        <div class="card-body">
            <a href="{article.link}" target="_blank" class="card-title">{alert_icon}{display_title}</a>
            <p class="card-summary">{display_summary}</p>
            <div class="card-meta">
                <span class="badge" style="background:{article.color}">{article.source}</span>
                <span class="country-tag">📍 {article.country}</span>
                {pub_html}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_ticker(all_articles: list[Article]):
    """Render breaking news ticker at the top."""
    # Take 10 most recent articles
    sorted_arts = sorted(all_articles, key=lambda a: a.published_dt, reverse=True)[:10]
    if not sorted_arts:
        return

    ticker_items = ""
    for a in sorted_arts:
        ticker_items += f'<a href="{a.link}" target="_blank">🔴 {a.title}</a>'

    st.markdown(f"""
    <div class="ticker-wrap">
        <div class="ticker-label">🔴 BREAKING</div>
        <div class="ticker-move">
            {ticker_items}
        </div>
    </div>
    """, unsafe_allow_html=True)


def articles_to_excel(articles: list[Article]) -> bytes:
    """Convert articles to Excel file bytes."""
    rows = []
    for a in articles:
        rows.append({
            "Region": a.region,
            "Title": a.title,
            "Summary": a.summary,
            "Source": a.source,
            "Country": a.country,
            "Link": a.link,
            "Published": a.published,
        })
    df = pd.DataFrame(rows)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="News")
    return buffer.getvalue()


def send_alert_email(matched_articles: list[Article], settings: dict) -> str:
    """Send email with keyword-matched articles."""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🚨 News Alert — {len(matched_articles)} keyword matches ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
        msg["From"] = settings["email"]
        msg["To"] = settings["recipient"]

        # Build HTML body
        html_rows = ""
        for a in matched_articles:
            html_rows += f"""
            <tr>
                <td style="padding:8px;border-bottom:1px solid #eee;">{a.region}</td>
                <td style="padding:8px;border-bottom:1px solid #eee;">
                    <a href="{a.link}">{a.title}</a><br>
                    <small style="color:#888;">{a.summary[:120]}…</small>
                </td>
                <td style="padding:8px;border-bottom:1px solid #eee;">{a.source}</td>
                <td style="padding:8px;border-bottom:1px solid #eee;">{a.published}</td>
            </tr>"""

        html = f"""
        <html><body>
        <h2>🚨 News Keyword Alert</h2>
        <p>The following {len(matched_articles)} articles matched your watch keywords:</p>
        <table style="border-collapse:collapse;width:100%;font-family:Arial,sans-serif;font-size:13px;">
        <tr style="background:#1e90ff;color:#fff;">
            <th style="padding:10px;text-align:left;">Region</th>
            <th style="padding:10px;text-align:left;">Article</th>
            <th style="padding:10px;text-align:left;">Source</th>
            <th style="padding:10px;text-align:left;">Published</th>
        </tr>
        {html_rows}
        </table>
        <br><p style="color:#888;font-size:12px;">Sent by Daily News Digest Dashboard</p>
        </body></html>"""

        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(settings["server"], settings["port"]) as server:
            server.starttls()
            server.login(settings["email"], settings["password"])
            server.sendmail(settings["email"], settings["recipient"], msg.as_string())

        return "✅ Alert email sent successfully!"
    except Exception as e:
        return f"❌ Failed to send email: {str(e)}"

# ──────────────────────── SIDEBAR ─────────────────────────────────────────

# Inject theme CSS
st.markdown(get_theme_css(st.session_state.dark_mode), unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 📰 News Digest v2.0")
    st.caption("Live RSS · 11 Regions · Full-Featured")
    st.divider()

    # ── Dark / Light toggle ──
    st.markdown("### 🎨 Appearance")
    dark_toggle = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode, key="dark_toggle")
    if dark_toggle != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_toggle
        st.rerun()

    st.divider()

    # ── Date & Timer ──
    st.markdown(f"**📅 Today:** {datetime.now().strftime('%A, %B %d, %Y')}")

    elapsed = time.time() - st.session_state.last_fetch_time
    remaining = max(0, CACHE_TTL_SECONDS - elapsed)
    mins, secs = divmod(int(remaining), 60)
    st.markdown(f"⏱️ **Next refresh in:** `{mins:02d}:{secs:02d}`")
    st.caption("Auto-refreshes every 60 minutes")

    st.divider()

    # ── Headlines count slider ──
    st.markdown("### 📊 Headlines")
    max_articles = st.slider("Max per region", min_value=5, max_value=50, value=DEFAULT_MAX_ARTICLES, step=5)

    st.divider()

    # ── Region Filter ──
    st.markdown("### 🌍 Regions")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Select All", use_container_width=True):
            for rname in REGIONS:
                st.session_state[REGIONS[rname]["id"]] = True
            st.rerun()
    with col_b:
        if st.button("Clear All", use_container_width=True):
            for rname in REGIONS:
                st.session_state[REGIONS[rname]["id"]] = False
            st.rerun()

    selected_regions = []
    for region_name in REGIONS:
        rid = REGIONS[region_name]["id"]
        default_val = st.session_state.get(rid, True)
        if st.checkbox(region_name, value=default_val, key=rid):
            selected_regions.append(region_name)

    st.divider()

    # ── Watch Keywords (Alerts) ──
    st.markdown("### 🔔 Watch Keywords")
    watch_kw_input = st.text_input(
        "Comma-separated keywords",
        value="",
        placeholder="e.g. Micron, semiconductor, AI",
        key="watch_keywords",
    )
    watch_keywords = [k.strip() for k in watch_kw_input.split(",") if k.strip()] if watch_kw_input else []
    if watch_keywords:
        st.success(f"Watching: {', '.join(watch_keywords)}")

    st.divider()

    # ── Email Alert Settings ──
    st.markdown("### 📧 Email Alert")
    with st.expander("Configure SMTP", expanded=False):
        st.session_state.smtp_server = st.text_input("SMTP Server", value=st.session_state.smtp_server)
        st.session_state.smtp_port = st.number_input("Port", value=st.session_state.smtp_port, step=1)
        st.session_state.smtp_email = st.text_input("Sender Email", value=st.session_state.smtp_email)
        st.session_state.smtp_password = st.text_input("App Password", value=st.session_state.smtp_password, type="password")
        st.session_state.smtp_recipient = st.text_input("Recipient Email", value=st.session_state.smtp_recipient)

    st.divider()

    # ── Refresh ──
    if st.button("🔄 Refresh Now", use_container_width=True):
        st.cache_data.clear()
        st.session_state.last_fetch_time = time.time()
        st.rerun()

    st.divider()
    st.caption("Powered by Copilot 🤖")

# ──────────────────────── MAIN CONTENT ────────────────────────────────────

# Header
st.markdown(f"""
<div style="text-align:center;padding:4px 0 12px;">
    <h1 style="font-size:2rem;font-weight:700;margin-bottom:2px;">
        📰 Daily <span style="color:var(--accent);">Global News</span> Digest
    </h1>
    <p style="color:var(--text-secondary);font-size:0.92rem;">
        Live RSS headlines from {len(selected_regions)} regions — {datetime.now().strftime('%A, %B %d, %Y')}
    </p>
</div>
""", unsafe_allow_html=True)

# ── Search bar ──
search_query = st.text_input(
    "🔍 Search headlines",
    placeholder="Type to filter articles across all regions...",
    key="search_bar",
)
search_keywords = [k.strip() for k in search_query.split() if k.strip()] if search_query else []

# ── Fetch all articles ──
all_articles: list[Article] = []
if selected_regions:
    with st.spinner("Fetching headlines from RSS feeds..."):
        all_articles = get_all_articles(selected_regions, max_articles)

# ── Apply search filter ──
if search_keywords:
    filtered = []
    for a in all_articles:
        combined = (a.title + " " + a.summary + " " + a.source + " " + a.country).lower()
        if all(kw.lower() in combined for kw in search_keywords):
            filtered.append(a)
    all_articles_filtered = filtered
else:
    all_articles_filtered = all_articles

# ── Breaking news ticker ──
render_ticker(all_articles)

# ── Stats row ──
col1, col2, col3, col4 = st.columns(4)
col1.metric("📰 Total Headlines", len(all_articles_filtered))
col2.metric("🌍 Regions", len(selected_regions))
col3.metric("📋 Max Per Region", max_articles)

# Find keyword matches count for alerts
matched_articles = []
if watch_keywords:
    for a in all_articles:
        combined = (a.title + " " + a.summary).lower()
        if any(kw.lower() in combined for kw in watch_keywords):
            matched_articles.append(a)
col4.metric("⚠️ Keyword Matches", len(matched_articles))

# ── Download & Email buttons ──
btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 2])
with btn_col1:
    if all_articles_filtered:
        excel_bytes = articles_to_excel(all_articles_filtered)
        st.download_button(
            label="📥 Download Excel",
            data=excel_bytes,
            file_name=f"news_digest_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
with btn_col2:
    if matched_articles and st.session_state.smtp_email and st.session_state.smtp_recipient:
        if st.button("📧 Send Alert Email", use_container_width=True):
            result = send_alert_email(
                matched_articles,
                {
                    "server": st.session_state.smtp_server,
                    "port": st.session_state.smtp_port,
                    "email": st.session_state.smtp_email,
                    "password": st.session_state.smtp_password,
                    "recipient": st.session_state.smtp_recipient,
                },
            )
            st.toast(result)
    elif matched_articles:
        st.button("📧 Send Alert Email", disabled=True, help="Configure SMTP in sidebar first", use_container_width=True)

st.divider()

# ── Summary Stats (expandable) ──
with st.expander("📊 Summary Stats & Word Cloud", expanded=False):
    if all_articles_filtered:
        stat_col1, stat_col2 = st.columns(2)

        # Articles by source — bar chart
        with stat_col1:
            st.markdown("**Articles by Source**")
            source_counts = Counter(a.source for a in all_articles_filtered)
            src_df = pd.DataFrame(source_counts.most_common(15), columns=["Source", "Count"])
            st.bar_chart(src_df.set_index("Source"), color="#1e90ff")

        # Word cloud
        with stat_col2:
            st.markdown("**Headline Word Cloud**")
            try:
                from wordcloud import WordCloud
                all_titles = " ".join(a.title for a in all_articles_filtered)
                # Remove common stop words
                stopwords = {"the", "a", "an", "in", "on", "at", "to", "for", "of", "and", "is",
                             "it", "that", "this", "with", "as", "by", "from", "or", "be", "are",
                             "was", "were", "has", "have", "had", "not", "but", "its", "s", "t",
                             "will", "can", "do", "does", "did", "been", "being", "their", "they",
                             "them", "he", "she", "his", "her", "we", "our", "you", "your", "more",
                             "about", "after", "over", "new", "says", "said"}
                bg_color = "#0f1923" if st.session_state.dark_mode else "#ffffff"
                wc = WordCloud(
                    width=600, height=350,
                    background_color=bg_color,
                    colormap="coolwarm",
                    stopwords=stopwords,
                    max_words=80,
                    min_font_size=10,
                ).generate(all_titles)
                fig, ax = plt.subplots(figsize=(6, 3.5))
                ax.imshow(wc, interpolation="bilinear")
                ax.axis("off")
                fig.patch.set_facecolor(bg_color)
                st.pyplot(fig, use_container_width=True)
                plt.close(fig)
            except ImportError:
                st.info("Install `wordcloud` for the word cloud feature: `pip install wordcloud`")

        # Articles by region pie
        st.markdown("**Articles by Region**")
        region_counts = Counter(a.region for a in all_articles_filtered)
        region_df = pd.DataFrame(region_counts.most_common(), columns=["Region", "Count"])
        st.bar_chart(region_df.set_index("Region"), color="#ff6f00")
    else:
        st.info("No articles to analyze.")

st.divider()

# ── Region Tabs ──
if selected_regions and all_articles_filtered:
    tabs = st.tabs(selected_regions)

    for tab, region_name in zip(tabs, selected_regions):
        with tab:
            region_articles = [a for a in all_articles_filtered if a.region == region_name]
            if region_articles:
                st.markdown(f"**Showing {len(region_articles)} headlines**")
                for idx, article in enumerate(region_articles):
                    render_card(article, idx, watch_keywords, search_keywords)
            else:
                st.info(f"No articles found for {region_name}. The feeds may be temporarily unavailable, or no articles matched your search.")
elif not selected_regions:
    st.warning("👈 Please select at least one region from the sidebar.")
else:
    st.info("No articles matched your search. Try different keywords.")

# Footer
st.divider()
st.markdown("""
<div style="text-align:center;padding:8px;font-size:0.78rem;color:var(--text-muted);">
    Data sourced from live RSS feeds &nbsp;|&nbsp;
    Auto-refreshes every 60 minutes &nbsp;|&nbsp;
    Powered by Copilot 🤖
</div>
""", unsafe_allow_html=True)
