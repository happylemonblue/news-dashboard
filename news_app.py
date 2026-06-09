#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║  📰 Daily Global News Digest — Streamlit Dashboard                      ║
║  Live RSS-powered news aggregator across 7 regions                      ║
║  Author: Lemon Leong (generated via Copilot)                            ║
║  Created: 2026-04-15                                                    ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import feedparser
from datetime import datetime, timezone
from dataclasses import dataclass, field
from dateutil import parser as dateparser
import time

# ──────────────────────── Page Configuration ──────────────────────────────

st.set_page_config(
    page_title="📰 Daily News Digest",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────── Configuration ───────────────────────────────────

MAX_ARTICLES_PER_REGION = 5
CACHE_TTL_SECONDS = 3600  # 1 hour

# Region definitions with RSS feed URLs
REGIONS = {
    "🇸🇬 Singapore": {
        "id": "singapore",
        "feeds": [
            {
                "url": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=6511",
                "source": "CNA",
                "country": "Singapore",
                "color": "#e67e22",
            },
            {
                "url": "https://www.straitstimes.com/news/singapore/rss.xml",
                "source": "The Straits Times",
                "country": "Singapore",
                "color": "#e74c3c",
            },
        ],
    },
    "🇲🇾 Malaysia": {
        "id": "malaysia",
        "feeds": [
            {
                "url": "https://www.malaymail.com/feed/rss/malaysia",
                "source": "Malay Mail",
                "country": "Malaysia",
                "color": "#1abc9c",
            },
            {
                "url": "https://www.thestar.com.my/rss/News/Nation",
                "source": "The Star",
                "country": "Malaysia",
                "color": "#f1c40f",
            },
        ],
    },
    "🌏 Other APAC": {
        "id": "otherapac",
        "feeds": [
            {
                "url": "https://www.aljazeera.com/xml/rss/all.xml",
                "source": "Al Jazeera",
                "country": "Asia-Pacific",
                "color": "#ff5722",
            },
            {
                "url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=19832390",
                "source": "CNBC Asia",
                "country": "Asia-Pacific",
                "color": "#f39c12",
            },
        ],
    },
    "🇭🇰 Hong Kong SAR": {
        "id": "hongkong",
        "feeds": [
            {
                "url": "https://rthk.hk/rthk/news/rss/e_expressnews_elocal.xml",
                "source": "RTHK",
                "country": "Hong Kong SAR",
                "color": "#3498db",
            },
            {
                "url": "https://www.thestandard.com.hk/newsfeed/latest/news.xml",
                "source": "The Standard",
                "country": "Hong Kong SAR",
                "color": "#00bcd4",
            },
        ],
    },
    "🇹🇼 Taiwan": {
        "id": "taiwan",
        "feeds": [
            {
                "url": "https://www.taiwannews.com.tw/rss",
                "source": "Taiwan News",
                "country": "Taiwan",
                "color": "#4caf50",
            },
            {
                "url": "https://focustaiwan.tw/rss",
                "source": "Focus Taiwan",
                "country": "Taiwan",
                "color": "#8bc34a",
            },
        ],
    },
    "🇺🇸 United States": {
        "id": "us",
        "feeds": [
            {
                "url": "https://www.reutersagency.com/feed/?taxonomy=best-sectors&post_type=best",
                "source": "Reuters",
                "country": "United States",
                "color": "#ff6f00",
            },
            {
                "url": "https://feeds.npr.org/1001/rss.xml",
                "source": "NPR",
                "country": "United States",
                "color": "#5c6bc0",
            },
        ],
    },
    "🌐 Global": {
        "id": "global",
        "feeds": [
            {
                "url": "http://feeds.bbci.co.uk/news/world/rss.xml",
                "source": "BBC World",
                "country": "Global",
                "color": "#b71c1c",
            },
            {
                "url": "http://feeds.reuters.com/Reuters/worldNews",
                "source": "Reuters World",
                "country": "Global",
                "color": "#ff6f00",
            },
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
    published: str = ""
    published_dt: datetime = field(default_factory=lambda: datetime.min.replace(tzinfo=timezone.utc))

# ──────────────────────── RSS Fetching ────────────────────────────────────

@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def fetch_feed(feed_url: str) -> list[dict]:
    """
    Fetch and parse a single RSS feed. Cached for 1 hour.
    Returns a list of raw entry dicts from feedparser.
    """
    try:
        feed = feedparser.parse(feed_url)
        if feed.bozo and not feed.entries:
            return []
        return [
            {
                "title": entry.get("title", "No title"),
                "summary": entry.get("summary", entry.get("description", "")),
                "link": entry.get("link", "#"),
                "published": entry.get("published", entry.get("updated", "")),
            }
            for entry in feed.entries
        ]
    except Exception:
        return []


def parse_published_date(date_str: str) -> datetime:
    """Safely parse a date string into a datetime object."""
    if not date_str:
        return datetime.min.replace(tzinfo=timezone.utc)
    try:
        dt = dateparser.parse(date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return datetime.min.replace(tzinfo=timezone.utc)


def clean_summary(raw: str, max_len: int = 200) -> str:
    """Strip HTML tags and truncate summary text."""
    import re
    text = re.sub(r"<[^>]+>", "", raw)  # Remove HTML tags
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    text = text.replace("&#8217;", "'").replace("&#8220;", '"').replace("&#8221;", '"')
    text = " ".join(text.split())  # Normalize whitespace
    if len(text) > max_len:
        text = text[:max_len].rsplit(" ", 1)[0] + "…"
    return text


def get_articles_for_region(region_name: str) -> list[Article]:
    """
    Fetch articles from all feeds for a given region,
    sort by published date, and return the top N.
    """
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
                    published=pub_display,
                    published_dt=pub_dt,
                )
            )

    # Sort by most recent first, then take top N
    all_articles.sort(key=lambda a: a.published_dt, reverse=True)
    return all_articles[:MAX_ARTICLES_PER_REGION]

# ──────────────────────── UI Rendering ────────────────────────────────────

def render_card(article: Article, index: int):
    """Render a single article as a styled card."""
    pub_html = ""
    if article.published:
        pub_html = f'<span style="font-size:0.75rem;color:#556677;">🕐 {article.published}</span>'

    st.markdown(f"""
    <div style="
        background: #162233;
        border: 1px solid #1e3348;
        border-left: 4px solid {article.color};
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 12px;
        animation: fadeIn 0.4s ease {index * 0.08}s forwards;
        opacity: 0;
    ">
        <a href="{article.link}" target="_blank" style="
            font-size: 1.02rem;
            font-weight: 600;
            color: #e8eef4;
            text-decoration: none;
            line-height: 1.45;
        ">{article.title}</a>
        <p style="font-size:0.86rem;color:#8899aa;margin:8px 0 12px;line-height:1.55;">
            {article.summary}
        </p>
        <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
            <span style="
                display:inline-block;
                padding:3px 10px;
                border-radius:20px;
                font-size:0.72rem;
                font-weight:600;
                color:#fff;
                background:{article.color};
            ">{article.source}</span>
            <span style="font-size:0.78rem;color:#667788;">📍 {article.country}</span>
            {pub_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


# Inject CSS animation
st.markdown("""
<style>
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(12px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 14px;
        font-size: 0.88rem;
    }
    section[data-testid="stSidebar"] {
        background: #0d1b2a;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────── Sidebar ─────────────────────────────────────────

with st.sidebar:
    st.markdown("## 📰 News Digest")
    st.caption("Live RSS-powered headlines across 7 regions")
    st.divider()

    st.markdown(f"**📅 Today:** {datetime.now().strftime('%A, %B %d, %Y')}")
    st.divider()

    # Region filter
    st.markdown("### 🌍 Regions")
    selected_regions = []
    for region_name in REGIONS:
        if st.checkbox(region_name, value=True, key=REGIONS[region_name]["id"]):
            selected_regions.append(region_name)

    st.divider()

    # Refresh
    if st.button("🔄 Refresh News", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.divider()

    # Feed health
    st.markdown("### ℹ️ Info")
    st.caption(f"Cache TTL: {CACHE_TTL_SECONDS // 60} minutes")
    st.caption(f"Max per region: {MAX_ARTICLES_PER_REGION}")
    st.caption("Powered by Copilot 🤖")

# ──────────────────────── Main Content ────────────────────────────────────

# Header
st.markdown(f"""
<div style="text-align:center;padding:8px 0 16px;">
    <h1 style="font-size:2rem;font-weight:700;margin-bottom:4px;">
        📰 Daily <span style="color:#1e90ff;">Global News</span> Digest
    </h1>
    <p style="color:#8899aa;font-size:0.92rem;">
        Live headlines from {len(selected_regions)} regions — {datetime.now().strftime('%A, %B %d, %Y')}
    </p>
</div>
""", unsafe_allow_html=True)

# Stats
col1, col2, col3 = st.columns(3)
col1.metric("🌍 Regions", len(selected_regions))
col2.metric("📋 Max Per Region", MAX_ARTICLES_PER_REGION)
col3.metric("⏱️ Cache TTL", f"{CACHE_TTL_SECONDS // 60} min")

st.divider()

# Tabs
if selected_regions:
    tabs = st.tabs(selected_regions)

    for tab, region_name in zip(tabs, selected_regions):
        with tab:
            with st.spinner(f"Fetching {region_name} headlines..."):
                articles = get_articles_for_region(region_name)

            if articles:
                st.markdown(f"**Showing {len(articles)} latest headlines**")
                for idx, article in enumerate(articles):
                    render_card(article, idx)
            else:
                st.warning(
                    f"⚠️ No articles found for {region_name}. "
                    "The RSS feeds may be temporarily unavailable. "
                    "Try refreshing in a few minutes."
                )
else:
    st.warning("👈 Please select at least one region from the sidebar.")

# Footer
st.divider()
st.markdown("""
<div style="text-align:center;padding:8px;font-size:0.78rem;color:#445566;">
    Data sourced from live RSS feeds &nbsp;|&nbsp;
    Auto-refreshes every 60 minutes &nbsp;|&nbsp;
    Powered by Copilot 🤖
</div>
""", unsafe_allow_html=True)
