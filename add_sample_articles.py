#!/usr/bin/env python3
"""Add sample articles from different sources to demonstrate the interface"""

import sqlite3
from datetime import datetime, timedelta
import random

# Sample articles from different sources
sample_articles = [
    {
        'source': 'The Daily Star',
        'title': 'Bangladesh Economy Shows Strong Growth in Q4',
        'summary': 'Bangladesh\'s economy demonstrated remarkable resilience with a 6.2% growth rate in the fourth quarter, driven by strong exports and domestic consumption.',
        'category': 'Business',
        'image_url': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=400&h=200&fit=crop',
        'url': 'https://www.thedailystar.net/business/economy/news/bangladesh-economy-shows-strong-growth-q4-2024-01-15'
    },
    {
        'source': 'bdnews24.com',
        'title': 'Dhaka Metro Rail Extension Plans Approved',
        'summary': 'The government has approved plans to extend the Dhaka Metro Rail network to reach Hazrat Shahjalal International Airport by 2026.',
        'category': 'National',
        'image_url': 'https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=400&h=200&fit=crop',
        'url': 'https://bdnews24.com/bangladesh/dhaka-metro-rail-extension-plans-approved-2024-01-15'
    },
    {
        'source': 'Dhaka Tribune',
        'title': 'Bangladesh Cricket Team Wins Series Against Zimbabwe',
        'summary': 'Bangladesh cricket team secured a convincing 3-1 series victory against Zimbabwe in the recently concluded ODI series.',
        'category': 'Sports',
        'image_url': 'https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?w=400&h=200&fit=crop',
        'url': 'https://www.dhakatribune.com/sports/cricket/bangladesh-cricket-team-wins-series-2024-01-15'
    },
    {
        'source': 'The Daily Star',
        'title': 'Education Minister Announces New Digital Learning Initiative',
        'summary': 'The Education Minister unveiled a comprehensive digital learning program aimed at enhancing educational quality across rural and urban schools.',
        'category': 'Education',
        'image_url': 'https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=400&h=200&fit=crop',
        'url': 'https://www.thedailystar.net/education/news/education-minister-announces-new-digital-learning-2024-01-15'
    },
    {
        'source': 'bdnews24.com',
        'title': 'Rohingya Crisis: International Aid Increases for 2024',
        'summary': 'International donors have pledged increased humanitarian aid for Rohingya refugees, focusing on education and healthcare improvements.',
        'category': 'International',
        'image_url': 'https://images.unsplash.com/photo-1469571486292-0ba58a3f068b?w=400&h=200&fit=crop',
        'url': 'https://bdnews24.com/international/rohingya-crisis-international-aid-increases-2024-01-15'
    },
    {
        'source': 'Dhaka Tribune',
        'title': 'Padma Bridge Boosts Regional Trade by 40%',
        'summary': 'The Padma Bridge has significantly enhanced regional connectivity, with trade volume increasing by 40% in the southern districts.',
        'category': 'Business',
        'image_url': 'https://images.unsplash.com/photo-1505142468610-359e7d316be0?w=400&h=200&fit=crop',
        'url': 'https://www.dhakatribune.com/business/padma-bridge-boosts-regional-trade-2024-01-15'
    },
    {
        'source': 'Daily Sylhet',
        'title': 'Sylhet Tea Gardens Report Record Harvest',
        'summary': 'Tea gardens in Sylhet division have reported their highest harvest in five years, with quality improvements noted across all major plantations.',
        'category': 'Agriculture',
        'image_url': 'https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=400&h=200&fit=crop',
        'url': 'https://www.dailysylhet.com/agriculture/sylhet-tea-gardens-record-harvest-2024-01-15'
    },
    {
        'source': 'Sylhet Protikhon',
        'title': 'Sylhet Medical College Receives New Equipment',
        'summary': 'Sylhet Medical College Hospital has received state-of-the-art medical equipment worth 50 crore taka to improve patient care.',
        'category': 'Health',
        'image_url': 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1f?w=400&h=200&fit=crop',
        'url': 'https://www.sylhetprotikhon.com/health/sylhet-medical-college-new-equipment-2024-01-15'
    }
]

def add_sample_articles():
    """Add sample articles to the database"""
    conn = sqlite3.connect('instance/news_scraper.db')
    cursor = conn.cursor()
    
    # Clear existing articles first
    cursor.execute('DELETE FROM article')
    
    # Add sample articles
    for i, article in enumerate(sample_articles):
        published_date = datetime.now() - timedelta(days=random.randint(1, 7))
        scraped_date = datetime.now() - timedelta(hours=random.randint(1, 24))
        
        cursor.execute('''
            INSERT INTO article (
                title, content, summary, url, source, 
                published_date, scraped_date, category, image_url, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            article['title'],
            article['summary'] + '\n\nThis is a sample article to demonstrate the Bangladesh News Reader interface. ' +
            'The full article content would be extracted from the original source when the scraper runs.',
            article['summary'],
            article['url'],
            article['source'],
            published_date.isoformat(),
            scraped_date.isoformat(),
            article['category'],
            article['image_url'],
            True
        ))
    
    conn.commit()
    conn.close()
    print(f"Added {len(sample_articles)} sample articles to the database")

if __name__ == '__main__':
    add_sample_articles()