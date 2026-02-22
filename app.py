import os
from flask import Flask, render_template, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__, static_folder='assets', static_url_path='/assets')

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
    return render_template('latest_update.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/devlog')
def devlog():
    return render_template('devlog.html')

@app.route('/community-tools')
def community_tools():
    return render_template('community_tools.html')

@app.route('/compendium')
def compendium():
    return render_template('compendium.html')

@app.route('/robots.txt')
def robots():
    content = """User-agent: *
Allow: /
Sitemap: /sitemap.xml
"""
    return Response(content, mimetype='text/plain')

@app.route('/sitemap.xml')
def sitemap():
    pages = ['/', '/about', '/devlog', '/latest-update', '/compendium', '/community-tools', '/bug-reporter']
    base = request.host_url.rstrip('/')
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for page in pages:
        xml += f'  <url><loc>{base}{page}</loc></url>\n'
    xml += '</urlset>'
    return Response(xml, mimetype='application/xml')

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
    app.run(debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true')