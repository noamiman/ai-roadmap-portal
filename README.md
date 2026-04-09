# AI Learning Roadmap Portal

A Hebrew AI learning portal generated from JSON data into a static website.

## Features

- Data-driven content from `data.json`
- Static site generation via `build_site.py`
- Clean UI template in `templates/base.html`
- Floating creators panel
- "Seen tutorial" markers saved in browser localStorage

## Project Structure

- `build_site.py` - static site generator and watch mode
- `data.json` - all sections, guides, and tools
- `templates/base.html` - HTML template, CSS, and client-side JS
- `index.html` - generated deploy-ready output file
- `favicon.svg` - site icon
- `requirements.txt` - Python dependencies
- `sample_data.csv` - sample data import format

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Build

Generate the site:

```bash
python build_site.py
```

Output:

- `index.html`

Watch mode (auto rebuild on file changes):

```bash
python build_site.py --watch
```

## Content Editing

Edit `data.json`, then rebuild:

```bash
python build_site.py
```

## Deploy

This project is static and can be deployed to:

- Netlify
- GitHub Pages
- Vercel (static)
- Any static hosting service

### Netlify (recommended)

- Connect your GitHub repo
- Publish directory: `.`
- Build command: leave empty if `index.html` is committed

## GitHub Push

```bash
git add .
git commit -m "Update content"
git push
```

## Notes

- `venv/` and `__pycache__/` are ignored by `.gitignore`.
- Seen markers are per browser/device because they use localStorage.
