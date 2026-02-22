# Drone Commander Hub

## Project Overview
Flask web app serving as a "Command Center" for the Drone Commander game — a sci-fi Visual Novel, RTS and RPG. Features a bug reporter, development log, compendium wiki, and community tools hub with a retro-futuristic cyber-glow UI.

## Tech Stack
- **Backend:** Python 3.9, Flask, Flask-SQLAlchemy
- **Database:** SQLite (default `instance/bugs.db`), configurable via `DATABASE_URL` env var
- **Frontend:** Bootstrap 5, inline CSS with custom "cyber-glow" theme, Courier New monospace font
- **Production server:** Gunicorn (4 workers, port 8000)
- **Containerization:** Docker

## Project Structure
```
app.py              # Flask app — routes, Bug model, REST API, SEO routes
requirements.txt    # flask, flask-sqlalchemy, gunicorn
Dockerfile          # Python 3.9-slim, gunicorn production image
backup.sh           # Zip backup script (outputs to parent directory)
instance/bugs.db    # SQLite database (gitignored data)
templates/
  landing.html      # Landing page — floating title, bottom dock nav, YouTube bg video
  about.html        # About page — game overview, screenshots, developer bio, community stats
  devlog.html       # Development log — timeline entries Dec 2025 - Feb 2026
  latest_update.html # Latest update — current progress and roadmap
  compendium.html   # Compendium — full game lore: species, factions, characters, science
  community_tools.html # Community tools hub — links to bug reporter, uploaders
  reporter.html     # Bug reporter form + log table
  todo.html         # Placeholder page for unfinished features
assets/
  audio/DCThemeV2.mp3 # Theme music with play/pause toggle
  img/dcBg.png      # Background image (Fel/Straker artwork)
  css/style.css     # Stylesheet (currently minimal, most CSS is inline)
```

## Key Routes
| Route              | Purpose                        |
|--------------------|--------------------------------|
| `/`                | Landing page (command center)  |
| `/about`           | About the game                 |
| `/devlog`          | Development log                |
| `/latest-update`   | Latest development update      |
| `/compendium`      | Game lore compendium           |
| `/community-tools` | Community tools hub            |
| `/bug-reporter`    | Bug reporter UI                |
| `/robots.txt`      | SEO crawler directives         |
| `/sitemap.xml`     | SEO sitemap                    |

## API Endpoints
| Endpoint             | Method | Description              |
|----------------------|--------|--------------------------|
| `/api/bugs`          | GET    | List all bugs (desc)     |
| `/api/bugs`          | POST   | Submit a bug (JSON body) |
| `/api/bugs/<int:id>` | DELETE | Delete a bug by ID       |

## Development
```bash
pip install -r requirements.txt
FLASK_DEBUG=true python app.py    # runs on http://127.0.0.1:5000
```

## Docker
```bash
docker build -t drone-commander-hub .
docker run -d -p 8000:8000 drone-commander-hub
```

## Backup
```bash
bash backup.sh    # creates dated zip in parent directory
```

## Conventions
- Single-file Flask app (`app.py`) — no blueprints yet
- Templates use inline `<style>` blocks rather than external CSS
- Color scheme: `#00ffcc` glow on dark `#121212` background
- All pages have SEO meta tags (description, Open Graph, Twitter Card)
- `make_project.py` was used to scaffold the project; safe to ignore
