#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
外刊推荐系统测试脚本
"""

import sys
import os

def test_imports():
    """测试所有模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        from database import DatabaseManager
        print("✅ database.py 导入成功")
        
        from crawler import ArticleCrawler
        print("✅ crawler.py 导入成功")
        
        from difficulty_analyzer import DifficultyAnalyzer
        print("✅ difficulty_analyzer.py 导入成功")
        
        from summarizer import ArticleSummarizer
        print("✅ summarizer.py 导入成功")
        
        from classifier import ArticleClassifier
        print("✅ classifier.py 导入成功")
        
        from app import app
        print("✅ app.py 导入成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_database():
    """测试数据库功能"""
    print("\n📊 测试数据库功能...")
    
    try:
        from database import DatabaseManager
        
        # 创建数据库实例
        db = DatabaseManager("test.db")
        print("✅ 数据库初始化成功")
        
        # 测试添加文章
        test_article = {
            'title': 'Test Article',
            'author': 'Test Author',
            'content': 'This is a test article content for testing purposes.',
            'url': 'https://example.com/test',
            'source': 'Test Source',
            'category': 'Technology',
            'word_count': 10
        }
        
        article_id = db.add_article(test_article)
        if article_id:
            print("✅ 文章添加成功")
        else:
            print("⚠️ 文章可能已存在")
        
        # 测试获取文章
        articles = db.get_articles(limit=5)
        print(f"✅ 获取文章成功，共 {len(articles)} 篇")
        
        # 测试获取分类
        categories = db.get_categories()
        print(f"✅ 获取分类成功，共 {len(categories)} 个分类")
        
        # 清理测试数据库
        if os.path.exists("test.db"):
            os.remove("test.db")
            print("✅ 测试数据库已清理")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        return False

def test_difficulty_analyzer():
    """测试难度分析器"""
    print("\n📈 测试难度分析器...")
    
    try:
        from difficulty_analyzer import DifficultyAnalyzer
        
        analyzer = DifficultyAnalyzer()
        
        test_text = """
        Artificial intelligence (AI) has revolutionized numerous industries, 
        transforming the way we work, communicate, and solve complex problems. 
        Machine learning algorithms, a subset of AI, enable computers to learn 
        and improve from experience without being explicitly programmed.
        """
        
        result = analyzer.analyze_difficulty(test_text)
        
        if result and 'difficulty_level' in result:
            print(f"✅ 难度分析成功: {result['difficulty_level']} (评分: {result['difficulty_score']})")
            return True
        else:
            print("❌ 难度分析结果格式错误")
            return False
            
    except Exception as e:
        print(f"❌ 难度分析器测试失败: {e}")
        return False

def test_summarizer():
    """测试摘要生成器"""
    print("\n📝 测试摘要生成器...")
    
    try:
        from summarizer import ArticleSummarizer
        
        summarizer = ArticleSummarizer()
        
        test_text = """
        Artificial intelligence (AI) has become one of the most transformative 
        technologies of the 21st century. From self-driving cars to virtual 
        assistants, AI is reshaping industries and changing the way we live and work. 
        Machine learning, a subset of AI, enables computers to learn and improve 
        from experience without being explicitly programmed. This technology has 
        applications in healthcare, finance, transportation, and many other sectors. 
        However, the rapid advancement of AI also raises important questions about 
        ethics, privacy, and the future of employment.
        """
        
        summary = summarizer.generate_summary(test_text, sentences_count=2)
        
        if summary and len(summary) > 0:
            print(f"✅ 摘要生成成功: {summary[:100]}...")
            return True
        else:
            print("❌ 摘要生成失败")
            return False
            
    except Exception as e:
        print(f"❌ 摘要生成器测试失败: {e}")
        return False

def test_classifier():
    """测试分类器"""
    print("\n🏷️ 测试分类器...")
    
    try:
        from classifier import ArticleClassifier
        
        classifier = ArticleClassifier()
        
        title = "New AI Technology Revolutionizes Healthcare"
        content = "Artificial intelligence is transforming the medical field with new diagnostic tools and treatment methods."
        
        category = classifier.classify_article(title, content)
        tags = classifier.extract_tags(title, content)
        
        if category and tags:
            print(f"✅ 分类成功: {category}")
            print(f"✅ 标签提取成功: {tags}")
            return True
        else:
            print("❌ 分类或标签提取失败")
            return False
            
    except Exception as e:
        print(f"❌ 分类器测试失败: {e}")
        return False

def test_web_app():
    """测试Web应用"""
    print("\n🌐 测试Web应用...")
    
    try:
        from app import app
        
        # 测试应用创建
        if app:
            print("✅ Flask应用创建成功")
            
            # 测试路由
            with app.test_client() as client:
                response = client.get('/')
                if response.status_code == 200:
                    print("✅ 主页路由正常")
                else:
                    print(f"⚠️ 主页路由状态码: {response.status_code}")
                
                response = client.get('/api/categories')
                if response.status_code == 200:
                    print("✅ API路由正常")
                else:
                    print(f"⚠️ API路由状态码: {response.status_code}")
            
            return True
        else:
            print("❌ Flask应用创建失败")
            return False
            
    except Exception as e:
        print(f"❌ Web应用测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 外刊推荐系统 - 系统测试")
    print("=" * 60)
    
    tests = [
        ("模块导入", test_imports),
        ("数据库功能", test_database),
        ("难度分析器", test_difficulty_analyzer),
        ("摘要生成器", test_summarizer),
        ("分类器", test_classifier),
        ("Web应用", test_web_app)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统运行正常")
        return True
    else:
        print("⚠️ 部分测试失败，请检查相关模块")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


