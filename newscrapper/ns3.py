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
import logging
import json

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('news_scraper.log')
    ]
)

class NewsDatabase:
    def __init__(self):
        self.db_path = 'news.db'
        self.lock = threading.Lock()  # Initialize lock first
        logging.info("Initializing database connection")
        self._create_connection()
        self.create_tables()
        
    def _create_connection(self):
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            logging.info("Database connection established")
        except sqlite3.Error as e:
            logging.error(f"Database connection error: {e}")
            raise

    def create_tables(self):
        try:
            with self.lock:  # Use lock for thread safety
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
            logging.info("Database tables created/verified")
        except sqlite3.Error as e:
            logging.error(f"Table creation error: {e}")
            raise

    def save_article(self, article):
        try:
            with self.lock:
                cursor = self.conn.cursor()
                # Check if article with same URL exists
                cursor.execute('SELECT id FROM news WHERE url = ?', (article['url'],))
                exists = cursor.fetchone()
                
                if not exists:
                    cursor.execute('''
                        INSERT INTO news (title, content, url, date, source)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (article['title'], article['content'], 
                          article['url'], article['date'], article['source']))
                    self.conn.commit()
                    logging.info(f"Saved new article: {article['title'][:50]}...")
                else:
                    logging.info(f"Article already exists: {article['title'][:50]}...")
        except sqlite3.Error as e:
            logging.error(f"Error saving article: {e}")
            self.conn.rollback()

        try:
            with self.lock:
                cursor = self.conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO news (title, content, url, date, source)
                    VALUES (?, ?, ?, ?, ?)
                ''', (article['title'], article['content'], 
                      article['url'], article['date'], article['source']))
                self.conn.commit()
            logging.info(f"Saved article: {article['title'][:50]}...")
        except sqlite3.Error as e:
            logging.error(f"Error saving article: {e}")
            self.conn.rollback()

    def get_recent_news(self, limit=50):
        try:
            with self.lock:
                cursor = self.conn.cursor()
                cursor.execute('''
                    SELECT * FROM news 
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (limit,))
                results = cursor.fetchall()
            logging.info(f"Retrieved {len(results)} recent articles")
            return results
        except sqlite3.Error as e:
            logging.error(f"Error fetching news: {e}")
            return []

    def __del__(self):
        try:
            if hasattr(self, 'conn') and hasattr(self, 'lock'):
                with self.lock:
                    self.conn.close()
                logging.info("Database connection closed")
        except Exception as e:
            logging.error(f"Error closing database: {e}")

            
class CNNScraper(threading.Thread):
    def __init__(self, queue, status_queue, db):  # Add db parameter
        threading.Thread.__init__(self)
        self.queue = queue
        self.status_queue = status_queue
        self.base_url = "https://www.cnn.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }
        self.db = db  # Use shared database instance
        self.running = True
        logging.info("CNN Scraper initialized")

    def get_article_links(self):
        try:
            sections = ['/world', '/politics', '/business', '/health']
            links = set()
            
            for section in sections:
                url = self.base_url + section
                logging.info(f"Fetching links from {url}")
                self.status_queue.put(("status", f"Checking {section} section..."))
                
                response = requests.get(url, headers=self.headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find container elements
                containers = soup.find_all(['div', 'article'], 
                    class_=['container__item', 'card', 'cd__content', 'container_lead-plus-headlines'])
                
                for container in containers:
                    for a in container.find_all('a', href=True):
                        href = a['href']
                        if href.startswith('/') and any(s in href for s in sections):
                            full_url = f"https://www.cnn.com{href}"
                            links.add(full_url)
                            logging.debug(f"Found link: {full_url}")

            links = list(links)
            logging.info(f"Total unique links found: {len(links)}")
            print(f"Found links: {links}")  # Terminal output
            return links

        except Exception as e:
            logging.error(f"Error getting article links: {e}")
            return []

    def scrape_article(self, url):
        try:
            logging.info(f"Scraping article: {url}")
            print(f"Scraping URL: {url}")  # Terminal output
            
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Title extraction
            title = ""
            title_selectors = ['h1', '.headline__text', '.article__title', '.article-title']
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = title_elem.text.strip()
                    break
            
            logging.info(f"Found title: {title[:50]}...")
            
            # Content extraction
            content = ""
            content_selectors = [
                '.article__content',
                '.article-body__content',
                '.body-text',
                '.zn-body__paragraph',
                '.article__main'
            ]
            
            for selector in content_selectors:
                content_elem = soup.select(selector)
                if content_elem:
                    paragraphs = []
                    for elem in content_elem:
                        paragraphs.extend(elem.find_all(['p', 'h2', 'h3']))
                    content = ' '.join([p.text.strip() for p in paragraphs if p.text.strip()])
                    if content:
                        break
            
            logging.info(f"Content length: {len(content)} characters")

            if title and content:
                article = {
                    'title': title,
                    'content': content,
                    'url': url,
                    'date': datetime.now().strftime("%Y-%m-%d"),
                    'source': 'CNN'
                }
                logging.info(f"Successfully scraped article: {title[:50]}...")
                return article
            else:
                logging.warning(f"Incomplete article - Title exists: {bool(title)}, Content exists: {bool(content)}")
                return None

        except Exception as e:
            logging.error(f"Error scraping article {url}: {e}")
            return None

    def scrape_cnn_news(self):
        articles = []
        links = self.get_article_links()
        
        if not links:
            msg = "No articles found. Retrying later..."
            logging.warning(msg)
            self.status_queue.put(("status", msg))
            return articles

        msg = f"Found {len(links)} articles to scrape"
        logging.info(msg)
        self.status_queue.put(("status", msg))
        
        for i, link in enumerate(links, 1):
            status_msg = f"Scraping article {i}/{len(links)}..."
            logging.info(status_msg)
            self.status_queue.put(("status", status_msg))
            
            time.sleep(random.uniform(2, 4))
            article = self.scrape_article(link)
            
            if article:
                articles.append(article)
                self.db.save_article(article)
                self.queue.put(article)
                self.status_queue.put(("article", article))
                logging.info(f"Article saved: {article['title'][:50]}...")
                print(f"Successfully scraped: {article['title'][:50]}...")
            
        return articles

    def run(self):
        while self.running:
            try:
                msg = "Starting to scrape CNN news..."
                logging.info(msg)
                self.status_queue.put(("status", msg))
                
                articles = self.scrape_cnn_news()
                
                if articles:
                    msg = f"Successfully scraped {len(articles)} articles"
                    logging.info(msg)
                    self.status_queue.put(("status", msg))
                else:
                    msg = "No articles scraped in this cycle"
                    logging.warning(msg)
                    self.status_queue.put(("status", msg))
                
                msg = "Waiting for next scrape cycle..."
                logging.info(msg)
                self.status_queue.put(("status", msg))
                
                time.sleep(300)  # 5 minutes between cycles
                
            except Exception as e:
                error_msg = f"Error in scraping cycle: {e}"
                logging.error(error_msg)
                self.status_queue.put(("status", error_msg))
                time.sleep(60)

    def stop(self):
        logging.info("Stopping CNN scraper")
        self.running = False

class ReutersScraper(threading.Thread):
    def __init__(self, queue, status_queue, db):
        threading.Thread.__init__(self)
        self.queue = queue
        self.status_queue = status_queue
        self.base_url = "https://www.reuters.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }
        self.db = db
        self.running = True
        logging.info("Reuters Scraper initialized")

    def get_article_links(self):
        try:
            sections = ['/world', '/business', '/technology']
            links = set()
            
            for section in sections:
                url = self.base_url + section
                logging.info(f"Fetching links from {url}")
                self.status_queue.put(("status", f"Checking Reuters {section} section..."))
                
                response = requests.get(url, headers=self.headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find article links - adjust selectors based on Reuters HTML structure
                articles = soup.find_all('a', href=True)
                for article in articles:
                    href = article['href']
                    if href.startswith('/') and any(s in href for s in sections):
                        full_url = f"https://www.reuters.com{href}"
                        links.add(full_url)
                        logging.debug(f"Found Reuters link: {full_url}")

            links = list(links)
            logging.info(f"Total Reuters links found: {len(links)}")
            return links

        except Exception as e:
            logging.error(f"Error getting Reuters article links: {e}")
            return []

    def scrape_article(self, url):
        try:
            logging.info(f"Scraping Reuters article: {url}")
            
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Title extraction - adjust selectors for Reuters
            title = ""
            title_elem = soup.find(['h1', 'h2'], class_=['article-header', 'article-title'])
            if title_elem:
                title = title_elem.text.strip()
            
            # Content extraction - adjust selectors for Reuters
            content = ""
            content_elem = soup.find(['div', 'article'], 
                                   class_=['article-body', 'article-text'])
            if content_elem:
                paragraphs = content_elem.find_all('p')
                content = ' '.join([p.text.strip() for p in paragraphs if p.text.strip()])
            
            if title and content:
                article = {
                    'title': title,
                    'content': content,
                    'url': url,
                    'date': datetime.now().strftime("%Y-%m-%d"),
                    'source': 'Reuters'
                }
                return article
            else:
                logging.warning(f"Incomplete Reuters article - Title exists: {bool(title)}, Content exists: {bool(content)}")
                return None

        except Exception as e:
            logging.error(f"Error scraping Reuters article {url}: {e}")
            return None

    def run(self):
        while self.running:
            try:
                msg = "Starting to scrape Reuters news..."
                logging.info(msg)
                self.status_queue.put(("status", msg))
                
                links = self.get_article_links()
                if not links:
                    continue

                for i, link in enumerate(links, 1):
                    if not self.running:
                        break
                        
                    status_msg = f"Scraping Reuters article {i}/{len(links)}..."
                    self.status_queue.put(("status", status_msg))
                    
                    article = self.scrape_article(link)
                    if article:
                        self.db.save_article(article)
                        self.queue.put(article)
                        self.status_queue.put(("article", article))
                
                time.sleep(300)  # 5 minutes between cycles
                
            except Exception as e:
                logging.error(f"Error in Reuters scraping cycle: {e}")
                time.sleep(60)

    def stop(self):
        logging.info("Stopping Reuters scraper")
        self.running = False

class NewsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.settings = self.load_config()  # Change from self.config to self.settings
        self.active_scrapers = {}
        self.queue = queue.Queue()
        self.status_queue = queue.Queue()
        self.db = NewsDatabase()
        
        # Initialize source states
        for source in self.settings["news_sources"]:  # Change here too
            source["active"] = True
            
        self.create_menu()
        self.create_widgets()
        self.start_scrapers()
        self.process_queues() 

    def load_config(self):
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            default_config = {
                "news_sources": [{"name": "CNN", 
                                "base_url": "https://www.cnn.com",
                                "sections": ["/world", "/politics", "/business", "/health"]}],
                "update_interval": 300,
                "max_articles": 50
            }
            with open('config.json', 'w') as f:
                json.dump(default_config, f, indent=4)
            return default_config

    def create_menu(self):
        menubar = tk.Menu(self)
        self.configure(menu=menubar)
        
        # File Menu (First)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Show News List", command=self.show_news_list)
        file_menu.add_command(label="Show Flash Cards", command=self.show_flash_cards)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit_app)
        
        # Sources Menu (Second)
        sources_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Sources", menu=sources_menu)
        
        # Create variables to track checkbutton states
        self.source_vars = {}
        for source in self.settings["news_sources"]:
            var = tk.BooleanVar(value=source["active"])
            self.source_vars[source["name"]] = var
            sources_menu.add_checkbutton(
                label=source["name"],
                variable=var,
                command=lambda s=source: self.toggle_source(s)
            )
        
        # View Menu (Third)
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Browser/Text View", command=self.toggle_view)
        
        # Help Menu (Last)
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        logging.info("Menu created")

    def toggle_source(self, source):
        source_name = source["name"]
        is_active = self.source_vars[source_name].get()
        source["active"] = is_active
        
        # Update configuration file
        with open('config.json', 'w') as f:
            json.dump(self.settings, indent=4, fp=f)  # Change here
            
        self.status_queue.put(("status", f"{'Enabled' if is_active else 'Disabled'} {source_name}"))
        self.restart_scrapers()

    def create_widgets(self):
        # Style configuration
        style = ttk.Style()
        style.configure("Title.TLabel", font=('Helvetica', 12, 'bold'))
        style.configure("Status.TLabel", font=('Helvetica', 10))
        
        # Main container
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Status frame at top
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.pack(fill='x', pady=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(self.status_frame, text="Starting...", 
                                    style="Status.TLabel")
        self.status_label.pack(side='left')
        
        # Progress frame
        self.progress_frame = ttk.Frame(self.main_frame)
        self.progress_frame.pack(fill='x', pady=(0, 10))
        
        # Progress label for latest article
        self.progress_label = ttk.Label(self.progress_frame, text="", 
                                    wraplength=700, style="Status.TLabel")
        self.progress_label.pack(fill='x')
        
        # Flash card frame
        self.card_frame = ttk.Frame(self.main_frame)
        self.card_frame.pack(expand=True, fill='both')
        
        # Title label
        self.title_label = ttk.Label(self.card_frame, text="", 
                                wraplength=700, style="Title.TLabel")
        self.title_label.pack(pady=10)

        # Content frame
        self.content_frame = ttk.Frame(self.card_frame)
        self.content_frame.pack(expand=True, fill='both', pady=10)
        
        # Text widget with scrollbar
        self.content_text = tk.Text(self.content_frame, wrap=tk.WORD, height=20,
                                font=('Helvetica', 10))
        self.content_text.pack(side='left', expand=True, fill='both')
        
        scrollbar = ttk.Scrollbar(self.content_frame, orient='vertical', 
                                command=self.content_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.content_text.configure(yscrollcommand=scrollbar.set)
        
        # HTML viewer frame
        self.html_frame = ttk.Frame(self.card_frame)
        self.html_view = tk.Text(self.html_frame, wrap=tk.WORD, 
                            font=('Helvetica', 10))
        html_scrollbar = ttk.Scrollbar(self.html_frame, orient='vertical', 
                                    command=self.html_view.yview)
        self.html_view.configure(yscrollcommand=html_scrollbar.set)
        
        self.html_view.pack(side='left', expand=True, fill='both')
        html_scrollbar.pack(side='right', fill='y')
        self.html_frame.pack(expand=True, fill='both')
        self.html_frame.pack_forget()  # Initially hidden

        # Navigation buttons frame - at the bottom
        self.nav_frame = ttk.Frame(self.card_frame)
        self.nav_frame.pack(side='bottom', pady=10)
        
        # URL button
        self.url_button = ttk.Button(self.nav_frame, text="Open in Browser", 
                                command=self.open_url)
        self.url_button.pack(side='left', padx=5)
        
        # Previous/Next buttons
        self.prev_button = ttk.Button(self.nav_frame, text="← Previous", 
                                    command=self.show_previous)
        self.prev_button.pack(side='left', padx=5)
        
        self.next_button = ttk.Button(self.nav_frame, text="Next →", 
                                    command=self.show_next)
        self.next_button.pack(side='left', padx=5)
        
        # Initialize news data
        self.current_index = 0
        self.news_items = []
        self.load_news()
        
        logging.info("GUI widgets created")

    def toggle_view(self):
        """Toggle between text and HTML view"""
        if self.content_frame.winfo_viewable():
            self.content_frame.pack_forget()
            self.html_frame.pack(expand=True, fill='both')
            if hasattr(self, 'current_url'):
                try:
                    response = requests.get(self.current_url)
                    self.html_view.delete('1.0', tk.END)
                    self.html_view.insert('1.0', response.text)
                except Exception as e:
                    self.html_view.delete('1.0', tk.END)
                    self.html_view.insert('1.0', f"Error loading content: {str(e)}")
        else:
            self.html_frame.pack_forget()
            self.content_frame.pack(expand=True, fill='both')
            

    def open_url(self):
        """Open the current URL in the default web browser"""
        if hasattr(self, 'current_url'):
            webbrowser.open(self.current_url)
            logging.info(f"Opening URL in external browser: {self.current_url}")

    def process_queues(self):
        # Process status queue
        try:
            while True:
                msg_type, msg = self.status_queue.get_nowait()
                if msg_type == "status":
                    self.status_label.config(text=msg)
                    logging.info(f"Status update: {msg}")
                elif msg_type == "article":
                    self.progress_label.config(
                        text=f"Latest article: {msg['title'][:100]}..."
                    )
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
                # Update navigation buttons whenever new articles are added
                self.update_navigation_buttons()
                if len(self.news_items) == 1:
                    self.show_current_news()
        except queue.Empty:
            pass
            
        self.after(100, self.process_queues)

    def update_navigation_buttons(self):
        # Enable/disable navigation buttons based on current position and total articles
        self.prev_button.state(['!disabled'] if self.current_index > 0 else ['disabled'])
        self.next_button.state(['!disabled'] if self.current_index < len(self.news_items) - 1 else ['disabled'])

    def show_current_news(self):
        if not self.news_items:
            self.title_label.config(text="No news available")
            self.content_text.delete('1.0', tk.END)
            self.update_navigation_buttons()
            return
            
        news = self.news_items[self.current_index]
        self.title_label.config(text=news[1])  # title
        self.content_text.delete('1.0', tk.END)
        self.content_text.insert('1.0', news[2])  # content
        self.current_url = news[3]  # url
        
        # Update navigation buttons
        self.update_navigation_buttons()
        logging.info(f"Displaying article: {news[1][:50]}...")


    def show_news_list(self):
        list_window = tk.Toplevel(self)
        list_window.title("News List")
        list_window.geometry("800x600")
        
        # Create main frame
        main_frame = ttk.Frame(list_window, padding="10")
        main_frame.pack(expand=True, fill='both')
        
        # Add source filter combobox
        filter_frame = ttk.Frame(main_frame)
        filter_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(filter_frame, text="Filter by source:").pack(side='left', padx=(0, 5))
        
        active_sources = [source["name"] for source in self.settings["news_sources"]  # Change here
                         if source["active"]]
        source_filter = ttk.Combobox(filter_frame, values=["All"] + active_sources)
        source_filter.set("All")
        source_filter.pack(side='left')
        
        # Create Treeview
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(expand=True, fill='both')
        
        columns = ('Title', 'Date', 'Source')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        tree.heading('Title', text='Title')
        tree.heading('Date', text='Date')
        tree.heading('Source', text='Source')
        tree.column('Title', width=500)
        tree.column('Date', width=100)
        tree.column('Source', width=100)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', expand=True, fill='both')
        scrollbar.pack(side='right', fill='y')
        
        def update_list(*args):
            tree.delete(*tree.get_children())
            selected_source = source_filter.get()
            filtered_news = (self.filter_news_by_source(selected_source) 
                           if selected_source != "All" else self.news_items)
            
            for news in filtered_news:
                tree.insert('', 0, values=(news[1], news[4], news[5]))
        
        source_filter.bind('<<ComboboxSelected>>', update_list)
        update_list()  # Initial population
        
        def on_select(event):
            selected_item = tree.selection()[0]
            selected_values = tree.item(selected_item)['values']
            
            # Find the corresponding news item
            for i, news in enumerate(self.news_items):
                if (news[1] == selected_values[0] and 
                    news[4] == selected_values[1] and 
                    news[5] == selected_values[2]):
                    self.current_index = i
                    self.show_current_news()
                    break
        
        tree.bind('<<TreeviewSelect>>', on_select)

    def quit_app(self):
        """Clean shutdown of the application."""
        logging.info("Application shutting down")
        self.stop_scrapers()
        self.save_config()
        self.destroy()

    def save_config(self):
        try:
            with open('config.json', 'w') as f:
                json.dump(self.settings, f, indent=4)  # Change here
            logging.info("Configuration saved")
        except Exception as e:
            logging.error(f"Error saving configuration: {e}")

    def load_news(self):
        self.news_items = self.db.get_recent_news()
        if self.news_items:
            self.show_current_news()
        logging.info(f"Loaded {len(self.news_items)} articles from database")

    def start_source_scraper(self, source):
        """Start a scraper thread for a specific source."""
        if source["name"] not in self.active_scrapers:
            if source["name"] == "CNN":
                scraper = CNNScraper(self.queue, self.status_queue, self.db)
            elif source["name"] == "Reuters":
                scraper = ReutersScraper(self.queue, self.status_queue, self.db)
            else:
                logging.warning(f"Unknown source type: {source['name']}")
                return
            
            scraper.start()
            self.active_scrapers[source["name"]] = scraper
            logging.info(f"Started scraper for {source['name']}")

    def restart_scrapers(self):
        """Restart all scraper threads based on active sources."""
        self.stop_scrapers()
        self.start_scrapers()
        logging.info("Restarted scrapers with new configuration")

    def stop_scrapers(self):
        """Stop all active scraper threads."""
        for name, scraper in self.active_scrapers.items():
            logging.info(f"Stopping scraper: {name}")
            scraper.stop()
            scraper.join(timeout=1)  # Wait for thread to finish
            
        self.active_scrapers.clear()

    def start_scrapers(self):
        """Start scraper threads for all active sources."""
        for source in self.settings["news_sources"]:
            if source["active"]:
                self.start_source_scraper(source)

    def filter_news_by_source(self, source_name=None):
        """Filter news items by source."""
        if source_name:
            return [news for news in self.news_items if news[5] == source_name]
        return self.news_items
    
    def show_previous(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_current_news()

    def show_next(self):
        if self.current_index < len(self.news_items) - 1:
            self.current_index += 1
            self.show_current_news()

    def show_flash_cards(self):
        self.card_frame.tkraise()
        logging.info("Switched to flash card view")

    def show_about(self):
        messagebox.showinfo("About", 
            "News Reader\nVersion 1.0\n\n"
            "A news reader application that scrapes and displays "
            "articles from multiple sources including CNN and Reuters.")
        logging.info("Showed about dialog")


if __name__ == "__main__":
    try:
        app = NewsApp()
        app.mainloop()
    except Exception as e:
        logging.error(f"Application error: {e}", exc_info=True)