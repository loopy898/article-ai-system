#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量预填充文章数据脚本：
从6个稳定的RSS源各抓取最多50篇，执行难度/摘要/分类并入库。
运行：
  .\.venv311\Scripts\activate
  python prefill.py
"""

from crawler import ArticleCrawler
from difficulty_analyzer import DifficultyAnalyzer
from summarizer import ArticleSummarizer
from classifier import ArticleClassifier

# 统一的RSS源与目标分类（每源抓取定额）
RSS_SOURCES = [
    ("The Economist", "https://www.economist.com/sections/business-finance/rss.xml", "Business"),
    ("The Economist", "https://www.economist.com/science-and-technology/rss.xml", "Technology"),
    ("The Economist", "https://www.economist.com/international/rss.xml", "Politics"),
    ("The New Yorker", "https://www.newyorker.com/feed/news", "Culture"),
    ("TIME", "https://time.com/feed/", "Politics"),
    ("Harvard Business Review", "https://hbr.org/feed", "Business"),
    ("National Geographic", "https://www.nationalgeographic.com/content/natgeo/en_us/rss/index.rss", "Environment"),
    ("Scientific American", "https://www.scientificamerican.com/feed/", "Technology"),
    ("The New York Times", "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml", "Politics"),
    ("The New York Times", "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml", "Business"),
    ("The New York Times", "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml", "Technology"),
    ("The New York Times", "https://rss.nytimes.com/services/xml/rss/nyt/Science.xml", "Environment"),
]

TARGET_PER_SOURCE = 50  # 每源定额，可按需调整

def main():
    crawler = ArticleCrawler()
    analyzer = DifficultyAnalyzer()
    summarizer = ArticleSummarizer()
    classifier = ArticleClassifier()

    # 分源抓取：每源各取 TARGET_PER_SOURCE
    articles = []
    for source_name, rss_url, default_category in RSS_SOURCES:
        print(f"[预填] 抓取 {source_name} ...")
        try:
            batch = crawler.crawl_rss_feed(rss_url, source_name, default_category, max_articles=TARGET_PER_SOURCE)
            articles.extend(batch)
        except Exception as e:
            print(f"[预填] 源失败 {source_name}: {e}")
            continue

    processed = []
    for article in articles:
        try:
            diff = analyzer.analyze_difficulty(article['content'])
            article['difficulty_level'] = diff['difficulty_level']
            article['difficulty_score'] = diff['difficulty_score']

            article['summary'] = summarizer.generate_summary(article['content'], sentences_count=3)

            category = classifier.classify_article(article['title'], article['content'], article['url'])
            article['category'] = category or article.get('category')
            article['tags'] = ', '.join(classifier.extract_tags(article['title'], article['content']))
            processed.append(article)
        except Exception:
            continue

    saved = crawler.save_articles_to_db(processed)
    print(f"预填完成，共处理 {len(processed)} 篇，保存 {saved} 篇。")

if __name__ == '__main__':
    main()


