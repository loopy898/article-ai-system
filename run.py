#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
外刊推荐系统启动脚本
"""

import os
import sys
import subprocess
import time
from database import DatabaseManager
from crawler import ArticleCrawler
from difficulty_analyzer import DifficultyAnalyzer
from summarizer import ArticleSummarizer
from classifier import ArticleClassifier

def check_dependencies():
    """检查依赖包是否安装"""
    # pip 名称与 import 名称映射
    package_import_map = {
        'requests': 'requests',
        'beautifulsoup4': 'bs4',
        'lxml': 'lxml',
        'flask': 'flask',
        'flask-cors': 'flask_cors',
        'textstat': 'textstat',
        'sumy': 'sumy',
        'nltk': 'nltk',
        'scikit-learn': 'sklearn',
        'jieba': 'jieba',
        'pandas': 'pandas',
        'numpy': 'numpy'
    }
    
    missing_packages = []
    for pip_name, import_name in package_import_map.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(pip_name)
    
    if missing_packages:
        print("❌ 缺少以下依赖包:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n请运行以下命令安装依赖:")
        print("pip install -r requirements.txt")
        return False
    
    print("✅ 所有依赖包已安装")
    return True

def initialize_system():
    """初始化系统"""
    print("🚀 正在初始化外刊推荐系统...")
    
    # 初始化数据库
    print("📊 初始化数据库...")
    db = DatabaseManager()
    print("✅ 数据库初始化完成")
    
    # 测试各个组件
    print("🔧 测试系统组件...")
    
    try:
        # 测试难度分析器
        analyzer = DifficultyAnalyzer()
        test_text = "This is a test article for difficulty analysis."
        result = analyzer.analyze_difficulty(test_text)
        print("✅ 难度分析器测试通过")
        
        # 测试摘要生成器
        summarizer = ArticleSummarizer()
        summary = summarizer.generate_summary(test_text, sentences_count=1)
        print("✅ 摘要生成器测试通过")
        
        # 测试分类器
        classifier = ArticleClassifier()
        category = classifier.classify_article("AI Technology News", test_text)
        print("✅ 分类器测试通过")
        
        # 测试爬虫
        crawler = ArticleCrawler()
        print("✅ 爬虫组件测试通过")
        
    except Exception as e:
        print(f"❌ 组件测试失败: {e}")
        return False
    
    print("✅ 系统初始化完成")
    return True

def crawl_initial_data():
    """爬取初始数据"""
    print("🕷️ 开始爬取初始文章数据...")
    
    try:
        crawler = ArticleCrawler()
        # 在本函数内实例化分析/摘要/分类器，避免 NameError
        analyzer = DifficultyAnalyzer()
        summarizer = ArticleSummarizer()
        classifier = ArticleClassifier()
        
        # 爬取少量文章进行测试
        print("正在从BBC News爬取文章...")
        bbc_articles = crawler.crawl_bbc_news(max_articles=5)
        
        print("正在从CNN News爬取文章...")
        cnn_articles = crawler.crawl_cnn_news(max_articles=5)
        
        all_articles = bbc_articles + cnn_articles
        
        if all_articles:
            print(f"📰 成功爬取 {len(all_articles)} 篇文章")
            
            # 处理文章
            processed_count = 0
            processed_articles = []
            for article in all_articles:
                try:
                    # 分析难度
                    difficulty_result = analyzer.analyze_difficulty(article['content'])
                    article['difficulty_level'] = difficulty_result['difficulty_level']
                    article['difficulty_score'] = difficulty_result['difficulty_score']
                    
                    # 生成摘要
                    summary = summarizer.generate_summary(article['content'], sentences_count=3)
                    article['summary'] = summary
                    
                    # 分类和标签
                    category = classifier.classify_article(
                        article['title'], 
                        article['content'], 
                        article['url']
                    )
                    article['category'] = category
                    
                    tags = classifier.extract_tags(article['title'], article['content'])
                    article['tags'] = ', '.join(tags)
                    
                    processed_articles.append(article)
                    processed_count += 1
                    
                except Exception as e:
                    print(f"⚠️ 处理文章失败: {e}")
                    continue
            
            # 保存到数据库
            saved_count = crawler.save_articles_to_db(processed_articles)
            print(f"💾 成功保存 {saved_count} 篇文章到数据库")
            
        else:
            print("⚠️ 未能爬取到文章，可能是网络问题")
            
    except Exception as e:
        print(f"❌ 爬取数据失败: {e}")
        print("💡 提示: 可以稍后在Web界面中手动爬取文章")

def start_web_server():
    """启动Web服务器"""
    print("🌐 启动Web服务器...")
    print("📱 系统将在 http://localhost:5000 启动")
    print("🔗 请在浏览器中打开上述地址访问系统")
    print("⏹️ 按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    try:
        from app import app
        app.run(debug=False, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动服务器失败: {e}")

def main():
    """主函数"""
    print("=" * 60)
    print("🎓 外刊推荐系统 - 四六级雅思托福学习助手")
    print("=" * 60)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 初始化系统
    if not initialize_system():
        sys.exit(1)
    
    # 询问是否爬取初始数据
    print("\n📋 系统初始化完成！")
    print("💡 建议先爬取一些文章数据以便测试系统功能")
    
    while True:
        choice = input("\n是否现在爬取初始文章数据？(y/n): ").lower().strip()
        if choice in ['y', 'yes', '是']:
            crawl_initial_data()
            break
        elif choice in ['n', 'no', '否']:
            print("⏭️ 跳过数据爬取，直接启动Web服务器")
            break
        else:
            print("请输入 y 或 n")
    
    # 启动Web服务器
    print("\n" + "=" * 60)
    start_web_server()

if __name__ == "__main__":
    main()
