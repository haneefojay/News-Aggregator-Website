// Configuration
window.CONFIG = {
    API_URL: window.location.hostname === 'localhost'
        ? 'http://localhost:8000/api/v1'
        : 'https://web-production-ceeda.up.railway.app/api/v1'
};

const API_URL = window.CONFIG.API_URL;
