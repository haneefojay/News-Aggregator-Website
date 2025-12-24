const API_URL = 'http://localhost:8000/api/v1';

let currentPage = 1;
let currentCategory = 'all';
let currentSource = '';
let searchQuery = '';

// DOM Elements
const newsGrid = document.getElementById('newsGrid');
const loading = document.getElementById('loading');
const noResults = document.getElementById('noResults');
const searchInput = document.getElementById('searchInput');
const customSelectTrigger = document.getElementById('customSelectTrigger');
const customOptionsList = document.getElementById('customOptionsList');
const selectedSourceText = document.getElementById('selectedSourceText');
const categoryButtons = document.querySelectorAll('.filter-btn');
const pageNumbers = document.getElementById('pageNumbers');
const prevPage = document.getElementById('prevPage');
const nextPage = document.getElementById('nextPage');
const syncBtn = document.getElementById('syncBtn');
const themeToggle = document.getElementById('themeToggle');

// Modal Elements
const articleModal = document.getElementById('articleModal');
const modalImage = document.getElementById('modalImage');
const modalCategory = document.getElementById('modalCategory');
const modalSource = document.getElementById('modalSource');
const modalDate = document.getElementById('modalDate');
const modalTitle = document.getElementById('modalTitle');
const modalAuthor = document.getElementById('modalAuthor');
const modalDescription = document.getElementById('modalDescription');
const modalSourceLink = document.getElementById('modalSourceLink');
const modalClose = document.querySelector('.modal-close');
const modalBackdrop = document.querySelector('.modal-backdrop');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    fetchNews();
    setupEventListeners();
});

function setupEventListeners() {
    // Search with debounce
    let timeout = null;
    searchInput.addEventListener('input', (e) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            searchQuery = e.target.value;
            currentPage = 1;
            fetchNews();
        }, 500);
    });

    // Category filtering
    categoryButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            categoryButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentCategory = btn.dataset.category;
            currentPage = 1;
            fetchNews();
        });
    });

    // Custom Source Dropdown Logic
    customSelectTrigger.addEventListener('click', (e) => {
        e.stopPropagation();
        customSelectTrigger.classList.toggle('active');
        customOptionsList.classList.toggle('show');
    });

    customOptionsList.querySelectorAll('li').forEach(option => {
        option.addEventListener('click', () => {
            currentSource = option.dataset.value;
            selectedSourceText.textContent = option.textContent;

            // UI styling
            customOptionsList.querySelectorAll('li').forEach(li => li.classList.remove('selected'));
            option.classList.add('selected');

            // Close dropdown
            customSelectTrigger.classList.remove('active');
            customOptionsList.classList.remove('show');

            currentPage = 1;
            fetchNews();
        });
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', () => {
        customSelectTrigger.classList.remove('active');
        customOptionsList.classList.remove('show');
    });

    // Pagination
    prevPage.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            fetchNews();
        }
    });

    nextPage.addEventListener('click', () => {
        currentPage++;
        fetchNews();
    });

    // Manual Sync
    syncBtn.addEventListener('click', async () => {
        const icon = syncBtn.querySelector('i');
        syncBtn.disabled = true;
        icon.classList.add('fa-spin');

        try {
            const response = await fetch(`${API_URL}/sync`, { method: 'POST' });
            if (response.ok) {
                // Wait a few seconds for the worker to start getting data
                setTimeout(() => {
                    fetchNews();
                    syncBtn.disabled = false;
                    icon.classList.remove('fa-spin');
                }, 3000);
            }
        } catch (error) {
            console.error('Sync error:', error);
            syncBtn.disabled = false;
            icon.classList.remove('fa-spin');
        }
    });

    // Theme Toggle
    themeToggle.addEventListener('click', () => {
        const isDark = document.body.getAttribute('data-theme') === 'light';
        setTheme(isDark ? 'dark' : 'light');
    });

    // Initial theme load
    const savedTheme = localStorage.getItem('pulse-theme') || 'dark';
    setTheme(savedTheme);

    // Modal Close
    modalClose.addEventListener('click', closeModal);
    modalBackdrop.addEventListener('click', closeModal);
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeModal();
    });
}

function setTheme(theme) {
    if (theme === 'light') {
        document.body.setAttribute('data-theme', 'light');
        themeToggle.querySelector('i').className = 'fa-solid fa-sun';
    } else {
        document.body.removeAttribute('data-theme');
        themeToggle.querySelector('i').className = 'fa-solid fa-moon';
    }
    localStorage.setItem('pulse-theme', theme);
}

function openModal(article) {
    modalImage.src = article.image_url || 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=1000&auto=format&fit=crop';
    modalCategory.textContent = article.category || 'Focus';
    modalSource.textContent = article.source;
    modalDate.textContent = formatDate(article.published_at);
    modalTitle.textContent = article.title;
    modalAuthor.innerHTML = `<i class="fa-solid fa-user-pen"></i> ${article.author || 'Pulse Reporter'}`;

    // Approach C: Summary-First (only show the lead)
    modalDescription.innerHTML = article.description || 'No description available for this article.';
    modalSourceLink.href = article.url;

    // Ensure any links in the summary open in new tabs
    modalDescription.querySelectorAll('a').forEach(link => {
        link.setAttribute('target', '_blank');
        link.setAttribute('rel', 'noopener noreferrer');
    });

    articleModal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    articleModal.classList.add('hidden');
    document.body.style.overflow = ''; // Restore scrolling
}

async function fetchNews() {
    showLoading(true);

    try {
        const params = new URLSearchParams({
            page: currentPage,
            page_size: 12
        });

        if (currentCategory !== 'all') params.append('category', currentCategory);
        if (currentSource) params.append('source', currentSource);
        if (searchQuery) params.append('q', searchQuery);

        const response = await fetch(`${API_URL}/articles?${params}`);
        const data = await response.json();

        displayNews(data.articles);
        updatePagination(data.total, data.page, data.page_size);
    } catch (error) {
        console.error('Error fetching news:', error);
        // If API fails, show "connection error" message
        newsGrid.innerHTML = '';
        noResults.classList.remove('hidden');
        noResults.querySelector('h3').textContent = 'Something went wrong';
        noResults.querySelector('p').textContent = 'We’re unable to connect to our servers right now. Please check your internet connection and try again.';
    } finally {
        showLoading(false);
    }
}

function displayNews(articles) {
    newsGrid.innerHTML = '';

    if (!articles || articles.length === 0) {
        noResults.classList.remove('hidden');
        return;
    }

    noResults.classList.add('hidden');

    articles.forEach(article => {
        const card = document.createElement('div');
        card.className = 'news-card';

        // Handle missing images with a nice gradient or placeholder
        const imageUrl = article.image_url || `https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=1000&auto=format&fit=crop`;

        card.innerHTML = `
            <img src="${imageUrl}" class="card-img" alt="${article.title}" loading="lazy"
                 onerror="this.src='https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=1000&auto=format&fit=crop'">
            <div class="card-content">
                <div class="card-meta">
                    <span class="category">${article.category || 'Focus'}</span>
                    <span class="source">${article.source}</span>
                </div>
                <h3 class="card-title">${article.title}</h3>
                <p class="card-desc">${article.description || 'Click to read full article content...'}</p>
                <div class="card-footer">
                    <div class="author">
                        <i class="fa-solid fa-user-pen"></i>
                        <span>${article.author || 'Pulse Reporter'}</span>
                    </div>
                    <div class="date">${formatDate(article.published_at)}</div>
                </div>
            </div>
        `;

        card.addEventListener('click', () => {
            openModal(article);
        });

        newsGrid.appendChild(card);
    });
}

function updatePagination(total, page, size) {
    const totalPages = Math.ceil(total / size) || 1;
    pageNumbers.textContent = `Page ${page} of ${totalPages}`;

    prevPage.disabled = page <= 1;
    nextPage.disabled = page >= totalPages;
}

function showLoading(show) {
    if (show) {
        loading.classList.remove('hidden');
        newsGrid.classList.add('hidden');
    } else {
        loading.classList.add('hidden');
        newsGrid.classList.remove('hidden');
    }
}

function formatDate(dateStr) {
    if (!dateStr) return 'Just now';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    });
}
