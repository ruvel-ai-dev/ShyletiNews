#!/usr/bin/env python3
"""Test script to verify each scraper individually"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapers import *
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_scraper(scraper_class, scraper_name):
    """Test a single scraper"""
    logger.info(f"\n{'='*50}")
    logger.info(f"Testing {scraper_name}")
    logger.info(f"{'='*50}")
    
    try:
        scraper = scraper_class()
        logger.info(f"Initialized {scraper_name}")
        
        # Test basic connectivity
        test_url = scraper.base_url
        logger.info(f"Testing connectivity to {test_url}")
        
        html = scraper.get_page(test_url)
        if html:
            logger.info(f"✓ Successfully connected to {test_url}")
            logger.info(f"Page length: {len(html)} characters")
        else:
            logger.error(f"✗ Failed to connect to {test_url}")
            return False
            
        # Test scraping a small number of articles
        logger.info(f"Testing article scraping...")
        try:
            found, saved, errors = scraper.scrape_articles(max_pages=1)
            logger.info(f"✓ Scraping completed: {found} found, {saved} saved")
            if errors:
                logger.warning(f"Errors: {errors}")
            return True
        except Exception as e:
            logger.error(f"✗ Scraping failed: {str(e)}")
            return False
            
    except Exception as e:
        logger.error(f"✗ Failed to initialize {scraper_name}: {str(e)}")
        return False

def main():
    """Test all scrapers"""
    scrapers_to_test = [
        (SylhetToday24Scraper, "Sylhet Today 24"),
        (DailySylhetScraper, "Daily Sylhet"),
        (SylhetProtikkhonScraper, "Sylhet Protikhon"),
        (DailyStarScraper, "The Daily Star"),
        (BDNews24Scraper, "bdnews24.com"),
        (DhakaTribuneScraper, "Dhaka Tribune"),
    ]
    
    results = {}
    
    for scraper_class, scraper_name in scrapers_to_test:
        success = test_scraper(scraper_class, scraper_name)
        results[scraper_name] = success
        time.sleep(2)  # Brief pause between tests
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info(f"SUMMARY")
    logger.info(f"{'='*50}")
    
    for scraper_name, success in results.items():
        status = "✓ WORKING" if success else "✗ FAILED"
        logger.info(f"{scraper_name}: {status}")

if __name__ == "__main__":
    main()