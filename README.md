# 📰 Daily Global News Digest v2.0

A **fully-featured, live RSS-powered** Streamlit web dashboard that aggregates top news headlines across **11 regions**.

## 🌍 Regions & Sources

| Region | Sources |
|---|---|
| 🇸🇬 Singapore | CNA, The Straits Times, TODAY |
| 🇲🇾 Malaysia | Malay Mail, The Star, Free Malaysia Today |
| 🌏 Other APAC | Al Jazeera, CNBC Asia |
| 🇭🇰 Hong Kong SAR | RTHK, The Standard, SCMP |
| 🇹🇼 Taiwan | Taiwan News, Focus Taiwan |
| 🇺🇸 United States | NPR, Reuters, AP News |
| 🌐 Global | BBC World, Reuters World, DW |
| 🇯🇵 Japan | NHK World, Japan Times |
| 🇰🇷 Korea | Yonhap News, Korea Herald |
| 🇮🇳 India | NDTV, Times of India |
| 🇪🇺 Europe | Euronews, DW Europe |

## ✨ Features

### 📰 Content
- **5–50 headlines per region** (adjustable slider)
- **11 region tabs** with multiple RSS sources each
- **Keyword search/filter** bar — filters across all tabs in real time
- **Article thumbnail images** from RSS media tags
- **Breaking News ticker** — scrolling marquee of 10 most recent headlines

### 📊 Analytics
- **Summary stats section** with articles-by-source bar chart
- **Word cloud** of headline keywords
- **Articles-by-region** breakdown
- **Auto-refresh countdown timer** in sidebar

### 🔔 Alerts
- **Watch Keywords** — comma-separated keywords to monitor (e.g. "Micron, semiconductor, AI")
- **Highlighted articles** — matching articles get a gold border + ⚠️ icon
- **Email alerts** — configure SMTP and send keyword-matched articles via email

### 🎨 Appearance
- **Dark / Light mode toggle**
- Animated card hover effects
- Color-coded source badges
- Responsive / mobile-friendly

### 📥 Export
- **Download as Excel** button — exports all visible headlines to `.xlsx`

## 🚀 Quick Start

```bash
git clone https://github.com/<YOUR_USERNAME>/news-dashboard.git
cd news-dashboard
pip install -r requirements.txt
streamlit run news_app.py
```

## ☁️ Deploy to Streamlit Community Cloud

1. Push this repo to **GitHub** (public)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **Create app** → select your repo → **Branch:** `main` → **Main file:** `news_app.py`
4. Click **Deploy** 🚀

## 📁 Project Structure

```
news-dashboard/
├── .streamlit/
│   └── config.toml          # Dark theme settings
├── .gitignore
├── README.md
├── news_app.py              # Main Streamlit application
└── requirements.txt         # Python dependencies
```

## 🔧 Customization

- **Add regions/feeds:** Edit the `REGIONS` dict in `news_app.py`
- **Change refresh interval:** Edit `CACHE_TTL_SECONDS`
- **Change theme colors:** Edit `.streamlit/config.toml`

---

*Built with ❤️ using [Streamlit](https://streamlit.io), [feedparser](https://feedparser.readthedocs.io/), and [wordcloud](https://amueller.github.io/word_cloud/)*
