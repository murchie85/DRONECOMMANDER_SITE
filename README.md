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
| `/api/waitlist` | POST | Join the map editor waitlist (JSON: `name`, `patreon_id`) |

### Example POST

```json
{
    "bug_type": "RPG",
    "description": "Healing drone fails to target lowest-HP unit",
    "submitter": "AlphaTester",
    "blocking": true
}
```

## Waitlist (Map Editor Prototype)

The waitlist form at the top of `/community-tools` stores signups in a **Google Sheet** — Render's free tier has an ephemeral filesystem, so anything written locally (including the SQLite db) is wiped on every redeploy. Entries go to Google instead.

**How it works:** the on-site form POSTs to `/api/waitlist` (Flask), which forwards the entry server-side to a hidden **Google Form** whose responses land in a linked Google Sheet (with automatic timestamps). Visitors never see or get redirected to the Google Form — it's just a free write-only API into the sheet. This route was chosen over an Apps Script webhook because Apps Script needed an OAuth grant that Google hard-blocked.

**Configuration** — three env vars, set on Render (Dashboard → service → Environment), none stored in the repo:

| Env var | Value |
|---------|-------|
| `WAITLIST_FORM_URL` | The Google Form's URL with `/viewform` replaced by `/formResponse` |
| `WAITLIST_ENTRY_NAME` | Form field id for Name (e.g. `entry.858741395`) |
| `WAITLIST_ENTRY_PATREON` | Form field id for Patreon ID (e.g. `entry.814813313`) |

If the env vars are unset, submissions get a friendly "Waitlist is not open yet" response — safe to deploy in any order. There's also a legacy fallback (`WAITLIST_WEBHOOK_URL`) for an Apps Script web-app URL, unused.

**To add a form field (e.g. OS):**

1. Add a Short-answer question to the Google Form (form must stay **published**, responder access **"Anyone with the link"** — requiring sign-in breaks server submissions).
2. Find its `entry.NNNN` id: **⋮ → Pre-fill form**, fill dummy values, **Get link** — the id is in the copied URL. (Or fetch the `/viewform` HTML and look in `FB_PUBLIC_LOAD_DATA_`.)
3. Add an `<input>` in the waitlist form in `templates/community_tools.html` and include it in the `fetch` body in the same file's script block.
4. In `app.py` (`add_waitlist`), read the new field and add it to the `requests.post` data dict with a new `WAITLIST_ENTRY_*` env var.
5. Set the new env var on Render.

**To test end-to-end:**

```bash
curl -X POST https://dronecommander.gg/api/waitlist \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","patreon_id":"TEST-001"}'
# → {"message": "Submitted for Patreon ID TEST-001"} + a new row in the sheet
```

⚠️ Keep the Google Form URL private — anyone who has it can append rows (though they can't read the sheet).

## Links

- [Patreon](https://www.patreon.com/DroneCommander)
- [itch.io](https://murchie85.itch.io/drone-commander)
- [YouTube](https://www.youtube.com/@McMurchie)
- [Reddit](https://www.reddit.com/r/DroneCommander/)
- [X / Twitter](https://x.com/OmegaStormX)
