# AI Roadmap Project

A curated AI learning portal in Hebrew, generated from JSON data into a static HTML site.

## What This Project Includes

- Static site generator in Python (`build_site.py`)
- Data-driven content source (`data.json`)
- Jinja2 template (`templates/base.html`)
- Generated site output (`ai_full_roadmap.html`)
- Floating creators panel and tutorial "seen" markers (saved in browser localStorage)

## Quick Start

### 1. Create and activate virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Build the site

```bash
python build_site.py
```

Output file:

- `ai_full_roadmap.html`

### 4. Auto rebuild on changes (watch mode)

```bash
python build_site.py --watch
```

## Project Structure

- `build_site.py` - main generator and watch mode
- `data.json` - all sections, guides, tools, creators
- `templates/base.html` - page structure, styles, scripts
- `favicon.svg` - tab icon
- `sample_data.csv` - sample import format
- `requirements.txt` - Python dependencies

## Editing Content

Most updates should be made in `data.json`:

- Add/edit sections
- Add guides and tools
- Add creators list

After editing, run:

```bash
python build_site.py
```

## Deploy

This is a static site. You can deploy `ai_full_roadmap.html` and related assets directly.

### Simple options

- GitHub Pages
- Netlify
- Vercel (static)
- Any static web server

## Push to GitHub

If not already connected to a remote:

```bash
git init
git add .
git commit -m "Initial commit: AI roadmap portal"
git branch -M main
git remote add origin <YOUR_REPO_URL>
git push -u origin main
```

## Notes

- `venv/` and `__pycache__/` are ignored via `.gitignore`.
- Seen tutorial marks are stored in browser `localStorage`, per browser/device.
