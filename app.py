import os
from datetime import datetime
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# Database will be created in the instance folder locally or persist via volume
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'A_VERY_SECRET_KEY_FOR_DEMO'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

class DeploymentHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize database and create default admin user if missing
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        hashed_pw = generate_password_hash('admin123')
        admin = User(username='admin', password_hash=hashed_pw)
        db.session.add(admin)
        db.session.commit()

# ----- Auth Routes -----
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'error')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ----- UI Routes -----
@app.route("/")
@login_required
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    # Adding authentication check so the template logic knows user state,
    # but the page itself is public to prove basic application hosting.
    return render_template("about.html")

@app.route("/history")
@login_required
def history():
    events = DeploymentHistory.query.order_by(DeploymentHistory.timestamp.desc()).all()
    # Format the timestamp slightly for the UI
    for event in events:
        event.timestamp = event.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    return render_template("history.html", history=events)

# ----- API Routes -----
@app.route("/api/health")
def health():
    # Public route so dashboard graphs can update even if polling unauth
    count = DeploymentHistory.query.count()
    return jsonify({
        "status": "ok",
        "total_deployments": count
    })

@app.route("/api/trigger", methods=["POST"])
@login_required
def trigger():
    try:
        new_event = DeploymentHistory(event_type="Manual Deploy", status="SUCCESS")
        db.session.add(new_event)
        db.session.commit()
        return jsonify({"status": "success", "event_id": new_event.id})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)