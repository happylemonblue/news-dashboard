# 📰 Daily Global News Digest

A **live RSS-powered** Streamlit web dashboard that aggregates top news headlines across **7 regions**:

| Region | Sources |
|---|---|
| 🇸🇬 Singapore | CNA, The Straits Times |
| 🇲🇾 Malaysia | Malay Mail, The Star |
| 🌏 Other APAC | Al Jazeera, CNBC Asia |
| 🇭🇰 Hong Kong SAR | RTHK, The Standard |
| 🇹🇼 Taiwan | Taiwan News, Focus Taiwan |
| 🇺🇸 United States | Reuters, NPR |
| 🌐 Global | BBC World, Reuters World |

## ✨ Features

- **Live RSS feeds** — headlines refresh automatically every 60 minutes
- **7 region tabs** with top 5 articles each
- **Sidebar filters** — toggle regions on/off
- **Dark-themed UI** with animated news cards
- **One-click refresh** button
- **Zero API keys needed** — works entirely on public RSS feeds

## 🚀 Quick Start (Local)

```bash
# 1. Clone this repo
git clone https://github.com/<YOUR_USERNAME>/news-dashboard.git
cd news-dashboard

# 2. Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run news_app.py
```

The app will open in your browser at `http://localhost:8501`.

## ☁️ Deploy to Streamlit Community Cloud (Free)

### Prerequisites
- A **GitHub account**
- A **Streamlit Community Cloud account** (free at [share.streamlit.io](https://share.streamlit.io))

### Step-by-step

1. **Push this repo to GitHub** (see instructions below)
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
3. Click **"Create app"** → **"Yup, I have an app"**
4. Select your **repository**, **branch** (`main`), and **main file** (`news_app.py`)
5. (Optional) Set a custom subdomain, e.g. `lemon-news-digest`
6. Click **"Deploy"**
7. Wait 2-3 minutes — your app will be live! 🎉

### Your app URL will be:
```
https://<your-app-name>.streamlit.app
```

## 🔧 Customization

### Add more RSS feeds
Edit the `REGIONS` dictionary in `news_app.py`:

```python
REGIONS = {
    "🇸🇬 Singapore": {
        "id": "singapore",
        "feeds": [
            {
                "url": "https://your-new-feed-url.com/rss",
                "source": "Source Name",
                "country": "Singapore",
                "color": "#e74c3c",
            },
            # ... add more feeds here
        ],
    },
    # ... more regions
}
```

### Change refresh interval
Edit `CACHE_TTL_SECONDS` at the top of `news_app.py`:

```python
CACHE_TTL_SECONDS = 1800  # 30 minutes
```

### Change max articles per region
```python
MAX_ARTICLES_PER_REGION = 10  # Show 10 instead of 5
```

## 📁 Project Structure

```
news-dashboard/
├── news_app.py          # Main Streamlit application
├── requirements.txt     # Python dependencies
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## 📝 License

MIT — free for personal and commercial use.

---

*Built with ❤️ using [Streamlit](https://streamlit.io) and [feedparser](https://feedparser.readthedocs.io/)*
