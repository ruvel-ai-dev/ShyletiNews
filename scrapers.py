import requests
from bs4 import BeautifulSoup
import trafilatura
import time
import logging
from datetime import datetime
from urllib.parse import urljoin, urlparse
import re
from models import Article, ScrapingLog
from app import db

logger = logging.getLogger(__name__)

class BaseScraper:
    def __init__(self, source_name, base_url):
        self.source_name = source_name
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def get_page(self, url, timeout=10):
        """Fetch a web page with error handling and rate limiting"""
        try:
            time.sleep(1)  # Rate limiting
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None
    
    def extract_text_content(self, url):
        """Extract clean text content using trafilatura"""
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                text = trafilatura.extract(downloaded)
                return text
            return None
        except Exception as e:
            logger.error(f"Error extracting text from {url}: {str(e)}")
            return None
    
    def clean_text(self, text):
        """Clean and normalize text content"""
        if not text:
            return ""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        return text
    
    def parse_date(self, date_string):
        """Parse date string to datetime object"""
        if not date_string:
            return None
        
        # Common date formats for Bangla websites
        date_formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%d %B %Y",
            "%d %b %Y",
            "%B %d, %Y",
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_string.strip(), fmt)
            except ValueError:
                continue
        
        logger.warning(f"Could not parse date: {date_string}")
        return None
    
    def extract_image(self, soup, article_url):
        """Extract the main image from an article"""
        try:
            # Look for various image selectors
            image_selectors = [
                'meta[property="og:image"]',
                'meta[name="twitter:image"]',
                '.featured-image img',
                '.article-image img',
                'img[class*="featured"]',
                'img[class*="main"]',
                'article img:first-of-type',
                '.content img:first-of-type',
                'img'
            ]
            
            for selector in image_selectors:
                img_tag = soup.select_one(selector)
                if img_tag:
                    if selector.startswith('meta'):
                        img_url = img_tag.get('content')
                    else:
                        img_url = img_tag.get('src') or img_tag.get('data-src')
                    
                    if img_url:
                        # Convert relative URLs to absolute
                        if img_url.startswith('//'):
                            img_url = 'https:' + img_url
                        elif img_url.startswith('/'):
                            img_url = urljoin(article_url, img_url)
                        elif not img_url.startswith('http'):
                            img_url = urljoin(article_url, img_url)
                        
                        # Check if it's a valid image URL
                        if any(ext in img_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                            return img_url
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting image: {str(e)}")
            return None
    
    def extract_category(self, url, soup):
        """Extract category from URL or content"""
        try:
            # Category mapping for common terms
            category_keywords = {
                'politics': ['politics', 'political', 'government', 'election', 'minister', 'parliament'],
                'business': ['business', 'economy', 'financial', 'trade', 'market', 'banking'],
                'sports': ['sports', 'football', 'cricket', 'game', 'match', 'player'],
                'entertainment': ['entertainment', 'movie', 'film', 'music', 'celebrity', 'actor'],
                'technology': ['technology', 'tech', 'digital', 'internet', 'software', 'computer'],
                'health': ['health', 'medical', 'hospital', 'doctor', 'disease', 'medicine'],
                'education': ['education', 'school', 'university', 'student', 'teacher', 'academic'],
                'international': ['international', 'world', 'global', 'foreign', 'abroad'],
                'local': ['local', 'district', 'city', 'area', 'community', 'regional'],
                'lifestyle': ['lifestyle', 'food', 'fashion', 'travel', 'culture', 'social']
            }
            
            # Check URL for category hints
            url_lower = url.lower()
            for category, keywords in category_keywords.items():
                if any(keyword in url_lower for keyword in keywords):
                    return category.title()
            
            # Check page content for category hints
            page_text = soup.get_text().lower()
            for category, keywords in category_keywords.items():
                keyword_count = sum(1 for keyword in keywords if keyword in page_text)
                if keyword_count >= 2:  # At least 2 keywords match
                    return category.title()
            
            # Check for category meta tags or breadcrumbs
            category_selectors = [
                'meta[property="article:section"]',
                'meta[name="category"]',
                '.breadcrumb li:last-child',
                '.category-tag',
                '.post-category'
            ]
            
            for selector in category_selectors:
                element = soup.select_one(selector)
                if element:
                    if selector.startswith('meta'):
                        category = element.get('content')
                    else:
                        category = element.get_text(strip=True)
                    
                    if category:
                        return category.title()
            
            return 'General'
            
        except Exception as e:
            logger.error(f"Error extracting category: {str(e)}")
            return 'General'

    def save_article(self, article_data):
        """Save article to database if it doesn't exist"""
        try:
            existing = Article.query.filter_by(url=article_data['url']).first()
            if existing:
                logger.info(f"Article already exists: {article_data['url']}")
                return False
            
            article = Article(
                title=self.clean_text(article_data.get('title', '')),
                content=self.clean_text(article_data.get('content', '')),
                summary=self.clean_text(article_data.get('summary', '')),
                url=article_data['url'],
                source=self.source_name,
                published_date=article_data.get('published_date'),
                author=self.clean_text(article_data.get('author', '')),
                category=self.clean_text(article_data.get('category', '')),
                image_url=article_data.get('image_url')
            )
            
            db.session.add(article)
            db.session.commit()
            logger.info(f"Saved article: {article.title[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error saving article: {str(e)}")
            db.session.rollback()
            return False

class SylhetToday24Scraper(BaseScraper):
    def __init__(self):
        super().__init__("Sylhet Today 24", "https://www.sylhettoday24.news/")
    
    def scrape_articles(self, max_pages=3):
        """Scrape articles from Sylhet Today 24"""
        articles_found = 0
        articles_saved = 0
        errors = []
        
        try:
            for page in range(1, max_pages + 1):
                page_url = f"{self.base_url}?page={page}" if page > 1 else self.base_url
                html = self.get_page(page_url)
                
                if not html:
                    errors.append(f"Failed to fetch page {page}")
                    continue
                
                soup = BeautifulSoup(html, 'html.parser')
                
                # Look for article links (adjust selectors based on actual site structure)
                article_links = soup.find_all('a', href=True)
                
                for link in article_links:
                    href = link.get('href')
                    if href and ('/news/' in href or '/post/' in href):
                        article_url = urljoin(self.base_url, href)
                        
                        # Extract article content
                        article_data = self.extract_article(article_url)
                        if article_data:
                            articles_found += 1
                            if self.save_article(article_data):
                                articles_saved += 1
                        
                        # Rate limiting
                        time.sleep(1)
                
                # Rate limiting between pages
                time.sleep(2)
                
        except Exception as e:
            error_msg = f"Error scraping {self.source_name}: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
        
        # Log scraping results
        log = ScrapingLog(
            source=self.source_name,
            articles_found=articles_found,
            articles_saved=articles_saved,
            errors='; '.join(errors) if errors else None,
            success=len(errors) == 0
        )
        db.session.add(log)
        db.session.commit()
        
        return articles_found, articles_saved, errors
    
    def extract_article(self, url):
        """Extract article details from a single article page"""
        try:
            html = self.get_page(url)
            if not html:
                return None
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract title
            title_tag = soup.find('h1') or soup.find('title')
            title = title_tag.get_text(strip=True) if title_tag else ""
            
            # Extract content using trafilatura
            content = self.extract_text_content(url)
            
            # Create summary (first 200 chars of content)
            summary = content[:200] + "..." if content and len(content) > 200 else content
            
            # Extract image
            image_url = self.extract_image(soup, url)
            
            # Extract category from URL or content
            category = self.extract_category(url, soup)
            
            return {
                'title': title,
                'content': content,
                'summary': summary,
                'url': url,
                'image_url': image_url,
                'published_date': None,  # Will be enhanced based on actual site structure
                'author': None,
                'category': category
            }
            
        except Exception as e:
            logger.error(f"Error extracting article from {url}: {str(e)}")
            return None

class DailySylhetScraper(BaseScraper):
    def __init__(self):
        super().__init__("Daily Sylhet", "https://dailysylhet.com/")
    
    def scrape_articles(self, max_pages=3):
        """Scrape articles from Daily Sylhet"""
        articles_found = 0
        articles_saved = 0
        errors = []
        
        try:
            for page in range(1, max_pages + 1):
                page_url = f"{self.base_url}page/{page}/" if page > 1 else self.base_url
                html = self.get_page(page_url)
                
                if not html:
                    errors.append(f"Failed to fetch page {page}")
                    continue
                
                soup = BeautifulSoup(html, 'html.parser')
                
                # Look for article links
                article_links = soup.find_all('a', href=True)
                
                for link in article_links:
                    href = link.get('href')
                    if href and self.base_url in href and ('news' in href or 'post' in href):
                        article_data = self.extract_article(href)
                        if article_data:
                            articles_found += 1
                            if self.save_article(article_data):
                                articles_saved += 1
                        
                        time.sleep(1)
                
                time.sleep(2)
                
        except Exception as e:
            error_msg = f"Error scraping {self.source_name}: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
        
        # Log results
        log = ScrapingLog(
            source=self.source_name,
            articles_found=articles_found,
            articles_saved=articles_saved,
            errors='; '.join(errors) if errors else None,
            success=len(errors) == 0
        )
        db.session.add(log)
        db.session.commit()
        
        return articles_found, articles_saved, errors
    
    def extract_article(self, url):
        """Extract article details from Daily Sylhet"""
        try:
            html = self.get_page(url)
            if not html:
                return None
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract title
            title_tag = soup.find('h1') or soup.find('title')
            title = title_tag.get_text(strip=True) if title_tag else ""
            
            # Extract content using trafilatura
            content = self.extract_text_content(url)
            
            # Create summary
            summary = content[:200] + "..." if content and len(content) > 200 else content
            
            # Extract image
            image_url = self.extract_image(soup, url)
            
            # Extract category
            category = self.extract_category(url, soup)
            
            return {
                'title': title,
                'content': content,
                'summary': summary,
                'url': url,
                'image_url': image_url,
                'published_date': None,
                'author': None,
                'category': category
            }
            
        except Exception as e:
            logger.error(f"Error extracting article from {url}: {str(e)}")
            return None

class SylhetProtikkhonScraper(BaseScraper):
    def __init__(self):
        super().__init__("Sylhet Protikhon", "https://sylhetprotikhon.com/")
    
    def scrape_articles(self, max_pages=3):
        """Scrape articles from Sylhet Protikhon"""
        articles_found = 0
        articles_saved = 0
        errors = []
        
        try:
            for page in range(1, max_pages + 1):
                page_url = f"{self.base_url}page/{page}/" if page > 1 else self.base_url
                html = self.get_page(page_url)
                
                if not html:
                    errors.append(f"Failed to fetch page {page}")
                    continue
                
                soup = BeautifulSoup(html, 'html.parser')
                
                # Look for article links
                article_links = soup.find_all('a', href=True)
                
                for link in article_links:
                    href = link.get('href')
                    if href and self.base_url in href:
                        article_data = self.extract_article(href)
                        if article_data:
                            articles_found += 1
                            if self.save_article(article_data):
                                articles_saved += 1
                        
                        time.sleep(1)
                
                time.sleep(2)
                
        except Exception as e:
            error_msg = f"Error scraping {self.source_name}: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
        
        # Log results
        log = ScrapingLog(
            source=self.source_name,
            articles_found=articles_found,
            articles_saved=articles_saved,
            errors='; '.join(errors) if errors else None,
            success=len(errors) == 0
        )
        db.session.add(log)
        db.session.commit()
        
        return articles_found, articles_saved, errors
    
    def extract_article(self, url):
        """Extract article details from Sylhet Protikhon"""
        try:
            html = self.get_page(url)
            if not html:
                return None
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract title
            title_tag = soup.find('h1') or soup.find('title')
            title = title_tag.get_text(strip=True) if title_tag else ""
            
            # Extract content using trafilatura
            content = self.extract_text_content(url)
            
            # Create summary
            summary = content[:200] + "..." if content and len(content) > 200 else content
            
            # Extract image
            image_url = self.extract_image(soup, url)
            
            # Extract category
            category = self.extract_category(url, soup)
            
            return {
                'title': title,
                'content': content,
                'summary': summary,
                'url': url,
                'image_url': image_url,
                'published_date': None,
                'author': None,
                'category': category
            }
            
        except Exception as e:
            logger.error(f"Error extracting article from {url}: {str(e)}")
            return None

# Add new scrapers for major English news sources
class DailyStarScraper(BaseScraper):
    def __init__(self):
        super().__init__("The Daily Star", "https://www.thedailystar.net/")
    
    def scrape_articles(self, max_pages=2):
        """Scrape articles from The Daily Star"""
        articles_found = 0
        articles_saved = 0
        errors = []
        
        try:
            # Get articles from different sections
            sections = ['frontpage', 'politics', 'business', 'sports', 'entertainment']
            
            for section in sections:
                section_url = f"{self.base_url}{section}"
                html = self.get_page(section_url)
                
                if not html:
                    errors.append(f"Failed to fetch {section} section")
                    continue
                
                soup = BeautifulSoup(html, 'html.parser')
                
                # Look for article links
                article_links = soup.find_all('a', href=True)
                
                for link in article_links:
                    href = link.get('href')
                    if href and ('news' in href or 'article' in href) and self.base_url in href:
                        article_data = self.extract_article(href)
                        if article_data:
                            articles_found += 1
                            if self.save_article(article_data):
                                articles_saved += 1
                        
                        time.sleep(1)
                
                time.sleep(2)
                
        except Exception as e:
            error_msg = f"Error scraping {self.source_name}: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
        
        # Log results
        log = ScrapingLog(
            source=self.source_name,
            articles_found=articles_found,
            articles_saved=articles_saved,
            errors='; '.join(errors) if errors else None,
            success=len(errors) == 0
        )
        db.session.add(log)
        db.session.commit()
        
        return articles_found, articles_saved, errors
    
    def extract_article(self, url):
        """Extract article details from The Daily Star"""
        try:
            html = self.get_page(url)
            if not html:
                return None
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract title
            title_tag = soup.find('h1') or soup.find('title')
            title = title_tag.get_text(strip=True) if title_tag else ""
            
            # Extract content using trafilatura
            content = self.extract_text_content(url)
            
            # Create summary
            summary = content[:200] + "..." if content and len(content) > 200 else content
            
            # Extract image
            image_url = self.extract_image(soup, url)
            
            # Extract category
            category = self.extract_category(url, soup)
            
            return {
                'title': title,
                'content': content,
                'summary': summary,
                'url': url,
                'image_url': image_url,
                'published_date': None,
                'author': None,
                'category': category
            }
            
        except Exception as e:
            logger.error(f"Error extracting article from {url}: {str(e)}")
            return None

class BDNews24Scraper(BaseScraper):
    def __init__(self):
        super().__init__("bdnews24.com", "https://bdnews24.com/")
    
    def scrape_articles(self, max_pages=2):
        """Scrape articles from bdnews24.com"""
        articles_found = 0
        articles_saved = 0
        errors = []
        
        try:
            # Get latest articles from homepage
            html = self.get_page(self.base_url)
            
            if not html:
                errors.append("Failed to fetch homepage")
                return articles_found, articles_saved, errors
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Look for article links
            article_links = soup.find_all('a', href=True)
            
            for link in article_links:
                href = link.get('href')
                if href and ('bangladesh' in href or 'news' in href) and self.base_url in href:
                    article_data = self.extract_article(href)
                    if article_data:
                        articles_found += 1
                        if self.save_article(article_data):
                            articles_saved += 1
                    
                    time.sleep(1)
                
        except Exception as e:
            error_msg = f"Error scraping {self.source_name}: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
        
        # Log results
        log = ScrapingLog(
            source=self.source_name,
            articles_found=articles_found,
            articles_saved=articles_saved,
            errors='; '.join(errors) if errors else None,
            success=len(errors) == 0
        )
        db.session.add(log)
        db.session.commit()
        
        return articles_found, articles_saved, errors
    
    def extract_article(self, url):
        """Extract article details from bdnews24.com"""
        try:
            html = self.get_page(url)
            if not html:
                return None
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract title
            title_tag = soup.find('h1') or soup.find('title')
            title = title_tag.get_text(strip=True) if title_tag else ""
            
            # Extract content using trafilatura
            content = self.extract_text_content(url)
            
            # Create summary
            summary = content[:200] + "..." if content and len(content) > 200 else content
            
            # Extract image
            image_url = self.extract_image(soup, url)
            
            # Extract category
            category = self.extract_category(url, soup)
            
            return {
                'title': title,
                'content': content,
                'summary': summary,
                'url': url,
                'image_url': image_url,
                'published_date': None,
                'author': None,
                'category': category
            }
            
        except Exception as e:
            logger.error(f"Error extracting article from {url}: {str(e)}")
            return None

class DhakaTribuneScraper(BaseScraper):
    def __init__(self):
        super().__init__("Dhaka Tribune", "https://www.dhakatribune.com/")
    
    def scrape_articles(self, max_pages=2):
        """Scrape articles from Dhaka Tribune"""
        articles_found = 0
        articles_saved = 0
        errors = []
        
        try:
            # Get latest articles from homepage
            html = self.get_page(self.base_url)
            
            if not html:
                errors.append("Failed to fetch homepage")
                return articles_found, articles_saved, errors
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Look for article links
            article_links = soup.find_all('a', href=True)
            
            for link in article_links:
                href = link.get('href')
                if href and ('news' in href or 'article' in href) and self.base_url in href:
                    article_data = self.extract_article(href)
                    if article_data:
                        articles_found += 1
                        if self.save_article(article_data):
                            articles_saved += 1
                    
                    time.sleep(1)
                
        except Exception as e:
            error_msg = f"Error scraping {self.source_name}: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
        
        # Log results
        log = ScrapingLog(
            source=self.source_name,
            articles_found=articles_found,
            articles_saved=articles_saved,
            errors='; '.join(errors) if errors else None,
            success=len(errors) == 0
        )
        db.session.add(log)
        db.session.commit()
        
        return articles_found, articles_saved, errors
    
    def extract_article(self, url):
        """Extract article details from Dhaka Tribune"""
        try:
            html = self.get_page(url)
            if not html:
                return None
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract title
            title_tag = soup.find('h1') or soup.find('title')
            title = title_tag.get_text(strip=True) if title_tag else ""
            
            # Extract content using trafilatura
            content = self.extract_text_content(url)
            
            # Create summary
            summary = content[:200] + "..." if content and len(content) > 200 else content
            
            # Extract image
            image_url = self.extract_image(soup, url)
            
            # Extract category
            category = self.extract_category(url, soup)
            
            return {
                'title': title,
                'content': content,
                'summary': summary,
                'url': url,
                'image_url': image_url,
                'published_date': None,
                'author': None,
                'category': category
            }
            
        except Exception as e:
            logger.error(f"Error extracting article from {url}: {str(e)}")
            return None

def run_all_scrapers():
    """Run all scrapers"""
    scrapers = [
        SylhetToday24Scraper(),
        DailySylhetScraper(),
        SylhetProtikkhonScraper(),
        DailyStarScraper(),
        BDNews24Scraper(),
        DhakaTribuneScraper()
    ]
    
    total_found = 0
    total_saved = 0
    all_errors = []
    
    for scraper in scrapers:
        logger.info(f"Starting scraper for {scraper.source_name}")
        found, saved, errors = scraper.scrape_articles()
        total_found += found
        total_saved += saved
        all_errors.extend(errors)
        logger.info(f"Completed {scraper.source_name}: {found} found, {saved} saved")
    
    logger.info(f"Total scraping completed: {total_found} found, {total_saved} saved")
    return total_found, total_saved, all_errors
