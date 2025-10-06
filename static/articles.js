// 全局变量
let currentArticles = [];
let currentCategories = [];
let currentSources = [];
let currentPage = 1;
let articlesPerPage = 12;
let totalArticles = 0;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    loadCategories();
    loadSources();
    loadArticles();
});

// 加载分类列表
async function loadCategories() {
    try {
        const response = await fetch('/api/categories');
        const data = await response.json();
        
        if (data.success) {
            currentCategories = data.data;
            const categorySelect = document.getElementById('categoryFilter');
            categorySelect.innerHTML = '<option value="">全部分类</option>';
            
            data.data.forEach(category => {
                const option = document.createElement('option');
                option.value = category.name;
                option.textContent = category.name;
                categorySelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('加载分类失败:', error);
    }
}

// 加载来源列表
async function loadSources() {
    try {
        const response = await fetch('/api/articles?limit=1000');
        const data = await response.json();
        
        if (data.success) {
            const sources = [...new Set(data.data.map(article => article.source).filter(Boolean))];
            currentSources = sources;
            
            const sourceSelect = document.getElementById('sourceFilter');
            sourceSelect.innerHTML = '<option value="">全部来源</option>';
            
            sources.forEach(source => {
                const option = document.createElement('option');
                option.value = source;
                option.textContent = source;
                sourceSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('加载来源失败:', error);
    }
}

// 加载文章列表
async function loadArticles(page = 1) {
    showLoading(true);
    currentPage = page;
    
    try {
        const category = document.getElementById('categoryFilter').value;
        const difficulty = document.getElementById('difficultyFilter').value;
        const source = document.getElementById('sourceFilter').value;
        const sortOrder = document.getElementById('sortOrder').value;
        
        let url = `/api/articles?limit=1000`;
        if (category) url += `&category=${encodeURIComponent(category)}`;
        if (difficulty) url += `&difficulty=${encodeURIComponent(difficulty)}`;
        if (source) url += `&source=${encodeURIComponent(source)}`;
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.success) {
            let articles = data.data;
            
            // 客户端排序
            articles = sortArticles(articles, sortOrder);
            
            currentArticles = articles;
            totalArticles = articles.length;
            
            // 分页处理
            const startIndex = (currentPage - 1) * articlesPerPage;
            const endIndex = startIndex + articlesPerPage;
            const pageArticles = articles.slice(startIndex, endIndex);
            
            displayArticles(pageArticles);
            updatePagination();
            updateArticleCount();
        } else {
            showError('加载文章失败: ' + data.error);
        }
    } catch (error) {
        console.error('加载文章失败:', error);
        showError('网络错误，请稍后重试');
    } finally {
        showLoading(false);
    }
}

// 排序文章
function sortArticles(articles, sortOrder) {
    switch (sortOrder) {
        case 'newest':
            return articles.sort((a, b) => new Date(b.created_at || b.publish_date) - new Date(a.created_at || a.publish_date));
        case 'oldest':
            return articles.sort((a, b) => new Date(a.created_at || a.publish_date) - new Date(b.created_at || b.publish_date));
        case 'difficulty_asc':
            return articles.sort((a, b) => (a.difficulty_score || 0) - (b.difficulty_score || 0));
        case 'difficulty_desc':
            return articles.sort((a, b) => (b.difficulty_score || 0) - (a.difficulty_score || 0));
        case 'length_asc':
            return articles.sort((a, b) => (a.word_count || 0) - (b.word_count || 0));
        case 'length_desc':
            return articles.sort((a, b) => (b.word_count || 0) - (a.word_count || 0));
        default:
            return articles;
    }
}

// 显示文章列表
function displayArticles(articles) {
    const articlesList = document.getElementById('articlesList');
    
    if (articles.length === 0) {
        articlesList.innerHTML = `
            <div class="no-articles">
                <i class="fas fa-search"></i>
                <h4>暂无文章</h4>
                <p>尝试调整筛选条件或<a href="#" onclick="crawlNewArticles()" class="text-primary">爬取新文章</a></p>
            </div>
        `;
        return;
    }
    
    articlesList.innerHTML = articles.map(article => `
        <div class="article-card">
            <div class="card-body">
                <div class="row">
                    <div class="col-md-8">
                        <h5 class="card-title mb-2">${article.title}</h5>
                        <div class="article-meta mb-3">
                            <i class="fas fa-user"></i> ${article.author || '未知作者'}
                            <i class="fas fa-calendar ms-3"></i> ${formatDate(article.publish_date)}
                            <i class="fas fa-globe ms-3"></i> ${article.source || '未知来源'}
                            <i class="fas fa-file-word ms-3"></i> ${article.word_count || 0} 词
                        </div>
                        ${article.summary ? `
                            <div class="summary-text">
                                <strong>摘要：</strong>${article.summary}
                            </div>
                        ` : ''}
                        <div class="mt-2">
                            ${article.tags ? article.tags.split(',').map(tag => 
                                `<span class="badge bg-secondary me-1">${tag.trim()}</span>`
                            ).join('') : ''}
                        </div>
                    </div>
                    <div class="col-md-4 text-end">
                        <div class="mb-2">
                            <span class="difficulty-badge difficulty-${(article.difficulty_level || 'unknown').toLowerCase()}">
                                ${getDifficultyText(article.difficulty_level)}
                            </span>
                        </div>
                        <div class="mb-2">
                            <span class="category-badge">${getCategoryText(article.category)}</span>
                        </div>
                        <div class="mb-2">
                            <span class="source-badge">${article.source || '未知来源'}</span>
                        </div>
                        ${article.difficulty_score ? `
                            <div class="text-muted small mb-3">
                                <i class="fas fa-chart-line"></i> 难度: ${article.difficulty_score}/100
                            </div>
                        ` : ''}
                        <div class="btn-group-vertical w-100">
                            <button class="btn btn-outline-primary btn-sm mb-1" onclick="viewArticle(${article.id})">
                                <i class="fas fa-eye me-1"></i>查看详情
                            </button>
                            ${article.url ? `
                                <a href="${article.url}" target="_blank" class="btn btn-outline-success btn-sm">
                                    <i class="fas fa-external-link-alt me-1"></i>阅读原文
                                </a>
                            ` : ''}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

// 查看文章详情
async function viewArticle(articleId) {
    try {
        const response = await fetch(`/api/articles/${articleId}`);
        const data = await response.json();
        
        if (data.success) {
            const article = data.data;
            const modal = new bootstrap.Modal(document.getElementById('articleModal'));
            
            document.getElementById('articleModalTitle').textContent = article.title;
            document.getElementById('articleModalLink').href = article.url || '#';
            
            document.getElementById('articleModalBody').innerHTML = `
                <div class="mb-3">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span class="difficulty-badge difficulty-${(article.difficulty_level || 'unknown').toLowerCase()}">
                            ${getDifficultyText(article.difficulty_level)}
                        </span>
                        <div>
                            <span class="category-badge me-2">${getCategoryText(article.category)}</span>
                            <span class="source-badge">${article.source || '未知来源'}</span>
                        </div>
                    </div>
                    <div class="article-meta">
                        <i class="fas fa-user"></i> ${article.author || '未知作者'}
                        <i class="fas fa-calendar ms-3"></i> ${formatDate(article.publish_date)}
                        <i class="fas fa-file-word ms-3"></i> ${article.word_count || 0} 词
                        ${article.difficulty_score ? `<i class="fas fa-chart-line ms-3"></i> 难度: ${article.difficulty_score}/100` : ''}
                    </div>
                </div>
                
                ${article.summary ? `
                    <div class="summary-text">
                        <h6><i class="fas fa-compress-alt me-2"></i>文章摘要</h6>
                        <p>${article.summary}</p>
                    </div>
                ` : ''}
                
                <div class="article-content">
                    <h6><i class="fas fa-file-text me-2"></i>文章内容</h6>
                    <div style="white-space: pre-wrap; line-height: 1.8;">${article.content}</div>
                </div>
                
                ${article.tags ? `
                    <div class="mt-3">
                        <h6><i class="fas fa-tags me-2"></i>标签</h6>
                        ${article.tags.split(',').map(tag => 
                            `<span class="badge bg-secondary me-1">${tag.trim()}</span>`
                        ).join('')}
                    </div>
                ` : ''}
                
                ${article.difficulty_score ? `
                    <div class="mt-3 p-3 bg-light rounded">
                        <h6><i class="fas fa-chart-line me-2"></i>难度分析</h6>
                        <p><strong>难度评分：</strong>${article.difficulty_score}/100</p>
                        <p><strong>推荐考试：</strong>${getRecommendedExam(article.difficulty_score)}</p>
                        <p><strong>学习建议：</strong>${getDifficultyAdvice(article.difficulty_level)}</p>
                    </div>
                ` : ''}
            `;
            
            modal.show();
        } else {
            showError('加载文章详情失败: ' + data.error);
        }
    } catch (error) {
        console.error('加载文章详情失败:', error);
        showError('网络错误，请稍后重试');
    }
}

// 搜索文章
async function searchArticles() {
    const keyword = document.getElementById('searchInput').value.trim();
    if (!keyword) {
        showError('请输入搜索关键词');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`/api/articles/search?q=${encodeURIComponent(keyword)}&limit=1000`);
        const data = await response.json();
        
        if (data.success) {
            currentArticles = data.data;
            totalArticles = data.data.length;
            currentPage = 1;
            
            const pageArticles = currentArticles.slice(0, articlesPerPage);
            displayArticles(pageArticles);
            updatePagination();
            updateArticleCount();
            
            showSuccess(`找到 ${data.total} 篇相关文章`);
        } else {
            showError('搜索失败: ' + data.error);
        }
    } catch (error) {
        console.error('搜索失败:', error);
        showError('网络错误，请稍后重试');
    } finally {
        showLoading(false);
    }
}

// 清除搜索
function clearSearch() {
    document.getElementById('searchInput').value = '';
    document.getElementById('categoryFilter').value = '';
    document.getElementById('difficultyFilter').value = '';
    document.getElementById('sourceFilter').value = '';
    document.getElementById('sortOrder').value = 'newest';
    loadArticles(1);
}

// 筛选文章
function filterArticles() {
    loadArticles(1);
}

// 爬取新文章
async function crawlNewArticles() {
    if (!confirm('确定要爬取新文章吗？这可能需要几分钟时间。')) {
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch('/api/crawl', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                max_articles: 50,
                source: 'all'
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess(data.message);
            loadArticles(1); // 重新加载文章列表
            loadSources(); // 重新加载来源列表
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

// 更新分页
function updatePagination() {
    const totalPages = Math.ceil(totalArticles / articlesPerPage);
    const pagination = document.getElementById('pagination');
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let paginationHTML = '';
    
    // 上一页
    if (currentPage > 1) {
        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="loadArticles(${currentPage - 1})">
                    <i class="fas fa-chevron-left"></i>
                </a>
            </li>
        `;
    }
    
    // 页码
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);
    
    if (startPage > 1) {
        paginationHTML += `<li class="page-item"><a class="page-link" href="#" onclick="loadArticles(1)">1</a></li>`;
        if (startPage > 2) {
            paginationHTML += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
        }
    }
    
    for (let i = startPage; i <= endPage; i++) {
        paginationHTML += `
            <li class="page-item ${i === currentPage ? 'active' : ''}">
                <a class="page-link" href="#" onclick="loadArticles(${i})">${i}</a>
            </li>
        `;
    }
    
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            paginationHTML += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
        }
        paginationHTML += `<li class="page-item"><a class="page-link" href="#" onclick="loadArticles(${totalPages})">${totalPages}</a></li>`;
    }
    
    // 下一页
    if (currentPage < totalPages) {
        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="loadArticles(${currentPage + 1})">
                    <i class="fas fa-chevron-right"></i>
                </a>
            </li>
        `;
    }
    
    pagination.innerHTML = paginationHTML;
}

// 更新文章计数
function updateArticleCount() {
    document.getElementById('articleCount').textContent = totalArticles;
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

function getRecommendedExam(score) {
    if (score < 30) return 'CET-4';
    if (score < 40) return 'CET-6';
    if (score < 50) return 'IELTS-6.0 / TOEFL-80';
    if (score < 60) return 'IELTS-6.5 / TOEFL-90';
    if (score < 70) return 'IELTS-7.0';
    return 'TOEFL-100+';
}

function getDifficultyAdvice(level) {
    const adviceMap = {
        'Beginner': '适合英语初学者，建议先掌握基础词汇和语法',
        'Intermediate': '适合有一定基础的学习者，重点学习长难句和复杂词汇',
        'Advanced': '适合英语水平较高的学习者，关注文章结构和逻辑关系',
        'Expert': '适合英语专业或高水平学习者，进行深度阅读和批判性思考'
    };
    return adviceMap[level] || '根据个人水平选择合适的学习方法';
}

// 分类显示文本（将 Unknown/未知 统一为“综合”）
function getCategoryText(cat) {
    if (!cat || String(cat).trim() === '') return '未分类';
    const c = String(cat).trim().toLowerCase();
    if (c === 'unknown' || c === '未知') return '综合';
    return cat;
}

// 搜索框回车事件
document.getElementById('searchInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        searchArticles();
    }
});