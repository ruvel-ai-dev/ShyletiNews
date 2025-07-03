# Bangladesh Sylheti News Scraper

## Overview

This is a Flask-based web application that scrapes news articles from various sources, stores them in a database, and provides a web interface for viewing, searching, and exporting the collected articles. The application is specifically designed to collect news related to Bangladesh and Sylheti content.

## System Architecture

### Backend Architecture
- **Framework**: Flask web framework with SQLAlchemy ORM
- **Database**: SQLite by default, configurable via environment variables
- **Web Scraping**: Custom scraper system using BeautifulSoup and Trafilatura
- **Scheduling**: Background scheduler for automated scraping tasks
- **Session Management**: Flask sessions with configurable secret key

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Flask
- **CSS Framework**: Bootstrap 5 with dark theme
- **Icons**: Feather Icons
- **JavaScript**: Vanilla JavaScript for interactivity
- **Responsive Design**: Mobile-first approach with Bootstrap grid system

## Key Components

### Database Models
- **Article Model**: Stores scraped news articles with metadata (title, content, URL, source, dates, author, category)
- **ScrapingLog Model**: Tracks scraping operations and their results for monitoring

### Scraper System
- **BaseScraper Class**: Foundation for all scrapers with common functionality
- **Rate Limiting**: Built-in delays to respect website policies
- **Content Extraction**: Uses Trafilatura for clean text extraction
- **Error Handling**: Comprehensive error logging and recovery

### Web Interface
- **Article Listing**: Paginated view with search and filtering capabilities
- **Article Details**: Full article view with metadata and original source links
- **Export Functionality**: CSV and JSON export options
- **Statistics Dashboard**: Overview of scraped content and sources

### Background Services
- **Scheduler**: Automated scraping every 4 hours
- **Cleanup Tasks**: Daily removal of old articles
- **Logging**: Comprehensive logging system for monitoring

## Data Flow

1. **Scraping Process**:
   - Scheduler triggers scraping jobs
   - Scrapers fetch articles from configured sources
   - Content is extracted and cleaned
   - Articles are stored in database with deduplication

2. **Web Interface**:
   - Users access articles through web interface
   - Search and filtering applied to database queries
   - Results paginated and displayed
   - Export functionality generates files on demand

3. **Data Export**:
   - CSV export for spreadsheet analysis
   - JSON export for programmatic access
   - Real-time generation based on current database state

## External Dependencies

### Python Libraries
- Flask: Web framework
- SQLAlchemy: Database ORM
- BeautifulSoup4: HTML parsing
- Trafilatura: Content extraction
- Requests: HTTP client
- Schedule: Task scheduling

### Frontend Dependencies
- Bootstrap 5: UI framework
- Feather Icons: Icon library
- Custom CSS and JavaScript for enhanced functionality

### Infrastructure
- SQLite: Default database (configurable to PostgreSQL)
- Environment variables for configuration
- ProxyFix middleware for deployment behind proxies

## Deployment Strategy

### Configuration
- Environment-based configuration using os.environ
- Database URL configurable via DATABASE_URL environment variable
- Session secret configurable via SESSION_SECRET environment variable

### Production Considerations
- ProxyFix middleware for reverse proxy deployment
- Database connection pooling with health checks
- Logging configuration for production monitoring
- Debug mode disabled in production

### Scaling Options
- Database can be switched to PostgreSQL for better performance
- Scheduler runs in background thread (can be externalized)
- Static files served through CDN for better performance

## Changelog

- July 03, 2025. Enhanced news scraper with:
  - Added 3 new major news sources (The Daily Star, bdnews24.com, Dhaka Tribune)
  - Added image extraction and display for articles
  - Improved automatic category detection (Politics, Business, Sports, etc.)
  - Made user interface more friendly with simple language
  - Added category badges and better visual design
  - Enhanced article cards with images and improved layout
- July 03, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.