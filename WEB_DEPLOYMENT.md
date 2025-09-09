# 🌐 ZeX-ATS-AI Web Deployment Guide

This guide covers deploying ZeX-ATS-AI to various web platforms.

## 🚀 Quick Deploy Buttons

### Vercel
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/your-repo/ATS_Checker-Enhancer)

### Netlify
[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=https://github.com/your-repo/ATS_Checker-Enhancer)

### Heroku
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/your-repo/ATS_Checker-Enhancer)

### Railway
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/your-repo/ATS_Checker-Enhancer)

### Render
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/your-repo/ATS_Checker-Enhancer)

## 📋 Manual Deployment Steps

### Vercel Deployment
```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel --prod
```

### Netlify Deployment
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Deploy
netlify deploy --prod --dir=dist
```

### Heroku Deployment
```bash
# Install Heroku CLI
# Create Heroku app
heroku create zex-ats-ai

# Add buildpack
heroku buildpacks:set heroku/python

# Deploy
git push heroku main
```

### Railway Deployment
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Deploy
railway up
```

### Docker Web Deployment
```bash
# Build Docker image
docker build -f Dockerfile.web -t zex-ats-ai-web .

# Run container
docker run -p 8000:8000 zex-ats-ai-web
```

## ⚙️ Environment Variables

Set these environment variables in your deployment platform:

```env
ENVIRONMENT=production
DATABASE_URL=sqlite:///./data/ats.db
CORS_ORIGINS=*
MAX_FILE_SIZE=52428800
OPENAI_API_KEY=your_openai_key (optional)
ANTHROPIC_API_KEY=your_anthropic_key (optional)
```

## 🔧 Platform-Specific Notes

### Vercel
- Uses serverless functions
- SQLite database recommended
- File uploads limited to 50MB

### Netlify
- Static site with serverless functions
- Good for demo/frontend deployment
- Backend API through functions

### Heroku
- Full application deployment
- PostgreSQL add-on available
- Automatic SSL certificate

### Railway
- Modern deployment platform
- Built-in database options
- Automatic scaling

### Render
- Docker and native builds supported
- Built-in database options
- Automatic SSL and CDN

## 📊 Feature Availability by Platform

| Platform | File Upload | Database | Background Jobs | WebSockets |
|----------|-------------|----------|-----------------|------------|
| Vercel   | ✅ 50MB     | SQLite   | Limited         | ❌         |
| Netlify  | ✅ 10MB     | External | Limited         | ❌         |
| Heroku   | ✅ 50MB     | PostgreSQL| ✅             | ✅         |
| Railway  | ✅ 100MB    | PostgreSQL| ✅             | ✅         |
| Render   | ✅ 100MB    | PostgreSQL| ✅             | ✅         |

## 🚦 Post-Deployment

After deployment, verify:
1. ✅ Health check: `/health`
2. ✅ API docs: `/docs`
3. ✅ Interactive demo: `/sandbox/`
4. ✅ File upload: Test with sample resume

## 🔍 Troubleshooting

Common issues and solutions:

1. **File upload fails**
   - Check file size limits
   - Verify CORS settings
   - Check environment variables

2. **Database connection error**
   - Verify DATABASE_URL
   - Check database service status
   - Review connection settings

3. **AI analysis fails**
   - Check API keys are set
   - Verify network connectivity
   - Review rate limits

4. **Build fails**
   - Check Python version (3.11+)
   - Verify dependencies
   - Review build logs
