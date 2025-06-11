from celery import current_app as celery_app
from datetime import datetime
from sqlalchemy.orm import Session
from src.database import get_db, engine
from src.config import settings
import requests
from bs4 import BeautifulSoup
import logging
import json
from sqlalchemy import text

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def scrape_website_data(self):
    """
    Daily task to scrape data from a website and save to database
    """
    try:
        # Example scraping logic - customize based on your needs
        url = settings.scrape_url
        
        # Make HTTP request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract data (customize based on website structure)
        scraped_data = {
            'title': soup.find('title').text if soup.find('title') else 'No title',
            'description': soup.find('meta', attrs={'name': 'description'})['content'] if soup.find('meta', attrs={'name': 'description'}) else 'No description',
            'scraped_at': datetime.utcnow().isoformat(),
            'url': url,
            'status': 'success'
        }
        
        # Save to database
        with engine.connect() as conn:
            # Create scraped_data table if it doesn't exist
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS scraped_data (
                    id SERIAL PRIMARY KEY,
                    title TEXT,
                    description TEXT,
                    url TEXT,
                    data JSONB,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Insert scraped data
            conn.execute(text("""
                INSERT INTO scraped_data (title, description, url, data, scraped_at)
                VALUES (:title, :description, :url, :data, :scraped_at)
            """), {
                'title': scraped_data['title'],
                'description': scraped_data['description'],
                'url': scraped_data['url'],
                'data': json.dumps(scraped_data),
                'scraped_at': datetime.utcnow()
            })
            
            conn.commit()
        
        logger.info(f"Successfully scraped data from {url}")
        return scraped_data
        
    except requests.RequestException as exc:
        logger.error(f"HTTP error while scraping: {str(exc)}")
        raise self.retry(exc=exc, countdown=300, max_retries=3)  # Retry after 5 minutes
        
    except Exception as exc:
        logger.error(f"Error scraping website data: {str(exc)}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)

@celery_app.task(bind=True)
def scrape_news_headlines(self):
    """
    Scrape news headlines from a news website
    """
    try:
        # Example: scraping from a news website
        url = "https://news.ycombinator.com/"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract headlines (customize based on website structure)
        headlines = []
        for item in soup.find_all('a', class_='storylink')[:10]:  # Get top 10 headlines
            headlines.append({
                'title': item.text.strip(),
                'url': item.get('href', ''),
                'scraped_at': datetime.utcnow().isoformat()
            })
        
        # Save to database
        with engine.connect() as conn:
            # Create headlines table if it doesn't exist
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS news_headlines (
                    id SERIAL PRIMARY KEY,
                    title TEXT,
                    url TEXT,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Insert headlines
            for headline in headlines:
                conn.execute(text("""
                    INSERT INTO news_headlines (title, url, scraped_at)
                    VALUES (:title, :url, :scraped_at)
                """), {
                    'title': headline['title'],
                    'url': headline['url'],
                    'scraped_at': datetime.utcnow()
                })
            
            conn.commit()
        
        logger.info(f"Successfully scraped {len(headlines)} headlines")
        return {'headlines_count': len(headlines), 'status': 'success'}
        
    except Exception as exc:
        logger.error(f"Error scraping news headlines: {str(exc)}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)