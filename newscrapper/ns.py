import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import threading
import queue
import webbrowser
import time
import random


class NewsDatabase:
    def __init__(self):
        self.db_path = 'news.db'
        self._create_connection()
        self.create_tables()
        
    def _create_connection(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            raise

    def create_tables(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT,
                    url TEXT UNIQUE,
                    date TEXT,
                    source TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")
            raise

    def save_article(self, article):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO news (title, content, url, date, source)
                VALUES (?, ?, ?, ?, ?)
            ''', (article['title'], article['content'], 
                  article['url'], article['date'], article['source']))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error saving article: {e}")
            self.conn.rollback()

    def get_recent_news(self, limit=50):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM news 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching news: {e}")
            return []

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()


    def __init__(self):
        self.conn = sqlite3.connect('news.db')
        self.create_tables()
        
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT,
                url TEXT,
                date TEXT,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
        
    def save_article(self, article):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO news (title, content, url, date, source)
            VALUES (?, ?, ?, ?, ?)
        ''', (article['title'], article['content'], 
              article['url'], article['date'], article['source']))
        self.conn.commit()
        
    def get_recent_news(self, limit=50):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM news 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        return cursor.fetchall()



class CNNScraper(threading.Thread):
    def __init__(self, queue, status_queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.status_queue = status_queue
        self.base_url = "https://www.cnn.com/world"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        }
        self.db = NewsDatabase()
        self.running = True

    def get_article_links(self):
        try:
            response = requests.get(self.base_url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            links = []
            # Find all link elements
            for a in soup.find_all('a', href=True):
                href = a['href']
                # Check if it's a news article link
                if href.startswith('/') and any(x in href.lower() for x in ['/world/', '/politics/', '/business/', '/tech/']):
                    full_url = f"https://www.cnn.com{href}"
                    if full_url not in links:
                        links.append(full_url)
            
            print(f"Found links: {links}")  # Debug print
            return links
        except Exception as e:
            print(f"Error getting article links: {e}")
            return []

    def scrape_article(self, url):
        try:
            print(f"Scraping URL: {url}")  # Debug print
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find title
            title = ""
            title_element = soup.find('h1')
            if title_element:
                title = title_element.text.strip()
            
            # Find content
            content = ""
            article_body = soup.find('div', class_='article__content')
            if article_body:
                # Get all paragraphs
                paragraphs = article_body.find_all(['p', 'h2', 'h3'])
                content = ' '.join([p.text.strip() for p in paragraphs if p.text.strip()])
            
            if not content:
                # Try alternative content locations
                content_elements = soup.select('.zn-body__paragraph, .el__article--section')
                if content_elements:
                    content = ' '.join([elem.text.strip() for elem in content_elements])

            print(f"Found title: {title[:50]}...")  # Debug print
            print(f"Content length: {len(content)}")  # Debug print

            if title and content:
                return {
                    'title': title,
                    'content': content,
                    'url': url,
                    'date': datetime.now().strftime("%Y-%m-%d"),
                    'source': 'CNN'
                }
            return None

        except Exception as e:
            print(f"Error scraping article {url}: {e}")
            return None

    def scrape_cnn_news(self):
        articles = []
        links = self.get_article_links()
        if not links:
            self.status_queue.put(("status", "No articles found. Retrying later..."))
            return articles

        self.status_queue.put(("status", f"Found {len(links)} articles to scrape"))
        
        for i, link in enumerate(links, 1):
            self.status_queue.put(("status", f"Scraping article {i}/{len(links)}..."))
            time.sleep(random.uniform(2, 4))  # Polite delay between requests
            
            article = self.scrape_article(link)
            if article:
                print(f"Successfully scraped: {article['title'][:50]}...")  # Debug print
                articles.append(article)
                self.db.save_article(article)
                self.queue.put(article)
                self.status_queue.put(("article", article))
            
        return articles

    def run(self):
        while self.running:
            try:
                self.status_queue.put(("status", "Starting to scrape CNN news..."))
                articles = self.scrape_cnn_news()
                if articles:
                    self.status_queue.put(("status", f"Successfully scraped {len(articles)} articles"))
                else:
                    self.status_queue.put(("status", "No articles scraped"))
                self.status_queue.put(("status", "Waiting for next scrape cycle..."))
                time.sleep(300)  # 5 minutes between scraping cycles
            except Exception as e:
                print(f"Error in scraping cycle: {e}")
                self.status_queue.put(("status", f"Error: {str(e)}"))
                time.sleep(60)  # Wait a minute before retrying on error

    def __init__(self, queue, status_queue):  # Added status_queue
        threading.Thread.__init__(self)
        self.queue = queue
        self.status_queue = status_queue  # For updating GUI with status
        self.base_url = "https://www.cnn.com/world"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124'
        }
        self.db = NewsDatabase()
        self.running = True

    def get_article_links(self):
        try:
            response = requests.get(self.base_url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            links = []
            containers = soup.find_all(['div', 'article'], class_=['container', 'card'])
            
            for container in containers:
                anchors = container.find_all('a', href=True)
                for anchor in anchors:
                    href = anchor['href']
                    if href.startswith('/') and ('/2024/' in href or '/2023/' in href):
                        full_url = f"https://www.cnn.com{href}"
                        links.append(full_url)
            
            return list(set(links))
        except Exception as e:
            print(f"Error getting article links: {e}")
            return []

    def scrape_article(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            title = ""
            content = ""
            
            title_element = soup.find(['h1', 'headline'])
            if title_element:
                title = title_element.text.strip()

            article_body = soup.find(['div', 'article'], class_=['article__content', 'body', 'article-body'])
            if article_body:
                paragraphs = article_body.find_all('p')
                content = ' '.join([p.text.strip() for p in paragraphs])
            
            if not content:
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

    def run(self):
        while self.running:
            try:
                self.status_queue.put(("status", "Starting to scrape CNN news..."))
                articles = self.scrape_cnn_news()
                self.status_queue.put(("status", "Waiting for next scrape cycle..."))
                time.sleep(300)  # Wait 5 minutes before next scrape
            except Exception as e:
                self.status_queue.put(("status", f"Error: {str(e)}"))

    def scrape_cnn_news(self):
        articles = []
        links = self.get_article_links()
        self.status_queue.put(("status", f"Found {len(links)} articles to scrape"))
        
        for i, link in enumerate(links, 1):
            self.status_queue.put(("status", f"Scraping article {i}/{len(links)}..."))
            time.sleep(random.uniform(2, 4))
            article = self.scrape_article(link)
            if article and article['content']:
                articles.append(article)
                self.db.save_article(article)
                self.queue.put(article)
                self.status_queue.put(("article", article))
                
        return articles
            
class NewsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("CNN News Reader")
        self.geometry("800x600")
        
        self.queue = queue.Queue()
        self.status_queue = queue.Queue()  # New queue for status updates
        self.db = NewsDatabase()
        self.scraper = CNNScraper(self.queue, self.status_queue)
        
        self.create_menu()
        self.create_widgets()
        
        # Start scraper thread
        self.scraper.start()
        
        # Start queue processing
        self.process_queues()
        
    def create_widgets(self):
        # Main container
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Status frame at top
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.pack(fill='x', pady=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(self.status_frame, text="Starting...")
        self.status_label.pack(side='left')
        
        # Progress frame
        self.progress_frame = ttk.Frame(self.main_frame)
        self.progress_frame.pack(fill='x', pady=(0, 10))
        
        # Progress label for latest article
        self.progress_label = ttk.Label(self.progress_frame, text="", wraplength=700)
        self.progress_label.pack(fill='x')
        
        # Flash card frame
        self.card_frame = ttk.Frame(self.main_frame)
        self.card_frame.pack(expand=True, fill='both')
        
        # Title label
        self.title_label = ttk.Label(self.card_frame, text="", wraplength=700)
        self.title_label.pack(pady=10)
        
        # Content text with scrollbar
        self.content_frame = ttk.Frame(self.card_frame)
        self.content_frame.pack(expand=True, fill='both', pady=10)
        
        self.content_text = tk.Text(self.content_frame, wrap=tk.WORD, height=20)
        self.content_text.pack(side='left', expand=True, fill='both')
        
        scrollbar = ttk.Scrollbar(self.content_frame, orient='vertical', 
                                command=self.content_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.content_text.configure(yscrollcommand=scrollbar.set)
        
        # URL button
        self.url_button = ttk.Button(self.card_frame, text="Open in Browser", 
                                   command=self.open_url)
        self.url_button.pack(pady=5)
        
        # Navigation buttons
        nav_frame = ttk.Frame(self.card_frame)
        nav_frame.pack(pady=10)
        
        self.prev_button = ttk.Button(nav_frame, text="Previous", 
                                    command=self.show_previous)
        self.prev_button.pack(side='left', padx=5)
        
        self.next_button = ttk.Button(nav_frame, text="Next", 
                                    command=self.show_next)
        self.next_button.pack(side='left', padx=5)
        
        # Initialize news data
        self.current_index = 0
        self.news_items = []
        self.load_news()


    def show_current_news(self):
        if not self.news_items:
            self.title_label.config(text="No news available")
            self.content_text.delete('1.0', tk.END)
            return
            
        news = self.news_items[self.current_index]
        self.title_label.config(text=news[1])  # title
        self.content_text.delete('1.0', tk.END)
        self.content_text.insert('1.0', news[2])  # content
        self.current_url = news[3]  # url

    def load_news(self):
        self.news_items = self.db.get_recent_news()
        if self.news_items:
            self.show_current_news()

    def show_previous(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_current_news()
            
    def show_next(self):
        if self.current_index < len(self.news_items) - 1:
            self.current_index += 1
            self.show_current_news()
            
    def open_url(self):
        if hasattr(self, 'current_url'):
            webbrowser.open(self.current_url)

    def create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Show News List", command=self.show_news_list)
        file_menu.add_command(label="Show Flash Cards", command=self.show_flash_cards)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit_app)
        
        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)


    def process_queues(self):
        # Process status queue
        try:
            while True:
                msg_type, msg = self.status_queue.get_nowait()
                if msg_type == "status":
                    self.status_label.config(text=msg)
                elif msg_type == "article":
                    self.progress_label.config(
                        text=f"Latest article: {msg['title'][:100]}..."
                    )
                    # Auto-show the latest article
                    if not self.news_items:
                        self.show_current_news()
        except queue.Empty:
            pass

        # Process article queue
        try:
            while True:
                article = self.queue.get_nowait()
                self.news_items.insert(0, (
                    None, article['title'], article['content'],
                    article['url'], article['date'], article['source']
                ))
                # Update the display if showing the first article
                if len(self.news_items) == 1:
                    self.show_current_news()
        except queue.Empty:
            pass
            
        # Schedule next queue check
        self.after(100, self.process_queues)

    def show_news_list(self):
        list_window = tk.Toplevel(self)
        list_window.title("News List")
        list_window.geometry("800x600")  # Made window larger
        
        # Create frame for treeview and scrollbar
        frame = ttk.Frame(list_window)
        frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Create Treeview
        tree = ttk.Treeview(frame, columns=('Title', 'Date'), show='headings')
        tree.heading('Title', text='Title')
        tree.heading('Date', text='Date')
        tree.column('Title', width=600)  # Made title column wider
        tree.column('Date', width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
        scrollbar.pack(side='right', fill='y')
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(expand=True, fill='both')
        
        # Populate with news items
        for news in self.news_items:
            tree.insert('', 0, values=(news[1], news[4]))  # Insert at top

        # Add double-click binding to open article
        def on_double_click(event):
            item = tree.selection()[0]
            item_index = tree.index(item)
            self.current_index = len(self.news_items) - 1 - item_index  # Reverse index
            self.show_current_news()
            list_window.destroy()
            
        tree.bind('<Double-1>', on_double_click)
            
    def show_flash_cards(self):
        self.card_frame.tkraise()
        
    def show_about(self):
        messagebox.showinfo("About", "CNN News Reader\nVersion 1.0")
        
    def process_queue(self):
        try:
            while True:
                article = self.queue.get_nowait()
                self.news_items.insert(0, (
                    None, article['title'], article['content'],
                    article['url'], article['date'], article['source']
                ))
        except queue.Empty:
            pass
        finally:
            self.after(1000, self.process_queue)
            
    def quit_app(self):
        self.scraper.stop()
        self.destroy()

if __name__ == "__main__":
    app = NewsApp()
    app.mainloop()



