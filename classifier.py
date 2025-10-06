import re
import jieba
from collections import Counter, defaultdict
import math
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import pickle
import os

class ArticleClassifier:
    def __init__(self):
        # 预定义分类关键词
        self.category_keywords = {
            'Technology': [
                'technology', 'artificial intelligence', 'ai', 'machine learning', 'computer', 'software', 'hardware',
                'internet', 'digital', 'cyber', 'robot', 'automation', 'data', 'algorithm', 'programming',
                'tech', 'innovation', 'startup', 'app', 'mobile', 'smartphone', 'cloud', 'blockchain',
                'virtual reality', 'vr', 'augmented reality', 'ar', 'iot', '5g', 'quantum'
            ],
            'Business': [
                'business', 'economy', 'economic', 'market', 'finance', 'financial', 'investment', 'investor',
                'company', 'corporation', 'enterprise', 'revenue', 'profit', 'stock', 'trading', 'bank',
                'banking', 'merger', 'acquisition', 'ipo', 'venture capital', 'startup', 'entrepreneur',
                'ceo', 'cfo', 'management', 'strategy', 'growth', 'expansion', 'competition', 'industry'
            ],
            'Health': [
                'health', 'medical', 'medicine', 'doctor', 'patient', 'hospital', 'clinic', 'treatment',
                'disease', 'illness', 'symptom', 'diagnosis', 'therapy', 'drug', 'pharmaceutical',
                'vaccine', 'covid', 'pandemic', 'epidemic', 'research', 'clinical trial', 'surgery',
                'cancer', 'diabetes', 'heart', 'mental health', 'psychology', 'wellness', 'fitness'
            ],
            'Education': [
                'education', 'school', 'university', 'college', 'student', 'teacher', 'professor',
                'learning', 'teaching', 'curriculum', 'academic', 'research', 'study', 'degree',
                'graduation', 'scholarship', 'tuition', 'campus', 'online learning', 'e-learning',
                'literacy', 'knowledge', 'skill', 'training', 'development', 'pedagogy'
            ],
            'Culture': [
                'culture', 'cultural', 'art', 'artist', 'music', 'movie', 'film', 'book', 'literature',
                'museum', 'gallery', 'exhibition', 'festival', 'tradition', 'heritage', 'history',
                'historical', 'ancient', 'modern', 'contemporary', 'creative', 'design', 'fashion',
                'entertainment', 'celebrity', 'media', 'social media', 'trend', 'lifestyle'
            ],
            'Politics': [
                'politics', 'political', 'government', 'president', 'minister', 'parliament', 'congress',
                'election', 'vote', 'voting', 'democracy', 'republic', 'policy', 'law', 'legal',
                'court', 'judge', 'justice', 'rights', 'freedom', 'liberty', 'constitution',
                'diplomacy', 'international', 'foreign policy', 'treaty', 'agreement', 'summit'
            ],
            'Environment': [
                'environment', 'environmental', 'climate', 'climate change', 'global warming', 'carbon',
                'emission', 'pollution', 'renewable', 'solar', 'wind', 'energy', 'sustainability',
                'green', 'eco', 'conservation', 'biodiversity', 'wildlife', 'forest', 'ocean',
                'recycling', 'waste', 'plastic', 'fossil fuel', 'greenhouse', 'temperature'
            ],
            'Sports': [
                'sport', 'sports', 'athlete', 'team', 'game', 'match', 'competition', 'tournament',
                'olympic', 'world cup', 'championship', 'football', 'soccer', 'basketball', 'tennis',
                'golf', 'swimming', 'running', 'cycling', 'fitness', 'training', 'coach', 'player',
                'score', 'victory', 'defeat', 'record', 'performance', 'stadium', 'arena'
            ]
        }
        
        # 来源兜底映射（常见媒体 → 默认分类）
        self.source_to_category = {
            # 科技
            'techcrunch': 'Technology', 'wired': 'Technology', 'the verge': 'Technology',
            'mit technology review': 'Technology', 'ars technica': 'Technology', 'engadget': 'Technology',
            'zdnet': 'Technology',
            # 商业/财经
            'harvard business review': 'Business', 'forbes': 'Business', 'business insider': 'Business',
            'financial times': 'Business', 'bloomberg': 'Business', 'marketwatch': 'Business',
            'the economist': 'Business',
            # 科学/环境/健康
            'scientific american': 'Environment', 'nature': 'Environment', 'new scientist': 'Environment',
            'science': 'Environment', 'webmd': 'Health', 'healthline': 'Health', 'medical news today': 'Health',
            # 教育/简易英语
            'voa learning english': 'Education', 'bbc learning english': 'Education', 'news in levels': 'Education'
        }
        # URL 关键字兜底（按子串命中分类）
        self.url_category_patterns = [
            (r'tech|technology|ai|ml|gadget|software|hardware|comput', 'Technology'),
            (r'business|market|econom|finance|stock|ipo|merger|bank', 'Business'),
            (r'health|medical|medicine|vaccine|covid|wellness|clinic|patient', 'Health'),
            (r'education|school|university|college|learning|student|teacher', 'Education'),
            (r'climate|environment|green|sustain|energy|pollution|emission', 'Environment'),
            (r'sport|sports|football|soccer|basketball|tennis|olympic|world-cup', 'Sports'),
            (r'politic|election|policy|government|congress|parliament', 'Politics'),
            (r'art|culture|movie|film|music|book|celebrity|entertain', 'Culture'),
        ]
        
        # 预定义标签关键词
        self.tag_keywords = {
            'Breaking News': ['breaking', 'urgent', 'latest', 'just in', 'developing'],
            'Analysis': ['analysis', 'analyze', 'expert', 'opinion', 'perspective', 'insight'],
            'Research': ['research', 'study', 'findings', 'discover', 'scientists', 'researchers'],
            'Interview': ['interview', 'exclusive', 'speaks', 'told', 'said', 'according to'],
            'Review': ['review', 'rating', 'critic', 'evaluation', 'assessment', 'opinion'],
            'Tutorial': ['how to', 'guide', 'tutorial', 'tips', 'advice', 'steps', 'learn'],
            'Opinion': ['opinion', 'editorial', 'viewpoint', 'perspective', 'commentary'],
            'Feature': ['feature', 'profile', 'spotlight', 'focus', 'highlight', 'showcase']
        }
        
        # 初始化机器学习分类器
        self.ml_classifier = None
        self.vectorizer = None
        self.is_trained = False
    
    def classify_article(self, title, content, url=None, source=None):
        """对文章进行分类"""
        # 合并标题和内容
        full_text = f"{title} {content}".lower()
        
        # 使用关键词匹配分类
        keyword_classification = self._classify_by_keywords(full_text)
        
        # 使用机器学习分类（如果已训练）
        ml_classification = None
        if self.is_trained:
            ml_classification = self._classify_by_ml(full_text)
        
        # 根据URL分类
        url_classification = self._classify_by_url(url) if url else None
        
        # 来源兜底
        source_classification = None
        if source:
            s = str(source).strip().lower()
            source_classification = self.source_to_category.get(s)
        
        # 综合分类结果（优先级：关键词 > URL > 来源 > 机器学习）
        final_category = self._combine_classifications(
            keyword_classification, url_classification, source_classification, ml_classification
        )
        
        # 兜底：避免 Unknown/空
        if not final_category or str(final_category).strip().lower() in ('unknown', '未知'):
            final_category = 'Culture'
        
        return final_category
    
    def _classify_by_keywords(self, text):
        """基于关键词的分类"""
        category_scores = {}
        
        for category, keywords in self.category_keywords.items():
            score = 0
            for keyword in keywords:
                # 计算关键词出现次数
                count = text.count(keyword.lower())
                # 根据关键词长度给予不同权重
                weight = len(keyword.split())  # 多词关键词权重更高
                score += count * weight
            
            category_scores[category] = score
        
        # 返回得分最高的分类
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            if category_scores[best_category] > 0:
                return best_category
        
        return 'Culture'  # 默认分类
    
    def _classify_by_ml(self, text):
        """使用机器学习分类"""
        if not self.is_trained or not self.ml_classifier:
            return None
        
        try:
            prediction = self.ml_classifier.predict([text])[0]
            return prediction
        except Exception as e:
            print(f"机器学习分类失败: {e}")
            return None
    
    def _classify_by_url(self, url):
        """基于URL的分类"""
        if not url:
            return None
        
        url_lower = url.lower()
        
        # 先尝试关键字词表（宽匹配）
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword in url_lower:
                    return category
        
        # 再尝试正则兜底
        for pattern, cat in self.url_category_patterns:
            if re.search(pattern, url_lower):
                return cat
        
        return None
    
    def _combine_classifications(self, *results):
        """综合多个分类结果。传入顺序体现优先级。"""
        # 过滤空值
        flat = [r for r in results if r]
        if not flat:
            return 'Culture'
        # 全一致
        if len(set(flat)) == 1:
            return flat[0]
        # 按传参顺序优先
        for r in results:
            if r:
                return r
        return 'Culture'
    
    def extract_tags(self, title, content):
        """提取文章标签"""
        full_text = f"{title} {content}".lower()
        tags = []
        
        # 基于关键词提取标签
        for tag, keywords in self.tag_keywords.items():
            for keyword in keywords:
                if keyword in full_text:
                    tags.append(tag)
                    break
        
        # 基于内容特征提取标签
        content_tags = self._extract_content_tags(content)
        tags.extend(content_tags)
        
        # 去重并限制数量
        tags = list(set(tags))[:5]
        
        return tags if tags else ['General']
    
    def _extract_content_tags(self, content):
        """基于内容特征提取标签"""
        tags = []
        
        # 检查是否包含数据/统计
        if re.search(r'\d+%|\d+\.\d+|\d+,\d+', content):
            tags.append('Data')
        
        # 检查是否包含引用
        if re.search(r'"[^"]*"|\'[^\']*\'', content):
            tags.append('Quotes')
        
        # 检查是否包含列表
        if re.search(r'\d+\.\s|•\s|-\s', content):
            tags.append('List')
        
        # 检查是否包含时间信息
        if re.search(r'\d{4}|\d{1,2}/\d{1,2}/\d{4}|january|february|march|april|may|june|july|august|september|october|november|december', content.lower()):
            tags.append('Timeline')
        
        # 检查文章长度
        word_count = len(content.split())
        if word_count > 1000:
            tags.append('Long Read')
        elif word_count < 300:
            tags.append('Quick Read')
        
        return tags
    
    def train_classifier(self, training_data):
        """训练机器学习分类器"""
        if not training_data:
            print("没有训练数据")
            return False
        
        try:
            texts = []
            labels = []
            
            for article in training_data:
                if 'title' in article and 'content' in article and 'category' in article:
                    text = f"{article['title']} {article['content']}"
                    texts.append(text)
                    labels.append(article['category'])
            
            if len(texts) < 10:
                print("训练数据不足")
                return False
            
            # 创建分类管道
            self.ml_classifier = Pipeline([
                ('tfidf', TfidfVectorizer(max_features=1000, stop_words='english')),
                ('classifier', MultinomialNB())
            ])
            
            # 训练分类器
            self.ml_classifier.fit(texts, labels)
            self.is_trained = True
            
            print(f"分类器训练完成，使用了 {len(texts)} 个样本")
            return True
            
        except Exception as e:
            print(f"训练分类器失败: {e}")
            return False
    
    def save_classifier(self, filepath='classifier_model.pkl'):
        """保存训练好的分类器"""
        if not self.is_trained:
            print("没有训练好的分类器可保存")
            return False
        
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(self.ml_classifier, f)
            print(f"分类器已保存到 {filepath}")
            return True
        except Exception as e:
            print(f"保存分类器失败: {e}")
            return False
    
    def load_classifier(self, filepath='classifier_model.pkl'):
        """加载训练好的分类器"""
        if not os.path.exists(filepath):
            print(f"分类器文件不存在: {filepath}")
            return False
        
        try:
            with open(filepath, 'rb') as f:
                self.ml_classifier = pickle.load(f)
            self.is_trained = True
            print(f"分类器已从 {filepath} 加载")
            return True
        except Exception as e:
            print(f"加载分类器失败: {e}")
            return False
    
    def get_category_keywords(self, category):
        """获取指定分类的关键词"""
        return self.category_keywords.get(category, [])
    
    def add_category_keywords(self, category, keywords):
        """添加分类关键词"""
        if category not in self.category_keywords:
            self.category_keywords[category] = []
        
        self.category_keywords[category].extend(keywords)
        self.category_keywords[category] = list(set(self.category_keywords[category]))

if __name__ == "__main__":
    # 测试示例
    classifier = ArticleClassifier()
    
    # 测试文章
    test_article = {
        'title': 'New AI Technology Revolutionizes Healthcare Industry',
        'content': 'Artificial intelligence is transforming the medical field with new diagnostic tools and treatment methods. Doctors are using machine learning algorithms to analyze patient data and improve outcomes.',
        'url': 'https://example.com/tech/ai-healthcare'
    }
    
    # 分类测试
    category = classifier.classify_article(
        test_article['title'], 
        test_article['content'], 
        test_article['url']
    )
    print(f"文章分类: {category}")
    
    # 标签提取测试
    tags = classifier.extract_tags(test_article['title'], test_article['content'])
    print(f"文章标签: {tags}")
    
    # 显示分类关键词
    keywords = classifier.get_category_keywords(category)
    print(f"{category} 分类关键词: {keywords[:10]}...")  # 只显示前10个
