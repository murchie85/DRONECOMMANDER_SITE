# Drone Commander — Command Center

The official web hub for **Drone Commander**, a sci-fi game blending **Visual Novel** storytelling with **RTS strategy** and **RPG exploration**. Command drones, build alliances, and shape the fate of the galaxy.

**Live site:** [dronecommander.gg](https://dronecommander.gg)

---

# 🚨 BANDWIDTH RULES — READ BEFORE ADDING ANY IMAGE OR ASSET 🚨

> **In August 2026 this site got SUSPENDED by Render for blowing through the 5 GB/month free bandwidth cap.** The cause: giant unoptimized PNGs (one character portrait was 8.9 MB at 4800×4800, displayed at 280px). Just ~200 compendium visits burned the whole month's quota. Everything below exists so that never happens again. **Do not undo it.**

## The Iron Rules

1. **Every image must be ≤ ~300 KB.** Use **WebP** (or JPEG for photos/OG images). Never commit a raw PNG export.
2. **Resize to display size.** Portraits show at 280px wide → save at ~800px max (2–3× retina headroom). Full-width art → 1600px max.
3. **Lazy-load everything below the fold:** `<img loading="lazy" decoding="async" ...>`. Only above-the-fold heroes load eagerly.
4. **Never replace an image keeping the same filename** — assets are cached for 30 days (`SEND_FILE_MAX_AGE_DEFAULT` in `app.py`). New art = new filename + updated template reference.
5. **OG/link-preview image stays JPEG** (`assets/img/cover.jpg`) — WebP breaks some platforms' preview cards.
6. **Video/audio never gets served from Render.** Embed YouTube; game downloads live on itch.io/Steam.

## The Guardrails (already in place — keep them)

| Guardrail | Where | What it does |
|-----------|-------|--------------|
| Pre-commit size gate | `.git/hooks/pre-commit` (local only, **recreate if you re-clone**) | Blocks any commit containing a file > 500 KB. Override only deliberately with `git commit --no-verify` |
| WebP + right-sizing | `assets/img/` | Aug 2026 pass took the site from 25.3 MB → 2.1 MB of images (Rexalia: 8.9 MB → 80 KB) |
| Lazy loading | all templates | Visitors only download images they scroll to |
| 30-day asset caching | `app.py` `SEND_FILE_MAX_AGE_DEFAULT` | Browsers/CDNs stop re-downloading unchanged assets |
| gzip/brotli HTML | `flask-compress` in `app.py` | Compendium HTML: 357 KB → 95 KB over the wire |
| Cloudflare (free plan) | DNS: `emerie`/`ethan.ns.cloudflare.com`, domain at Porkbun | Proxies all traffic, caches `/assets/*` at the edge with **unmetered** bandwidth — cached hits never touch Render's meter. SSL mode: Full (strict). **Do NOT enable "Cache Everything"** (would cache HTML and delay content updates) |

## Billing setup (Aug 2026)

- **Render Hobby plan + card on file** — 5 GB/month free, then metered at **$0.15/GB**. There is **no spend cap on Render** — protection comes from the layers above plus the payment card:
- The card on file is a **Revolut virtual card with a limited balance** — worst case a charge declines and the site suspends again; no scary bill is possible.
- **Do not upgrade to Pro for bandwidth** — $25/month buys only 20 GB more included (= $3 of overage). Pro is for teams, not bandwidth.
- Deploys **do not auto-trigger while suspended** — after unsuspending, push a commit (or Manual Deploy in the dashboard) to ship anything pushed during the suspension.
- Check **Render Dashboard → Billing → Included Usage** occasionally; Render also emails as usage climbs.

---

## Pages

| Route | Description |
|-------|-------------|
| `/` | Landing page — background video, bottom dock nav |
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
