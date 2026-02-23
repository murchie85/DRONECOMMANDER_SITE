import os
from flask import Flask, render_template, request, jsonify, Response, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from markupsafe import escape

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

BOARD_CATEGORIES = ['General', 'Lore', 'Suggestions', 'GameChat']
MAX_POSTS_PER_DAY = 30
MAX_POSTS_PER_USER_PER_DAY = 4
POST_RETENTION_DAYS = 30

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(30), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    replies = db.relationship('Post', backref=db.backref('parent', remote_side=[id]),
                              lazy='dynamic', order_by='Post.timestamp.asc()')

def prune_old_posts():
    cutoff = datetime.utcnow() - timedelta(days=POST_RETENTION_DAYS)
    Post.query.filter(Post.timestamp < cutoff).delete()
    db.session.commit()

def check_throttle(username):
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    global_count = Post.query.filter(Post.timestamp >= today).count()
    if global_count >= MAX_POSTS_PER_DAY:
        return 'The board has reached its daily post limit. Try again tomorrow.'
    user_count = Post.query.filter(Post.timestamp >= today, Post.username == username).count()
    if user_count >= MAX_POSTS_PER_USER_PER_DAY:
        return f'Username "{username}" has reached its daily limit ({MAX_POSTS_PER_USER_PER_DAY} posts). Try again tomorrow.'
    return None

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
    pages = ['/', '/about', '/devlog', '/latest-update', '/compendium', '/community-tools', '/bug-reporter', '/board']
    base = request.host_url.rstrip('/')
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for page in pages:
        xml += f'  <url><loc>{base}{page}</loc></url>\n'
    xml += '</urlset>'
    return Response(xml, mimetype='application/xml')

# BOARD ROUTES
@app.route('/board')
def board():
    with app.app_context():
        prune_old_posts()
    counts = {}
    for cat in BOARD_CATEGORIES:
        counts[cat] = Post.query.filter_by(category=cat, parent_id=None).count()
    return render_template('board.html', categories=BOARD_CATEGORIES, counts=counts)

@app.route('/board/<category>')
def board_category(category):
    if category not in BOARD_CATEGORIES:
        return redirect(url_for('board'))
    threads = Post.query.filter_by(category=category, parent_id=None)\
        .order_by(Post.timestamp.desc()).limit(100).all()
    return render_template('board_category.html', category=category, threads=threads)

@app.route('/board/<category>/thread/<int:thread_id>')
def board_thread(category, thread_id):
    if category not in BOARD_CATEGORIES:
        return redirect(url_for('board'))
    thread = Post.query.get_or_404(thread_id)
    replies = Post.query.filter_by(parent_id=thread_id).order_by(Post.timestamp.asc()).all()
    return render_template('board_thread.html', category=category, thread=thread, replies=replies)

@app.route('/board/<category>/new', methods=['POST'])
def board_new_thread(category):
    if category not in BOARD_CATEGORIES:
        return redirect(url_for('board'))
    username = request.form.get('username', '').strip()[:50] or 'Anonymous Pilot'
    message = request.form.get('message', '').strip()[:2000]
    if not message:
        return redirect(url_for('board_category', category=category))
    error = check_throttle(username)
    if error:
        threads = Post.query.filter_by(category=category, parent_id=None)\
            .order_by(Post.timestamp.desc()).limit(100).all()
        return render_template('board_category.html', category=category, threads=threads, error=error)
    post = Post(username=username, message=message, category=category)
    db.session.add(post)
    db.session.commit()
    return redirect(url_for('board_category', category=category))

@app.route('/board/<category>/thread/<int:thread_id>/reply', methods=['POST'])
def board_reply(category, thread_id):
    if category not in BOARD_CATEGORIES:
        return redirect(url_for('board'))
    thread = Post.query.get_or_404(thread_id)
    username = request.form.get('username', '').strip()[:50] or 'Anonymous Pilot'
    message = request.form.get('message', '').strip()[:2000]
    if not message:
        return redirect(url_for('board_thread', category=category, thread_id=thread_id))
    error = check_throttle(username)
    if error:
        replies = Post.query.filter_by(parent_id=thread_id).order_by(Post.timestamp.asc()).all()
        return render_template('board_thread.html', category=category, thread=thread, replies=replies, error=error)
    reply = Post(username=username, message=message, category=category, parent_id=thread_id)
    db.session.add(reply)
    db.session.commit()
    return redirect(url_for('board_thread', category=category, thread_id=thread_id))

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