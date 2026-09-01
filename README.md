# CivicTrack - AI-Powered Municipal Incident Management System

## 📋 Overview

**CivicTrack** is an intelligent municipal incident reporting and management platform powered by **Google's Gemini AI**. It enables citizens, engineers, and administrators to report, analyze, and resolve public infrastructure hazards with automated triage and intelligent recommendations.

## 🚀 Features

### Core Functionality
- **Citizen Incident Reporting** - Report infrastructure hazards with location tagging
- **AI-Powered Triage** - Automatic severity assessment using Gemini AI
- **Department Admin Portal** - Manage and track incidents by category
- **Supervisory Dashboard** - System-wide oversight and user management
- **GIS Integration** - Real-time incident mapping and geolocation
- **REST API** - Full-featured API for integrations and analytics

### AI Capabilities (Powered by Gemini)
- **Intelligent Severity Assessment** - Context-aware severity classification
- **Resolution Guidance** - AI-generated recommendations for fixing issues
- **Pattern Recognition** - Detect infrastructure trends and hotspots
- **Natural Language Analysis** - Understand incident descriptions contextually
- **Risk Factor Identification** - Automatic hazard and risk assessment
- **City-Wide Insights** - Analytics on systemic infrastructure problems

## 📦 Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Google Gemini API Key (get it free from [Google AI Studio](https://aistudio.google.com/app/apikey))

### 1. Clone and Install Dependencies

```bash
cd CivicTrack
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file in the project root:

```env
# Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# Database Configuration (Optional - defaults to SQLite)
# DATABASE_URL=postgresql://user:password@localhost/civictrack
```

**⚠️ SECURITY WARNING:**
- Never commit `.env` file to version control
- Keep your API key private and secure
- Use environment variables for all secrets

### 3. Initialize Database

```bash
python app.py
```

The database will auto-initialize on first run with:
- SuperAdmin account: `superadmin` / password: `Admin@123`
- Demo Department Admin: `admin` / password: `Admin@123`

## 🔑 Getting a Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Get API Key"
3. Create a new API key in your Google Cloud project
4. Copy the key and add it to your `.env` file
5. Enable the Generative AI API in your Google Cloud Console

> **Free Tier**: Gemini API offers free tier with generous rate limits suitable for municipal deployments

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────┐
│           CivicTrack Application                │
├─────────────────────────────────────────────────┤
│                                                   │
│  ┌────────────────┐      ┌──────────────────┐  │
│  │   Web Routes   │      │  Admin Panel     │  │
│  │  (Report/View) │      │ (Status Updates) │  │
│  └────────┬───────┘      └────────┬─────────┘  │
│           │                       │             │
│           └───────────┬───────────┘             │
│                       │                         │
│                ┌──────▼──────┐                 │
│                │  Issue Model │                │
│                │  + AI Fields │                │
│                └──────┬───────┘                │
│                       │                         │
│           ┌───────────┴───────────┐            │
│           │                       │            │
│      ┌────▼─────────┐    ┌───────▼────┐      │
│      │  Gemini AI   │    │  SQLite DB │      │
│      │  Analyzer    │    │  (Issues)  │      │
│      └──────────────┘    └────────────┘      │
│                                               │
└─────────────────────────────────────────────────┘
```

## 🧠 AI Integration Details

### Gemini AI Module (`gemini_ai.py`)

The application includes a dedicated AI module that handles all Gemini interactions:

#### Class: `GeminiAnalyzer`

**Main Methods:**

1. **`analyze_incident_severity()`**
   - Analyzes incident details contextually
   - Returns severity level with confidence score
   - Identifies risk factors and immediate actions
   
   ```python
   analyzer = get_analyzer()
   result = analyzer.analyze_incident_severity(
       category="Power Grid",
       description="Live electrical wire hanging near school",
       location="Main Street, Ward 5"
   )
   # Result:
   # {
   #     'severity': 'Critical',
   #     'confidence': 0.95,
   #     'reasoning': 'Electrical hazard in proximity to children',
   #     'risk_factors': ['Electrocution risk', 'Public safety'],
   #     'immediate_action': 'Evacuate area and contact power department'
   # }
   ```

2. **`generate_resolution_guidance()`**
   - Provides department-specific recommendations
   - Estimates resolution timeline
   - Identifies required resources
   
   ```python
   guidance = analyzer.generate_resolution_guidance(
       issue_id=1,
       category="Water Supply",
       description="Main water line burst",
       severity="Critical"
   )
   # Result:
   # {
   #     'recommendations': [...],
   #     'timeline_hours': 4,
   #     'required_departments': ['Water', 'Traffic'],
   #     'cost_estimate': 'High'
   # }
   ```

3. **`extract_insights_from_batch()`**
   - Analyzes multiple incidents for patterns
   - Identifies infrastructure hotspots
   - Provides systemic recommendations
   
   ```python
   insights = analyzer.extract_insights_from_batch(
       issues=[issue1, issue2, issue3, ...]
   )
   # Result:
   # {
   #     'patterns': ['Power outages in east zone', ...],
   #     'infrastructure_hotspots': ['Main Street', 'Ward 5', ...],
   #     'systemic_recommendations': [...]
   # }
   ```

### Fallback Mode

If Gemini API is unavailable, the system automatically falls back to rule-based assessment:
- Uses keyword matching for severity classification
- Maintains app functionality without AI features
- Logs warnings for admin awareness

## 📡 API Endpoints

### Public Endpoints

#### GET `/api/incidents`
Retrieve all incidents with full details
```bash
curl http://localhost:5000/api/incidents
```

Response:
```json
[
  {
    "id": 1,
    "title": "Broken Streetlight",
    "category": "Power Grid",
    "severity": "High",
    "ai_confidence": 0.92,
    "ai_reasoning": "Non-functional lighting creates safety hazard",
    "status": "Pending",
    ...
  }
]
```

#### GET `/api/analytics`
Get incident statistics
```bash
curl http://localhost:5000/api/analytics
```

Response:
```json
{
  "by_category": {
    "Power Grid": 5,
    "Water Supply": 3,
    "Roads & Potholes": 7
  },
  "by_severity": {
    "Critical": 2,
    "High": 4,
    "Medium": 6,
    "Low": 3
  }
}
```

#### GET `/api/issue/<id>/recommendations`
Get AI recommendations for specific incident
```bash
curl http://localhost:5000/api/issue/1/recommendations
```

Response:
```json
{
  "issue_id": 1,
  "title": "Broken Streetlight",
  "current_severity": "High",
  "ai_recommendations": {
    "recommendations": ["Replace bulb", "Check wiring", ...],
    "timeline_hours": 24,
    "required_departments": ["Electrical"],
    "cost_estimate": "Low"
  }
}
```

#### GET `/api/insights`
Get city-wide infrastructure insights
```bash
curl http://localhost:5000/api/insights?limit=50
```

## 🛠️ Usage Examples

### For Citizens: Report an Issue

```python
# POST request to /report
{
  "title": "Pothole creating traffic hazard",
  "category": "Roads & Potholes",
  "description": "Large pothole (1m diameter) in center lane, causing accidents",
  "location": "Main Street, Junction with Park Road",
  "latitude": 17.385,
  "longitude": 78.487
}

# AI Analysis Result:
# Severity: High
# Reasoning: "Traffic hazard with size suggests structural damage"
# Risk Factors: ["Vehicle damage", "Accident potential"]
# Action: "Mark area, notify road department immediately"
```

### For Administrators: View Recommendations

```python
# GET /api/issue/1/recommendations

# AI Response:
{
  "recommendations": [
    "Assess pavement condition",
    "Measure pothole dimensions",
    "Check underlying soil stability",
    "Plan road resurfacing if needed"
  ],
  "timeline_hours": 48,
  "required_departments": ["Roads & Infrastructure"],
  "cost_estimate": "Medium"
}
```

### For Supervisors: City-Wide Analysis

```python
# GET /api/insights?limit=100

# AI Response:
{
  "patterns": [
    "Clustering of power failures in east zone",
    "Seasonal water main breaks in winter",
    "Traffic congestion correlated with road hazards"
  ],
  "infrastructure_hotspots": [
    "Main Street-Park Road intersection",
    "Industrial Zone Water Main",
    "East Ward Electrical Grid"
  ],
  "systemic_recommendations": [
    "Upgrade east zone power distribution",
    "Schedule preventive water main maintenance",
    "Implement predictive road monitoring"
  ]
}
```

## 📊 Database Schema

### Issue Model
```python
Issue
├── id (Primary Key)
├── title (String)
├── category (String) - Roads, Power, Water, Sanitation, etc.
├── description (Text) - Full incident details
├── location (String) - Address/location
├── latitude (Float) - GPS coordinate
├── longitude (Float) - GPS coordinate
├── severity (String) - Critical/High/Medium/Low (AI-determined)
├── ai_confidence (Float) - AI confidence 0-1
├── ai_reasoning (Text) - Why AI assigned that severity
├── ai_recommendations (Text) - JSON-stored recommendations
├── status (String) - Pending/In Progress/Resolved
├── created_at (DateTime)
└── user_id (Foreign Key to User)
```

## 🔐 Security Considerations

### API Key Management
- Store API keys in `.env` file (Git-ignored)
- Use environment variables in production
- Rotate keys regularly
- Monitor API usage in Google Cloud Console

### Data Privacy
- Incident data contains location information - handle carefully
- User authentication required for sensitive operations
- Admin panel restricted to authorized users
- API endpoints validate permissions

### Best Practices
```python
# ✅ DO: Use environment variables
api_key = os.environ.get('GEMINI_API_KEY')

# ❌ DON'T: Hardcode API keys
api_key = "AIzaSyABC123..."  # NEVER!

# ✅ DO: Check for API availability
if analyzer.available:
    result = analyzer.analyze_incident_severity(...)

# ❌ DON'T: Assume API is always available
result = analyzer.analyze_incident_severity(...)
```

## 🚀 Deployment

### Local Development
```bash
python app.py
# Access at http://localhost:5000
```

### Production (using Gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Environment Variables Required
```env
GEMINI_API_KEY=your_key
SECRET_KEY=production_secret_key
FLASK_ENV=production
DATABASE_URL=postgresql://user:pass@host/civictrack
```

## 📈 Performance & Rate Limiting

**Gemini API Rate Limits:**
- Free tier: 60 requests/minute
- Paid tier: Up to 1,500 requests/minute
- Batch analysis recommended for historical data

**Optimization Tips:**
- Cache AI analysis results for repeated queries
- Batch multiple incidents for system insights
- Implement request queuing for high volume
- Use fallback mode gracefully

## 🐛 Troubleshooting

### "GEMINI_API_KEY not found"
```bash
# Verify .env file exists and has the key
cat .env | grep GEMINI_API_KEY

# Test API connection
python -c "from gemini_ai import get_analyzer; print(get_analyzer().available)"
```

### "AI features unavailable"
- Check internet connection
- Verify API key validity in Google Cloud Console
- Check rate limiting hasn't been exceeded
- Review logs for specific errors

### Database Errors
```bash
# Reset database
rm civictrack_v2.db
python app.py  # Reinitialize
```

## 📚 Additional Resources

- [Google Gemini API Documentation](https://ai.google.dev/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Flask-Login Guide](https://flask-login.readthedocs.io/)

## 📝 License

This project is provided as-is for municipal incident management.

## 🤝 Contributing

To improve AI capabilities:
1. Test with various incident types
2. Collect feedback on recommendations
3. Improve prompts in `gemini_ai.py`
4. Submit improvements for review

## 📧 Support

For issues or questions:
- Review application logs
- Check `.env` configuration
- Verify API key permissions
- Consult Gemini API documentation

---

**Version:** 2.0 (AI-Enhanced)  
**Last Updated:** September 2026  
**Status:** ✅ Production Ready
