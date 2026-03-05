#!/usr/bin/env python3
"""
Scrape a public Patreon post, download its image, and inject into latest_update.html.

Usage:
    python scrape_patreon.py <post_id_or_url>
    python scrape_patreon.py --inject /tmp/patreon_post_12345.json   # re-inject from saved JSON
    python scrape_patreon.py --no-inject <post_id_or_url>            # scrape only, skip inject

Examples:
    python scrape_patreon.py 151416678
    python scrape_patreon.py https://www.patreon.com/posts/meet-ryn-ghost-151416678
"""
import sys
import re
import json
import urllib.request
import os
from datetime import datetime
from html import escape

TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'templates', 'latest_update.html')
START_MARKER = '<!-- SCRAPED-POST-START -->'
END_MARKER = '<!-- SCRAPED-POST-END -->'


def extract_post_id(arg):
    """Extract numeric post ID from a URL or raw ID."""
    match = re.search(r'(\d{6,})', arg)
    if match:
        return match.group(1)
    return None


def extract_text(node):
    """Recursively extract text from Patreon's JSON content format."""
    text = ''
    node_type = node.get('type', '')

    if node_type == 'paragraph':
        for child in node.get('content', []):
            if child.get('type') == 'text':
                t = child.get('text', '')
                marks = child.get('marks', [])
                for m in marks:
                    if m.get('type') == 'bold':
                        t = f'**{t}**'
                    elif m.get('type') == 'italic':
                        t = f'*{t}*'
                text += t
        text += '\n\n'
    elif node_type == 'heading':
        level = node.get('attrs', {}).get('level', 2)
        heading_text = ''
        for child in node.get('content', []):
            if child.get('type') == 'text':
                heading_text += child.get('text', '')
        text = '#' * level + ' ' + heading_text + '\n\n'

    for child in node.get('content', []):
        if isinstance(child, dict) and child.get('type') not in ('text',):
            text += extract_text(child)

    return text


def fetch_post(post_id):
    """Fetch post data from Patreon's API."""
    url = f'https://www.patreon.com/api/posts/{post_id}'
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
    })
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())


def content_to_html(content):
    """Convert scraped markdown-ish content into HTML cards.

    Returns a list of HTML card strings.  Splits on **bold headings** to
    create separate cards for each section (e.g. "Currently working on").
    """
    # Split content into sections by **bold heading** lines
    # Pattern: a block that is just **heading text**
    parts = re.split(r'\n\n\s*\*\*(.+?)\*\*\s*(?:\n\n|$)', content.strip())

    cards_html = []

    # --- First section (before any bold heading) ---
    intro_blocks = [b.strip() for b in parts[0].split('\n\n') if b.strip()]
    intro_paras = []
    intro_items = []
    for block in intro_blocks:
        block = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', escape(block)
                        .replace('&lt;strong&gt;', '<strong>')
                        .replace('&lt;/strong&gt;', '</strong>'))
        # Heuristic: short lines without ending punctuation are list items
        if len(block) < 120 and not block.rstrip().endswith(('.', '!', '?')):
            intro_items.append(block)
        else:
            intro_paras.append(block)

    items_html = ''
    if intro_items:
        li = '\n'.join(f'                <li><strong>{it}</strong></li>'
                       for it in intro_items)
        items_html = f'\n            <ul>\n{li}\n            </ul>'

    paras_html = '\n'.join(f'            <p>{p}</p>' for p in intro_paras)
    if paras_html or items_html:
        cards_html.append(f'{paras_html}{items_html}')

    # --- Subsequent sections (heading + content pairs) ---
    for i in range(1, len(parts), 2):
        heading = parts[i]
        body = parts[i + 1] if i + 1 < len(parts) else ''
        lines = [l.strip() for l in body.split('\n\n') if l.strip()]

        items = []
        paras = []
        for line in lines:
            line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>',
                          escape(line)
                          .replace('&lt;strong&gt;', '<strong>')
                          .replace('&lt;/strong&gt;', '</strong>'))
            if len(line) < 120 and not line.rstrip().endswith(('.', '!', '?')):
                items.append(line)
            else:
                paras.append(line)

        is_wip = any(kw in heading.lower()
                     for kw in ['working on', 'in progress', 'upcoming', 'next'])
        border = ' style="border-color: rgba(255,204,0,0.3);"' if is_wip else ''
        h3_style = ' style="color: #ffcc00;"' if is_wip else ''

        body_parts = '\n'.join(f'            <p>{p}</p>' for p in paras)
        if items:
            li = '\n'.join(f'                <li>{it}</li>' for it in items)
            body_parts += f'\n            <ul>\n{li}\n            </ul>'

        cards_html.append(
            f'<div class="update-card"{border}>\n'
            f'            <h3{h3_style}>{escape(heading)}</h3>\n'
            f'{body_parts}\n'
            f'        </div>'
        )

    return cards_html


def inject_latest_update(post_data):
    """Replace content between markers in latest_update.html with new post."""
    with open(TEMPLATE_PATH, 'r') as f:
        html = f.read()

    if START_MARKER not in html or END_MARKER not in html:
        print(f'ERROR: Markers not found in {TEMPLATE_PATH}')
        print(f'  Expected {START_MARKER} and {END_MARKER}')
        sys.exit(1)

    # Parse date for display
    try:
        dt = datetime.strptime(post_data['date'], '%Y-%m-%d')
        date_display = dt.strftime('%B %d, %Y').upper()
        month_year = dt.strftime('%b %Y')
    except (ValueError, KeyError):
        date_display = post_data.get('date', 'UNKNOWN').upper()
        month_year = post_data.get('date', '')

    title = post_data.get('title', 'Update')

    # Build image HTML
    image_block = ''
    if post_data.get('image'):
        image_block = (
            '            <div style="text-align: center; margin-bottom: 20px;">\n'
            f'                <a href="{post_data.get("url", "#")}" target="_blank" rel="noopener">\n'
            f'                    <img src="/{post_data["image"]}" alt="{escape(title)}"'
            ' style="max-width: 100%; border-radius: 8px;'
            ' border: 1px solid rgba(0,255,204,0.3);'
            ' box-shadow: 0 0 20px rgba(0,255,204,0.1);">\n'
            '                </a>\n'
            '            </div>\n'
        )

    # Convert content to HTML cards
    cards = content_to_html(post_data.get('content', ''))

    # Build the first card (intro with image)
    first_card_body = cards[0] if cards else ''
    intro_card = (
        '        <div class="update-card">\n'
        f'            <p style="color:#00ffcc; font-size: 0.8rem; margin-bottom: 14px;">'
        f'{date_display}</p>\n'
        f'{image_block}'
        f'{first_card_body}\n'
        '        </div>'
    )

    # Additional cards (from bold-heading sections)
    extra_cards = '\n\n        '.join(cards[1:]) if len(cards) > 1 else ''

    # Assemble the full replacement block
    section_title = f'        <h2 class="section-title">// {escape(title)} &mdash; {month_year}</h2>'
    new_content = f'{START_MARKER}\n{section_title}\n{intro_card}'
    if extra_cards:
        new_content += f'\n\n        {extra_cards}'
    new_content += f'\n        {END_MARKER}'

    # Replace between markers
    pattern = re.compile(
        re.escape(START_MARKER) + r'.*?' + re.escape(END_MARKER),
        re.DOTALL
    )
    html = pattern.sub(new_content, html)

    with open(TEMPLATE_PATH, 'w') as f:
        f.write(html)

    print(f'\nInjected into {TEMPLATE_PATH}')
    print(f'  Title: {title}')
    print(f'  Date:  {date_display}')
    print(f'  Image: {post_data.get("image", "none")}')


def main():
    skip_inject = '--no-inject' in sys.argv
    inject_only = '--inject' in sys.argv

    args = [a for a in sys.argv[1:] if not a.startswith('--')]

    # --inject mode: load JSON and inject, no scraping
    if inject_only:
        if not args:
            print('Usage: python scrape_patreon.py --inject <json_file>')
            sys.exit(1)
        json_file = args[0]
        with open(json_file, 'r') as f:
            post_data = json.load(f)
        print(f'Loaded {json_file}')
        inject_latest_update(post_data)
        return

    if not args:
        print(__doc__)
        sys.exit(1)

    post_id = extract_post_id(args[0])
    if not post_id:
        print(f'Error: Could not extract post ID from "{args[0]}"')
        sys.exit(1)

    print(f'Fetching post {post_id}...')
    data = fetch_post(post_id)
    attrs = data['data']['attributes']

    title = attrs.get('title', 'Untitled')
    date = attrs.get('published_at', 'Unknown')[:10]
    image_url = None
    if attrs.get('image'):
        image_url = attrs['image'].get('url')
    post_file_url = None
    if attrs.get('post_file'):
        post_file_url = attrs['post_file'].get('url')

    # Extract text content
    content_text = ''
    if attrs.get('content_json_string'):
        content_json = json.loads(attrs['content_json_string'])
        content_text = extract_text(content_json).strip()
    elif attrs.get('content'):
        content_text = attrs['content']

    # Print summary
    print(f'\nTitle: {title}')
    print(f'Date:  {date}')
    print(f'URL:   {attrs.get("url", "N/A")}')
    print(f'Likes: {attrs.get("like_count", 0)}')
    print(f'Image: {image_url or "None"}')
    print(f'\n--- Content ---\n')
    print(content_text)

    # Download image if available
    img_url = post_file_url or image_url
    filename = None
    if img_url:
        ext = '.jpeg' if 'jpeg' in img_url or 'jpg' in img_url else '.png'
        safe_title = re.sub(r'[^a-zA-Z0-9]+', '_', title).strip('_').lower()
        filename = f'assets/img/{safe_title}{ext}'
        os.makedirs('assets/img', exist_ok=True)

        print(f'\nDownloading image to {filename}...')
        req = urllib.request.Request(img_url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
        })
        with urllib.request.urlopen(req, timeout=30) as resp:
            with open(filename, 'wb') as f:
                f.write(resp.read())
        print(f'Saved: {filename}')

    # Save content as JSON for easy re-use
    output = {
        'title': title,
        'date': date,
        'url': attrs.get('url', ''),
        'content': content_text,
        'image': filename,
        'likes': attrs.get('like_count', 0)
    }
    json_file = f'/tmp/patreon_post_{post_id}.json'
    with open(json_file, 'w') as f:
        json.dump(output, f, indent=2)
    print(f'JSON saved: {json_file}')

    # Inject into latest_update.html
    if not skip_inject:
        inject_latest_update(output)
    else:
        print('\nSkipped injection (--no-inject)')


if __name__ == '__main__':
    main()
