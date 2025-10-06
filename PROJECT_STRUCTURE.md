# 项目结构说明

## 📁 文件结构

```
ermian/
├── 📄 README.md                    # 项目说明文档
├── 📄 PROJECT_STRUCTURE.md         # 项目结构说明
├── 📄 requirements.txt             # Python依赖包列表
├── 🐍 run.py                      # 系统启动脚本
├── 🐍 test_system.py              # 系统测试脚本
├── 🐍 app.py                      # Flask Web应用主文件
├── 🐍 database.py                 # 数据库管理模块
├── 🐍 crawler.py                  # 网页爬虫模块
├── 🐍 difficulty_analyzer.py      # 难度分析模块
├── 🐍 summarizer.py               # 摘要生成模块
├── 🐍 classifier.py               # 智能分类模块
├── 📁 templates/                  # HTML模板目录
│   └── 📄 index.html              # 主页面模板
├── 📁 static/                     # 静态资源目录
│   └── 📄 app.js                  # 前端JavaScript代码
└── 📁 data/                       # 数据存储目录（运行时生成）
    ├── 📄 articles.db             # SQLite数据库文件
    └── 📄 classifier_model.pkl    # 机器学习分类模型（可选）
```

## 🔧 核心模块说明

### 1. 数据库模块 (`database.py`)
- **功能**: 管理SQLite数据库，处理文章的增删改查
- **主要类**: `DatabaseManager`
- **核心方法**:
  - `init_database()`: 初始化数据库表结构
  - `add_article()`: 添加文章到数据库
  - `get_articles()`: 获取文章列表
  - `search_articles()`: 搜索文章
  - `get_categories()`: 获取分类列表

### 2. 爬虫模块 (`crawler.py`)
- **功能**: 爬取外刊网站的文章内容
- **主要类**: `ArticleCrawler`
- **支持网站**: BBC News, CNN News
- **核心方法**:
  - `crawl_bbc_news()`: 爬取BBC文章
  - `crawl_cnn_news()`: 爬取CNN文章
  - `crawl_all_sources()`: 爬取所有源的文章
  - `save_articles_to_db()`: 保存文章到数据库

### 3. 难度分析模块 (`difficulty_analyzer.py`)
- **功能**: 分析英文文本的难度等级
- **主要类**: `DifficultyAnalyzer`
- **分析指标**:
  - Flesch Reading Ease
  - Flesch-Kincaid Grade Level
  - Gunning Fog Index
  - 词汇复杂度
  - 句法复杂度
- **核心方法**:
  - `analyze_difficulty()`: 分析文本难度
  - `get_difficulty_explanation()`: 获取难度解释

### 4. 摘要生成模块 (`summarizer.py`)
- **功能**: 自动生成文章摘要
- **主要类**: `ArticleSummarizer`
- **支持算法**:
  - TextRank
  - LSA (Latent Semantic Analysis)
  - Luhn
  - LexRank
  - 关键词提取
- **核心方法**:
  - `generate_summary()`: 生成摘要
  - `generate_multiple_summaries()`: 生成多种摘要
  - `get_summary_quality_score()`: 评估摘要质量

### 5. 智能分类模块 (`classifier.py`)
- **功能**: 自动分类文章和提取标签
- **主要类**: `ArticleClassifier`
- **分类方法**:
  - 关键词匹配
  - 机器学习分类（可选）
  - URL分析
- **支持分类**: Technology, Business, Health, Education, Culture, Politics, Environment, Sports
- **核心方法**:
  - `classify_article()`: 分类文章
  - `extract_tags()`: 提取标签
  - `train_classifier()`: 训练机器学习模型

### 6. Web应用模块 (`app.py`)
- **功能**: Flask Web服务器，提供API接口
- **主要路由**:
  - `GET /`: 主页
  - `GET /api/articles`: 获取文章列表
  - `GET /api/articles/<id>`: 获取文章详情
  - `GET /api/articles/search`: 搜索文章
  - `GET /api/recommend`: 推荐文章
  - `POST /api/crawl`: 爬取新文章
  - `POST /api/analyze-difficulty`: 分析文本难度
  - `POST /api/generate-summary`: 生成摘要
  - `POST /api/classify`: 智能分类

## 🎨 前端界面说明

### 主页面 (`templates/index.html`)
- **设计风格**: 现代化响应式设计
- **主要功能**:
  - 文章浏览和搜索
  - 智能推荐
  - 分类和难度筛选
  - 学习工具集成
- **技术栈**: HTML5, CSS3, Bootstrap 5, JavaScript ES6+

### 前端脚本 (`static/app.js`)
- **功能**: 处理用户交互和API调用
- **主要功能**:
  - 文章列表展示
  - 搜索和筛选
  - 智能推荐
  - 模态框交互
  - 学习工具调用

## 🚀 启动和部署

### 开发环境启动
```bash
# 安装依赖
pip install -r requirements.txt

# 运行系统
python run.py

# 运行测试
python test_system.py
```

### 生产环境部署
```bash
# 使用Gunicorn部署
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📊 数据流程

```
1. 爬虫爬取文章 → 2. 难度分析 → 3. 摘要生成 → 4. 智能分类 → 5. 存储数据库
                                                                    ↓
6. Web界面展示 ← 5. API接口 ← 4. 数据库查询 ← 3. 用户请求
```

## 🔧 配置说明

### 数据库配置
- 默认使用SQLite数据库 (`articles.db`)
- 支持MySQL等关系型数据库（需修改连接配置）

### 爬虫配置
- 支持自定义爬取间隔和数量
- 可扩展支持更多外刊网站
- 支持代理设置（如需要）

### 难度分析配置
- 可调整难度等级阈值
- 支持自定义考试等级映射
- 可扩展更多分析指标

## 🛠️ 扩展开发

### 添加新的外刊源
1. 在 `crawler.py` 中添加新的爬取方法
2. 实现文章解析逻辑
3. 更新 `crawl_all_sources()` 方法

### 添加新的分类
1. 在 `classifier.py` 中更新 `category_keywords`
2. 在数据库中插入新分类
3. 更新前端筛选选项

### 添加新的摘要算法
1. 在 `summarizer.py` 中实现新算法
2. 更新 `summarizers` 字典
3. 在前端添加选择选项

## 📝 注意事项

1. **网络依赖**: 爬虫功能需要网络连接
2. **NLTK数据**: 首次运行会自动下载NLTK数据包
3. **数据库文件**: SQLite数据库文件会在首次运行时创建
4. **端口占用**: 默认使用5000端口，确保端口未被占用
5. **依赖版本**: 建议使用Python 3.8+版本

## 🔍 故障排除

### 常见问题
1. **模块导入失败**: 检查依赖包是否安装完整
2. **爬虫失败**: 检查网络连接和目标网站状态
3. **数据库错误**: 检查文件权限和磁盘空间
4. **前端显示异常**: 检查静态资源路径和浏览器控制台

### 调试模式
```bash
# 启用Flask调试模式
export FLASK_DEBUG=1
python app.py
```


