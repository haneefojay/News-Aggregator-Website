// Configuration
window.CONFIG = {
    API_URL: window.location.hostname === 'localhost'
        ? 'http://localhost:8000/api/v1'
        : 'https://web-production-8e0b4.up.railway.app/api/v1'
};

const API_URL = window.CONFIG.API_URL;
