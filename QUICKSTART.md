# 🚀 Quick Start Guide - CivicTrack with Gemini AI

## Get Started in 5 Minutes

### 1️⃣ Get Your API Key (30 seconds)
```bash
# Visit: https://aistudio.google.com/app/apikey
# Click "Get API Key"
# Copy the key
```

### 2️⃣ Create .env File (30 seconds)
```bash
# Create .env in project root:
GEMINI_API_KEY=paste_your_key_here
SECRET_KEY=dev-secret-key-123
FLASK_ENV=development
```

### 3️⃣ Install Dependencies (2 minutes)
```bash
pip install -r requirements.txt
```

### 4️⃣ Run Application (1 minute)
```bash
python app.py
```

✅ **Done!** App is now running at `http://localhost:5000`

---

## 🎯 What You Can Do Now

### Report an Issue
1. Go to homepage → "Submit Incident"
2. Fill in details (title, category, description, location)
3. AI automatically analyzes and assigns severity
4. Track your report in dashboard

### View AI Results
1. **Home Page**: See AI severity badges on all incidents
2. **Confidence Score**: How certain the AI is
3. **Reasoning**: Why AI chose that severity
4. **Recommendations**: What to do next

### Admin Features
1. Go to Admin Panel (if you're an admin)
2. View all incidents with AI analysis
3. Request recommendations: `/api/issue/{id}/recommendations`
4. City insights: `/api/insights`

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| `README.md` | Complete project documentation |
| `GEMINI_AI_GUIDE.md` | Detailed AI integration guide |
| `gemini_ai.py` | AI module source code |
| `.env.example` | Configuration template |

---

## 🧪 Test It

### Test Incident
```
Title: "Electrical wire hazard near school"
Category: Power Grid
Description: "Live electrical line hanging 2 meters above playground, immediate danger to children"
Location: "Oak Elementary School, Main Street"
```

**Expected AI Result**: Severity = **CRITICAL** (High Confidence)

### Test API
```bash
# Get all incidents with AI data
curl http://localhost:5000/api/incidents

# Get recommendations for issue #1
curl http://localhost:5000/api/issue/1/recommendations

# Get city-wide insights
curl http://localhost:5000/api/insights
```

---

## 🆘 Troubleshooting

| Issue | Fix |
|-------|-----|
| API key not found | Copy key to `.env` file |
| Port 5000 in use | `python app.py --port 5001` |
| Database error | `rm civictrack_v2.db && python app.py` |
| AI not working | Check internet, verify API key in Google Cloud |

---

## 🔐 Remember!

✅ Keep `.env` in `.gitignore`  
✅ Never commit secrets to git  
✅ Rotate API keys periodically  
✅ Monitor API usage in Google Cloud  

---

**Next Steps:**
- Read full `README.md` for advanced features
- Explore `GEMINI_AI_GUIDE.md` for AI details
- Visit [Gemini API docs](https://ai.google.dev/docs)

**Questions?** Check the comprehensive guides above! 📖
