# ShyletiNews 📰

A Bangla-language news aggregator for Sylhet-based stories, built to provide quick access to local headlines from verified Bangladeshi sources. The platform uses web scraping and automated categorisation to pull news articles and display them in a simple, mobile-friendly format.

---

## 🔍 Features

- Scrapes and stores real-time news from Bangladeshi websites
- Categorises articles by topic (e.g., Sports, Business, National)
- Displays full article text in Bangla
- Allows users to return to source or read within app
- Clean dark mode UI for easy readability
- Includes metadata like publish date, source, and tags

---

## 🖼 Interface Previews

### 🏠 Main News Feed

Displays a list of the most recent news stories, sorted by date and grouped by source. Articles include thumbnail images, category tags, and short descriptions.

<img src="https://raw.githubusercontent.com/ruvel-ai-dev/ShyletiNews/main/Main_Page.jpg" alt="Main Page" width="800"/>

---

### 📄 Full Article View

Each article has its own page, showing the full Bangla news content, source metadata, and navigation options to return to the feed or visit the original site.

<img src="https://raw.githubusercontent.com/ruvel-ai-dev/ShyletiNews/main/Article_Page.jpg" alt="Article Page" width="800"/>

---

## ⚙️ Technologies Used

- **Python** with `BeautifulSoup` and `Requests` for web scraping
- **Flask** for backend routing
- **HTML/CSS** for frontend templating
- **Replit** for initial deployment and testing

---

## 🌍 Purpose

This project is part of a wider exploration into building tools for underrepresented languages and regions. Sylhet and Bangla-language content often receive limited digital representation, and this project aims to offer a practical, localised news platform to help bridge that gap.

---

## 📫 Contact

Built by **Ruvel Miah**  
For questions, feedback, or collaboration, feel free to [open an issue](https://github.com/ruvel-ai-dev/ShyletiNews/issues) or reach out directly.

---

## 📦 Deployment

This project was initially developed and hosted on Replit. You can deploy it on your own server or container by cloning the repo and installing dependencies:

```bash
git clone https://github.com/ruvel-ai-dev/ShyletiNews.git
cd ShyletiNews
pip install -r requirements.txt
python app.py

```

Once the server is running, open `http://localhost:5000` in your browser to
access the site.

The application stores its SQLite database in `instance/news_scraper.db` by
default. Ensure the `instance` directory exists (it is created automatically
when running the app) or adjust the location by setting the `DATABASE_URL`
environment variable.



