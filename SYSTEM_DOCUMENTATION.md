# 外刊推荐系统 - 完整技术文档

## 📋 系统概述

外刊推荐系统是一个专为四六级、雅思托福等英语考试设计的智能外刊学习平台，集成了文章爬取、难度分析、智能摘要、自动分类等AI功能。

**当前状态**: 536篇文章，8个分类，80+外刊源

---

## 🏗️ 技术架构

### 核心技术栈
- **后端框架**: Flask 2.3.3 (Python Web框架)
- **数据库**: SQLite 3 (轻量级关系型数据库)
- **前端框架**: Bootstrap 5.1.3 + 原生JavaScript
- **爬虫框架**: requests + BeautifulSoup4 + feedparser
- **自然语言处理**: 
  - textstat (文本统计分析)
  - jieba (中文分词)
  - sumy (文本摘要)
  - scikit-learn (机器学习)
- **其他依赖**: 
  - nltk (自然语言工具包)
  - numpy (数值计算)
  - python-dateutil (日期处理)

### 系统架构图
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端界面      │    │   Flask API     │    │   数据处理层    │
│  Bootstrap +    │◄──►│   路由控制      │◄──►│  AI分析模块     │
│  JavaScript     │    │   JSON API      │    │  爬虫模块       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                ▲
                                │
                       ┌─────────────────┐
                       │   SQLite数据库   │
                       │   文章存储       │
                       └─────────────────┘
```

---

## 📁 文件结构与详细说明

### 🔧 **核心后端文件**

#### 1. **app.py** - Flask Web应用主控制器
**框架**: Flask 2.3.3
**作用**: 系统的核心控制器，处理所有HTTP请求和API接口

**主要功能**:
- **路由管理**: 定义所有Web路由和API端点
- **请求处理**: 处理GET/POST请求，返回JSON响应
- **模板渲染**: 渲染HTML模板
- **错误处理**: 统一的错误处理机制

**关键API接口**:
```python
# 页面路由
GET  /                    # 主页
GET  /articles           # 文章库页面

# API接口
GET  /api/articles       # 获取文章列表 (支持分类/难度筛选)
GET  /api/articles/<id>  # 获取文章详情
GET  /api/articles/search # 搜索文章
GET  /api/categories     # 获取分类列表
GET  /api/difficulty-stats # 获取难度统计
GET  /api/recommend      # 智能推荐
POST /api/crawl          # 触发爬虫
POST /api/analyze-difficulty # 文本难度分析
POST /api/generate-summary   # 摘要生成
POST /api/classify       # 智能分类
```

#### 2. **database.py** - 数据库管理模块
**框架**: SQLite3 (Python标准库)
**作用**: 数据库操作的统一接口

**数据库设计**:
```sql
-- 文章表
CREATE TABLE articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT,
    content TEXT NOT NULL,
    summary TEXT,
    url TEXT UNIQUE,
    source TEXT,
    category TEXT,
    tags TEXT,
    publish_date DATE,
    difficulty_level TEXT,
    difficulty_score INTEGER,
    recommended_exam TEXT,
    word_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 分类表
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT
);
```

**核心方法**:
- `init_database()`: 初始化数据库表结构
- `add_article()`: 添加文章（防重复）
- `get_articles()`: 获取文章列表（支持筛选）
- `search_articles()`: 全文搜索
- `get_difficulty_stats()`: 统计分析

#### 3. **crawler.py** - 网页爬虫模块
**框架**: requests + BeautifulSoup4 + feedparser
**作用**: 从80+外刊网站自动爬取文章

**支持的外刊源**:
- **主流媒体**: BBC News, CNN, The Guardian, Reuters, NPR
- **科技媒体**: TechCrunch, Wired, MIT Technology Review, The Verge
- **商业媒体**: Forbes, Business Insider, Harvard Business Review
- **学术期刊**: Nature, Scientific American, Science Magazine
- **其他优质源**: TIME, The Economist, The Atlantic等

**爬取策略**:
```python
# RSS源配置示例
rss_sources = [
    ("BBC News", "http://feeds.bbci.co.uk/news/rss.xml", "Politics"),
    ("TechCrunch", "https://techcrunch.com/feed/", "Technology"),
    ("Scientific American", "http://rss.sciam.com/ScientificAmerican-Global", "Environment")
]
```

**核心功能**:
- `crawl_all_sources()`: 批量爬取所有RSS源
- `crawl_rss_feed()`: 解析RSS并提取正文
- `_download_article_text()`: 通用正文提取
- `save_articles_to_db()`: 批量保存到数据库

#### 4. **difficulty_analyzer.py** - 文本难度分析模块
**框架**: textstat + 自定义算法
**作用**: 分析英文文本难度，映射到考试等级

**分析维度**:
- **可读性指标**: Flesch Reading Ease, Flesch-Kincaid Grade Level
- **词汇复杂度**: 复杂词汇比例、平均词长
- **句法复杂度**: 平均句长、句子结构复杂度
- **综合评分**: 0-100分制

**难度等级映射**:
```python
difficulty_mapping = {
    "Beginner": "CET-4",      # 0-30分
    "Intermediate": "CET-6",   # 30-50分  
    "Advanced": "IELTS 6.5-7.0", # 50-70分
    "Expert": "TOEFL 100+"     # 70-100分
}
```

#### 5. **summarizer.py** - 文本摘要生成模块
**框架**: sumy + 多种算法
**作用**: 自动生成文章摘要

**支持算法**:
- **TextRank**: 基于图的排序算法（推荐）
- **LSA**: 潜在语义分析
- **Luhn**: 基于词频的经典算法
- **LexRank**: 基于词汇相似度

**质量评估**:
- 摘要覆盖度
- 信息密度
- 可读性评分

#### 6. **classifier.py** - 智能分类模块
**框架**: scikit-learn + jieba + 关键词匹配
**作用**: 自动分类文章并提取标签

**分类体系**:
- Technology (科技)
- Business (商业)
- Health (健康)
- Education (教育)
- Culture (文化)
- Politics (政治)
- Environment (环境)
- Sports (体育)

**分类方法**:
- **关键词匹配**: 基于预定义关键词库
- **机器学习**: TF-IDF + 朴素贝叶斯
- **URL分析**: 根据文章URL判断分类
- **综合决策**: 多种方法结果融合

---

### 🎨 **前端文件**

#### 7. **templates/index.html** - 主页模板
**框架**: Bootstrap 5.1.3 + Font Awesome 6.0
**作用**: 系统主页，展示核心功能

**页面结构**:
```html
<!-- 导航栏 -->
<nav class="navbar">...</nav>

<!-- 英雄区域 -->
<div class="hero-section">...</div>

<!-- 统计面板 -->
<div class="stats-section">...</div>

<!-- 三大核心功能 -->
<div class="row">
    <div class="feature-card">难度分析</div>
    <div class="feature-card">摘要生成</div>
    <div class="feature-card">智能分类</div>
</div>

<!-- 快速访问 -->
<div class="quick-access">...</div>

<!-- 功能模态框 -->
<div class="modal" id="difficultyModal">...</div>
<div class="modal" id="summaryModal">...</div>
<div class="modal" id="classifyModal">...</div>
```

**设计特色**:
- **现代化UI**: 渐变背景、毛玻璃效果、卡片设计
- **响应式布局**: 支持移动端和桌面端
- **交互动画**: 悬停效果、过渡动画
- **功能优先**: 三大功能突出展示

#### 8. **templates/articles.html** - 文章库页面
**框架**: Bootstrap 5.1.3 + 自定义CSS
**作用**: 专门的文章浏览和管理页面

**功能特性**:
- **高级筛选**: 分类、难度、来源、排序
- **搜索功能**: 全文搜索支持
- **分页显示**: 每页12篇文章
- **文章卡片**: 展示标题、摘要、元信息
- **详情查看**: 模态框显示完整内容

#### 9. **static/app.js** - 主页JavaScript
**框架**: 原生JavaScript + Bootstrap JS
**作用**: 主页交互逻辑

**核心功能**:
```javascript
// 统计数据加载
loadStats()

// 智能推荐
recommendByExam(examLevel)

// 三大工具功能
analyzeDifficulty()    // 难度分析
generateSummary()      // 摘要生成  
classifyText()         // 智能分类

// 搜索和查看
performSearch()
viewArticle(id)
```

#### 10. **static/articles.js** - 文章页JavaScript
**框架**: 原生JavaScript + Bootstrap JS
**作用**: 文章库页面交互

**核心功能**:
```javascript
// 文章列表管理
loadArticles(page)
filterArticles()
searchArticles()

// 分页控制
updatePagination()

// 文章操作
viewArticle(id)
crawlNewArticles()
```

---

### 🚀 **工具脚本**

#### 11. **run.py** - 系统启动脚本
**作用**: 一键启动整个系统

**启动流程**:
1. 检查依赖包安装
2. 初始化数据库
3. 爬取初始数据（可选）
4. 启动Flask服务器

#### 12. **simple_prefill.py** - 数据预填充脚本
**作用**: 快速获取大量文章数据

**执行模式**:
- `python simple_prefill.py`: 完整模式（目标500篇）
- `python simple_prefill.py --quick`: 快速模式（测试用）

#### 13. **enhanced_prefill.py** - 增强预填充脚本
**作用**: 爬取文章并进行AI处理

**处理流程**:
1. 批量爬取文章
2. 难度分析
3. 摘要生成
4. 智能分类
5. 保存到数据库

#### 14. **test_system.py** - 系统测试脚本
**作用**: 全面测试系统功能

**测试项目**:
- 模块导入测试
- 数据库功能测试
- AI模块功能测试
- Web应用测试

---

### 📋 **配置文件**

#### 15. **requirements.txt** - Python依赖包
```txt
Flask==2.3.3
requests==2.32.3
beautifulsoup4==4.12.2
feedparser==6.0.10
textstat==0.7.3
jieba==0.42.1
sumy==0.11.0
scikit-learn==1.3.0
nltk==3.8.1
numpy==1.24.3
python-dateutil==2.8.2
```

#### 16. **README.md** - 项目说明文档
**内容**:
- 项目介绍
- 安装部署指南
- 使用说明
- API文档
- 开发指南

#### 17. **PROJECT_STRUCTURE.md** - 项目结构说明
**内容**:
- 详细的文件结构
- 开发规范
- 代码组织原则

---

## 🔄 **系统工作流程**

### 1. **数据获取流程**
```
RSS源列表 → feedparser解析 → BeautifulSoup提取正文 → 数据清洗 → 存入数据库
```

### 2. **AI处理流程**
```
原始文章 → 难度分析 → 摘要生成 → 智能分类 → 标签提取 → 更新数据库
```

### 3. **用户交互流程**
```
用户请求 → Flask路由 → 业务逻辑处理 → 数据库查询 → JSON响应 → 前端渲染
```

---

## 🎯 **核心功能详解**

### 1. **智能难度分析**
- **输入**: 英文文本
- **处理**: 多维度分析（词汇、句法、可读性）
- **输出**: 难度等级 + 评分 + 推荐考试

### 2. **自动摘要生成**
- **算法**: TextRank、LSA、Luhn、LexRank
- **参数**: 可调节摘要句数和方法
- **质量**: 自动评估摘要质量

### 3. **智能文章分类**
- **方法**: 关键词匹配 + 机器学习 + URL分析
- **分类**: 8大类别自动识别
- **标签**: 自动提取相关标签

### 4. **个性化推荐**
- **依据**: 考试等级（CET-4/6、IELTS、TOEFL）
- **算法**: 难度匹配 + 内容相关性
- **结果**: 推荐最适合的文章

### 5. **高级搜索**
- **全文搜索**: 标题、内容、作者
- **多维筛选**: 分类、难度、来源、时间
- **排序**: 时间、难度、篇幅多种排序

---

## 📊 **数据统计**

### 当前数据规模
- **文章总数**: 536篇
- **外刊源数**: 80+个
- **分类覆盖**: 8个主要分类
- **更新频率**: 支持实时爬取

### 数据质量
- **去重机制**: URL唯一性约束
- **内容过滤**: 最小200字符
- **来源可靠**: 知名外刊媒体
- **时效性**: 支持最新文章获取

---

## 🔧 **部署和运行**

### 环境要求
- Python 3.8+
- 8GB+ 内存推荐
- 网络连接（爬取功能）

### 快速启动
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 初始化数据
python simple_prefill.py --quick

# 3. 启动系统
python app.py
```

### 访问地址
- **主页**: http://127.0.0.1:5000
- **文章库**: http://127.0.0.1:5000/articles
- **API文档**: 内置于系统启动信息

---

## 🚀 **技术亮点**

1. **模块化设计**: 各功能模块独立，易于维护和扩展
2. **AI集成**: 集成多种NLP技术，提供智能化服务
3. **数据丰富**: 80+外刊源，保证内容质量和多样性
4. **用户体验**: 现代化UI设计，响应式布局
5. **API完整**: RESTful API设计，支持前后端分离
6. **容错机制**: 完善的错误处理和异常恢复
7. **扩展性强**: 易于添加新的外刊源和AI功能

这个系统为英语学习者提供了一个功能完整、技术先进的外刊学习平台！