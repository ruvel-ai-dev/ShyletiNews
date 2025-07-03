from flask import render_template, request, jsonify, redirect, url_for, flash, send_file, make_response
from app import app, db
from models import Article, ScrapingLog
from scrapers import run_all_scrapers
from datetime import datetime, timedelta
import csv
import json
import io
import logging

logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Main page showing recent articles"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    source = request.args.get('source', '')
    category = request.args.get('category', '')
    
    # Build query
    query = Article.query.filter_by(is_active=True)
    
    # Apply filters
    if search:
        query = query.filter(
            db.or_(
                Article.title.contains(search),
                Article.content.contains(search)
            )
        )
    
    if source:
        query = query.filter(Article.source == source)
    
    if category:
        query = query.filter(Article.category == category)
    
    # Order by scraped date and paginate
    articles = query.order_by(Article.scraped_date.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # Get available sources and categories for filters
    sources = db.session.query(Article.source).distinct().all()
    sources = [s[0] for s in sources if s[0]]
    
    categories = db.session.query(Article.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    
    # Get scraping statistics
    total_articles = Article.query.filter_by(is_active=True).count()
    recent_scrapes = ScrapingLog.query.order_by(ScrapingLog.timestamp.desc()).limit(5).all()
    
    return render_template('index.html', 
                         articles=articles,
                         sources=sources,
                         categories=categories,
                         search=search,
                         selected_source=source,
                         selected_category=category,
                         total_articles=total_articles,
                         recent_scrapes=recent_scrapes)

@app.route('/article/<int:article_id>')
def article_detail(article_id):
    """Show article details"""
    article = Article.query.get_or_404(article_id)
    return render_template('article.html', article=article)

@app.route('/scrape')
def manual_scrape():
    """Manually trigger scraping"""
    try:
        found, saved, errors = run_all_scrapers()
        
        if errors:
            flash(f'Scraping completed with errors: {"; ".join(errors)}', 'warning')
        else:
            flash(f'Scraping completed successfully! Found {found} articles, saved {saved} new articles.', 'success')
            
    except Exception as e:
        logger.error(f"Error in manual scraping: {str(e)}")
        flash(f'Error occurred during scraping: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/export')
def export_page():
    """Export page"""
    return render_template('export.html')

@app.route('/export/csv')
def export_csv():
    """Export articles to CSV"""
    try:
        articles = Article.query.filter_by(is_active=True).order_by(Article.scraped_date.desc()).all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ID', 'Title', 'Source', 'URL', 'Published Date', 'Scraped Date', 'Author', 'Category', 'Summary'])
        
        # Write data
        for article in articles:
            writer.writerow([
                article.id,
                article.title,
                article.source,
                article.url,
                article.published_date.strftime('%Y-%m-%d %H:%M:%S') if article.published_date else '',
                article.scraped_date.strftime('%Y-%m-%d %H:%M:%S') if article.scraped_date else '',
                article.author or '',
                article.category or '',
                article.summary or ''
            ])
        
        output.seek(0)
        
        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=sylheti_news_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return response
        
    except Exception as e:
        logger.error(f"Error exporting CSV: {str(e)}")
        flash(f'Error exporting CSV: {str(e)}', 'error')
        return redirect(url_for('export_page'))

@app.route('/export/json')
def export_json():
    """Export articles to JSON"""
    try:
        articles = Article.query.filter_by(is_active=True).order_by(Article.scraped_date.desc()).all()
        
        data = {
            'export_date': datetime.now().isoformat(),
            'total_articles': len(articles),
            'articles': [article.to_dict() for article in articles]
        }
        
        # Create response
        response = make_response(json.dumps(data, indent=2, ensure_ascii=False))
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Disposition'] = f'attachment; filename=sylheti_news_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        return response
        
    except Exception as e:
        logger.error(f"Error exporting JSON: {str(e)}")
        flash(f'Error exporting JSON: {str(e)}', 'error')
        return redirect(url_for('export_page'))

@app.route('/stats')
def stats():
    """Show scraping statistics"""
    # Get article count by source
    source_stats = db.session.query(
        Article.source,
        db.func.count(Article.id).label('count')
    ).filter_by(is_active=True).group_by(Article.source).all()
    
    # Get recent scraping logs
    recent_logs = ScrapingLog.query.order_by(ScrapingLog.timestamp.desc()).limit(10).all()
    
    # Get articles by date (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    daily_stats = db.session.query(
        db.func.date(Article.scraped_date).label('date'),
        db.func.count(Article.id).label('count')
    ).filter(
        Article.scraped_date >= thirty_days_ago,
        Article.is_active == True
    ).group_by(db.func.date(Article.scraped_date)).order_by('date').all()
    
    return render_template('stats.html',
                         source_stats=source_stats,
                         recent_logs=recent_logs,
                         daily_stats=daily_stats)

@app.route('/search')
def search():
    """Search articles"""
    query = request.args.get('q', '')
    if not query:
        flash('Please enter a search term', 'warning')
        return redirect(url_for('index'))
    
    # Search in title and content
    articles = Article.query.filter(
        db.or_(
            Article.title.contains(query),
            Article.content.contains(query)
        ),
        Article.is_active == True
    ).order_by(Article.scraped_date.desc()).limit(50).all()
    
    return render_template('search_results.html', 
                         articles=articles, 
                         query=query,
                         total_found=len(articles))

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
