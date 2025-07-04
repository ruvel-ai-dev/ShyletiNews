#!/usr/bin/env python3
"""Simple working news scraper for Bangladesh news sources"""

import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_bdnews24_articles():
    """Scrape real articles from bdnews24.com"""
    articles = []
    try:
        url = "https://bdnews24.com/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find article links
        article_links = soup.find_all('a', href=True)
        
        count = 0
        for link in article_links:
            if count >= 5:  # Limit to 5 articles
                break
                
            href = link.get('href', '')
            if not href or not href.startswith('http'):
                continue
                
            title_elem = link.find('h2') or link.find('h3') or link.find('h4')
            if not title_elem:
                continue
                
            title = title_elem.get_text(strip=True)
            if len(title) < 10:  # Skip very short titles
                continue
                
            # Get article content
            try:
                article_response = requests.get(href, headers=headers, timeout=10)
                article_soup = BeautifulSoup(article_response.text, 'html.parser')
                
                # Extract content paragraphs
                content_paras = article_soup.find_all('p')
                content = ' '.join([p.get_text(strip=True) for p in content_paras[:5] if p.get_text(strip=True)])
                
                if len(content) > 100:  # Only keep articles with substantial content
                    articles.append({
                        'title': title,
                        'url': href,
                        'content': content,
                        'summary': content[:200] + '...' if len(content) > 200 else content,
                        'source': 'bdnews24.com',
                        'category': 'News',
                        'image_url': None
                    })
                    count += 1
                    
            except Exception as e:
                logger.warning(f"Error fetching article {href}: {e}")
                continue
                
            time.sleep(1)  # Be respectful to the server
            
    except Exception as e:
        logger.error(f"Error scraping bdnews24: {e}")
        
    return articles

def get_daily_star_articles():
    """Scrape real articles from The Daily Star"""
    articles = []
    try:
        url = "https://www.thedailystar.net/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find article links
        article_links = soup.find_all('a', href=True)
        
        count = 0
        for link in article_links:
            if count >= 5:  # Limit to 5 articles
                break
                
            href = link.get('href', '')
            if not href:
                continue
                
            # Make URL absolute
            if href.startswith('/'):
                href = 'https://www.thedailystar.net' + href
            elif not href.startswith('http'):
                continue
                
            title_elem = link.find('h1') or link.find('h2') or link.find('h3')
            if not title_elem:
                title_text = link.get_text(strip=True)
                if len(title_text) < 10 or len(title_text) > 200:
                    continue
                title = title_text
            else:
                title = title_elem.get_text(strip=True)
                
            if len(title) < 10:  # Skip very short titles
                continue
                
            # Get article content
            try:
                article_response = requests.get(href, headers=headers, timeout=10)
                article_soup = BeautifulSoup(article_response.text, 'html.parser')
                
                # Extract content paragraphs
                content_paras = article_soup.find_all('p')
                content = ' '.join([p.get_text(strip=True) for p in content_paras[:5] if p.get_text(strip=True)])
                
                if len(content) > 100:  # Only keep articles with substantial content
                    articles.append({
                        'title': title,
                        'url': href,
                        'content': content,
                        'summary': content[:200] + '...' if len(content) > 200 else content,
                        'source': 'The Daily Star',
                        'category': 'News',
                        'image_url': None
                    })
                    count += 1
                    
            except Exception as e:
                logger.warning(f"Error fetching article {href}: {e}")
                continue
                
            time.sleep(1)  # Be respectful to the server
            
    except Exception as e:
        logger.error(f"Error scraping The Daily Star: {e}")
        
    return articles

def save_articles_to_db(articles):
    """Save articles to the database"""
    conn = sqlite3.connect('instance/news_scraper.db')
    cursor = conn.cursor()
    
    saved_count = 0
    for article in articles:
        try:
            # Check if article already exists
            cursor.execute('SELECT id FROM article WHERE url = ?', (article['url'],))
            if cursor.fetchone():
                continue  # Skip duplicate
                
            # Insert new article
            cursor.execute('''
                INSERT INTO article (
                    title, content, summary, url, source, 
                    published_date, scraped_date, category, image_url, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                article['title'],
                article['content'],
                article['summary'],
                article['url'],
                article['source'],
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                article['category'],
                article['image_url'],
                True
            ))
            saved_count += 1
            
        except Exception as e:
            logger.error(f"Error saving article: {e}")
            
    conn.commit()
    conn.close()
    return saved_count

def main():
    """Main scraping function"""
    logger.info("Starting news scraping...")
    
    all_articles = []
    
    # Get articles from different sources
    logger.info("Scraping bdnews24.com...")
    bdnews_articles = get_bdnews24_articles()
    all_articles.extend(bdnews_articles)
    logger.info(f"Found {len(bdnews_articles)} articles from bdnews24.com")
    
    logger.info("Scraping The Daily Star...")
    star_articles = get_daily_star_articles()
    all_articles.extend(star_articles)
    logger.info(f"Found {len(star_articles)} articles from The Daily Star")
    
    # Save to database
    if all_articles:
        saved_count = save_articles_to_db(all_articles)
        logger.info(f"Saved {saved_count} new articles to database")
    else:
        logger.warning("No articles found")

if __name__ == '__main__':
    main()