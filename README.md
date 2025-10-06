# 外刊推荐系统

> 专为四六级、雅思托福等英语考试设计的智能外刊学习平台

## 🎯 项目简介

本系统是一个智能化的外刊推荐平台，专门针对大学生在四六级、雅思托福等英语考试上的学习需求而设计。系统通过爬取外刊文章、智能分析难度、自动生成摘要和分类，为学习者提供个性化的英语阅读材料推荐。

## ✨ 主要功能

### 🕷️ 智能爬虫
- 支持爬取BBC News、CNN等知名外刊网站
- 自动提取文章标题、作者、内容、发布日期等信息
- 智能过滤和去重，确保数据质量

### 📊 难度分级
- 基于词汇量、句法复杂度等多维度指标分析文章难度
- 将难度等级映射至常见考试难度（CET-4、CET-6、IELTS、TOEFL等）
- 提供详细的难度分析报告和学习建议

### 📝 摘要生成
- 支持多种摘要算法（TextRank、LSA、Luhn、LexRank等）
- 自动生成文章摘要，提高阅读效率
- 可调节摘要长度和质量

### 🏷️ 智能分类
- 基于关键词和机器学习算法自动分类文章
- 支持8大分类：科技、商业、健康、教育、文化、政治、环境、体育
- 自动提取文章标签，便于筛选和搜索

### 🌐 Web界面
- 现代化的响应式设计
- 支持文章浏览、搜索、筛选
- 智能推荐功能，根据考试等级推荐文章
- 内置学习工具：难度分析、摘要生成、智能分类

## 🛠️ 技术栈

### 后端技术
- **Python 3.8+** - 主要编程语言
- **Flask** - Web框架
- **SQLite** - 数据库
- **Requests + BeautifulSoup** - 网页爬虫
- **textstat** - 文本难度分析
- **sumy** - 摘要生成
- **scikit-learn** - 机器学习分类
- **NLTK** - 自然语言处理

### 前端技术
- **HTML5 + CSS3** - 页面结构 and 样式
- **Bootstrap 5** - UI框架
- **JavaScript (ES6+)** - 交互逻辑
- **Font Awesome** - 图标库

## 📦 安装部署

### 环境要求
- Python 3.8 或更高版本
- pip 包管理器

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/loopy898/article-ai-system.git
cd article-ai-system
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **运行系统**
```bash
python run.py
```

4. **访问系统**
打开浏览器访问：http://localhost:5000

## 🚀 快速开始

### 1. 启动系统
```bash
python run.py
```

### 2. 爬取文章数据
- 在Web界面点击"爬取新文章"按钮
- 或使用API接口：`POST /api/crawl`

### 3. 浏览和搜索文章
- 使用分类和难度筛选器
- 在搜索框输入关键词搜索
- 点击文章查看详细内容

### 4. 智能推荐
- 选择你的考试目标（CET-4、CET-6、IELTS等）
- 系统会自动推荐适合难度的文章

### 5. 使用学习工具
- **难度分析**：粘贴英文文本，获取难度评估
- **摘要生成**：输入长文章，生成简洁摘要
- **智能分类**：输入文章标题和内容，自动分类

## 📚 API接口文档

### 文章相关
- `GET /api/articles` - 获取文章列表
- `GET /api/articles/<id>` - 获取文章详情
- `GET /api/articles/search?q=关键词` - 搜索文章
- `GET /api/recommend` - 推荐文章

### 分类和统计
- `GET /api/categories` - 获取分类列表
- `GET /api/difficulty-stats` - 获取难度统计

### 功能接口
- `POST /api/crawl` - 爬取新文章
- `POST /api/analyze-difficulty` - 分析文本难度
- `POST /api/generate-summary` - 生成摘要
- `POST /api/classify` - 智能分类

## 🎓 使用场景

### 四六级备考
- 选择CET-4或CET-6难度
- 阅读适合水平的文章
- 通过摘要快速了解文章内容
- 分析文章难度，评估自己的阅读水平

### 雅思托福准备
- 选择对应的IELTS或TOEFL难度等级
- 阅读学术类文章，提高阅读速度
- 使用摘要功能，练习快速理解文章主旨
- 通过难度分析，了解自己的薄弱环节

### 日常英语学习
- 浏览不同分类的文章，扩大知识面
- 使用智能推荐，发现感兴趣的内容
- 通过难度分析，循序渐进地提高阅读水平

## 🔧 系统架构

```
外刊推荐系统
├── 数据层
│   ├── 爬虫模块 (crawler.py)
│   ├── 数据库管理 (database.py)
│   └── 数据存储 (SQLite)
├── 分析层
│   ├── 难度分析 (difficulty_analyzer.py)
│   ├── 摘要生成 (summarizer.py)
│   └── 智能分类 (classifier.py)
├── 服务层
│   └── Web API (app.py)
└── 展示层
    ├── 前端界面 (templates/index.html)
    └── 静态资源 (static/app.js)
```

## 📈 功能特色

### 智能难度匹配
- 基于Flesch Reading Ease、Flesch-Kincaid Grade Level等指标
- 综合考虑词汇复杂度、句法复杂度等因素
- 精确映射到具体考试等级

### 个性化推荐
- 根据用户选择的考试等级推荐文章
- 支持按分类、难度、关键词筛选
- 智能排序，优先显示高质量文章

### 学习工具集成
- 内置难度分析工具，随时检测文本难度
- 多种摘要算法，满足不同需求
- 智能分类功能，快速了解文章主题

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

### 开发环境设置
1. Fork项目到你的GitHub账户
2. 克隆你的Fork到本地
3. 创建新的功能分支
4. 提交你的更改
5. 推送到你的Fork
6. 创建Pull Request

## 🙏 致谢

感谢以下开源项目的支持：
- [Flask](https://flask.palletsprojects.com/) - Web框架
- [Bootstrap](https://getbootstrap.com/) - UI框架
- [textstat](https://github.com/shivam5992/textstat) - 文本统计
- [sumy](https://github.com/miso-belica/sumy) - 摘要生成
- [scikit-learn](https://scikit-learn.org/) - 机器学习

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件至：1706636899@qq.com

---

**祝你在英语学习的道路上越走越远！** 🎓✨
