import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin, urlparse
from datetime import datetime
import json
from database import DatabaseManager
import feedparser

class ArticleCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.db = DatabaseManager()
        
    def crawl_bbc_news(self, max_articles=20):
        """爬取BBC News文章"""
        print("开始爬取BBC News...")
        articles = []
        
        # BBC News主要页面
        urls = [
            'https://www.bbc.com/news',
            'https://www.bbc.com/news/technology',
            'https://www.bbc.com/news/business',
            'https://www.bbc.com/news/health',
            'https://www.bbc.com/news/science-environment'
        ]
        
        for url in urls:
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 查找文章链接
                article_links = []
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if '/news/' in href and href not in article_links:
                        full_url = urljoin('https://www.bbc.com', href)
                        if self._is_valid_article_url(full_url):
                            article_links.append(full_url)
                
                # 爬取每篇文章
                for article_url in article_links[:max_articles//len(urls)]:
                    try:
                        article = self._crawl_bbc_article(article_url)
                        if article:
                            articles.append(article)
                            time.sleep(1)  # 避免请求过快
                    except Exception as e:
                        print(f"爬取文章失败 {article_url}: {e}")
                        continue
                        
            except Exception as e:
                print(f"爬取页面失败 {url}: {e}")
                continue
        
        return articles
    
    def _crawl_bbc_article(self, url):
        """爬取单篇BBC文章"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 提取标题
            title_elem = soup.find('h1', {'data-testid': 'headline'}) or soup.find('h1', class_='story-headline')
            if not title_elem:
                return None
            title = title_elem.get_text().strip()
            
            # 提取内容
            content_elem = soup.find('div', {'data-testid': 'story-body'}) or soup.find('div', class_='story-body')
            if not content_elem:
                return None
            
            # 提取段落文本
            paragraphs = content_elem.find_all('p')
            content = '\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
            
            if len(content) < 200:  # 内容太短，跳过
                return None
            
            # 提取作者
            author_elem = soup.find('span', {'data-testid': 'byline'}) or soup.find('span', class_='byline')
            author = author_elem.get_text().strip() if author_elem else "BBC News"
            
            # 提取发布日期
            date_elem = soup.find('time', {'data-testid': 'timestamp'}) or soup.find('time')
            publish_date = None
            if date_elem:
                date_str = date_elem.get('datetime') or date_elem.get_text()
                try:
                    publish_date = datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
                except:
                    publish_date = datetime.now().date()
            
            # 确定分类
            category = self._determine_category_from_url(url)
            
            article_data = {
                'title': title,
                'author': author,
                'content': content,
                'url': url,
                'source': 'BBC News',
                'publish_date': publish_date,
                'category': category,
                'word_count': len(content.split())
            }
            
            return article_data
            
        except Exception as e:
            print(f"解析文章失败 {url}: {e}")
            return None
    
    def crawl_cnn_news(self, max_articles=20):
        """爬取CNN News文章"""
        print("开始爬取CNN News...")
        articles = []
        
        # CNN主要页面
        urls = [
            'https://edition.cnn.com/',
            'https://edition.cnn.com/business',
            'https://edition.cnn.com/health',
            'https://edition.cnn.com/tech',
            'https://edition.cnn.com/world'
        ]
        
        for url in urls:
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 查找文章链接
                article_links = []
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if '/2024/' in href and href not in article_links:
                        full_url = urljoin('https://edition.cnn.com', href)
                        if self._is_valid_article_url(full_url):
                            article_links.append(full_url)
                
                # 爬取每篇文章
                for article_url in article_links[:max_articles//len(urls)]:
                    try:
                        article = self._crawl_cnn_article(article_url)
                        if article:
                            articles.append(article)
                            time.sleep(1)
                    except Exception as e:
                        print(f"爬取文章失败 {article_url}: {e}")
                        continue
                        
            except Exception as e:
                print(f"爬取页面失败 {url}: {e}")
                continue
        
        return articles
    
    def _crawl_cnn_article(self, url):
        """爬取单篇CNN文章"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 提取标题
            title_elem = soup.find('h1', class_='headline__text') or soup.find('h1')
            if not title_elem:
                return None
            title = title_elem.get_text().strip()
            
            # 提取内容
            content_elem = soup.find('div', class_='article__content') or soup.find('div', class_='l-container')
            if not content_elem:
                return None
            
            paragraphs = content_elem.find_all('p')
            content = '\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
            
            if len(content) < 200:
                return None
            
            # 提取作者
            author_elem = soup.find('span', class_='metadata__byline__author')
            author = author_elem.get_text().strip() if author_elem else "CNN"
            
            # 提取发布日期
            date_elem = soup.find('div', class_='update-time')
            publish_date = datetime.now().date()
            if date_elem:
                date_text = date_elem.get_text()
                # 简单的日期解析
                if 'hours ago' in date_text or 'minutes ago' in date_text:
                    publish_date = datetime.now().date()
            
            category = self._determine_category_from_url(url)
            
            article_data = {
                'title': title,
                'author': author,
                'content': content,
                'url': url,
                'source': 'CNN',
                'publish_date': publish_date,
                'category': category,
                'word_count': len(content.split())
            }
            
            return article_data
            
        except Exception as e:
            print(f"解析文章失败 {url}: {e}")
            return None
    
    def _is_valid_article_url(self, url):
        """检查URL是否为有效的文章链接"""
        if not url:
            return False
        
        # 排除非文章页面
        exclude_patterns = [
            '/video/', '/live/', '/gallery/', '/interactive/',
            '/weather/', '/sport/', '/entertainment/',
            '/travel/', '/style/', '/food/'
        ]
        
        for pattern in exclude_patterns:
            if pattern in url:
                return False
        
        # 确保是文章页面
        return '/news/' in url or '/2024/' in url
    
    def _determine_category_from_url(self, url):
        """根据URL确定文章分类"""
        url_lower = url.lower()
        
        if 'technology' in url_lower or 'tech' in url_lower:
            return 'Technology'
        elif 'business' in url_lower or 'economy' in url_lower:
            return 'Business'
        elif 'health' in url_lower or 'medical' in url_lower:
            return 'Health'
        elif 'science' in url_lower or 'environment' in url_lower:
            return 'Environment'
        elif 'politics' in url_lower or 'political' in url_lower:
            return 'Politics'
        elif 'sport' in url_lower or 'sports' in url_lower:
            return 'Sports'
        else:
            return 'Culture'
    
    def crawl_all_sources(self, max_articles_per_source=20):
        """爬取所有源的文章"""
        all_articles = []
        
        # 优先使用稳定的 RSS 源
        rss_sources = [
            # BBC - 多个分类
            ("BBC News", "http://feeds.bbci.co.uk/news/rss.xml", "Politics"),
            ("BBC World", "http://feeds.bbci.co.uk/news/world/rss.xml", "Politics"),
            ("BBC Business", "http://feeds.bbci.co.uk/news/business/rss.xml", "Business"),
            ("BBC Technology", "http://feeds.bbci.co.uk/news/technology/rss.xml", "Technology"),
            ("BBC Health", "http://feeds.bbci.co.uk/news/health/rss.xml", "Health"),
            ("BBC Science", "http://feeds.bbci.co.uk/news/science_and_environment/rss.xml", "Environment"),
            ("BBC Education", "http://feeds.bbci.co.uk/news/education/rss.xml", "Education"),
            
            # CNN - 多个分类
            ("CNN Top Stories", "http://rss.cnn.com/rss/edition.rss", "Politics"),
            ("CNN World", "http://rss.cnn.com/rss/edition_world.rss", "Politics"),
            ("CNN Business", "http://rss.cnn.com/rss/money_news_international.rss", "Business"),
            ("CNN Technology", "http://rss.cnn.com/rss/edition_technology.rss", "Technology"),
            ("CNN Health", "http://rss.cnn.com/rss/edition_health.rss", "Health"),
            
            # The Guardian - 多个分类
            ("The Guardian World", "https://www.theguardian.com/world/rss", "Politics"),
            ("The Guardian Business", "https://www.theguardian.com/business/rss", "Business"),
            ("The Guardian Technology", "https://www.theguardian.com/technology/rss", "Technology"),
            ("The Guardian Environment", "https://www.theguardian.com/environment/rss", "Environment"),
            ("The Guardian Education", "https://www.theguardian.com/education/rss", "Education"),
            ("The Guardian Culture", "https://www.theguardian.com/culture/rss", "Culture"),
            ("The Guardian Sport", "https://www.theguardian.com/sport/rss", "Sports"),
            ("The Guardian Science", "https://www.theguardian.com/science/rss", "Environment"),
            
            # Reuters - 多个分类
            ("Reuters World", "https://www.reuters.com/rssFeed/worldNews", "Politics"),
            ("Reuters Business", "https://www.reuters.com/rssFeed/businessNews", "Business"),
            ("Reuters Technology", "https://www.reuters.com/rssFeed/technologyNews", "Technology"),
            ("Reuters Health", "https://www.reuters.com/rssFeed/healthNews", "Health"),
            ("Reuters Environment", "https://www.reuters.com/rssFeed/environmentNews", "Environment"),
            ("Reuters Sports", "https://www.reuters.com/rssFeed/sportsNews", "Sports"),
            
            # NPR - 多个分类
            ("NPR News", "https://feeds.npr.org/1001/rss.xml", "Politics"),
            ("NPR World", "https://feeds.npr.org/1004/rss.xml", "Politics"),
            ("NPR Business", "https://feeds.npr.org/1006/rss.xml", "Business"),
            ("NPR Technology", "https://feeds.npr.org/1019/rss.xml", "Technology"),
            ("NPR Health", "https://feeds.npr.org/1128/rss.xml", "Health"),
            ("NPR Education", "https://feeds.npr.org/1013/rss.xml", "Education"),
            ("NPR Science", "https://feeds.npr.org/1007/rss.xml", "Environment"),
            
            # Associated Press
            ("Associated Press", "https://feeds.apnews.com/rss/apf-topnews", "Politics"),
            ("AP Business", "https://feeds.apnews.com/rss/apf-business", "Business"),
            ("AP Technology", "https://feeds.apnews.com/rss/apf-technology", "Technology"),
            ("AP Health", "https://feeds.apnews.com/rss/apf-health", "Health"),
            ("AP Sports", "https://feeds.apnews.com/rss/apf-sports", "Sports"),
            
            # TIME Magazine
            ("TIME", "https://feeds.feedburner.com/time/topstories", "Politics"),
            ("TIME Business", "https://feeds.feedburner.com/time/business", "Business"),
            ("TIME Health", "https://feeds.feedburner.com/time/health", "Health"),
            ("TIME Science", "https://feeds.feedburner.com/time/science", "Environment"),
            
            # Newsweek
            ("Newsweek", "https://www.newsweek.com/rss", "Politics"),
            ("Newsweek Tech", "https://www.newsweek.com/tech-science/rss", "Technology"),
            ("Newsweek Health", "https://www.newsweek.com/health/rss", "Health"),
            
            # The Economist
            ("The Economist", "https://www.economist.com/rss", "Business"),
            
            # 科技类专业媒体
            ("TechCrunch", "https://techcrunch.com/feed/", "Technology"),
            ("Wired", "https://www.wired.com/feed/rss", "Technology"),
            ("Ars Technica", "http://feeds.arstechnica.com/arstechnica/index", "Technology"),
            ("The Verge", "https://www.theverge.com/rss/index.xml", "Technology"),
            ("MIT Technology Review", "https://www.technologyreview.com/feed/", "Technology"),
            ("Engadget", "https://www.engadget.com/rss.xml", "Technology"),
            ("ZDNet", "https://www.zdnet.com/news/rss.xml", "Technology"),
            
            # 商业类专业媒体
            ("Forbes", "https://www.forbes.com/real-time/feed2/", "Business"),
            ("Business Insider", "https://www.businessinsider.com/rss", "Business"),
            ("Financial Times", "https://www.ft.com/rss/home", "Business"),
            ("Harvard Business Review", "https://hbr.org/feed", "Business"),
            ("Bloomberg", "https://feeds.bloomberg.com/markets/news.rss", "Business"),
            ("Wall Street Journal", "https://feeds.a.dj.com/rss/RSSWorldNews.xml", "Business"),
            ("MarketWatch", "https://feeds.marketwatch.com/marketwatch/topstories/", "Business"),
            
            # 科学健康类
            ("Scientific American", "http://rss.sciam.com/ScientificAmerican-Global", "Environment"),
            ("Nature News", "https://www.nature.com/nature.rss", "Environment"),
            ("New Scientist", "https://www.newscientist.com/feed/home/", "Environment"),
            ("Science Magazine", "https://www.science.org/rss/news_current.xml", "Environment"),
            ("WebMD Health News", "https://www.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC", "Health"),
            ("Medical News Today", "https://www.medicalnewstoday.com/rss", "Health"),
            ("Healthline", "https://www.healthline.com/rss", "Health"),
            
            # 教育类
            ("Education Week", "https://www.edweek.org/feed", "Education"),
            ("Chronicle of Higher Education", "https://www.chronicle.com/section/News/6/rss", "Education"),
            ("Inside Higher Ed", "https://www.insidehighered.com/rss.xml", "Education"),
            
            # 环境类
            ("Environmental News Network", "https://www.enn.com/rss", "Environment"),
            ("Climate Central", "https://www.climatecentral.org/rss.xml", "Environment"),
            ("National Geographic", "https://www.nationalgeographic.com/pages/article/feeds", "Environment"),
            
            # 文化类
            ("Smithsonian Magazine", "https://www.smithsonianmag.com/rss/latest_articles/", "Culture"),
            ("The New Yorker", "https://www.newyorker.com/feed/news", "Culture"),
            ("The Atlantic", "https://www.theatlantic.com/feed/all/", "Culture"),
            ("Slate", "https://slate.com/feeds/all.rss", "Culture"),
            ("Vox", "https://www.vox.com/rss/index.xml", "Culture"),
            
            # 体育类
            ("ESPN", "https://www.espn.com/espn/rss/news", "Sports"),
            ("Sports Illustrated", "https://www.si.com/rss/si_topstories.rss", "Sports"),
            ("BBC Sport", "http://feeds.bbci.co.uk/sport/rss.xml", "Sports"),
            ("CNN Sports", "http://rss.cnn.com/rss/edition_sport.rss", "Sports"),
            
            # 国际媒体
            ("Al Jazeera", "https://www.aljazeera.com/xml/rss/all.xml", "Politics"),
            ("Deutsche Welle", "https://rss.dw.com/rdf/rss-en-all", "Politics"),
            ("France 24", "https://www.france24.com/en/rss", "Politics"),
            ("RT News", "https://www.rt.com/rss/", "Politics"),
            
            # 其他优质源
            ("Politico", "https://www.politico.com/rss/politicopicks.xml", "Politics"),
            ("The Hill", "https://thehill.com/news/feed/", "Politics"),
            ("Foreign Affairs", "https://www.foreignaffairs.com/rss.xml", "Politics"),
            ("Foreign Policy", "https://foreignpolicy.com/feed/", "Politics")
        ]

        for source_name, rss_url, default_category in rss_sources:
            try:
                articles = self.crawl_rss_feed(rss_url, source_name, default_category, max_articles_per_source)
                all_articles.extend(articles)
            except Exception as e:
                print(f"RSS源失败 {source_name}: {e}")
                continue
        
        print(f"总共爬取到 {len(all_articles)} 篇文章")
        return all_articles

    def crawl_rss_feed(self, rss_url, source_name, default_category, max_articles=50):
        """基于RSS稳定抓取文章列表并获取正文"""
        print(f"开始爬取RSS: {source_name}")
        feed = feedparser.parse(rss_url)
        articles = []
        
        for entry in feed.entries[:max_articles]:
            try:
                title = entry.title if hasattr(entry, 'title') else ''
                link = entry.link if hasattr(entry, 'link') else ''
                author = getattr(entry, 'author', source_name)
                published = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6]).date()
                
                # 抓正文页面，容错尽量简单
                content_text = self._download_article_text(link)
                if not content_text or len(content_text) < 200:
                    # RSS摘要兜底
                    summary = getattr(entry, 'summary', '')
                    content_text = summary if len(summary) > 200 else None
                
                if not content_text:
                    continue
                
                category = default_category
                article_data = {
                    'title': title,
                    'author': author,
                    'content': content_text,
                    'url': link,
                    'source': source_name,
                    'publish_date': published,
                    'category': category,
                    'word_count': len(content_text.split())
                }
                articles.append(article_data)
                time.sleep(0.2)
            except Exception as e:
                print(f"解析RSS文章失败 {source_name}: {e}")
                continue
        
        return articles

    def _download_article_text(self, url):
        """下载页面并尽量抽取正文（通用兜底版）"""
        try:
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, 'html.parser')
            # 常见正文容器兜底
            selectors = [
                'article',
                'div.article__content',
                'div.c-article-content',
                'div#content',
                'div.entry-content',
                'section.article-body',
                'div.l-container'
            ]
            texts = []
            for sel in selectors:
                node = soup.select_one(sel)
                if node:
                    ps = node.find_all(['p','li'])
                    texts = [p.get_text().strip() for p in ps if p.get_text().strip()]
                    if len(' '.join(texts)) > 200:
                        break
            if not texts:
                # 全页兜底
                ps = soup.find_all('p')
                texts = [p.get_text().strip() for p in ps if p.get_text().strip()]
            return '\n'.join(texts)
        except Exception:
            return None
    
    def save_articles_to_db(self, articles):
        """将文章保存到数据库"""
        saved_count = 0
        for article in articles:
            article_id = self.db.add_article(article)
            if article_id:
                saved_count += 1
        
        print(f"成功保存 {saved_count} 篇文章到数据库")
        return saved_count

if __name__ == "__main__":
    crawler = ArticleCrawler()
    articles = crawler.crawl_all_sources(max_articles_per_source=15)
    crawler.save_articles_to_db(articles)
