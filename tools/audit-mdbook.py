#!/usr/bin/env python3
"""Audit the generated mdBook sources and final staged Pages tree.

This is *not* the LaTeX parser. It validates the published artifacts, catches
orphaned links/resources and unexpected changes to the generated site structure.
"""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


class Links(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.links = []

    def handle_starttag(self, tag, attrs):
        fields = dict(attrs)
        if fields.get('id'):
            self.ids.add(fields['id'])
        if tag == 'a' and fields.get('href') is not None:
            self.links.append(('href', fields['href']))
        if tag in ('script', 'img') and fields.get('src') is not None:
            self.links.append(('src', fields['src']))
        if tag == 'link' and fields.get('rel', '').lower() == 'stylesheet' and fields.get('href') is not None:
            self.links.append(('href', fields['href']))


def parse_markup(path):
    parser = Links()
    parser.feed(path.read_text(encoding='utf-8'))
    return parser


def skip_url(raw):
    u = urlsplit(raw)
    return bool(u.scheme or u.netloc or raw.startswith('//'))


def target_of(base, raw, root):
    u = urlsplit(raw)
    if skip_url(raw):
        return None
    path = unquote(u.path)
    if '\\' in path or '\x00' in path:
        raise ValueError(f'Unsafe path: {raw}')
    if path.startswith('/diabat-manual/'):
        # mdBook site-url can produce root-relative URLs on the Pages site.
        resolved = (root / path.removeprefix('/diabat-manual/')).resolve()
    elif path == '/diabat-manual':
        resolved = (root / 'index.html').resolve()
    else:
        resolved = ((base.parent / path) if path else base).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError(f'Link escapes generated tree: {base}: {raw}')
    if resolved.is_dir():
        resolved /= 'index.html'
    return resolved, unquote(u.fragment)


def audit_sources(book, report):
    src = book / 'src'
    summary = src / 'SUMMARY.md'
    if not summary.is_file():
        raise ValueError('Missing generated SUMMARY.md')
    data = json.loads(report.read_text(encoding='utf8'))
    stats = data['statistics']
    pages = list(src.glob('*.md'))
    if stats['pages'] < 12 or len(pages) < 12:
        raise ValueError(f'Suspiciously small online Manual ({len(pages)} pages)')
    if stats['resolved_links'] < 200:
        raise ValueError(f'Suspiciously few links ({stats["resolved_links"]})')
    for key in ('keywords','overview_items','script_labels','example_labels','original_input_files','references_used'):
        if not isinstance(stats[key], int) or stats[key] < 1:
            raise ValueError(f'Missing or invalid conversion metric: {key}')
    for required in ('diabat.css','diabat-highlight.js','references.md','example-inputs.md', 'diabatization.md'):
        if not (src / required).is_file():
            raise ValueError(f'Missing generated resource: src/{required}')
    for key, location in data['labels'].items():
        dest = src / location['page']
        if not dest.is_file():
            raise ValueError(f'Report label points to a missing page: {key}: {dest}')
    anchor_cache = {}
    checked = 0
    for page in pages:
        content = page.read_text(encoding='utf8')
        if 'L"owdin' in content:
            raise ValueError(f'Unconverted LaTeX diaeresis in {page.name}: L"owdin; fix latex2md before publishing')
        parser = parse_markup(page)
        anchor_cache[page.resolve()] = parser.ids
        # This is validation of converter-owned Markdown, not LaTeX parsing.
        links = [m.group(1) for m in re.finditer(r'!?\[[^\]\n]*\]\(([^\s)]+)(?:\s+[^)]*)?\)', content)]
        links.extend(raw for _,raw in parser.links)
        for raw in links:
            if skip_url(raw):
                continue
            resolved, frag = target_of(page, raw, src)
            # In source form only, the PDF is deliberately co-deployed *later*.
            if raw == 'diabat.pdf' and page.name == 'README.md':
                continue
            if not resolved.is_file():
                raise ValueError(f'Missing generated Markdown link: {page.relative_to(src)} -> {raw}')
            if frag and resolved.suffix == '.md':
                if resolved not in anchor_cache:
                    anchor_cache[resolved] = parse_markup(resolved).ids
                if frag not in anchor_cache[resolved]:
                    raise ValueError(f'Missing Markdown target anchor: {page.relative_to(src)} -> {raw}')
            checked += 1
    print(f'SOURCE AUDIT OK: {len(pages)} markdown pages, {len(data["labels"])} report labels, {checked} local links and resources')


def audit_site(site, pdf):
    # target_of() and the HTML cache use absolute paths; normalize the root
    # before relative_to() so errors report the actual missing link/anchor.
    site = site.resolve()
    pdf = pdf.resolve()
    for target in ('index.html','diabat.pdf','diabat.css','diabat-highlight.js',
                   'searchindex.js', 'diabatization.html','references.html','build-info.json'):
        if not (site / target).is_file() or not (site / target).stat().st_size:
            raise ValueError(f'Missing or empty deployed target: {target}')
    if hashlib.sha256(pdf.read_bytes()).digest() != hashlib.sha256((site/'diabat.pdf').read_bytes()).digest():
        raise ValueError('Published PDF differs from PDF produced by this build')
    pages = list(site.rglob('*.html'))
    cache = {page.resolve(): parse_markup(page) for page in pages}
    seen = 0
    for page, parsed in cache.items():
        for _, raw in parsed.links:
            if skip_url(raw):
                continue
            target, frag = target_of(page, raw, site)
            if not target.is_file():
                raise ValueError(f'Missing deployed link or resource: {page.relative_to(site)} -> {raw}')
            if frag and target.suffix == '.html':
                if target not in cache:
                    raise ValueError(f'HTML page omitted from audit: {target}')
                if frag not in cache[target].ids:
                    raise ValueError(f'Missing published HTML anchor: {page.relative_to(site)} -> {raw}')
            seen += 1
    report = json.loads((site/'build-info.json').read_text(encoding='utf8'))
    if report.get('site_mode') != 'mdbook':
        raise ValueError('Published manifest does not indicate mdbook mode')
    print(f'SITE AUDIT OK: {len(pages)} HTML pages, {seen} internal links/resources, identical PDF')


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('sources')
    s.add_argument('book', type=Path)
    h = sub.add_parser('site')
    h.add_argument('site', type=Path)
    h.add_argument('pdf', type=Path)
    opt = ap.parse_args()
    try:
        if opt.cmd == 'sources':
            audit_sources(opt.book, opt.book / 'conversion-report.json')
        else:
            audit_site(opt.site, opt.pdf)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f'MDBOOK AUDIT FAILED: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
