// Configuration
window.CONFIG = {
    API_URL: window.location.hostname === 'localhost'
        ? 'http://localhost:8000/api/v1'
        : 'https://your-backend-url.railway.app/api/v1' // Update this after backend deployment
};

const API_URL = window.CONFIG.API_URL;
