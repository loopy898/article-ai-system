import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="None"):
         # 动态设置数据库路径
        if db_path is None:
            if os.path.exists('/data'):
                self.db_path = '/data/articles.db'  # Railway 持久化目录
            else:
                self.db_path = 'articles.db'  # 本地开发
        else:
            self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建文章表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT,
                content TEXT NOT NULL,
                summary TEXT,
                url TEXT UNIQUE,
                source TEXT,
                publish_date DATE,
                difficulty_level TEXT,
                difficulty_score REAL,
                category TEXT,
                tags TEXT,
                word_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建分类表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建标签表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建文章标签关联表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS article_tags (
                article_id INTEGER,
                tag_id INTEGER,
                FOREIGN KEY (article_id) REFERENCES articles (id),
                FOREIGN KEY (tag_id) REFERENCES tags (id),
                PRIMARY KEY (article_id, tag_id)
            )
        ''')
        
        # 插入默认分类
        default_categories = [
            ('Technology', '科技类文章'),
            ('Business', '商业类文章'),
            ('Health', '健康类文章'),
            ('Education', '教育类文章'),
            ('Culture', '文化类文章'),
            ('Politics', '政治类文章'),
            ('Environment', '环境类文章'),
            ('Sports', '体育类文章')
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)
        ''', default_categories)
        
        conn.commit()
        conn.close()
    
    def add_article(self, article_data):
        """添加文章到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO articles (
                    title, author, content, summary, url, source, 
                    publish_date, difficulty_level, difficulty_score, 
                    category, tags, word_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                article_data.get('title'),
                article_data.get('author'),
                article_data.get('content'),
                article_data.get('summary'),
                article_data.get('url'),
                article_data.get('source'),
                article_data.get('publish_date'),
                article_data.get('difficulty_level'),
                article_data.get('difficulty_score'),
                article_data.get('category'),
                article_data.get('tags'),
                article_data.get('word_count')
            ))
            
            article_id = cursor.lastrowid
            conn.commit()
            return article_id
            
        except sqlite3.IntegrityError:
            print(f"文章已存在: {article_data.get('url')}")
            return None
        finally:
            conn.close()
    
    def get_articles(self, limit=50, category=None, difficulty=None):
        """获取文章列表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM articles WHERE 1=1"
        params = []
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if difficulty:
            query += " AND difficulty_level = ?"
            params.append(difficulty)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        articles = cursor.fetchall()
        
        conn.close()
        return articles
    
    def get_article_by_id(self, article_id):
        """根据ID获取文章详情"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM articles WHERE id = ?", (article_id,))
        article = cursor.fetchone()
        
        conn.close()
        return article
    
    def search_articles(self, keyword, limit=20):
        """搜索文章"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM articles 
            WHERE title LIKE ? OR content LIKE ? OR summary LIKE ?
            ORDER BY created_at DESC LIMIT ?
        ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', limit))
        
        articles = cursor.fetchall()
        conn.close()
        return articles
    
    def get_categories(self):
        """获取所有分类"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM categories")
        categories = cursor.fetchall()
        
        conn.close()
        return categories
    
    def get_difficulty_stats(self):
        """获取难度统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT difficulty_level, COUNT(*) as count 
            FROM articles 
            WHERE difficulty_level IS NOT NULL
            GROUP BY difficulty_level
        ''')
        
        stats = cursor.fetchall()
        conn.close()
        return stats
