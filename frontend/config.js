// Configuration
window.CONFIG = {
    API_URL: window.location.hostname === 'localhost'
        ? 'http://localhost:8000/api/v1'
        : 'https://news-aggregator-website-production.up.railway.app/api/v1'
};

const API_URL = window.CONFIG.API_URL;
