#!/usr/bin/env python3
"""Collect public RSS headlines for the static NEWS RADAR site."""
import datetime as dt
import email.utils
import hashlib
import html
import json
import pathlib
import re
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'data' / 'news.json'
FEEDS = [
    ('nhk', 'NHK・主要', '国内', 'https://news.web.nhk/n-data/conf/na/rss/cat0.xml'),
    ('nhk_social', 'NHK・社会', '社会', 'https://news.web.nhk/n-data/conf/na/rss/cat1.xml'),
    ('nhk_world', 'NHK・国際', '国際', 'https://news.web.nhk/n-data/conf/na/rss/cat6.xml'),
    ('forest', '窓の杜', 'IT・AI', 'https://forest.watch.impress.co.jp/data/rss/1.0/wf/feed.rdf'),
    ('pcwatch', 'PC Watch', 'IT・AI', 'https://pc.watch.impress.co.jp/data/rss/1.0/pcw/feed.rdf'),
    ('nippon', 'nippon.com', '国内', 'https://www.nippon.com/ja/rss-others/news.xml'),
    ('yahoo_impress', 'Yahoo!ニュース・Impress', 'IT・AI', 'https://news.yahoo.co.jp/rss/media/impress/all.xml'),
]
ATOM = '{http://www.w3.org/2005/Atom}'
DC_DATE = '{http://purl.org/dc/elements/1.1/}date'


def child_text(node, names):
    for name in names:
        el = node.find(name)
        if el is not None and el.text:
            return el.text.strip()
        # RDF 1.0 feeds usually namespace <title>, <link>, and <description>.
        local = name.rsplit('}', 1)[-1]
        for el in node:
            if el.tag.rsplit('}', 1)[-1] == local and el.text:
                return el.text.strip()
    return ''


def clean(value):
    value = re.sub(r'<[^>]*>', ' ', html.unescape(value or ''))
    return re.sub(r'\s+', ' ', value).strip()


def date_ms(value, fallback):
    if not value:
        return fallback
    try:
        parsed = email.utils.parsedate_to_datetime(value)
        if parsed is None:
            parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=dt.timezone.utc)
        return int(parsed.timestamp() * 1000)
    except (ValueError, TypeError, OverflowError):
        try:
            return int(dt.datetime.fromisoformat(value.replace('Z', '+00:00')).timestamp() * 1000)
        except (ValueError, TypeError):
            return fallback


def collect(feed, now_ms):
    id_, name, category, url = feed
    request = urllib.request.Request(url, headers={'User-Agent': 'NewsRadarRSS/1.0 (+https://github.com/kagoya/newsradar)', 'Accept': 'application/rss+xml, application/xml, text/xml'})
    with urllib.request.urlopen(request, timeout=18) as response:
        xml = response.read(2_000_000)
    root = ET.fromstring(xml)
    items = [node for node in root.iter() if node.tag.rsplit('}', 1)[-1] in ('item', 'entry')]
    articles = []
    for item in items[:45]:
        title = clean(child_text(item, ['title', f'{ATOM}title']))
        link = child_text(item, ['link'])
        if not link:
            atom_link = item.find(f'{ATOM}link')
            link = atom_link.get('href', '') if atom_link is not None else ''
        if not title or not link.startswith(('http://', 'https://')):
            continue
        # Public Pages edition deliberately does not redistribute RSS summaries.
        description = ''
        published = child_text(item, ['pubDate', f'{ATOM}published', f'{ATOM}updated', DC_DATE])
        article_id = hashlib.sha256((link.split('#')[0] + '|' + title).encode('utf-8')).hexdigest()[:20]
        articles.append({'id': article_id, 'title': title, 'description': description, 'url': link, 'source': name, 'category': category, 'issued': date_ms(published, now_ms), 'lang': 'ja'})
    return articles


def main():
    now = dt.datetime.now(dt.timezone.utc)
    now_ms = int(now.timestamp() * 1000)
    previous = {}
    if OUTPUT.exists():
        try:
            previous = json.loads(OUTPUT.read_text(encoding='utf-8'))
        except (ValueError, OSError):
            pass
    articles = []
    states = {}
    for feed in FEEDS:
        id_ = feed[0]
        try:
            data = collect(feed, now_ms)
            articles.extend(data)
            states[id_] = {'ok': bool(data), 'count': len(data), 'message': f'{len(data)}件取得' if data else '記事がありません'}
        except Exception as error:
            # Preserve prior data for a source when temporarily unavailable.
            existing = [a for a in previous.get('articles', []) if a.get('source') == feed[1]]
            articles.extend(existing)
            states[id_] = {'ok': False, 'count': len(existing), 'message': f'取得失敗（保存済み{len(existing)}件）'}
            print(f'{id_}: {type(error).__name__}: {error}')
    unique = {a['id']: a for a in articles}
    ordered = sorted(unique.values(), key=lambda a: a['issued'], reverse=True)[:500]
    if not ordered:
        raise RuntimeError('No news received and no stored fallback exists; preserve the previous snapshot')
    result = {'generatedAt': now.isoformat(), 'articles': ordered, 'states': states}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
    print(f'Wrote {len(ordered)} articles from {sum(s["ok"] for s in states.values())} feeds')


if __name__ == '__main__':
    main()
