import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import random

class CNNScraper:
    def __init__(self):
        self.base_url = "https://www.cnn.com/world"  # Changed to world section
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }

    def get_article_links(self):
        """Get all article links from CNN World section"""
        try:
            response = requests.get(self.base_url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            links = []
            # Look for links in the main content area
            containers = soup.find_all(['div', 'article'], class_=['container', 'card'])
            
            for container in containers:
                anchors = container.find_all('a', href=True)
                for anchor in anchors:
                    href = anchor['href']
                    # Only get article links
                    if href.startswith('/') and '/2024/' in href or '/2023/' in href:
                        full_url = f"https://www.cnn.com{href}"
                        links.append(full_url)
            
            links = list(set(links))  # Remove duplicates
            print(f"Found links: {links}")  # Debug print
            return links
            
        except Exception as e:
            print(f"Error getting article links: {e}")
            return []

    def scrape_article(self, url):
        """Scrape individual article content"""
        try:
            print(f"Scraping URL: {url}")  # Debug print
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find article title and content
            title = ""
            content = ""
            
            # Get title (multiple possible selectors)
            title_element = soup.find(['h1', 'headline'])
            if title_element:
                title = title_element.text.strip()
                print(f"Found title: {title}")  # Debug print

            # Get content (multiple possible selectors)
            article_body = soup.find(['div', 'article'], class_=['article__content', 'body', 'article-body'])
            if article_body:
                paragraphs = article_body.find_all('p')
                content = ' '.join([p.text.strip() for p in paragraphs])
                print(f"Found content length: {len(content)}")  # Debug print
            
            if not content:  # Try alternative content location
                paragraphs = soup.find_all('div', class_='paragraph')
                content = ' '.join([p.text.strip() for p in paragraphs])

            return {
                'title': title,
                'content': content,
                'url': url,
                'date': datetime.now().strftime("%Y-%m-%d"),
                'source': 'CNN'
            }
        except Exception as e:
            print(f"Error scraping article {url}: {e}")
            return None

    def clean_text(self, text):
        """Clean collected text"""
        if text:
            # Remove special characters
            text = text.replace('\n', ' ').replace('\r', '')
            # Remove extra spaces
            text = ' '.join(text.split())
            return text
        return ""

    def scrape_cnn_news(self):
        """Main function to scrape CNN news"""
        articles = []
        
        # Get article links
        links = self.get_article_links()
        print(f"Found {len(links)} articles")
        
        # Scrape each article
        for link in links:
            # Add random delay
            time.sleep(random.uniform(2, 4))
            
            article = self.scrape_article(link)
            if article and article['content']:
                article['content'] = self.clean_text(article['content'])
                articles.append(article)
                print(f"Successfully scraped: {article['title'][:50]}...")
        
        return articles

    def save_articles(self, articles):
        """Save articles to CSV file"""
        df = pd.DataFrame(articles)
        date = datetime.now().strftime("%Y%m%d")
        filename = f'cnn_articles_{date}.csv'
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Saved {len(articles)} articles to {filename}")
        return df

def main():
    scraper = CNNScraper()
    articles = scraper.scrape_cnn_news()
    df = scraper.save_articles(articles)
    return df

if __name__ == "__main__":
    df = main()