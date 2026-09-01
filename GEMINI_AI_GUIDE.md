# CivicTrack Gemini AI Integration Guide

## 🎯 AI Implementation Overview

This guide explains how Gemini AI is integrated into CivicTrack and how to use it effectively.

## 📌 What AI Does in CivicTrack

### 1. **Incident Severity Assessment** ⚠️
When a citizen reports an issue, AI analyzes it contextually and assigns:
- **Severity Level**: Critical, High, Medium, or Low
- **Confidence Score**: 0.0 to 1.0 (how certain the AI is)
- **Risk Factors**: Identified hazards
- **Immediate Actions**: First steps to take

**Example:**
```
Report: "Electrical wire hanging near playground"
Category: Power Grid

AI Analysis:
├─ Severity: CRITICAL (0.98 confidence)
├─ Risk: "Electrocution hazard to children"
├─ Action: "Evacuate area immediately, call emergency services"
└─ Timeline: "Resolve within 2 hours"
```

### 2. **Resolution Recommendations** 💡
Admins can request AI-powered guidance for fixing issues:
- Step-by-step repair procedures
- Required equipment and personnel
- Estimated timeline
- Department coordination
- Cost estimates

**Example:**
```
Issue: Pothole on Main Street

AI Recommendations:
├─ Steps: ["Assess damage", "Mark area", "Fill pothole", "Test stability"]
├─ Timeline: 24-48 hours
├─ Departments: Road Maintenance, Traffic Control
├─ Cost: Medium
└─ Equipment: Asphalt, paving roller, safety gear
```

### 3. **City-Wide Insights** 🏙️
System analyzes all incidents to identify:
- Infrastructure hotspots (problem areas)
- Patterns and trends
- Systemic issues requiring policy changes
- Resource allocation recommendations

**Example:**
```
Analysis of 150 recent incidents:

Patterns Detected:
├─ Power failures cluster in East Zone (15 incidents)
├─ Water main breaks increase in winter (seasonal trend)
├─ Road deterioration follows traffic patterns
└─ Public complaints spike after extreme weather

Recommendations:
├─ Upgrade East Zone electrical infrastructure
├─ Schedule preventive water main maintenance
├─ Implement predictive road monitoring
└─ Pre-position repair crews before storm seasons
```

---

## 🔧 How to Set Up

### Step 1: Get Your Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Get API Key" button
3. Create new API key (if prompted, create a new Google Cloud project)
4. Copy the generated key

### Step 2: Configure Your Environment

Create `.env` file in the project root:

```bash
# Linux/Mac
echo 'GEMINI_API_KEY=your_api_key_here' > .env

# Windows PowerShell
Set-Content .env -Value 'GEMINI_API_KEY=your_api_key_here'
```

**Add to .env:**
```env
GEMINI_API_KEY=AIzaSyDu1234567890abcdefgh...
SECRET_KEY=your-secret-key-123
FLASK_ENV=development
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

Key new packages:
- `google-generativeai==0.3.5` - Gemini AI SDK
- `python-dotenv==1.0.0` - Environment variable loading

### Step 4: Run the Application

```bash
python app.py
```

The app will:
- Load your API key from `.env`
- Test Gemini connection
- Initialize database with AI-enhanced schema
- Start server at `http://localhost:5000`

---

## 🧠 AI Architecture

### How It Works Behind the Scenes

```
User Reports Issue
        ↓
    ┌───────────────────────────────────┐
    │  App Receives Report Data         │
    │  - Title, Category, Description   │
    │  - Location, GPS Coordinates      │
    └─────────────┬─────────────────────┘
                  ↓
    ┌───────────────────────────────────┐
    │  Gemini AI Analysis Triggered     │
    │  - Process description            │
    │  - Understand context             │
    │  - Assess risks                   │
    └─────────────┬─────────────────────┘
                  ↓
    ┌───────────────────────────────────┐
    │  AI Returns Analysis              │
    │  - Severity Level                 │
    │  - Confidence Score               │
    │  - Risk Factors                   │
    │  - Recommendations                │
    └─────────────┬─────────────────────┘
                  ↓
    ┌───────────────────────────────────┐
    │  Save to Database                 │
    │  - Store all AI findings          │
    │  - Link to user who reported      │
    │  - Create actionable ticket       │
    └─────────────┬─────────────────────┘
                  ↓
    Admin Dashboard Shows AI Results
```

### Core AI Module: `gemini_ai.py`

**Class: `GeminiAnalyzer`**

```python
from gemini_ai import get_analyzer

# Get the AI analyzer instance
analyzer = get_analyzer()

# Use it for analysis
result = analyzer.analyze_incident_severity(
    category="Water Supply",
    description="Water pipe burst, street flooded",
    location="Park Avenue, Ward 5"
)

print(result)
# {
#     'severity': 'Critical',
#     'confidence': 0.96,
#     'reasoning': 'Large water loss in public area creates flooding hazard',
#     'risk_factors': ['Flooding', 'Water loss', 'Traffic disruption'],
#     'immediate_action': 'Close street, call water department emergency line'
# }
```

---

## 📊 Data Integration

### New Database Fields

When you create an issue, these AI fields are now stored:

```python
class Issue(db.Model):
    # Existing fields
    id, title, category, description, location, latitude, longitude
    status, created_at, user_id
    
    # NEW AI-ENHANCED FIELDS:
    severity           # AI-determined severity level
    ai_confidence      # How certain (0.0 to 1.0)
    ai_reasoning       # Text explanation from AI
    ai_recommendations # JSON-stored recommendations
```

### Example Database Record

```sql
INSERT INTO issue (title, category, description, location, 
                  severity, ai_confidence, ai_reasoning)
VALUES (
    'Broken Traffic Light',
    'Power Grid',
    'Traffic light at Main & Park not functioning, creating hazard',
    'Main Street & Park Avenue',
    'High',
    0.92,
    'Non-functional traffic control creates vehicle collision risk'
);
```

---

## 🔌 API Endpoints

### New AI-Enhanced Endpoints

#### 1. Get Incident Recommendations
```bash
GET /api/issue/{issue_id}/recommendations

Example:
curl http://localhost:5000/api/issue/1/recommendations

Response:
{
    "issue_id": 1,
    "title": "Broken Streetlight",
    "current_severity": "High",
    "ai_recommendations": {
        "recommendations": [
            "Inspect fixture for electrical damage",
            "Check wiring integrity",
            "Replace bulb or ballast as needed",
            "Test circuit safety"
        ],
        "timeline_hours": 24,
        "required_departments": ["Electrical", "Public Works"],
        "cost_estimate": "Low"
    }
}
```

#### 2. Get City-Wide Insights
```bash
GET /api/insights?limit=50

Example:
curl http://localhost:5000/api/insights?limit=100

Response:
{
    "patterns": [
        "Clustering of power outages in East Zone",
        "Seasonal increase in water main breaks"
    ],
    "infrastructure_hotspots": [
        "Main Street intersection",
        "Industrial Zone"
    ],
    "systemic_recommendations": [
        "Upgrade aging power infrastructure",
        "Implement preventive maintenance schedule"
    ]
}
```

#### 3. Get All Incidents (Enhanced)
```bash
GET /api/incidents

Now returns AI fields:
{
    "id": 1,
    "title": "...",
    "severity": "High",
    "ai_confidence": 0.92,
    "ai_reasoning": "..."
}
```

---

## 🎓 Example Use Cases

### Case 1: Citizen Reports Issue

**What citizen enters:**
```
Title: "Big hole in road causing car damage"
Category: Roads & Potholes
Description: "1.5 meter pothole on main road, already damaged 3 cars this week"
Location: "Main Street near Market"
GPS: 17.3850, 78.4867
```

**AI Analysis:**
```
Severity: HIGH
Confidence: 0.89
Reasoning: "Dangerous road condition with documented damage pattern"
Risk Factors: ["Vehicle damage risk", "Traffic hazard", "Liability"]
Action: "Mark area, contact road dept for urgent repair"
```

---

### Case 2: Admin Requests Guidance

**Admin wants to know:** How to fix the pothole?

**AI Provides:**
```
Steps:
1. Safety assessment - cones and barriers
2. Measure dimensions and depth
3. Clean debris and loose material
4. Fill with hot asphalt
5. Compact with rolling
6. Temperature cure (24 hours)

Timeline: 48 hours
Resources: Road maintenance crew, asphalt truck
Cost: Low
```

---

### Case 3: System Generates Insights

**Question:** What patterns in last 100 incidents?

**AI Response:**
```
Findings:
- 23 power-related issues (mostly East Zone)
- 15 water-related issues (70% in winter)
- 34 road issues (follow traffic patterns)
- 28 sanitation issues (cluster near markets)

Recommendation:
1. Prioritize East Zone electrical grid upgrade
2. Schedule water main inspection before winter
3. Implement predictive road monitoring
4. Increase sanitation crew in market areas
```

---

## ⚙️ Configuration Options

### In `gemini_ai.py`

You can customize AI behavior:

```python
# Model selection (default: gemini-pro)
self.model = genai.GenerativeModel('gemini-pro')

# Change to other available models:
# - 'gemini-pro-vision' for image analysis (future enhancement)
# - 'gemini-1.5-pro' for advanced reasoning (if available)

# Customize prompts for different use cases
prompt = f"""
Analyze this {category} incident from municipal perspective.
Consider: Public safety, infrastructure impact, budget constraints.
Provide assessment as JSON.
"""
```

### API Configuration

In `app.py`:

```python
# Control AI features
analyzer = get_analyzer()

if analyzer.available:
    # AI is enabled
    result = analyzer.analyze_incident_severity(...)
else:
    # Fallback to rule-based severity
    result = fallback_assessment(...)
```

---

## 🚨 Error Handling

### When AI Unavailable

If API key missing or Gemini unreachable:

```python
# Automatic fallback behavior:
1. Log warning: "AI features unavailable"
2. Use rule-based severity assessment
3. Store as if AI analyzed it
4. Continue normal operation

Result: App works with or without AI!
```

### Checking AI Status

```python
# In your code:
from gemini_ai import get_analyzer

analyzer = get_analyzer()
print(f"AI Available: {analyzer.available}")

if analyzer.available:
    print("✓ Gemini API connected")
else:
    print("⚠ Using fallback analysis mode")
```

---

## 📈 Performance Tips

### Optimizing AI Usage

1. **Batch Analysis**
   ```python
   # Good: Analyze 10 issues at once
   insights = analyzer.extract_insights_from_batch(issues)
   
   # Avoid: Analyzing same issue 10 times
   for i in range(10):
       result = analyzer.analyze_incident_severity(...)
   ```

2. **Cache Results**
   ```python
   # Once analyzed, stored in database
   # Don't re-analyze same issue
   issue = Issue.query.get(1)
   use_stored_severity = issue.severity  # Already AI-analyzed
   ```

3. **Rate Limiting**
   - Free tier: 60 requests/minute
   - Paid tier: 1,500 requests/minute
   - Monitor usage in Google Cloud Console

---

## 🔐 Security Best Practices

### ✅ DO

```bash
# Store API key in .env
echo 'GEMINI_API_KEY=AIzaSy...' > .env

# Keep .env in .gitignore
echo '.env' >> .gitignore

# Rotate keys periodically
# Monitor API usage for unusual activity
```

### ❌ DON'T

```python
# ❌ Never hardcode keys
GEMINI_API_KEY = "AIzaSyABC123..."

# ❌ Never commit .env to git
git add .env  # WRONG!

# ❌ Never share API keys
Email: "Here's my key: AIzaSy..."

# ❌ Never log API keys
print(f"Key: {api_key}")  # WRONG!
```

---

## 📚 Learning Resources

### Gemini API
- [Official Docs](https://ai.google.dev/docs)
- [API Reference](https://ai.google.dev/api)
- [Model Capabilities](https://ai.google.dev/models)

### CivicTrack
- Main README: `README.md`
- This guide: `GEMINI_AI_GUIDE.md`
- Source code: `gemini_ai.py`

---

## 🆘 Troubleshooting

### Problem: "GEMINI_API_KEY not found"

**Solution:**
```bash
# 1. Check .env exists
ls -la .env

# 2. Check it has the key
cat .env | grep GEMINI_API_KEY

# 3. Copy from .env.example
cp .env.example .env
# Then edit .env with your real key
```

### Problem: "API key invalid"

**Solution:**
```bash
# 1. Check key format (should start with AIzaSy)
echo $GEMINI_API_KEY

# 2. Verify in Google Cloud Console
# - Visit console.cloud.google.com
# - Check API is enabled
# - Check key restrictions

# 3. Regenerate key if needed
# Go back to https://aistudio.google.com/app/apikey
```

### Problem: "Rate limit exceeded"

**Solution:**
```bash
# 1. Wait before retrying (auto-retry in code)
# 2. Check usage in Google Cloud Console
# 3. Upgrade to paid tier if needed
# 4. Implement caching to reduce calls
```

---

## 📞 Support

For issues:
1. Check error logs: `python app.py` (look for stack traces)
2. Verify API key in `.env`
3. Test connection: `python -c "from gemini_ai import get_analyzer; print(get_analyzer().available)"`
4. Review [Gemini docs](https://ai.google.dev/docs)

---

**Ready to use AI in CivicTrack?** Start by running the app and reporting a test issue! 🚀
