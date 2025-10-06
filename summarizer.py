from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.luhn import LuhnSummarizer
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.summarizers.lex_rank import LexRankSummarizer
import re
import nltk
from collections import Counter
import math

class ArticleSummarizer:
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
        
        # 初始化不同的摘要器
        self.summarizers = {
            'lsa': LsaSummarizer(),
            'luhn': LuhnSummarizer(),
            'textrank': TextRankSummarizer(),
            'lexrank': LexRankSummarizer()
        }
        
        # 英文停用词
        self.stop_words = set(nltk.corpus.stopwords.words('english'))
    
    def generate_summary(self, text, method='textrank', sentences_count=3):
        """生成文章摘要"""
        if not text or len(text.strip()) < 200:
            return "文章内容过短，无法生成摘要。"
        
        try:
            # 清理文本
            cleaned_text = self._clean_text(text)
            
            # 使用指定方法生成摘要
            if method in self.summarizers:
                summary = self._extractive_summary(cleaned_text, method, sentences_count)
            else:
                # 默认使用关键词提取方法
                summary = self._keyword_based_summary(cleaned_text, sentences_count)
            
            return summary
            
        except Exception as e:
            print(f"摘要生成失败: {e}")
            return self._fallback_summary(text, sentences_count)
    
    def _extractive_summary(self, text, method, sentences_count):
        """使用抽取式摘要方法"""
        try:
            # 创建解析器
            parser = PlaintextParser.from_string(text, Tokenizer("english"))
            
            # 获取摘要器
            summarizer = self.summarizers[method]
            
            # 生成摘要
            summary_sentences = summarizer(parser.document, sentences_count)
            
            # 转换为文本
            summary = ' '.join([str(sentence) for sentence in summary_sentences])
            
            return summary
            
        except Exception as e:
            print(f"抽取式摘要失败 ({method}): {e}")
            return self._keyword_based_summary(text, sentences_count)
    
    def _keyword_based_summary(self, text, sentences_count):
        """基于关键词的摘要生成"""
        try:
            # 分句
            sentences = self._split_sentences(text)
            
            if len(sentences) <= sentences_count:
                return text
            
            # 计算句子重要性分数
            sentence_scores = self._calculate_sentence_scores(sentences)
            
            # 选择最重要的句子
            top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:sentences_count]
            
            # 按原文顺序排列
            selected_sentences = [sent for sent, score in sorted(top_sentences, key=lambda x: sentences.index(x[0]))]
            
            return ' '.join(selected_sentences)
            
        except Exception as e:
            print(f"关键词摘要失败: {e}")
            return self._fallback_summary(text, sentences_count)
    
    def _calculate_sentence_scores(self, sentences):
        """计算句子重要性分数"""
        # 提取所有词汇
        all_words = []
        for sentence in sentences:
            words = self._extract_words(sentence)
            all_words.extend(words)
        
        # 计算词频
        word_freq = Counter(all_words)
        
        # 计算每个句子的分数
        sentence_scores = {}
        for sentence in sentences:
            words = self._extract_words(sentence)
            if not words:
                continue
            
            # 基于词频和位置计算分数
            freq_score = sum(word_freq[word] for word in words) / len(words)
            position_score = self._get_position_score(sentence, sentences)
            length_score = self._get_length_score(sentence)
            
            # 综合分数
            total_score = freq_score * 0.5 + position_score * 0.3 + length_score * 0.2
            sentence_scores[sentence] = total_score
        
        return sentence_scores
    
    def _extract_words(self, text):
        """提取文本中的词汇"""
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        # 过滤停用词和短词
        words = [word for word in words if word not in self.stop_words and len(word) > 2]
        return words
    
    def _get_position_score(self, sentence, all_sentences):
        """根据句子位置计算分数"""
        position = all_sentences.index(sentence)
        total = len(all_sentences)
        
        # 开头和结尾的句子得分更高
        if position < total * 0.1 or position > total * 0.9:
            return 1.0
        elif position < total * 0.2 or position > total * 0.8:
            return 0.8
        else:
            return 0.5
    
    def _get_length_score(self, sentence):
        """根据句子长度计算分数"""
        word_count = len(sentence.split())
        
        # 中等长度的句子得分更高
        if 10 <= word_count <= 25:
            return 1.0
        elif 5 <= word_count <= 35:
            return 0.8
        else:
            return 0.5
    
    def _split_sentences(self, text):
        """分句"""
        # 简单的分句方法
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
    
    def _clean_text(self, text):
        """清理文本"""
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        # 移除特殊字符
        text = re.sub(r'[^\w\s.,!?;:\-()]', '', text)
        return text.strip()
    
    def _fallback_summary(self, text, sentences_count):
        """备用摘要方法"""
        sentences = self._split_sentences(text)
        
        if len(sentences) <= sentences_count:
            return text
        
        # 简单选择前几句和后几句
        selected = []
        if sentences_count >= 2:
            selected.append(sentences[0])  # 第一句
            if sentences_count > 2:
                selected.extend(sentences[1:sentences_count-1])  # 中间几句
            selected.append(sentences[-1])  # 最后一句
        else:
            selected.append(sentences[0])
        
        return ' '.join(selected)
    
    def generate_multiple_summaries(self, text, sentences_count=3):
        """生成多种方法的摘要"""
        summaries = {}
        
        for method in ['textrank', 'lsa', 'luhn', 'lexrank']:
            try:
                summary = self.generate_summary(text, method, sentences_count)
                summaries[method] = summary
            except Exception as e:
                print(f"方法 {method} 失败: {e}")
                summaries[method] = "摘要生成失败"
        
        # 添加关键词摘要
        try:
            keyword_summary = self._keyword_based_summary(text, sentences_count)
            summaries['keyword'] = keyword_summary
        except Exception as e:
            print(f"关键词摘要失败: {e}")
            summaries['keyword'] = "摘要生成失败"
        
        return summaries
    
    def get_summary_quality_score(self, original_text, summary):
        """评估摘要质量"""
        if not summary or len(summary.strip()) < 50:
            return 0
        
        # 计算压缩比
        compression_ratio = len(summary.split()) / len(original_text.split())
        
        # 计算覆盖率（摘要中的关键词在原文中的比例）
        original_words = set(self._extract_words(original_text))
        summary_words = set(self._extract_words(summary))
        
        if not original_words:
            coverage = 0
        else:
            coverage = len(summary_words.intersection(original_words)) / len(original_words)
        
        # 综合评分
        quality_score = (1 - compression_ratio) * 0.6 + coverage * 0.4
        return min(max(quality_score, 0), 1)

if __name__ == "__main__":
    # 测试示例
    summarizer = ArticleSummarizer()
    
    sample_text = """
    Artificial intelligence (AI) has become one of the most transformative technologies of the 21st century. 
    From self-driving cars to virtual assistants, AI is reshaping industries and changing the way we live and work. 
    Machine learning, a subset of AI, enables computers to learn and improve from experience without being explicitly programmed. 
    This technology has applications in healthcare, finance, transportation, and many other sectors. 
    However, the rapid advancement of AI also raises important questions about ethics, privacy, and the future of employment. 
    As we continue to develop more sophisticated AI systems, it is crucial to consider both the benefits and potential risks. 
    The future of AI depends on how we choose to develop and deploy these powerful technologies.
    """
    
    print("原文摘要生成测试：")
    print("=" * 50)
    
    # 生成单一摘要
    summary = summarizer.generate_summary(sample_text, method='textrank', sentences_count=2)
    print(f"TextRank摘要: {summary}")
    print()
    
    # 生成多种摘要
    summaries = summarizer.generate_multiple_summaries(sample_text, sentences_count=2)
    for method, summary in summaries.items():
        print(f"{method.upper()}摘要: {summary}")
        print()
    
    # 评估摘要质量
    quality = summarizer.get_summary_quality_score(sample_text, summary)
    print(f"摘要质量评分: {quality:.2f}")
