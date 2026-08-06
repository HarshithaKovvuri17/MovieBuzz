/**
 * CinePulse Movie Review Application Frontend Logic
 * Supports 10+ Recent Telugu Movies, Sentiment Classification, and Single-Admin Dashboard.
 */

// Global Application State
let currentUser = null;
let currentAuthMode = 'login'; // 'login' or 'signup'
let currentView = 'movies'; // 'movies' or 'admin'
let currentAdminSubtab = 'users'; // 'users' or 'reviews'
let moviesData = [];
let adminData = { stats: {}, users: [], reviews: [] };

// DOM Loaded Initialization
// Theme Switcher System (Light / Dark Mode)
function initTheme() {
    const savedTheme = localStorage.getItem('moviebuzz_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('moviebuzz_theme', newTheme);
    updateThemeIcon(newTheme);
    showToast(`Switched to ${newTheme.toUpperCase()} mode!`, 'info');
}

function updateThemeIcon(theme) {
    const icon = document.getElementById('theme-icon');
    if (!icon) return;
    if (theme === 'light') {
        icon.className = 'fa-solid fa-moon';
        icon.style.color = '#f59e0b';
    } else {
        icon.className = 'fa-solid fa-sun';
        icon.style.color = '#fbbf24';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    checkAuthState();
    loadMovies();
});

// Toast Notifications Helper
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    let iconClass = 'fa-circle-info';
    if (type === 'success') iconClass = 'fa-circle-check';
    if (type === 'error') iconClass = 'fa-circle-xmark';

    toast.innerHTML = `<i class="fa-solid ${iconClass}"></i> <span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Authentication Check
async function checkAuthState() {
    try {
        const response = await fetch('/api/me');
        const data = await response.json();
        
        if (data.authenticated) {
            currentUser = data.user;
            renderAuthNav(true);
            document.getElementById('login-prompt-banner').classList.add('hidden');
        } else {
            currentUser = null;
            renderAuthNav(false);
            document.getElementById('login-prompt-banner').classList.remove('hidden');
        }
    } catch (err) {
        console.error("Auth check failed:", err);
        renderAuthNav(false);
    }
}

// Render Navigation Auth Section & View Tabs
function renderAuthNav(isLoggedIn) {
    const authNav = document.getElementById('auth-nav');
    const viewTabs = document.getElementById('view-tabs');
    const guestNav = document.getElementById('guest-nav-controls');

    if (isLoggedIn && currentUser) {
        if (guestNav) guestNav.classList.add('hidden');

        authNav.innerHTML = `
            <div class="user-badge ${currentUser.is_admin ? 'admin-user' : ''}">
                <i class="fa-solid ${currentUser.is_admin ? 'fa-user-shield' : 'fa-circle-user'}"></i>
                <span>${escapeHtml(currentUser.username)} ${currentUser.is_admin ? '(Admin)' : ''}</span>
            </div>
            <button class="btn btn-outline btn-sm" onclick="handleLogout()">
                <i class="fa-solid fa-right-from-bracket"></i> Log Out
            </button>
        `;

        if (currentUser.is_admin) {
            viewTabs.classList.remove('hidden');
        } else {
            viewTabs.classList.add('hidden');
            switchView('movies');
        }
    } else {
        if (guestNav) guestNav.classList.remove('hidden');
        authNav.innerHTML = '';
        viewTabs.classList.add('hidden');
        switchView('movies');
    }
}

// Switch Views (Movies vs Admin Portal)
function switchView(viewName) {
    currentView = viewName;
    const moviesSection = document.getElementById('section-movies-view');
    const adminSection = document.getElementById('section-admin-view');
    const moviesTabBtn = document.getElementById('view-btn-movies');
    const adminTabBtn = document.getElementById('view-btn-admin');

    if (viewName === 'admin') {
        if (!currentUser || !currentUser.is_admin) {
            showToast("Admin access required. Please log in as admin.", "error");
            openAuthModal('login');
            fillUser('admin', 'admin');
            return;
        }

        moviesSection.classList.add('hidden');
        adminSection.classList.remove('hidden');
        moviesTabBtn.classList.remove('active');
        adminTabBtn.classList.add('active');

        loadAdminData();
    } else {
        moviesSection.classList.remove('hidden');
        adminSection.classList.add('hidden');
        moviesTabBtn.classList.add('active');
        adminTabBtn.classList.remove('active');
    }
}

// Auth Modal Functions
function openAuthModal(mode = 'login') {
    currentAuthMode = mode;
    switchAuthTab(mode);
    document.getElementById('auth-modal').classList.remove('hidden');
    document.getElementById('auth-error-msg').classList.add('hidden');
}

function closeAuthModal() {
    document.getElementById('auth-modal').classList.add('hidden');
}

function switchAuthTab(mode) {
    currentAuthMode = mode;
    const loginTab = document.getElementById('tab-login');
    const signupTab = document.getElementById('tab-signup');
    const btnText = document.getElementById('auth-btn-text');
    const errorMsg = document.getElementById('auth-error-msg');

    errorMsg.classList.add('hidden');

    if (mode === 'login') {
        loginTab.classList.add('active');
        signupTab.classList.remove('active');
        btnText.textContent = 'Log In';
    } else {
        signupTab.classList.add('active');
        loginTab.classList.remove('active');
        btnText.textContent = 'Sign Up';
    }
}

// Helper to autofill username & password
function fillUser(username, password) {
    document.getElementById('auth-username').value = username;
    document.getElementById('auth-password').value = password;
    showToast(`Autofilled ${username} credentials!`, 'info');
}

// Auth Form Submission (Login / Signup)
async function handleAuthSubmit(event) {
    event.preventDefault();
    const usernameInput = document.getElementById('auth-username').value.trim();
    const passwordInput = document.getElementById('auth-password').value.trim();
    const errorMsg = document.getElementById('auth-error-msg');
    const submitBtn = document.getElementById('auth-submit-btn');

    if (!usernameInput || !passwordInput) {
        errorMsg.textContent = 'Please enter both username and password.';
        errorMsg.classList.remove('hidden');
        return;
    }

    submitBtn.disabled = true;
    errorMsg.classList.add('hidden');

    const endpoint = currentAuthMode === 'login' ? '/api/login' : '/api/signup';

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: usernameInput, password: passwordInput })
        });
        const data = await response.json();

        if (response.ok && data.success) {
            currentUser = data.user;
            renderAuthNav(true);
            closeAuthModal();
            document.getElementById('login-prompt-banner').classList.add('hidden');
            showToast(data.message, 'success');

            if (currentUser.is_admin) {
                switchView('admin');
            } else {
                renderMovies();
            }
        } else {
            errorMsg.textContent = data.message || 'Authentication failed.';
            errorMsg.classList.remove('hidden');
        }
    } catch (err) {
        console.error("Auth error:", err);
        errorMsg.textContent = 'Network error. Please try again.';
        errorMsg.classList.remove('hidden');
    } finally {
        submitBtn.disabled = false;
    }
}

// Logout Handler
async function handleLogout() {
    try {
        await fetch('/api/logout', { method: 'POST' });
        currentUser = null;
        renderAuthNav(false);
        document.getElementById('login-prompt-banner').classList.remove('hidden');
        showToast('You have been logged out.', 'info');
        switchView('movies');
        renderMovies();
    } catch (err) {
        console.error("Logout failed:", err);
    }
}

// Load Movies & Review Stats
async function loadMovies() {
    const spinner = document.getElementById('loading-spinner');
    const grid = document.getElementById('movies-grid');

    try {
        const response = await fetch('/api/movies');
        const data = await response.json();

        if (data.success) {
            moviesData = data.movies;
            spinner.classList.add('hidden');
            grid.classList.remove('hidden');
            document.getElementById('movie-count-badge').textContent = `${moviesData.length} Movies`;
            renderMovies();
        }
    } catch (err) {
        console.error("Failed to load movies:", err);
        spinner.innerHTML = `<p style="color:var(--negative-color)">Error loading movies from SQLite database.</p>`;
    }
}

// Render Movies Grid (10+ Telugu Movies)
function renderMovies() {
    const grid = document.getElementById('movies-grid');
    grid.innerHTML = '';

    moviesData.forEach(movie => {
        const card = document.createElement('div');
        card.className = 'movie-card';

        // Render Recent Reviews Feed HTML
        let reviewsFeedHtml = '';
        if (movie.reviews && movie.reviews.length > 0) {
            reviewsFeedHtml = movie.reviews.map(r => `
                <div class="review-item">
                    <div class="review-item-header">
                        <span class="review-author"><i class="fa-solid fa-user-circle"></i> ${escapeHtml(r.username)}</span>
                        <span class="review-badge ${r.sentiment}">${r.sentiment}</span>
                    </div>
                    <div class="review-text-content">"${escapeHtml(r.review_text)}"</div>
                </div>
            `).join('');
        } else {
            reviewsFeedHtml = `<div style="font-size:0.85rem; color:var(--text-muted); font-style:italic;">No reviews submitted yet. Express your view first!</div>`;
        }

        card.innerHTML = `
            <div class="poster-wrapper" onclick="openMovieDetailModal(${movie.id})">
                <img src="${movie.poster_url}" alt="${escapeHtml(movie.title)}" class="poster-img" loading="lazy">
                <div class="poster-overlay">
                    <div class="poster-info">
                        <h3 class="movie-title">${escapeHtml(movie.title)}</h3>
                        <div class="movie-meta">
                            <span><i class="fa-solid fa-film"></i> ${escapeHtml(movie.genre)}</span>
                            <span><i class="fa-solid fa-calendar-days"></i> ${escapeHtml(movie.release_period)}</span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card-body">
                <p class="movie-desc">${escapeHtml(movie.description)}</p>

                <!-- Aggregated Sentiment Stats Card -->
                <div class="sentiment-stats-card">
                    <div class="stats-header">
                        <span><i class="fa-solid fa-chart-pie"></i> Community Sentiment Stats</span>
                        <span>Total: ${movie.total_reviews}</span>
                    </div>
                    <div class="stats-grid">
                        <div class="stat-pill positive">
                            <span class="stat-label"><i class="fa-solid fa-thumbs-up"></i> Positive</span>
                            <span class="stat-val" id="pos-count-${movie.id}">${movie.positive_count}</span>
                        </div>
                        <div class="stat-pill negative">
                            <span class="stat-label"><i class="fa-solid fa-thumbs-down"></i> Negative</span>
                            <span class="stat-val" id="neg-count-${movie.id}">${movie.negative_count}</span>
                        </div>
                    </div>
                </div>

                <!-- Action Button to Open Reviews Showcase Modal -->
                <button class="btn btn-primary btn-sm btn-full" onclick="openMovieDetailModal(${movie.id})">
                    <i class="fa-solid fa-comments"></i> Write Review & View All
                </button>
            </div>
        `;

        grid.appendChild(card);
    });
}

// Handle Review Submission
async function handleReviewSubmit(event, movieId) {
    event.preventDefault();
    if (!currentUser) {
        openAuthModal('login');
        return;
    }

    const textarea = document.getElementById(`review-input-${movieId}`);
    const submitBtn = document.getElementById(`submit-btn-${movieId}`);
    const reviewText = textarea.value.trim();

    if (!reviewText) {
        showToast('Please enter review text before submitting.', 'error');
        return;
    }

    submitBtn.disabled = true;

    try {
        const response = await fetch('/api/reviews', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ movie_id: movieId, review_text: reviewText })
        });
        const data = await response.json();

        if (response.ok && data.success) {
            moviesData = data.movies;
            const sentimentUpper = data.sentiment.toUpperCase();
            showToast(`Review saved to SQLite! Sentiment: ${sentimentUpper}`, data.sentiment === 'positive' ? 'success' : 'error');
            textarea.value = '';
            renderMovies();
        } else {
            showToast(data.message || 'Failed to submit review.', 'error');
        }
    } catch (err) {
        console.error("Review submission error:", err);
        showToast('Error submitting review. Please try again.', 'error');
    } finally {
        if (submitBtn) submitBtn.disabled = false;
    }
}

// ==========================================================================
// ADMIN PORTAL FUNCTIONS
// ==========================================================================

async function loadAdminData() {
    try {
        const response = await fetch('/api/admin/data');
        const data = await response.json();

        if (response.ok && data.success) {
            adminData = data;
            renderAdminDashboard();
        } else {
            showToast(data.message || "Failed to load admin data", "error");
        }
    } catch (err) {
        console.error("Admin data fetch error:", err);
        showToast("Error loading Admin Dashboard data.", "error");
    }
}

function renderAdminDashboard() {
    const { stats, users, reviews } = adminData;

    // 1. Update KPI Stats
    document.getElementById('kpi-users').textContent = stats.total_users || 0;
    document.getElementById('kpi-movies').textContent = stats.total_movies || 0;
    document.getElementById('kpi-reviews').textContent = stats.total_reviews || 0;
    document.getElementById('kpi-pos').textContent = stats.total_positive || 0;
    document.getElementById('kpi-neg').textContent = stats.total_negative || 0;

    document.getElementById('user-count-badge').textContent = users.length;
    document.getElementById('review-count-badge').textContent = reviews.length;

    // 2. Render Users Table
    const usersTableBody = document.getElementById('admin-users-table-body');
    usersTableBody.innerHTML = users.map(u => `
        <tr>
            <td><strong>#${u.id}</strong></td>
            <td><i class="fa-solid fa-user-circle"></i> <strong>${escapeHtml(u.username)}</strong></td>
            <td>
                <span class="user-role-badge ${u.is_admin ? 'admin' : 'user'}">
                    ${u.is_admin ? 'SINGLE ADMIN' : 'USER'}
                </span>
            </td>
            <td>${u.created_at ? u.created_at.substring(0, 19) : 'N/A'}</td>
            <td><strong>${u.review_count}</strong> reviews</td>
        </tr>
    `).join('');

    // 3. Render Reviews Table
    const reviewsTableBody = document.getElementById('admin-reviews-table-body');
    if (reviews.length === 0) {
        reviewsTableBody.innerHTML = `<tr><td colspan="8" style="text-align:center; color:var(--text-muted); padding:2rem;">No reviews submitted yet.</td></tr>`;
    } else {
        reviewsTableBody.innerHTML = reviews.map(r => `
            <tr>
                <td>#${r.id}</td>
                <td><strong>${escapeHtml(r.username)}</strong></td>
                <td><span class="movie-code-badge">${r.movie_code}</span></td>
                <td><strong>${escapeHtml(r.movie_title)}</strong></td>
                <td style="max-width:300px; word-break:break-word;">"${escapeHtml(r.review_text)}"</td>
                <td><span class="review-badge ${r.sentiment}">${r.sentiment}</span></td>
                <td style="font-size:0.8rem; color:var(--text-muted);">${r.created_at ? r.created_at.substring(0, 19) : ''}</td>
                <td>
                    <button class="btn-delete-sm" onclick="handleDeleteReview(${r.id})">
                        <i class="fa-solid fa-trash"></i> Delete
                    </button>
                </td>
            </tr>
        `).join('');
    }
}

function switchAdminSubtab(subtabName) {
    currentAdminSubtab = subtabName;
    const usersSubtabBtn = document.getElementById('admin-tab-btn-users');
    const reviewsSubtabBtn = document.getElementById('admin-tab-btn-reviews');
    const usersPanel = document.getElementById('admin-subpanel-users');
    const reviewsPanel = document.getElementById('admin-subpanel-reviews');

    if (subtabName === 'reviews') {
        reviewsSubtabBtn.classList.add('active');
        usersSubtabBtn.classList.remove('active');
        reviewsPanel.classList.remove('hidden');
        usersPanel.classList.add('hidden');
    } else {
        usersSubtabBtn.classList.add('active');
        reviewsSubtabBtn.classList.remove('active');
        usersPanel.classList.remove('hidden');
        reviewsPanel.classList.add('hidden');
    }
}

async function handleDeleteReview(reviewId) {
    if (!confirm(`Are you sure you want to delete Review #${reviewId}?`)) return;

    try {
        const response = await fetch(`/api/admin/reviews/${reviewId}`, { method: 'DELETE' });
        const data = await response.json();

        if (response.ok && data.success) {
            showToast(data.message, "success");
            loadAdminData();
            loadMovies(); // Refresh movie cards in background
        } else {
            showToast(data.message || "Failed to delete review", "error");
        }
    } catch (err) {
        console.error("Delete review error:", err);
        showToast("Error deleting review.", "error");
    }
}

// Split-Screen Movie Detail Modal Functions
async function openMovieDetailModal(movieId) {
    const movie = moviesData.find(m => m.id === movieId);
    if (!movie) return;

    const modal = document.getElementById('movie-detail-modal');
    const posterImg = document.getElementById('detail-modal-poster');
    const titleEl = document.getElementById('detail-modal-title');
    const metaEl = document.getElementById('detail-modal-meta');
    const statsEl = document.getElementById('detail-modal-stats');
    const countBadge = document.getElementById('detail-modal-review-count');
    const formContainer = document.getElementById('modal-review-form-container');
    const reviewsList = document.getElementById('detail-modal-reviews-list');

    posterImg.src = movie.poster_url;
    titleEl.textContent = movie.title;
    metaEl.innerHTML = `
        <span><i class="fa-solid fa-film"></i> ${escapeHtml(movie.genre)}</span>
        <span><i class="fa-solid fa-calendar-days"></i> ${escapeHtml(movie.release_period)}</span>
    `;
    statsEl.innerHTML = `
        <span class="stat-pill pos"><i class="fa-solid fa-thumbs-up"></i> ${movie.positive_count} Positive</span>
        <span class="stat-pill neg"><i class="fa-solid fa-thumbs-down"></i> ${movie.negative_count} Negative</span>
    `;

    // Render Review Submission Form at top of reviews
    if (currentUser) {
        formContainer.innerHTML = `
            <div class="modal-review-form-title">
                <i class="fa-solid fa-pen-to-square"></i> Write a Review for ${escapeHtml(movie.title)}
            </div>
            <form onsubmit="handleModalReviewSubmit(event, ${movie.id})">
                <textarea 
                    id="modal-review-input-${movie.id}" 
                    class="modal-review-textarea" 
                    placeholder="Write your review here (e.g. 'This movie is amazing')..." 
                    required></textarea>
                <button type="submit" id="modal-submit-btn-${movie.id}" class="btn btn-primary btn-sm btn-full">
                    <i class="fa-solid fa-paper-plane"></i> Submit Review
                </button>
            </form>
        `;
    } else {
        formContainer.innerHTML = `
            <button class="btn btn-outline btn-sm btn-full" onclick="window.location.href='/login'">
                <i class="fa-solid fa-lock"></i> Log in to Submit a Review
            </button>
        `;
    }

    reviewsList.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:1.5rem;"><i class="fa-solid fa-spinner fa-spin"></i> Loading user reviews...</div>';
    modal.classList.remove('hidden');

    try {
        const response = await fetch(`/api/movies/${movieId}/reviews`);
        const data = await response.json();
        const reviews = data.reviews || [];

        countBadge.textContent = `${reviews.length} Reviews`;

        if (reviews.length === 0) {
            reviewsList.innerHTML = `
                <div style="text-align:center; padding:2rem; color:var(--text-muted);">
                    <i class="fa-solid fa-comment-slash" style="font-size:2rem; margin-bottom:0.5rem; display:block;"></i>
                    No user reviews submitted yet for ${escapeHtml(movie.title)}. Be the first to write a review above!
                </div>
            `;
        } else {
            reviewsList.innerHTML = reviews.map(r => `
                <div class="modal-review-card">
                    <div class="modal-review-header">
                        <div class="modal-review-user">
                            <i class="fa-solid fa-circle-user"></i> ${escapeHtml(r.username)}
                        </div>
                        <span class="badge ${r.sentiment}">${r.sentiment.toUpperCase()}</span>
                    </div>
                    <div class="modal-review-text">"${escapeHtml(r.review_text)}"</div>
                    <div class="modal-review-date"><i class="fa-regular fa-clock"></i> ${new Date(r.created_at).toLocaleString()}</div>
                </div>
            `).join('');
        }
    } catch (err) {
        console.error("Failed to load reviews:", err);
        reviewsList.innerHTML = '<div style="color:var(--danger-color); text-align:center; padding:1rem;">Failed to load reviews.</div>';
    }
}

// Handle Modal Review Submission
async function handleModalReviewSubmit(event, movieId) {
    event.preventDefault();
    if (!currentUser) {
        window.location.href = '/login';
        return;
    }

    const textarea = document.getElementById(`modal-review-input-${movieId}`);
    const submitBtn = document.getElementById(`modal-submit-btn-${movieId}`);
    const reviewText = textarea.value.trim();

    if (!reviewText) {
        showToast('Please enter review text before submitting.', 'error');
        return;
    }

    submitBtn.disabled = true;

    try {
        const response = await fetch('/api/reviews', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ movie_id: movieId, review_text: reviewText })
        });
        const data = await response.json();

        if (response.ok && data.success) {
            moviesData = data.movies;
            const sentimentUpper = data.sentiment.toUpperCase();
            showToast(`Review saved! Sentiment: ${sentimentUpper}`, data.sentiment === 'positive' ? 'success' : 'error');
            
            // Refresh main cards in background & re-open modal to refresh reviews
            renderMovies();
            openMovieDetailModal(movieId);
        } else {
            showToast(data.message || 'Failed to submit review.', 'error');
            submitBtn.disabled = false;
        }
    } catch (err) {
        console.error("Modal review submission error:", err);
        showToast("Error submitting review.", "error");
        submitBtn.disabled = false;
    }
}

function closeMovieDetailModal() {
    const modal = document.getElementById('movie-detail-modal');
    if (modal) modal.classList.add('hidden');
}

// Escape HTML utility
function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
