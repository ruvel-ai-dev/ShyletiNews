from app import db
from datetime import datetime
from sqlalchemy import Text, DateTime, String, Integer, Boolean

class Article(db.Model):
    id = db.Column(Integer, primary_key=True)
    title = db.Column(String(500), nullable=False)
    content = db.Column(Text, nullable=True)
    summary = db.Column(Text, nullable=True)
    url = db.Column(String(1000), nullable=False, unique=True)
    source = db.Column(String(100), nullable=False)
    published_date = db.Column(DateTime, nullable=True)
    scraped_date = db.Column(DateTime, default=datetime.utcnow)
    author = db.Column(String(200), nullable=True)
    category = db.Column(String(100), nullable=True)
    is_active = db.Column(Boolean, default=True)

    def __repr__(self):
        return f'<Article {self.title[:50]}...>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'summary': self.summary,
            'url': self.url,
            'source': self.source,
            'published_date': self.published_date.isoformat() if self.published_date else None,
            'scraped_date': self.scraped_date.isoformat() if self.scraped_date else None,
            'author': self.author,
            'category': self.category,
            'is_active': self.is_active
        }

class ScrapingLog(db.Model):
    id = db.Column(Integer, primary_key=True)
    source = db.Column(String(100), nullable=False)
    timestamp = db.Column(DateTime, default=datetime.utcnow)
    articles_found = db.Column(Integer, default=0)
    articles_saved = db.Column(Integer, default=0)
    errors = db.Column(Text, nullable=True)
    success = db.Column(Boolean, default=True)

    def __repr__(self):
        return f'<ScrapingLog {self.source} - {self.timestamp}>'
