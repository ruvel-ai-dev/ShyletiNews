import schedule
import time
import threading
import logging
from scrapers import run_all_scrapers
from app import app

logger = logging.getLogger(__name__)

class NewsScraperScheduler:
    def __init__(self):
        self.running = False
        self.thread = None
    
    def start_scheduler(self):
        """Start the background scheduler"""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.running = True
        
        # Schedule scraping every 4 hours
        schedule.every(4).hours.do(self.run_scraping_job)
        
        # Schedule daily cleanup at 2 AM
        schedule.every().day.at("02:00").do(self.cleanup_old_articles)
        
        # Start the scheduler thread
        self.thread = threading.Thread(target=self.scheduler_loop, daemon=True)
        self.thread.start()
        
        logger.info("News scraper scheduler started")
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("News scraper scheduler stopped")
    
    def scheduler_loop(self):
        """Main scheduler loop"""
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def run_scraping_job(self):
        """Run the scraping job"""
        logger.info("Starting scheduled scraping job")
        
        with app.app_context():
            try:
                found, saved, errors = run_all_scrapers()
                logger.info(f"Scheduled scraping completed: {found} found, {saved} saved")
                
                if errors:
                    logger.error(f"Scraping errors: {errors}")
                    
            except Exception as e:
                logger.error(f"Error in scheduled scraping: {str(e)}")
    
    def cleanup_old_articles(self):
        """Clean up old articles (older than 30 days)"""
        logger.info("Starting cleanup of old articles")
        
        with app.app_context():
            try:
                from models import Article
                from datetime import datetime, timedelta
                from app import db
                
                thirty_days_ago = datetime.utcnow() - timedelta(days=30)
                old_articles = Article.query.filter(Article.scraped_date < thirty_days_ago).all()
                
                for article in old_articles:
                    db.session.delete(article)
                
                db.session.commit()
                logger.info(f"Cleaned up {len(old_articles)} old articles")
                
            except Exception as e:
                logger.error(f"Error in cleanup: {str(e)}")
                db.session.rollback()

# Global scheduler instance
scheduler = NewsScraperScheduler()

def start_background_scheduler():
    """Start the background scheduler"""
    scheduler.start_scheduler()

def stop_background_scheduler():
    """Stop the background scheduler"""
    scheduler.stop_scheduler()
