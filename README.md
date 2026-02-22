# Drone Commander — Command Center

The official web hub for **Drone Commander**, a sci-fi game blending **Visual Novel** storytelling with **RTS strategy** and **RPG exploration**. Command drones, build alliances, and shape the fate of the galaxy.

**Live site:** [dronecommander.gg](https://dronecommander.gg)

---

## Pages

| Route | Description |
|-------|-------------|
| `/` | Landing page — background video, bottom dock nav, audio toggle |
| `/about` | Game overview, genre pillars, screenshots, developer bio, community stats |
| `/devlog` | Development timeline — Dec 2025 to Feb 2026 |
| `/latest-update` | Current progress, highlights, and roadmap |
| `/compendium` | Full game lore — species, factions, characters, science, Sekarri & Vionite lore |
| `/community-tools` | Hub linking to bug reporter, script uploader, map uploader |
| `/bug-reporter` | Report and track bugs across RPG, RTS, VN and system components |

## Tech Stack

- **Backend:** Python 3.9, Flask, Flask-SQLAlchemy
- **Database:** SQLite (configurable via `DATABASE_URL` env var)
- **Frontend:** Bootstrap 5, inline CSS with "cyber-glow" theme (#00ffcc on #121212)
- **Production:** Gunicorn (4 workers), Docker
- **Hosting:** Render.com
- **SEO:** Meta descriptions, Open Graph, Twitter Cards, JSON-LD, sitemap.xml, robots.txt

## Local Development

```bash
pip install -r requirements.txt
FLASK_DEBUG=true python app.py
# → http://127.0.0.1:5000
```

## Docker

```bash
docker build -t drone-commander .
docker run -d -p 8000:8000 drone-commander
```

## Backup

```bash
bash backup.sh
# Creates a dated zip in the parent directory
```

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/bugs` | GET | List all bugs (newest first) |
| `/api/bugs` | POST | Submit a bug (JSON body) |
| `/api/bugs/<id>` | DELETE | Delete a bug by ID |

### Example POST

```json
{
    "bug_type": "RPG",
    "description": "Healing drone fails to target lowest-HP unit",
    "submitter": "AlphaTester",
    "blocking": true
}
```

## Links

- [Patreon](https://www.patreon.com/DroneCommander)
- [itch.io](https://murchie85.itch.io/drone-commander)
- [YouTube](https://www.youtube.com/@McMurchie)
- [Reddit](https://www.reddit.com/r/DroneCommander/)
- [X / Twitter](https://x.com/OmegaStormX)
