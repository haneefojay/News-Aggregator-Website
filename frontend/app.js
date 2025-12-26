// API_URL is loaded from config.js

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
const infiniteScrollTrigger = document.getElementById('infiniteScrollTrigger');
const syncBtn = document.getElementById('syncBtn');
const installBtn = document.getElementById('installBtn');

let isLoading = false;
let hasMore = true;
let deferredPrompt = null;

// Modal Elements
const articleModal = document.getElementById('articleModal');
const modalImage = document.getElementById('modalImage');
const modalCategory = document.getElementById('modalCategory');
const modalSource = document.getElementById('modalSource');
const modalDate = document.getElementById('modalDate');
const modalTitle = document.getElementById('modalTitle');
const modalIntelligence = document.getElementById('modalIntelligence');
const modalAuthor = document.getElementById('modalAuthor');
const modalDescription = document.getElementById('modalDescription');
const modalSourceLink = document.getElementById('modalSourceLink');
const modalClose = document.querySelector('.modal-close');
const modalBackdrop = document.querySelector('.modal-backdrop');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    fetchNews();
    setupEventListeners();
    setupInfiniteScroll();
    setupPWAInstall();
});

function setupInfiniteScroll() {
    const observer = new IntersectionObserver((entries) => {
        const entry = entries[0];
        if (entry.isIntersecting && !isLoading && hasMore && currentCategory !== 'saved') {
            currentPage++;
            fetchNews(true);
        }
    }, { rootMargin: '100px' });

    observer.observe(infiniteScrollTrigger);
}

function setupPWAInstall() {
    // Capture the install prompt event
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        // Show the install button
        installBtn.classList.remove('hidden');
    });

    // Handle install button click
    installBtn.addEventListener('click', async () => {
        if (!deferredPrompt) return;

        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;

        if (outcome === 'accepted') {
            console.log('PWA installed successfully');
        }

        deferredPrompt = null;
        installBtn.classList.add('hidden');
    });

    // Hide button if already installed
    window.addEventListener('appinstalled', () => {
        installBtn.classList.add('hidden');
        deferredPrompt = null;
    });
}

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

    // Modal Close
    modalClose.addEventListener('click', closeModal);
    modalBackdrop.addEventListener('click', closeModal);
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeModal();
    });
}



function openModal(article) {
    modalImage.src = article.image_url || 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=1000&auto=format&fit=crop';
    modalCategory.textContent = article.category || 'Focus';
    modalSource.textContent = article.source;
    modalDate.textContent = formatDate(article.published_at);
    modalTitle.textContent = article.title;
    modalAuthor.innerHTML = `<i class="fa-solid fa-user-pen"></i> ${article.author || 'Pulse Reporter'}`;

    // Render Modal Intelligence
    modalIntelligence.innerHTML = `
        <div class="badge badge-read-time">
            <i class="fa-regular fa-clock"></i> ${article.read_time_minutes || 3} min read
        </div>
    `;

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

async function fetchNews(append = false) {
    if (isLoading) return;
    isLoading = true;

    // Show appropriate loader
    if (!append) {
        showLoading(true);
        infiniteScrollTrigger.classList.add('hidden');
        currentPage = 1; // Reset to page 1 on new search/filter
        hasMore = true; // Reset hasMore flag
    } else {
        infiniteScrollTrigger.classList.remove('hidden');
    }

    try {
        // Special handling for "Saved" category
        if (currentCategory === 'saved') {
            let filtered = getSavedArticles();

            if (currentSource) {
                filtered = filtered.filter(a => a.source === currentSource);
            }

            if (searchQuery) {
                const q = searchQuery.toLowerCase();
                filtered = filtered.filter(a =>
                    a.title.toLowerCase().includes(q) ||
                    (a.description && a.description.toLowerCase().includes(q))
                );
            }

            displayNews(filtered, false);
            hasMore = false; // No infinite scroll for saved items
            infiniteScrollTrigger.classList.add('hidden');
            return;
        }

        const params = new URLSearchParams({
            page: currentPage,
            page_size: 12
        });

        if (currentCategory !== 'all') params.append('category', currentCategory);
        if (currentSource) params.append('source', currentSource);
        if (searchQuery) params.append('q', searchQuery);

        console.log('Fetching page:', currentPage);
        const response = await fetch(`${API_URL}/articles?${params}`);
        const data = await response.json();

        console.log('Response:', {
            articlesCount: data.articles.length,
            currentPage: data.page,
            totalPages: data.total_pages,
            total: data.total
        });

        if (data.articles.length === 0) {
            hasMore = false;
            infiniteScrollTrigger.classList.add('hidden');
            if (!append) {
                newsGrid.innerHTML = ''; // Clear old articles
                noResults.classList.remove('hidden');
            }
        } else {
            hasMore = currentPage < data.total_pages;
            displayNews(data.articles, append);

            // Show or hide the trigger based on whether there's more content
            if (hasMore) {
                infiniteScrollTrigger.classList.remove('hidden');
                console.log('More pages available. Showing trigger.');
            } else {
                infiniteScrollTrigger.classList.add('hidden');
                console.log('No more pages. Hiding trigger.');
            }
        }

    } catch (error) {
        console.error('Error fetching news:', error);
        if (!append) {
            newsGrid.innerHTML = '';
            noResults.classList.remove('hidden');
            noResults.querySelector('h3').textContent = 'Something went wrong';
            noResults.querySelector('p').textContent = 'We\'re unable to connect to our servers right now.';
        }
    } finally {
        isLoading = false;
        if (!append) showLoading(false);
    }
}

function displayNews(articles, append = false) {
    if (!append) {
        newsGrid.innerHTML = '';
    }

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


            <div class="card-intelligence">
                <div class="badge badge-read-time">
                    <i class="fa-regular fa-clock"></i> ${article.read_time_minutes || 3}m
                </div>
                <button class="bookmark-btn ${isSaved(article.id) ? 'saved' : ''}" data-id="${article.id}" title="${isSaved(article.id) ? 'Remove from Saved' : 'Save for Later'}">
                    <i class="fa-${isSaved(article.id) ? 'solid' : 'regular'} fa-star"></i>
                </button>
            </div>
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

        // Card click: Open Modal (ignore bookmark button clicks)
        card.addEventListener('click', (e) => {
            if (!e.target.closest('.bookmark-btn')) {
                openModal(article);
            }
        });

        // Bookmark Click
        const bookmarkBtn = card.querySelector('.bookmark-btn');
        bookmarkBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleBookmark(article);

            // UI visual update
            const icon = bookmarkBtn.querySelector('i');
            bookmarkBtn.classList.toggle('saved');
            if (bookmarkBtn.classList.contains('saved')) {
                icon.classList.remove('fa-regular');
                icon.classList.add('fa-solid');
            } else {
                icon.classList.remove('fa-solid');
                icon.classList.add('fa-regular');

                // If in "Saved" view, remove card instantly
                if (currentCategory === 'saved') {
                    card.style.opacity = '0';
                    setTimeout(() => card.remove(), 300);
                }
            }
        });

        newsGrid.appendChild(card);
    });
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



// --- Bookmarking Logic ---

function getSavedArticles() {
    const saved = localStorage.getItem('pulse-bookmarks');
    return saved ? JSON.parse(saved) : [];
}

function isSaved(articleId) {
    const saved = getSavedArticles();
    return saved.some(a => a.id === articleId);
}

function toggleBookmark(article) {
    let saved = getSavedArticles();
    if (isSaved(article.id)) {
        // Remove
        saved = saved.filter(a => a.id !== article.id);
    } else {
        // Add (Limit to 50 to prevent overflow)
        if (saved.length >= 50) saved.shift();
        saved.push(article);
    }
    localStorage.setItem('pulse-bookmarks', JSON.stringify(saved));
}
