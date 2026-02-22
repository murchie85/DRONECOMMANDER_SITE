import os

def create_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"✅ Created: {path}")

# --- CONTENT DEFINITIONS ---

requirements_txt = """
flask
flask-sqlalchemy
"""

app_py = """
import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# CONFIGURATION
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///bugs.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# MODEL
class Bug(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bug_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    submitter = db.Column(db.String(100), default='Drone Player')
    blocking = db.Column(db.Boolean, default=False)
    resolved = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'bug_type': self.bug_type,
            'description': self.description,
            'submitter': self.submitter,
            'blocking': 'Yes' if self.blocking else 'No',
            'resolved': self.resolved,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M')
        }

with app.app_context():
    db.create_all()

# ROUTES
@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/bug-reporter')
def bug_reporter():
    return render_template('reporter.html')

@app.route('/script-uploader')
def script_uploader():
    return render_template('todo.html', title="Script Uploader")

@app.route('/map-uploader')
def map_uploader():
    return render_template('todo.html', title="Map Uploader")

@app.route('/latest-update')
def latest_update():
    return render_template('todo.html', title="Latest Update")

# API
@app.route('/api/bugs', methods=['GET'])
def get_bugs():
    bugs = Bug.query.order_by(Bug.timestamp.desc()).all()
    return jsonify([b.to_dict() for b in bugs])

@app.route('/api/bugs', methods=['POST'])
def add_bug():
    data = request.json
    new_bug = Bug(
        bug_type=data.get('bug_type'),
        description=data.get('description'),
        submitter=data.get('submitter') or 'Drone Player',
        blocking=data.get('blocking', False)
    )
    db.session.add(new_bug)
    db.session.commit()
    return jsonify({'message': 'Bug reported!'}), 201

@app.route('/api/bugs/<int:id>', methods=['DELETE'])
def delete_bug(id):
    bug = Bug.query.get_or_404(id)
    db.session.delete(bug)
    db.session.commit()
    return jsonify({'message': 'Deleted'}), 200

if __name__ == '__main__':
    app.run(debug=True)
"""

landing_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Drone Commander Hub</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #121212; color: #00ffcc; font-family: 'Courier New', monospace; overflow: hidden; }
        .bg-video {
            position: fixed; right: 0; bottom: 0; min-width: 100%; min-height: 100%;
            z-index: -1; opacity: 0.4; pointer-events: none;
        }
        .hero-content {
            height: 100vh; display: flex; flex-direction: column;
            justify-content: center; align-items: center;
            text-align: center; z-index: 1;
        }
        .btn-drone {
            background: transparent; border: 2px solid #00ffcc; color: #00ffcc;
            padding: 15px 30px; margin: 10px; text-transform: uppercase;
            transition: 0.3s; width: 250px;
        }
        .btn-drone:hover { background: #00ffcc; color: #000; box-shadow: 0 0 15px #00ffcc; }
    </style>
</head>
<body>
    <div class="bg-video">
        <iframe width="100%" height="100%" 
        src="https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=1&mute=1&controls=0&loop=1&playlist=dQw4w9WgXcQ" 
        frameborder="0" allow="autoplay; encrypted-media"></iframe>
    </div>
    <div class="hero-content">
        <h1 class="display-3 fw-bold">DRONE COMMANDER</h1>
        <p class="lead">Command Center Access</p>
        <div class="mt-4">
            <a href="/bug-reporter" class="btn btn-drone">Bug Reporter</a>
            <a href="/script-uploader" class="btn btn-drone">Script Uploader</a>
            <a href="/map-uploader" class="btn btn-drone">Map Uploader</a>
            <a href="/latest-update" class="btn btn-drone">Latest Update</a>
        </div>
    </div>
</body>
</html>
"""

reporter_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Bug Reporter - Drone Commander</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #0f0f0f; color: #e0e0e0; font-family: sans-serif; }
        .container { max-width: 900px; margin-top: 30px; }
        .card { background-color: #1f1f1f; border: 1px solid #333; }
        .form-control, .form-select { background-color: #2b2b2b; border: 1px solid #444; color: #fff; }
        table { color: #ddd; }
        th { border-bottom: 2px solid #00ffcc !important; color: #00ffcc; }
        .admin-btn { color: red; cursor: pointer; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2>🐛 Drone Commander Bug Log</h2>
            <a href="/" class="btn btn-outline-secondary btn-sm">Back to Hub</a>
        </div>
        <div class="row mb-3">
            <div class="col-md-3">
                <select id="filterType" class="form-select" onchange="loadBugs()">
                    <option value="ALL">All Types</option>
                    <option value="RPG">RPG</option>
                    <option value="RTS">RTS</option>
                    <option value="VN">Visual Novel</option>
                    <option value="SYSTEM">System</option>
                    <option value="OTHER">Other</option>
                </select>
            </div>
            <div class="col-md-9 text-end">
                <button class="btn btn-success" onclick="toggleForm()">+ Report New Bug</button>
            </div>
        </div>
        <div id="bugForm" class="card p-3 mb-4" style="display:none;">
            <h5>New Incident Report</h5>
            <div class="row g-2">
                <div class="col-md-3">
                    <select id="newType" class="form-select">
                        <option value="RPG">RPG</option>
                        <option value="RTS">RTS</option>
                        <option value="VN">Visual Novel</option>
                        <option value="SYSTEM">System</option>
                        <option value="OTHER">Other</option>
                    </select>
                </div>
                <div class="col-md-6">
                    <input type="text" id="newDesc" class="form-control" placeholder="Describe the bug...">
                </div>
                <div class="col-md-3">
                    <input type="text" id="newSubmitter" class="form-control" placeholder="Name (Optional)">
                </div>
                <div class="col-md-12 mt-2 d-flex justify-content-between">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="newBlocking">
                        <label class="form-check-label">Blocks Playability?</label>
                    </div>
                    <button class="btn btn-primary btn-sm" onclick="submitBug()">Submit Report</button>
                </div>
            </div>
        </div>
        <table class="table table-dark table-hover">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Type</th>
                    <th>Description</th>
                    <th>Reporter</th>
                    <th>Blocker</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody id="bugTableBody"></tbody>
        </table>
    </div>
    <script>
        async function loadBugs() {
            const response = await fetch('/api/bugs');
            const bugs = await response.json();
            const filter = document.getElementById('filterType').value;
            const tbody = document.getElementById('bugTableBody');
            tbody.innerHTML = '';
            bugs.forEach(bug => {
                if (filter !== 'ALL' && bug.bug_type !== filter) return;
                let row = `<tr>
                    <td>${bug.timestamp}</td>
                    <td><span class="badge bg-secondary">${bug.bug_type}</span></td>
                    <td>${bug.description}</td>
                    <td>${bug.submitter}</td>
                    <td style="color: ${bug.blocking === 'Yes' ? 'red' : 'gray'}">${bug.blocking}</td>
                    <td><span class="admin-btn" onclick="deleteBug(${bug.id})">×</span></td>
                </tr>`;
                tbody.innerHTML += row;
            });
        }
        async function submitBug() {
            const data = {
                bug_type: document.getElementById('newType').value,
                description: document.getElementById('newDesc').value,
                submitter: document.getElementById('newSubmitter').value,
                blocking: document.getElementById('newBlocking').checked
            };
            await fetch('/api/bugs', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            document.getElementById('newDesc').value = '';
            toggleForm();
            loadBugs();
        }
        async function deleteBug(id) {
            if(!confirm('Admin Action: Delete this report?')) return;
            await fetch(`/api/bugs/${id}`, { method: 'DELETE' });
            loadBugs();
        }
        function toggleForm() {
            const form = document.getElementById('bugForm');
            form.style.display = form.style.display === 'none' ? 'block' : 'none';
        }
        loadBugs();
    </script>
</body>
</html>
"""

todo_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Drone Commander - WIP</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>body{background:#121212; color:#fff; text-align:center; padding-top:20%;}</style>
</head>
<body>
    <h1>{{ title }}</h1>
    <p>Module offline. Awaiting deployment.</p>
    <a href="/" class="btn btn-outline-light">Return to Command</a>
</body>
</html>
"""

# --- EXECUTION ---

# Create templates directory
if not os.path.exists('templates'):
    os.makedirs('templates')
    print("✅ Created: templates/ directory")

# Create files
create_file('requirements.txt', requirements_txt)
create_file('app.py', app_py)
create_file('templates/landing.html', landing_html)
create_file('templates/reporter.html', reporter_html)
create_file('templates/todo.html', todo_html)

print("\n🚀 Drone Commander Project Created!")
print("Run 'pip install -r requirements.txt' then 'python app.py'")