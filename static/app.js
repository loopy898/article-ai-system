// 全局变量
let currentArticles = [];
let currentCategories = [];
let currentDifficultyStats = [];

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    loadStats();
});

// 加载统计数据
async function loadStats() {
    try {
        // 加载文章统计
        const articlesResponse = await fetch('/api/articles?limit=1000');
        const articlesData = await articlesResponse.json();
        
        if (articlesData.success) {
            const articles = articlesData.data;
            document.getElementById('totalArticles').textContent = articles.length;
            
            if (articles.length > 0) {
                const avgScore = articles.reduce((sum, article) => 
                    sum + (article.difficulty_score || 0), 0) / articles.length;
                document.getElementById('avgDifficulty').textContent = avgScore.toFixed(1);
                
                const latestArticle = articles[0];
                document.getElementById('lastUpdate').textContent = formatDate(latestArticle.created_at);
            }
        }
        
        // 加载分类统计
        const categoriesResponse = await fetch('/api/categories');
        const categoriesData = await categoriesResponse.json();
        
        if (categoriesData.success) {
            document.getElementById('totalCategories').textContent = categoriesData.data.length;
        }
        
    } catch (error) {
        console.error('加载统计数据失败:', error);
    }
}

// 显示推荐区域
function showRecommendations() {
    const section = document.getElementById('recommendSection');
    section.style.display = section.style.display === 'none' ? 'block' : 'none';
    
    if (section.style.display === 'block') {
        section.scrollIntoView({ behavior: 'smooth' });
    }
}

// 显示爬虫对话框
function showCrawlDialog() {
    if (confirm('确定要更新文章库吗？系统将从多个外刊网站爬取最新文章，这可能需要几分钟时间。')) {
        crawlNewArticles();
    }
}

// 显示搜索对话框
function showSearchDialog() {
    const modal = new bootstrap.Modal(document.getElementById('searchModal'));
    modal.show();
}

// 执行搜索
async function performSearch() {
    const keyword = document.getElementById('searchKeyword').value.trim();
    if (!keyword) {
        showError('请输入搜索关键词');
        return;
    }
    
    try {
        const response = await fetch(`/api/articles/search?q=${encodeURIComponent(keyword)}&limit=10`);
        const data = await response.json();
        
        if (data.success) {
            displaySearchResults(data.data, keyword);
        } else {
            showError('搜索失败: ' + data.error);
        }
    } catch (error) {
        console.error('搜索失败:', error);
        showError('网络错误，请稍后重试');
    }
}

// 显示搜索结果
function displaySearchResults(articles, keyword) {
    const container = document.getElementById('searchResults');
    
    if (articles.length === 0) {
        container.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                没有找到包含"${keyword}"的文章
            </div>
        `;
        return;
    }
    
    container.innerHTML = `
        <div class="alert alert-success">
            <i class="fas fa-check-circle me-2"></i>
            找到 ${articles.length} 篇相关文章
        </div>
        <div class="list-group">
            ${articles.map(article => `
                <div class="list-group-item">
                    <h6 class="mb-1">${article.title}</h6>
                    <p class="mb-1 text-muted small">${article.summary ? article.summary.substring(0, 100) + '...' : '暂无摘要'}</p>
                    <small class="text-muted">
                        <span class="badge difficulty-badge difficulty-${(article.difficulty_level || 'unknown').toLowerCase()} me-1">
                            ${getDifficultyText(article.difficulty_level)}
                        </span>
                        <span class="badge category-badge me-1">${getCategoryText(article.category)}</span>
                        ${article.source} • ${formatDate(article.publish_date)}
                    </small>
                    <div class="mt-2">
                        <button class="btn btn-outline-primary btn-sm" onclick="viewArticleFromSearch(${article.id})">
                            查看详情
                        </button>
                        <a href="/articles" class="btn btn-primary btn-sm ms-2">
                            前往文章库
                        </a>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

// 从搜索结果查看文章
async function viewArticleFromSearch(articleId) {
    // 关闭搜索模态框
    const searchModal = bootstrap.Modal.getInstance(document.getElementById('searchModal'));
    searchModal.hide();
    
    // 查看文章详情
    await viewArticle(articleId);
}

// 根据考试等级推荐文章
async function recommendByExam(examLevel) {
    // 更新按钮状态
    document.querySelectorAll('.exam-level-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    showLoading(true);
    
    try {
        const response = await fetch(`/api/recommend?exam_level=${encodeURIComponent(examLevel)}&limit=6`);
        const data = await response.json();
        
        if (data.success) {
            displayRecommendedArticles(data.data, examLevel);
        } else {
            showError('推荐失败: ' + data.error);
        }
    } catch (error) {
        console.error('推荐失败:', error);
        showError('网络错误，请稍后重试');
    } finally {
        showLoading(false);
    }
}

// 显示推荐文章
function displayRecommendedArticles(articles, examLevel) {
    const container = document.getElementById('recommendedArticles');
    
    if (articles.length === 0) {
        container.innerHTML = `
            <div class="text-center py-4">
                <i class="fas fa-info-circle fa-2x text-muted mb-2"></i>
                <p class="text-muted">暂无适合 ${examLevel} 水平的文章，请尝试其他考试等级或<a href="#" onclick="crawlNewArticles()" class="text-primary">更新文章库</a></p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = `
        <div class="alert alert-success">
            <i class="fas fa-magic me-2"></i>
            为您推荐 ${articles.length} 篇适合 ${examLevel} 水平的文章
        </div>
        <div class="row">
            ${articles.map(article => `
                <div class="col-md-6 mb-3">
                    <div class="card h-100">
                        <div class="card-body">
                            <h6 class="card-title">${article.title}</h6>
                            <p class="card-text text-muted small">
                                <i class="fas fa-user me-1"></i>${article.author || '未知作者'}
                                <i class="fas fa-globe ms-2 me-1"></i>${article.source}
                                <i class="fas fa-file-word ms-2 me-1"></i>${article.word_count || 0} 词
                            </p>
                            ${article.summary ? `
                                <p class="card-text small">${article.summary.substring(0, 120)}...</p>
                            ` : ''}
                            <div class="d-flex justify-content-between align-items-center mt-auto">
                                <span class="badge difficulty-badge difficulty-${(article.difficulty_level || 'unknown').toLowerCase()}">
                                    ${getDifficultyText(article.difficulty_level)}
                                </span>
                                <div>
                                    <button class="btn btn-outline-primary btn-sm" onclick="viewArticle(${article.id})">
                                        查看详情
                                    </button>
                                    ${article.url ? `
                                        <a href="${article.url}" target="_blank" class="btn btn-outline-success btn-sm ms-1">
                                            阅读原文
                                        </a>
                                    ` : ''}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
        <div class="text-center mt-3">
            <a href="/articles" class="btn btn-primary">
                <i class="fas fa-book me-2"></i>查看更多文章
            </a>
        </div>
    `;
}

// 查看文章详情
async function viewArticle(articleId) {
    try {
        const response = await fetch(`/api/articles/${articleId}`);
        const data = await response.json();
        
        if (data.success) {
            const article = data.data;
            
            // 创建并显示模态框
            const modalHTML = `
                <div class="modal fade" id="articleDetailModal" tabindex="-1">
                    <div class="modal-dialog modal-xl">
                        <div class="modal-content">
                            <div class="modal-header" style="background: linear-gradient(45deg, #667eea, #764ba2); color: white;">
                                <h5 class="modal-title">${article.title}</h5>
                                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <div class="mb-3">
                                    <div class="d-flex justify-content-between align-items-center mb-2">
                                        <span class="badge difficulty-badge difficulty-${(article.difficulty_level || 'unknown').toLowerCase()}">
                                            ${getDifficultyText(article.difficulty_level)}
                                        </span>
                                        <div>
                                            <span class="badge category-badge me-2">${getCategoryText(article.category)}</span>
                                            <span class="badge bg-info">${article.source || '未知来源'}</span>
                                        </div>
                                    </div>
                                    <p class="text-muted">
                                        <i class="fas fa-user me-1"></i>${article.author || '未知作者'}
                                        <i class="fas fa-calendar ms-3 me-1"></i>${formatDate(article.publish_date)}
                                        <i class="fas fa-file-word ms-3 me-1"></i>${article.word_count || 0} 词
                                        ${article.difficulty_score ? `<i class="fas fa-chart-line ms-3 me-1"></i>难度: ${article.difficulty_score}/100` : ''}
                                    </p>
                                </div>
                                
                                ${article.summary ? `
                                    <div class="alert alert-info">
                                        <h6><i class="fas fa-compress-alt me-2"></i>文章摘要</h6>
                                        <p class="mb-0">${article.summary}</p>
                                    </div>
                                ` : ''}
                                
                                <div class="article-content" style="max-height: 400px; overflow-y: auto; line-height: 1.8;">
                                    <h6><i class="fas fa-file-text me-2"></i>文章内容</h6>
                                    <div style="white-space: pre-wrap;">${article.content}</div>
                                </div>
                                
                                ${article.tags ? `
                                    <div class="mt-3">
                                        <h6><i class="fas fa-tags me-2"></i>标签</h6>
                                        ${article.tags.split(',').map(tag => 
                                            `<span class="badge bg-secondary me-1">${tag.trim()}</span>`
                                        ).join('')}
                                    </div>
                                ` : ''}
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                                ${article.url ? `
                                    <a href="${article.url}" target="_blank" class="btn btn-primary">
                                        <i class="fas fa-external-link-alt me-2"></i>阅读原文
                                    </a>
                                ` : ''}
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // 移除旧的模态框
            const oldModal = document.getElementById('articleDetailModal');
            if (oldModal) {
                oldModal.remove();
            }
            
            // 添加新的模态框
            document.body.insertAdjacentHTML('beforeend', modalHTML);
            
            // 显示模态框
            const modal = new bootstrap.Modal(document.getElementById('articleDetailModal'));
            modal.show();
            
        } else {
            showError('加载文章详情失败: ' + data.error);
        }
    } catch (error) {
        console.error('加载文章详情失败:', error);
        showError('网络错误，请稍后重试');
    }
}

// 爬取新文章
async function crawlNewArticles() {
    showLoading(true);
    
    try {
        const response = await fetch('/api/crawl', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                max_articles: 100,
                source: 'all'
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess(data.message);
            loadStats(); // 重新加载统计数据
        } else {
            showError('爬取失败: ' + data.error);
        }
    } catch (error) {
        console.error('爬取失败:', error);
        showError('网络错误，请稍后重试');
    } finally {
        showLoading(false);
    }
}

// 分析文本难度
async function analyzeDifficulty() {
    const text = document.getElementById('difficultyText').value.trim();
    if (!text) {
        showError('请输入要分析的文本');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch('/api/analyze-difficulty', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: text })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const result = data.data;
            document.getElementById('difficultyResult').innerHTML = `
                <div class="alert alert-success">
                    <h6><i class="fas fa-chart-line me-2"></i>难度分析结果</h6>
                    <div class="row">
                        <div class="col-md-6">
                            <p><strong>难度等级：</strong>
                                <span class="badge difficulty-badge difficulty-${result.difficulty_level.toLowerCase()}">
                                    ${getDifficultyText(result.difficulty_level)}
                                </span>
                            </p>
                            <p><strong>难度评分：</strong>${result.difficulty_score}/100</p>
                            <p><strong>推荐考试：</strong>${result.recommended_exam}</p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>词汇复杂度：</strong>${result.details.vocab_complexity}/100</p>
                            <p><strong>句法复杂度：</strong>${result.details.syntax_complexity}/100</p>
                            <p><strong>平均句长：</strong>${result.details.avg_sentence_length} 词/句</p>
                        </div>
                    </div>
                </div>
            `;
        } else {
            showError('分析失败: ' + data.error);
        }
    } catch (error) {
        console.error('分析失败:', error);
        showError('网络错误，请稍后重试');
    } finally {
        showLoading(false);
    }
}

// 生成摘要
async function generateSummary() {
    const text = document.getElementById('summaryText').value.trim();
    const method = document.getElementById('summaryMethod').value;
    const count = document.getElementById('summaryCount').value;
    
    if (!text) {
        showError('请输入要摘要的文本');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch('/api/generate-summary', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                text: text,
                method: method,
                sentences_count: parseInt(count)
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const result = data.data;
            document.getElementById('summaryResult').innerHTML = `
                <div class="alert alert-success">
                    <h6><i class="fas fa-file-text me-2"></i>摘要生成结果</h6>
                    <p><strong>摘要方法：</strong>${method.toUpperCase()}</p>
                    <p><strong>质量评分：</strong>${(result.quality_score * 100).toFixed(1)}%</p>
                    <hr>
                    <h6>生成的摘要：</h6>
                    <div class="p-3 bg-light rounded" style="white-space: pre-wrap;">${result.summary}</div>
                </div>
            `;
        } else {
            showError('摘要生成失败: ' + data.error);
        }
    } catch (error) {
        console.error('摘要生成失败:', error);
        showError('网络错误，请稍后重试');
    } finally {
        showLoading(false);
    }
}

// 智能分类
async function classifyText() {
    const title = document.getElementById('classifyTitle').value.trim();
    const content = document.getElementById('classifyContent').value.trim();
    
    if (!title && !content) {
        showError('请输入标题或内容');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch('/api/classify', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                title: title,
                content: content
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const result = data.data;
            document.getElementById('classifyResult').innerHTML = `
                <div class="alert alert-success">
                    <h6><i class="fas fa-tags me-2"></i>分类结果</h6>
                    <p><strong>分类：</strong>
                        <span class="badge category-badge">${result.category}</span>
                    </p>
                    <p><strong>标签：</strong>
                        ${result.tags.map(tag => `<span class="badge bg-secondary me-1">${tag}</span>`).join('')}
                    </p>
                </div>
            `;
        } else {
            showError('分类失败: ' + data.error);
        }
    } catch (error) {
        console.error('分类失败:', error);
        showError('网络错误，请稍后重试');
    } finally {
        showLoading(false);
    }
}

// 显示加载状态
function showLoading(show) {
    document.getElementById('loading').style.display = show ? 'block' : 'none';
}

// 显示成功消息
function showSuccess(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-success alert-dismissible fade show position-fixed';
    alert.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alert.innerHTML = `
        <i class="fas fa-check-circle me-2"></i>${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alert);
    
    setTimeout(() => {
        if (alert.parentNode) {
            alert.parentNode.removeChild(alert);
        }
    }, 3000);
}

// 显示错误消息
function showError(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-danger alert-dismissible fade show position-fixed';
    alert.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alert.innerHTML = `
        <i class="fas fa-exclamation-circle me-2"></i>${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alert);
    
    setTimeout(() => {
        if (alert.parentNode) {
            alert.parentNode.removeChild(alert);
        }
    }, 5000);
}

// 工具函数
function formatDate(dateString) {
    if (!dateString) return '未知';
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN');
}

function getDifficultyText(level) {
    const difficultyMap = {
        'Beginner': '初级',
        'Intermediate': '中级', 
        'Advanced': '高级',
        'Expert': '专家级'
    };
    return difficultyMap[level] || level || '未知';
}

// 分类显示文本（将 Unknown/未知 统一为“综合”）
function getCategoryText(cat) {
    if (!cat || String(cat).trim() === '') return '未分类';
    const c = String(cat).trim().toLowerCase();
    if (c === 'unknown' || c === '未知') return '综合';
    return cat;
}