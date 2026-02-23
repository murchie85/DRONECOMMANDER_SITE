#!/usr/bin/env python3
"""
Scrape a public Patreon post and output its content + download image.

Usage:
    python scrape_patreon.py <post_id_or_url>

Examples:
    python scrape_patreon.py 151416678
    python scrape_patreon.py https://www.patreon.com/posts/meet-ryn-ghost-151416678
"""
import sys
import re
import json
import urllib.request
import os

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

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    post_id = extract_post_id(sys.argv[1])
    if not post_id:
        print(f'Error: Could not extract post ID from "{sys.argv[1]}"')
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
        'image': filename if img_url else None,
        'likes': attrs.get('like_count', 0)
    }
    json_file = f'/tmp/patreon_post_{post_id}.json'
    with open(json_file, 'w') as f:
        json.dump(output, f, indent=2)
    print(f'JSON saved: {json_file}')

if __name__ == '__main__':
    main()
