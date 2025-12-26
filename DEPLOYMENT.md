# 🚀 Deployment Guide - Pulse News Aggregator

This guide will help you deploy Pulse to test the PWA installation on mobile devices.

---

## 📱 Quick Deploy (Recommended for Testing)

### Frontend Deployment (Vercel) - FREE

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm install -g vercel
   ```

2. **Deploy Frontend**:
   ```bash
   cd "c:\Users\DELL\Desktop\News Aggregrator Website"
   vercel --prod
   ```

3. **Follow the prompts**:
   - Set up and deploy: `Y`
   - Which scope: Choose your account
   - Link to existing project: `N`
   - Project name: `pulse-news` (or your choice)
   - Directory: `./frontend`
   - Override settings: `N`

4. **Your frontend will be live** at: `https://pulse-news-xxx.vercel.app`

### Backend Deployment (Railway) - FREE Tier

#### Option 1: Using Railway CLI

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**:
   ```bash
   railway login
   ```

3. **Initialize and Deploy**:
   ```bash
   railway init
   railway up
   ```

4. **Add PostgreSQL**:
   - Go to Railway dashboard
   - Click "New" → "Database" → "PostgreSQL"
   - Copy the `DATABASE_URL` connection string

5. **Add Redis**:
   - Click "New" → "Database" → "Redis"
   - Copy the `REDIS_URL` connection string

6. **Set Environment Variables**:
   ```bash
   railway variables set DATABASE_URL="your-postgres-url"
   railway variables set REDIS_URL="your-redis-url"
   railway variables set CELERY_BROKER_URL="your-redis-url/1"
   railway variables set CELERY_RESULT_BACKEND="your-redis-url/2"
   railway variables set NEWSAPI_KEY="your-key"
   railway variables set GUARDIAN_API_KEY="your-key"
   railway variables set NYTIMES_API_KEY="your-key"
   ```

7. **Get your backend URL**:
   ```bash
   railway domain
   ```
   Example: `https://pulse-backend-production.up.railway.app`

#### Option 2: Using Railway Web Dashboard

1. Go to [railway.app](https://railway.app)
2. Click "Start a New Project"
3. Choose "Deploy from GitHub repo"
4. Select your repository
5. Add PostgreSQL and Redis from the dashboard
6. Set environment variables in Settings → Variables
7. Deploy!

### Update Frontend Config

Once your backend is deployed, update `frontend/config.js`:

```javascript
window.CONFIG = {
    API_URL: window.location.hostname === 'localhost' 
        ? 'http://localhost:8000/api/v1'
        : 'https://YOUR-RAILWAY-URL.railway.app/api/v1' // ← Update this
};
```

Then redeploy frontend:
```bash
vercel --prod
```

---

## 🔧 Alternative: Render (Backend)

### Deploy to Render (Free Tier)

1. Go to [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: pulse-backend
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add PostgreSQL:
   - Click "New +" → "PostgreSQL"
   - Copy connection string
6. Add Redis:
   - Use Upstash (free tier): [upstash.com](https://upstash.com)
7. Set environment variables in Render dashboard
8. Deploy!

---

## 📱 Testing PWA on Mobile

### After Deployment:

1. **Open your Vercel URL** on your mobile device:
   - Example: `https://pulse-news.vercel.app`

2. **Install the PWA**:
   - **Android (Chrome)**:
     - Tap the menu (⋮) → "Add to Home screen"
     - Or look for the install banner at the bottom
   
   - **iOS (Safari)**:
     - Tap the Share button
     - Scroll and tap "Add to Home Screen"
     - Tap "Add"

3. **Test Features**:
   - ✅ App icon on home screen
   - ✅ Splash screen on launch
   - ✅ Standalone mode (no browser UI)
   - ✅ Offline support (try airplane mode)
   - ✅ Infinite scroll
   - ✅ Bookmark system
   - ✅ Theme toggle

---

## 🔐 CORS Configuration

Don't forget to update your backend CORS settings in `app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://pulse-news.vercel.app",  # Add your Vercel URL
        "https://your-custom-domain.com"   # If you have one
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🎯 Post-Deployment Checklist

- [ ] Frontend deployed to Vercel
- [ ] Backend deployed to Railway/Render
- [ ] PostgreSQL database connected
- [ ] Redis connected
- [ ] Environment variables set
- [ ] CORS configured
- [ ] Frontend config.js updated with backend URL
- [ ] Database migrations run (`alembic upgrade head`)
- [ ] Celery worker running (if using Railway, add as separate service)
- [ ] Test PWA installation on mobile
- [ ] Test all features (search, filter, bookmark, infinite scroll)

---

## 🐛 Troubleshooting

### PWA Not Installing
- Ensure you're using HTTPS (Vercel provides this automatically)
- Check manifest.json is accessible: `https://your-url.vercel.app/manifest.json`
- Check service worker: `https://your-url.vercel.app/sw.js`
- Open DevTools → Application → Manifest (check for errors)

### API Not Connecting
- Check CORS settings in backend
- Verify backend URL in `config.js`
- Check browser console for errors
- Ensure backend is running and accessible

### Database Connection Issues
- Verify DATABASE_URL format
- Check if PostgreSQL is running
- Run migrations: `alembic upgrade head`

---

## 💰 Cost Breakdown (Free Tier)

- **Vercel**: Free (100GB bandwidth, unlimited projects)
- **Railway**: Free ($5 credit/month, ~500 hours)
- **Render**: Free (750 hours/month, sleeps after inactivity)
- **Upstash Redis**: Free (10,000 commands/day)

**Total Monthly Cost**: $0 for testing! 🎉

---

## 🚀 Next Steps After Testing

1. Custom domain setup
2. Set up monitoring (Sentry, LogRocket)
3. Configure CDN for static assets
4. Set up CI/CD pipeline
5. Add analytics
6. Implement user authentication
7. Scale to paid tiers as needed

---

## 📧 Need Help?

If you encounter issues:
1. Check the deployment logs
2. Verify environment variables
3. Test locally first
4. Check browser console for errors

**Happy Deploying! 🎉**
