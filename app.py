from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
from datetime import datetime
import os

from database import DatabaseManager
from crawler import ArticleCrawler
from difficulty_analyzer import DifficultyAnalyzer
from summarizer import ArticleSummarizer
from classifier import ArticleClassifier

app = Flask(__name__)
CORS(app)

# 初始化组件
db = DatabaseManager()
crawler = ArticleCrawler()
difficulty_analyzer = DifficultyAnalyzer()
summarizer = ArticleSummarizer()
classifier = ArticleClassifier()

# 安全序列化数据库行到字典（兼容字符串/日期）
def _serialize_article_row(row):
    def _date_to_str(v):
        try:
            # date/datetime
            return v.isoformat()
        except Exception:
            # 已是字符串或 None
            return v
    return {
        'id': row[0],
        'title': row[1],
        'author': row[2],
        'content': row[3],
        'summary': row[4],
        'url': row[5],
        'source': row[6],
        'publish_date': _date_to_str(row[7]),
        'difficulty_level': row[8],
        'difficulty_score': row[9],
        'category': row[10],
        'tags': row[11],
        'word_count': row[12],
        'created_at': row[13]
    }

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/articles')
def articles():
    """文章库页面"""
    return render_template('articles.html')

@app.route('/api/articles', methods=['GET'])
def get_articles():
    """获取文章列表"""
    try:
        # 获取查询参数
        limit = request.args.get('limit', 20, type=int)
        category = request.args.get('category')
        difficulty = request.args.get('difficulty')
        page = request.args.get('page', 1, type=int)
        
        # 获取文章
        articles = db.get_articles(limit=limit, category=category, difficulty=difficulty)
        
        # 转换为字典格式
        articles_data = [_serialize_article_row(a) for a in articles]
        
        return jsonify({
            'success': True,
            'data': articles_data,
            'total': len(articles_data)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/articles/<int:article_id>', methods=['GET'])
def get_article(article_id):
    """获取单篇文章详情"""
    try:
        article = db.get_article_by_id(article_id)
        
        if not article:
            return jsonify({
                'success': False,
                'error': '文章不存在'
            }), 404
        
        article_dict = _serialize_article_row(article)
        
        return jsonify({
            'success': True,
            'data': article_dict
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/articles/search', methods=['GET'])
def search_articles():
    """搜索文章"""
    try:
        keyword = request.args.get('q', '')
        limit = request.args.get('limit', 20, type=int)
        
        if not keyword:
            return jsonify({
                'success': False,
                'error': '搜索关键词不能为空'
            }), 400
        
        articles = db.search_articles(keyword, limit)
        
        articles_data = [_serialize_article_row(a) for a in articles]
        
        return jsonify({
            'success': True,
            'data': articles_data,
            'total': len(articles_data),
            'keyword': keyword
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """获取所有分类"""
    try:
        categories = db.get_categories()
        
        categories_data = []
        for category in categories:
            category_dict = {
                'id': category[0],
                'name': category[1],
                'description': category[2],
                'created_at': category[3]
            }
            categories_data.append(category_dict)
        
        return jsonify({
            'success': True,
            'data': categories_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/difficulty-stats', methods=['GET'])
def get_difficulty_stats():
    """获取难度统计"""
    try:
        stats = db.get_difficulty_stats()
        
        stats_data = []
        for stat in stats:
            stat_dict = {
                'difficulty_level': stat[0],
                'count': stat[1]
            }
            stats_data.append(stat_dict)
        
        return jsonify({
            'success': True,
            'data': stats_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/crawl', methods=['POST'])
def crawl_articles():
    """爬取新文章"""
    try:
        data = request.get_json()
        max_articles = data.get('max_articles', 10)
        source = data.get('source', 'all')  # 'bbc', 'cnn', 'all'
        
        # 根据源选择爬取方法
        if source == 'bbc':
            articles = crawler.crawl_bbc_news(max_articles)
        elif source == 'cnn':
            articles = crawler.crawl_cnn_news(max_articles)
        else:
            articles = crawler.crawl_all_sources(max_articles // 2)
        
        # 处理每篇文章
        processed_articles = []
        failed_count = 0
        for article in articles:
            try:
                # 分析难度
                difficulty_result = difficulty_analyzer.analyze_difficulty(article['content'])
                article['difficulty_level'] = difficulty_result['difficulty_level']
                article['difficulty_score'] = difficulty_result['difficulty_score']
                
                # 生成摘要
                summary = summarizer.generate_summary(article['content'], sentences_count=3)
                article['summary'] = summary
                
                # 分类和标签
                category = classifier.classify_article(
                    article['title'], 
                    article['content'], 
                    article.get('url'),
                    article.get('source')
                )
                article['category'] = category
                
                tags = classifier.extract_tags(article['title'], article['content'])
                article['tags'] = ', '.join(tags)
                
                processed_articles.append(article)
                
            except Exception as e:
                print(f"处理文章失败: {e}")
                failed_count += 1
                continue
        
        # 保存到数据库
        saved_count = crawler.save_articles_to_db(processed_articles)
        processed_ok = len(processed_articles)
        skipped_count = max(processed_ok - saved_count, 0)
        crawled_count = len(articles)
        
        return jsonify({
            'success': True,
            'message': f'爬取:{crawled_count} | 处理成功:{processed_ok} | 保存:{saved_count} | 跳过(重复):{skipped_count} | 处理失败:{failed_count}',
            'crawled_count': crawled_count,
            'processed_ok': processed_ok,
            'saved_count': saved_count,
            'skipped_count': skipped_count,
            'failed_count': failed_count
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analyze-difficulty', methods=['POST'])
def analyze_difficulty():
    """分析文本难度"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({
                'success': False,
                'error': '文本内容不能为空'
            }), 400
        
        result = difficulty_analyzer.analyze_difficulty(text)
        explanation = difficulty_analyzer.get_difficulty_explanation(result)
        
        return jsonify({
            'success': True,
            'data': result,
            'explanation': explanation
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/generate-summary', methods=['POST'])
def generate_summary():
    """生成文章摘要"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        method = data.get('method', 'textrank')
        sentences_count = data.get('sentences_count', 3)
        
        if not text:
            return jsonify({
                'success': False,
                'error': '文本内容不能为空'
            }), 400
        
        summary = summarizer.generate_summary(text, method, sentences_count)
        quality_score = summarizer.get_summary_quality_score(text, summary)
        
        return jsonify({
            'success': True,
            'data': {
                'summary': summary,
                'method': method,
                'sentences_count': sentences_count,
                'quality_score': quality_score
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/classify', methods=['POST'])
def classify_text():
    """分类文本"""
    try:
        data = request.get_json()
        title = data.get('title', '')
        content = data.get('content', '')
        url = data.get('url', '')
        source = data.get('source', '')
        
        if not title and not content:
            return jsonify({
                'success': False,
                'error': '标题或内容不能为空'
            }), 400
        
        category = classifier.classify_article(title, content, url, source)
        tags = classifier.extract_tags(title, content)
        
        return jsonify({
            'success': True,
            'data': {
                'category': category,
                'tags': tags
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/recommend', methods=['GET'])
def recommend_articles():
    """推荐文章"""
    try:
        # 获取推荐参数
        difficulty = request.args.get('difficulty')
        category = request.args.get('category')
        exam_level = request.args.get('exam_level')  # CET-4, CET-6, IELTS-6.0等
        limit = request.args.get('limit', 10, type=int)
        
        # 根据考试等级确定难度
        if exam_level:
            if 'CET-4' in exam_level:
                difficulty = 'Beginner'
            elif 'CET-6' in exam_level:
                difficulty = 'Intermediate'
            elif 'IELTS-6.0' in exam_level or 'TOEFL-80' in exam_level:
                difficulty = 'Intermediate'
            elif 'IELTS-6.5' in exam_level or 'TOEFL-90' in exam_level:
                difficulty = 'Advanced'
            elif 'IELTS-7.0' in exam_level or 'TOEFL-100' in exam_level:
                difficulty = 'Advanced'
            else:
                difficulty = 'Expert'
        
        # 获取推荐文章
        articles = db.get_articles(limit=limit, category=category, difficulty=difficulty)
        
        articles_data = []
        for a in articles:
            d = _serialize_article_row(a)
            # 推荐列表无需 content/created_at
            d.pop('content', None)
            d.pop('created_at', None)
            articles_data.append(d)
        
        return jsonify({
            'success': True,
            'data': articles_data,
            'recommendation_criteria': {
                'difficulty': difficulty,
                'category': category,
                'exam_level': exam_level
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': '接口不存在'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': '服务器内部错误'
    }), 500

if __name__ == '__main__':
    # 创建templates目录
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # 创建static目录
    if not os.path.exists('static'):
        os.makedirs('static')
    
    print("外刊推荐系统启动中...")
    print("API接口文档:")
    print("GET  /api/articles - 获取文章列表")
    print("GET  /api/articles/<id> - 获取文章详情")
    print("GET  /api/articles/search?q=关键词 - 搜索文章")
    print("GET  /api/categories - 获取分类列表")
    print("GET  /api/difficulty-stats - 获取难度统计")
    print("GET  /api/recommend - 推荐文章")
    print("POST /api/crawl - 爬取新文章")
    print("POST /api/analyze-difficulty - 分析文本难度")
    print("POST /api/generate-summary - 生成摘要")
    print("POST /api/classify - 分类文本")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

import os
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
    