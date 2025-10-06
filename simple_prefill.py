#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版数据预填充脚本
专注于快速获取大量文章，不进行复杂处理
"""

import sys
import time
from crawler import ArticleCrawler
from database import DatabaseManager

def main():
    """主函数 - 快速批量爬取文章"""
    print("=" * 60)
    print("外刊推荐系统 - 简化版数据预填充")
    print("=" * 60)
    
    # 初始化组件
    print("初始化系统组件...")
    crawler = ArticleCrawler()
    db = DatabaseManager()
    
    # 检查当前文章数量
    current_articles = db.get_articles(limit=10000)
    print(f"当前数据库中有 {len(current_articles)} 篇文章")
    
    target_articles = 500  # 目标文章数量
    if len(current_articles) >= target_articles:
        print(f"已达到目标文章数量 ({target_articles} 篇)")
        show_statistics(db)
        return
    
    needed_articles = target_articles - len(current_articles)
    print(f"需要爬取 {needed_articles} 篇文章")
    
    # 执行爬取
    total_crawled = 0
    batch_count = 0
    
    while total_crawled < needed_articles:
        batch_count += 1
        print(f"\n开始第 {batch_count} 批爬取...")
        
        # 每批爬取更多文章
        articles_per_source = max(3, min(10, (needed_articles - total_crawled) // 20))
        print(f"每个源爬取 {articles_per_source} 篇文章...")
        
        try:
            # 爬取文章
            articles = crawler.crawl_all_sources(max_articles_per_source=articles_per_source)
            print(f"本批爬取到 {len(articles)} 篇文章")
            
            if not articles:
                print("本批未获取到新文章，等待后重试...")
                time.sleep(10)
                continue
            
            # 保存文章
            saved_count = crawler.save_articles_to_db(articles)
            total_crawled += saved_count
            
            print(f"批次 {batch_count} 完成 - 新增: {saved_count} 篇")
            print(f"总进度: {total_crawled + len(current_articles)}/{target_articles}")
            
            # 检查是否达到目标
            if total_crawled >= needed_articles:
                break
                
            # 批次间短暂休息
            if total_crawled < needed_articles:
                print("等待 10 秒后继续...")
                time.sleep(10)
                
        except KeyboardInterrupt:
            print("\n用户中断，正在保存当前进度...")
            break
        except Exception as e:
            print(f"批次处理出错: {e}")
            print("等待 30 秒后重试...")
            time.sleep(30)
            continue
    
    # 最终统计
    print(f"\n" + "=" * 60)
    print("数据预填充完成！")
    show_statistics(db)
    print("=" * 60)

def show_statistics(db):
    """显示数据库统计信息"""
    final_articles = db.get_articles(limit=10000)
    print(f"最终文章数量: {len(final_articles)} 篇")
    
    # 统计各分类文章数量
    print("\n各分类文章统计:")
    categories = {}
    sources = {}
    
    for article in final_articles:
        # 处理元组格式的数据
        if isinstance(article, tuple):
            # 假设数据库返回的是元组格式 (id, title, author, content, url, source, publish_date, category, ...)
            category = article[7] if len(article) > 7 and article[7] else '未分类'
            source = article[5] if len(article) > 5 and article[5] else '未知来源'
        else:
            # 字典格式
            category = article.get('category', '未分类')
            source = article.get('source', '未知来源')
        
        categories[category] = categories.get(category, 0) + 1
        sources[source] = sources.get(source, 0) + 1
    
    for category, count in sorted(categories.items()):
        print(f"  {category}: {count} 篇")
    
    print(f"\n共有 {len(sources)} 个不同来源:")
    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {source}: {count} 篇")
    
    if len(sources) > 10:
        print(f"  ... 还有 {len(sources) - 10} 个其他来源")

def quick_crawl():
    """快速爬取模式 - 获取少量文章用于测试"""
    print("快速爬取模式...")
    
    crawler = ArticleCrawler()
    db = DatabaseManager()
    
    # 选择几个可靠的源进行快速爬取
    reliable_sources = [
        ("BBC News", "http://feeds.bbci.co.uk/news/rss.xml", "Politics"),
        ("BBC Technology", "http://feeds.bbci.co.uk/news/technology/rss.xml", "Technology"),
        ("BBC Business", "http://feeds.bbci.co.uk/news/business/rss.xml", "Business"),
        ("The Guardian World", "https://www.theguardian.com/world/rss", "Politics"),
        ("The Guardian Technology", "https://www.theguardian.com/technology/rss", "Technology"),
        ("NPR News", "https://feeds.npr.org/1001/rss.xml", "Politics"),
        ("TechCrunch", "https://techcrunch.com/feed/", "Technology"),
        ("Scientific American", "http://rss.sciam.com/ScientificAmerican-Global", "Environment"),
    ]
    
    all_articles = []
    for source_name, rss_url, category in reliable_sources:
        try:
            print(f"爬取 {source_name}...")
            articles = crawler.crawl_rss_feed(rss_url, source_name, category, max_articles=5)
            all_articles.extend(articles)
            print(f"  获得 {len(articles)} 篇文章")
            time.sleep(1)
        except Exception as e:
            print(f"  失败: {e}")
    
    # 保存文章
    saved_count = crawler.save_articles_to_db(all_articles)
    print(f"\n快速爬取完成，保存 {saved_count} 篇文章")
    
    # 显示统计
    show_statistics(db)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        quick_crawl()
    else:
        main()