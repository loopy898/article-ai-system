import textstat
import re
import nltk
from collections import Counter
import math

class DifficultyAnalyzer:
    def __init__(self):
        # 下载必要的NLTK数据
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        # 四六级、雅思托福词汇量参考
        self.vocab_levels = {
            'CET-4': 4000,      # 大学英语四级
            'CET-6': 6000,      # 大学英语六级
            'IELTS-6.0': 5000,  # 雅思6.0
            'IELTS-6.5': 6000,  # 雅思6.5
            'IELTS-7.0': 7000,  # 雅思7.0
            'TOEFL-80': 6000,   # 托福80分
            'TOEFL-90': 7000,   # 托福90分
            'TOEFL-100': 8000,  # 托福100分
        }
        
        # 难度等级映射
        self.difficulty_mapping = {
            'Beginner': ['CET-4'],
            'Intermediate': ['CET-6', 'IELTS-6.0', 'TOEFL-80'],
            'Advanced': ['IELTS-6.5', 'IELTS-7.0', 'TOEFL-90'],
            'Expert': ['TOEFL-100']
        }
    
    def analyze_difficulty(self, text):
        """分析文章难度"""
        if not text or len(text.strip()) < 100:
            return {
                'difficulty_level': 'Unknown',
                'difficulty_score': 0,
                'recommended_exam': 'Unknown',
                'details': {}
            }
        
        # 基础文本统计
        word_count = len(text.split())
        sentence_count = textstat.sentence_count(text)
        char_count = len(text)
        
        # 计算各种难度指标
        flesch_reading_ease = textstat.flesch_reading_ease(text)
        flesch_kincaid_grade = textstat.flesch_kincaid_grade(text)
        gunning_fog = textstat.gunning_fog(text)
        smog_index = textstat.smog_index(text)
        automated_readability = textstat.automated_readability_index(text)
        
        # 词汇复杂度分析
        vocab_complexity = self._analyze_vocabulary_complexity(text)
        
        # 句法复杂度分析
        syntax_complexity = self._analyze_syntax_complexity(text)
        
        # 综合难度评分 (0-100)
        difficulty_score = self._calculate_comprehensive_score(
            flesch_reading_ease, flesch_kincaid_grade, gunning_fog,
            vocab_complexity, syntax_complexity
        )
        
        # 确定难度等级
        difficulty_level = self._determine_difficulty_level(difficulty_score)
        
        # 推荐考试
        recommended_exam = self._recommend_exam_level(difficulty_score)
        
        return {
            'difficulty_level': difficulty_level,
            'difficulty_score': round(difficulty_score, 2),
            'recommended_exam': recommended_exam,
            'details': {
                'flesch_reading_ease': round(flesch_reading_ease, 2),
                'flesch_kincaid_grade': round(flesch_kincaid_grade, 2),
                'gunning_fog': round(gunning_fog, 2),
                'smog_index': round(smog_index, 2),
                'automated_readability': round(automated_readability, 2),
                'vocab_complexity': round(vocab_complexity, 2),
                'syntax_complexity': round(syntax_complexity, 2),
                'word_count': word_count,
                'sentence_count': sentence_count,
                'avg_sentence_length': round(word_count / sentence_count, 2) if sentence_count > 0 else 0
            }
        }
    
    def _analyze_vocabulary_complexity(self, text):
        """分析词汇复杂度"""
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        word_count = len(words)
        
        if word_count == 0:
            return 0
        
        # 计算平均词长
        avg_word_length = sum(len(word) for word in words) / word_count
        
        # 计算长词比例 (6个字母以上)
        long_words = [word for word in words if len(word) > 6]
        long_word_ratio = len(long_words) / word_count
        
        # 计算复杂词汇比例 (基于词频)
        complex_words = self._get_complex_words(words)
        complex_word_ratio = len(complex_words) / word_count
        
        # 词汇复杂度评分 (0-100)
        vocab_score = (avg_word_length * 10 + long_word_ratio * 30 + complex_word_ratio * 40)
        return min(vocab_score, 100)
    
    def _analyze_syntax_complexity(self, text):
        """分析句法复杂度"""
        # 使用 NLTK 进行分句，避免 textstat 无 sentence_split 方法
        sentences = nltk.sent_tokenize(text)
        if not sentences:
            return 0
        
        total_clauses = 0
        total_phrases = 0
        
        for sentence in sentences:
            # 计算从句数量 (简单启发式)
            clause_indicators = ['that', 'which', 'who', 'whom', 'whose', 'where', 'when', 'why', 'how']
            clauses = sum(1 for indicator in clause_indicators if indicator in sentence.lower())
            total_clauses += clauses
            
            # 计算短语数量 (介词短语等)
            phrase_indicators = ['in', 'on', 'at', 'by', 'for', 'with', 'from', 'to', 'of']
            phrases = sum(1 for indicator in phrase_indicators if indicator in sentence.lower())
            total_phrases += phrases
        
        avg_clauses_per_sentence = total_clauses / len(sentences)
        avg_phrases_per_sentence = total_phrases / len(sentences)
        
        # 句法复杂度评分 (0-100)
        syntax_score = (avg_clauses_per_sentence * 20 + avg_phrases_per_sentence * 15)
        return min(syntax_score, 100)
    
    def _get_complex_words(self, words):
        """识别复杂词汇"""
        # 基于词长和词频的简单判断
        complex_words = []
        word_freq = Counter(words)
        
        for word in words:
            # 长词 (>6字母) 或低频词
            if len(word) > 6 or word_freq[word] == 1:
                complex_words.append(word)
        
        return complex_words
    
    def _calculate_comprehensive_score(self, flesch, fk_grade, gunning_fog, vocab_complexity, syntax_complexity):
        """计算综合难度评分"""
        # 将Flesch Reading Ease转换为0-100分数 (分数越高越难)
        flesch_score = max(0, 100 - flesch)
        
        # 标准化其他指标到0-100
        fk_score = min(fk_grade * 5, 100)  # 年级水平 * 5
        gunning_score = min(gunning_fog * 4, 100)  # Gunning Fog * 4
        
        # 加权平均
        weights = {
            'flesch': 0.25,
            'fk_grade': 0.20,
            'gunning_fog': 0.20,
            'vocab_complexity': 0.20,
            'syntax_complexity': 0.15
        }
        
        comprehensive_score = (
            flesch_score * weights['flesch'] +
            fk_score * weights['fk_grade'] +
            gunning_score * weights['gunning_fog'] +
            vocab_complexity * weights['vocab_complexity'] +
            syntax_complexity * weights['syntax_complexity']
        )
        
        return comprehensive_score
    
    def _determine_difficulty_level(self, score):
        """根据分数确定难度等级"""
        if score < 30:
            return 'Beginner'
        elif score < 50:
            return 'Intermediate'
        elif score < 70:
            return 'Advanced'
        else:
            return 'Expert'
    
    def _recommend_exam_level(self, score):
        """根据分数推荐考试等级"""
        if score < 30:
            return 'CET-4'
        elif score < 40:
            return 'CET-6'
        elif score < 50:
            return 'IELTS-6.0 / TOEFL-80'
        elif score < 60:
            return 'IELTS-6.5 / TOEFL-90'
        elif score < 70:
            return 'IELTS-7.0'
        else:
            return 'TOEFL-100+'
    
    def get_difficulty_explanation(self, difficulty_data):
        """获取难度分析解释"""
        level = difficulty_data['difficulty_level']
        score = difficulty_data['difficulty_score']
        exam = difficulty_data['recommended_exam']
        details = difficulty_data['details']
        
        explanation = f"""
        难度分析结果：
        
        总体难度：{level} (评分: {score}/100)
        推荐考试：{exam}
        
        详细指标：
        • 可读性指数：{details['flesch_reading_ease']} (0-100，分数越高越易读)
        • 年级水平：{details['flesch_kincaid_grade']} 年级
        • 词汇复杂度：{details['vocab_complexity']}/100
        • 句法复杂度：{details['syntax_complexity']}/100
        • 平均句长：{details['avg_sentence_length']} 词/句
        • 文章长度：{details['word_count']} 词，{details['sentence_count']} 句
        
        学习建议：
        """
        
        if level == 'Beginner':
            explanation += "适合英语初学者，词汇和语法相对简单，建议先掌握基础词汇。"
        elif level == 'Intermediate':
            explanation += "适合有一定英语基础的学习者，建议重点学习长难句和复杂词汇。"
        elif level == 'Advanced':
            explanation += "适合英语水平较高的学习者，建议关注文章结构和逻辑关系。"
        else:
            explanation += "适合英语专业或高水平学习者，建议进行深度阅读和批判性思考。"
        
        return explanation

if __name__ == "__main__":
    # 测试示例
    analyzer = DifficultyAnalyzer()
    
    sample_text = """
    Artificial intelligence (AI) has revolutionized numerous industries, transforming the way we work, communicate, and solve complex problems. 
    Machine learning algorithms, a subset of AI, enable computers to learn and improve from experience without being explicitly programmed. 
    This technological advancement has profound implications for various sectors, including healthcare, finance, transportation, and education.
    """
    
    result = analyzer.analyze_difficulty(sample_text)
    print("难度分析结果：")
    print(f"难度等级: {result['difficulty_level']}")
    print(f"难度评分: {result['difficulty_score']}")
    print(f"推荐考试: {result['recommended_exam']}")
    print("\n详细解释：")
    print(analyzer.get_difficulty_explanation(result))
