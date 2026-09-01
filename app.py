import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'civictrack-key-9982314')

database_url = os.environ.get('DATABASE_URL')

if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, 'civictrack_v2.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

_db_initialized = False

def init_db():
    global _db_initialized
    if _db_initialized:
        return
    try:
        with app.app_context():
            db.create_all()
        _db_initialized = True
        print("Database initialized")
    except Exception as e:
        print(f"Database init error: {e}")

@app.before_request
def ensure_db():
    init_db()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='Citizen')
    department = db.Column(db.String(50), nullable=True)
    issues = db.relationship('Issue', backref='reporter', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Issue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    severity = db.Column(db.String(20), default='Medium', index=True)
    ai_confidence = db.Column(db.Float, default=0.0)
    ai_reasoning = db.Column(db.Text, nullable=True)
    ai_recommendations = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Pending', index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'description': self.description,
            'location': self.location,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'severity': self.severity,
            'ai_confidence': self.ai_confidence,
            'ai_reasoning': self.ai_reasoning,
            'ai_recommendations': self.ai_recommendations,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'reporter': self.reporter.username if self.reporter else 'Unknown'
        }

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issue.id'), nullable=False, index=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    message = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    is_read = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    issue = db.relationship('Issue', backref='notifications', lazy='joined')
    recipient = db.relationship('User', backref='notifications', lazy='joined')

    def to_dict(self):
        return {
            'id': self.id,
            'issue_id': self.issue_id,
            'message': self.message,
            'severity': self.severity,
            'is_read': self.is_read,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'issue_title': self.issue.title if self.issue else '',
            'reporter': self.issue.reporter.username if self.issue and self.issue.reporter else 'Unknown'
        }

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except:
        return None

def calculate_ai_severity(category, description):
    desc = description.lower()
    critical_keywords = ['electrical', 'hazard', 'fire', 'explosion', 'live wire', 'collapse', 'flooding']
    high_keywords = ['leak', 'sewage', 'blocked', 'outage', 'broken main', 'traffic light']
    
    if any(kw in desc for kw in critical_keywords):
        return 'Critical'
    elif category in ['Power Grid', 'Water Supply'] or any(kw in desc for kw in high_keywords):
        return 'High'
    elif category in ['Roads & Potholes', 'Sanitation']:
        return 'Medium'
    return 'Low'

def get_analyzer():
    try:
        from gemini_ai import get_analyzer as _get
        return _get()
    except:
        return None

def create_notifications_for_issue(issue):
    admins = User.query.filter(User.role.in_(['Admin', 'SuperAdmin'])).all()
    severity_labels = {
        'Critical': 'CRITICAL',
        'High': 'HIGH',
        'Medium': 'MEDIUM',
        'Low': 'LOW'
    }
    label = severity_labels.get(issue.severity, issue.severity.upper())
    for admin in admins:
        if admin.role == 'Admin' and issue.category != admin.department and admin.department is not None:
            continue
        notif = Notification(
            issue_id=issue.id,
            recipient_id=admin.id,
            message=f"[{label}] New incident reported: {issue.title}",
            severity=issue.severity
        )
        db.session.add(notif)
    db.session.commit()

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

@app.route('/')
def index():
    recent_issues = Issue.query.order_by(Issue.created_at.desc()).limit(6).all()
    total_reported = Issue.query.count()
    total_resolved = Issue.query.filter_by(status='Resolved').count()
    total_critical = Issue.query.filter_by(severity='Critical').count()
    return render_template('index.html', issues=recent_issues, reported=total_reported, resolved=total_resolved, critical=total_critical)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        email = (request.form.get('email') or '').strip().lower()
        password = request.form.get('password')
        role = request.form.get('role', 'Citizen')
        
        if not username or not email or not password:
            flash('Username, email, and password are required.', 'warning')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Email address is already registered.', 'warning')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first():
            flash('Username is already taken.', 'warning')
            return redirect(url_for('register'))

        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Account registered successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = (request.form.get('email') or '').strip().lower()
        password = request.form.get('password') or ''
        
        if not email or not password:
            flash('Email and password are required.', 'warning')
            return redirect(url_for('login'))
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            if user.role == 'SuperAdmin':
                return redirect(url_for('admin_super'))
            elif user.role == 'Admin':
                return redirect(url_for('admin_dept'))
            return redirect(url_for('dashboard'))
        flash('Invalid credentials. Check your email and password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/report', methods=['GET', 'POST'])
@login_required
def report():
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        description = request.form.get('description')
        location = request.form.get('location')
        lat = request.form.get('latitude', type=float)
        lng = request.form.get('longitude', type=float)

        severity = calculate_ai_severity(category, description)
        ai_confidence = 0.0
        ai_reasoning = ''
        ai_recommendations = ''

        analyzer = get_analyzer()
        if analyzer:
            try:
                ai_analysis = analyzer.analyze_incident_severity(
                    category=category,
                    description=description,
                    location=location
                )
                severity = ai_analysis.get('severity', severity)
                ai_confidence = ai_analysis.get('confidence', 0.0)
                ai_reasoning = ai_analysis.get('reasoning', '')
                recs = ai_analysis.get('recommendations', [])
                if isinstance(recs, list):
                    ai_recommendations = ', '.join(recs)
                else:
                    ai_recommendations = str(recs) if recs else ''
            except Exception as e:
                print(f"AI analysis error: {e}")

        new_issue = Issue(
            title=title,
            category=category,
            description=description,
            location=location,
            latitude=lat,
            longitude=lng,
            severity=severity,
            ai_confidence=ai_confidence,
            ai_reasoning=ai_reasoning,
            ai_recommendations=ai_recommendations,
            user_id=current_user.id
        )
        db.session.add(new_issue)
        db.session.commit()
        create_notifications_for_issue(new_issue)

        flash(f'Incident submitted successfully! AI Analysis: {severity} severity', 'success')
        return redirect(url_for('dashboard'))
    return render_template('report.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role in ['Admin', 'SuperAdmin']:
        issues = Issue.query.order_by(Issue.created_at.desc()).all()
    else:
        issues = Issue.query.filter_by(user_id=current_user.id).order_by(Issue.created_at.desc()).all()

    pending = sum(1 for i in issues if i.status == 'Pending')
    in_progress = sum(1 for i in issues if i.status == 'In Progress')
    resolved = sum(1 for i in issues if i.status == 'Resolved')
    
    return render_template('dashboard.html', issues=issues, pending=pending, in_progress=in_progress, resolved=resolved)

@app.route('/admin/super')
@login_required
def admin_super():
    if current_user.role != 'SuperAdmin':
        flash('Access restricted to Super Admin officers only.', 'danger')
        return redirect(url_for('dashboard'))
    
    all_issues = Issue.query.order_by(Issue.created_at.desc()).all()
    all_users = User.query.order_by(User.id.asc()).all()
    critical_count = sum(1 for i in all_issues if i.severity == 'Critical')
    pending_count = sum(1 for i in all_issues if i.status == 'Pending')
    
    return render_template('admin_super.html', issues=all_issues, users=all_users, critical=critical_count, pending=pending_count)

@app.route('/admin/dept')
@login_required
def admin_dept():
    if current_user.role not in ['Admin', 'SuperAdmin']:
        flash('Access restricted to Department Admins.', 'danger')
        return redirect(url_for('dashboard'))

    if current_user.role == 'SuperAdmin':
        issues = Issue.query.order_by(Issue.created_at.desc()).all()
    else:
        dept = current_user.department
        if dept:
            issues = Issue.query.filter_by(category=dept).order_by(Issue.created_at.desc()).all()
        else:
            issues = Issue.query.order_by(Issue.created_at.desc()).all()
    return render_template('admin_dept.html', issues=issues)

@app.route('/admin/monitoring')
@login_required
def admin_monitoring():
    if current_user.role not in ['Admin', 'SuperAdmin']:
        flash('Access restricted to administrative officers.', 'danger')
        return redirect(url_for('dashboard'))

    all_issues = Issue.query.order_by(Issue.created_at.desc()).limit(30).all()
    notifications = Notification.query.filter_by(recipient_id=current_user.id).order_by(Notification.created_at.desc()).limit(20).all()
    unread_count = Notification.query.filter_by(recipient_id=current_user.id, is_read=False).count()
    critical_count = sum(1 for i in all_issues if i.severity == 'Critical')
    pending_count = sum(1 for i in all_issues if i.status == 'Pending')

    return render_template(
        'admin_monitoring.html',
        issues=all_issues,
        notifications=notifications,
        unread_count=unread_count,
        critical=critical_count,
        pending=pending_count
    )

@app.route('/api/notifications')
@login_required
def api_notifications():
    if current_user.role not in ['Admin', 'SuperAdmin']:
        return jsonify({'error': 'Unauthorized'}), 403

    notifications = Notification.query.filter_by(recipient_id=current_user.id).order_by(Notification.created_at.desc()).limit(20).all()
    return jsonify([n.to_dict() for n in notifications])

@app.route('/api/notifications/unread-count')
@login_required
def api_notifications_unread_count():
    if current_user.role not in ['Admin', 'SuperAdmin']:
        return jsonify({'error': 'Unauthorized'}), 403

    count = Notification.query.filter_by(recipient_id=current_user.id, is_read=False).count()
    return jsonify({'unread_count': count})

@app.route('/api/notifications/read', methods=['POST'])
@login_required
def api_notifications_read():
    if current_user.role not in ['Admin', 'SuperAdmin']:
        return jsonify({'error': 'Unauthorized'}), 403

    Notification.query.filter_by(recipient_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    return jsonify({'success': True})

@app.route('/admin/user/<int:user_id>/change-role', methods=['POST'])
@login_required
def change_role(user_id):
    if current_user.role != 'SuperAdmin':
        flash('Only Super Admins can change user roles.', 'danger')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role', 'Citizen')
    new_department = request.form.get('department') or None
    
    if new_role in ['Citizen', 'Admin', 'SuperAdmin']:
        user.role = new_role
        user.department = new_department
        db.session.commit()
        flash(f'User {user.username} role updated to {new_role}.', 'success')
    else:
        flash('Invalid role specified.', 'danger')
    
    return redirect(url_for('admin_super'))

@app.route('/issue/<int:issue_id>/update', methods=['POST'])
@login_required
def update_issue_status(issue_id):
    if current_user.role not in ['Admin', 'SuperAdmin']:
        flash('Unauthorized permission level.', 'danger')
        return redirect(url_for('dashboard'))
    
    issue = Issue.query.get_or_404(issue_id)
    new_status = request.form.get('status')
    if new_status in ['Pending', 'In Progress', 'Resolved']:
        issue.status = new_status
        db.session.commit()
        flash(f'Incident #{issue.id} status updated to {new_status}.', 'success')
    
    if current_user.role == 'SuperAdmin':
        return redirect(url_for('admin_super'))
    elif current_user.role == 'Admin':
        return redirect(url_for('admin_dept'))
    return redirect(url_for('dashboard'))

@app.route('/api/incidents', methods=['GET'])
def api_incidents():
    incidents = Issue.query.order_by(Issue.created_at.desc()).all()
    return jsonify([i.to_dict() for i in incidents])

@app.route('/api/analytics', methods=['GET'])
def api_analytics():
    categories = db.session.query(Issue.category, db.func.count(Issue.id)).group_by(Issue.category).all()
    severities = db.session.query(Issue.severity, db.func.count(Issue.id)).group_by(Issue.severity).all()
    return jsonify({
        'by_category': dict(categories),
        'by_severity': dict(severities)
    })

@app.route('/api/issue/<int:issue_id>/recommendations', methods=['GET'])
def get_issue_recommendations(issue_id):
    issue = Issue.query.get_or_404(issue_id)
    
    analyzer = get_analyzer()
    if analyzer:
        try:
            recommendations = analyzer.generate_resolution_guidance(
                issue_id=issue.id,
                category=issue.category,
                description=issue.description,
                severity=issue.severity
            )
        except:
            recommendations = {"recommendations": ["Contact relevant department"], "timeline": "Depends on severity"}
    else:
        recommendations = {"recommendations": ["Contact relevant department"], "timeline": "Depends on severity"}
    
    return jsonify({
        'issue_id': issue.id,
        'title': issue.title,
        'current_severity': issue.severity,
        'ai_recommendations': recommendations
    })

@app.route('/api/insights', methods=['GET'])
def get_system_insights():
    limit = request.args.get('limit', 20, type=int)
    recent_issues = Issue.query.order_by(Issue.created_at.desc()).limit(limit).all()
    
    analyzer = get_analyzer()
    if analyzer:
        try:
            insights = analyzer.extract_insights_from_batch(
                issues=[i.to_dict() for i in recent_issues]
            )
        except:
            insights = {"patterns": [], "hotspots": [], "recommendations": []}
    else:
        insights = {"patterns": [], "hotspots": [], "recommendations": []}
    
    return jsonify(insights)

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', code=404, message='Page not found'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html', code=500, message='Internal server error. Please try again later.'), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
