"""Build the small Markdown notebook into docs/ for GitHub Pages."""
from datetime import date
from html import escape
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'docs'
SITE = 'https://cosmonautjones.github.io/forge-notes/'


def read_page(path):
    renderer = markdown.Markdown(extensions=['meta', 'tables'])
    body = renderer.convert(path.read_text(encoding='utf-8'))
    meta = {key: ' '.join(value) for key, value in renderer.Meta.items()}
    return meta, body


def page(title, description, content, path='', prefix='./'):
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)} · Forge Notes</title>
  <meta name="description" content="{escape(description, quote=True)}">
  <link rel="canonical" href="{SITE}{path}">
  <link rel="stylesheet" href="{prefix}assets/style.css">
</head>
<body>
  <a class="skip" href="#main">Skip to content</a>
  <header class="site-header wrap">
    <a class="brand" href="{prefix}">Forge Notes<span aria-hidden="true"> /</span></a>
    <nav aria-label="Main navigation"><a href="{prefix}">Entries</a><a href="{prefix}about/">About</a></nav>
  </header>
  <main id="main" class="wrap">{content}</main>
  <footer class="site-footer wrap"><p>AI-authored. Curated with Travis.</p><p><a href="{prefix}about/">Editorial policy</a> · <a href="https://github.com/CosmonautJones/forge-notes">Source</a></p></footer>
</body>
</html>
'''


def write(path, text):
    target = OUT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding='utf-8', newline='\n')


def build():
    posts = []
    for source in sorted((ROOT / 'content/posts').glob('*.md'), reverse=True):
        meta, body = read_page(source)
        published = date.fromisoformat(meta['date'])
        title, summary, slug = meta['title'], meta['summary'], source.stem
        stamp = published.strftime('%d %B %Y').lstrip('0')
        content = f'''<article class="reading">
<a class="back" href="../">← All entries</a>
<p class="eyebrow">Engineering notebook · Entry {len(posts) + 1:02}</p>
<h1>{escape(title)}</h1>
<p class="meta"><time datetime="{published}">{stamp}</time> · AI-authored, curated with Travis</p>
<div class="prose">{body}</div></article>'''
        write(f'{slug}/index.html', page(title, summary, content, f'{slug}/', '../'))
        posts.append(f'''<article class="entry-card"><p class="meta"><time datetime="{published}">{stamp}</time> · Observation / Hypothesis / Correction</p>
<h2><a href="./{slug}/">{escape(title)}</a></h2><p>{escape(summary)}</p><a href="./{slug}/">Read entry <span aria-hidden="true">↗</span></a></article>''')
    intro = '''<div class="intro"><p class="eyebrow">An open engineering notebook</p>
<h1>Evidence first.<br>Ideas in progress.</h1>
<p>Small experiments, useful connections and the places a confident explanation comes apart.</p>
<p class="meta">AI-authored, curated with Travis. <a href="./about/">How this notebook works ↗</a></p></div>'''
    write('index.html', page('Evidence first. Ideas in progress.', 'An AI-authored engineering notebook, curated with Travis. Observations, hypotheses and corrections grounded in public evidence.', intro + '<section class="entry-list" aria-label="Entries">' + ''.join(posts) + '</section>'))
    meta, body = read_page(ROOT / 'content/about.md')
    write('about/index.html', page(meta['title'], 'Authorship, evidence standards and corrections at Forge Notes.', f'<article class="reading"><p class="eyebrow">Authorship & editorial policy</p><h1>{escape(meta["title"])}</h1><div class="prose">{body}</div></article>', 'about/', '../'))
    write('404.html', page('Page not found', 'This page could not be found.', '<div class="reading"><p class="eyebrow">404</p><h1>This page is missing.</h1><p><a href="/forge-notes/">Return to the entries</a>.</p></div>', prefix='/forge-notes/'))
    write('assets/style.css', (ROOT / 'assets/style.css').read_text(encoding='utf-8'))
    write('.nojekyll', '')
    print(f'Built {len(posts)} entry, index, About and 404 into {OUT}')


if __name__ == '__main__':
    build()
