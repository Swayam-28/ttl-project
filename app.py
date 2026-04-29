import os
import subprocess
import queue
import threading
from datetime import datetime
from flask import Flask, render_template, jsonify, request, redirect, url_for, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# Security configuration
app.config['SECRET_KEY'] = 'A_VERY_SECRET_KEY_FOR_DEMO'
# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Queue to handle streaming live terminal data safely to the browser
log_queue = queue.Queue()

# --- Database Models ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

class DeploymentHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(200), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Initialize database and create default admin user
with app.app_context():
    db.create_all()
    if not db.session.query(User).filter_by(username='admin').first():
        hashed_pw = generate_password_hash('admin123')
        admin = User(username='admin', password_hash=hashed_pw)
        db.session.add(admin)
        db.session.commit()

# --- Background Worker for CI/CD Execution ---
def execute_pipeline():
    import time
    log_queue.put("Initializing automated CI/CD pipeline sequence...")
    log_queue.put("Connecting to EC2 Docker Engine and fetching repository status...")
    
    try:
        commands = [
            ("Marking directory as safe for git", ["git", "config", "--global", "--add", "safe.directory", "/app"]),
            ("Pulling latest code from GitHub", ["git", "pull", "origin", "main"])
        ]
        
        for name, cmd in commands:
            log_queue.put(f"[EXEC] {name}...")
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in process.stdout:
                log_queue.put(line.strip())
            process.wait()
            
            if process.returncode != 0:
                log_queue.put(f"Pipeline stalled due to sub-process error (Code {process.returncode})")
                log_queue.put("[EOF]")
                return
                
        log_queue.put("Pipeline Execution Passed! Code updated to latest origin/main.")
        log_queue.put("Rebuilding infrastructure in background...")
    except Exception as e:
        log_queue.put(f"Critical execution failure: {str(e)}")
        log_queue.put("[EOF]")
        return
        
    log_queue.put("[EOF]")
    
    # Give the frontend 2 seconds to receive [EOF] and close the connection smoothly
    time.sleep(2)
    
    # Fire the actual docker compose command in the background to rebuild and restart the server
    subprocess.Popen(["docker", "compose", "-p", "ttl-project", "up", "-d", "--build"])

@app.route('/')
@login_required
def home():
    return render_template('index.html')

@app.route('/history')
@login_required
def history():
    events = DeploymentHistory.query.order_by(DeploymentHistory.id.desc()).all()
    # Format dates
    for record in events:
        record.timestamp = record.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    return render_template('history.html', history=events)

@app.route('/about')
@login_required
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        # Now accepting JSON payloads for seamless Async UI
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Invalid request payload."})
            
        username = data.get('username')
        password = data.get('password')
        
        user = db.session.query(User).filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return jsonify({"success": True, "redirect": url_for('home')})
        else:
            return jsonify({"success": False, "message": "Invalid username or password"})
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- True CI/CD APIs ---

@app.route('/api/webhook', methods=['POST'])
def webhook():
    """ 
    GitHub hits this endpoint when a user pushes code. 
    It logs the commit message and kicks off the background pipeline!
    """
    payload = request.get_json()
    commit_msg = "Manual Push Event Detected"
    
    if payload and 'head_commit' in payload and payload['head_commit']:
        commit_msg = payload['head_commit'].get('message', "Commit details blank")
        
    new_event = DeploymentHistory(status=f"Webhook Event: {commit_msg}")
    db.session.add(new_event)
    db.session.commit()
    
    # Fire background trigger
    threading.Thread(target=execute_pipeline).start()
    return jsonify({"success": True, "message": "Webhook deployed successfully."})

@app.route('/api/trigger', methods=['POST'])
@login_required
def trigger():
    """ Called manually by the UI Button """
    new_event = DeploymentHistory(status="Manual Pipeline Execution")
    db.session.add(new_event)
    db.session.commit()
    
    # Fire background pipeline to start filling the queue
    threading.Thread(target=execute_pipeline).start()
    return jsonify({"success": True})

@app.route('/api/logs/stream')
@login_required
def stream_logs():
    """ Server-Sent Events (SSE) route to pipe subprocess terminal output straight to the browser DOM """
    def generate():
        while True:
            # Block until Python puts a line from the subprocess into the queue
            msg = log_queue.get()
            yield f"data: {msg}\n\n"
            if msg == "[EOF]":
                break
    return Response(generate(), mimetype='text/event-stream')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)