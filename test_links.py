import urllib.request
import re

pages = [
    'http://192.168.193.147:5000/',
    'http://192.168.193.147:5000/projects',
    'http://192.168.193.147:5000/project/MPLAD-2026-001',
    'http://192.168.193.147:5000/risk-analysis',
    'http://192.168.193.147:5000/analytics',
    'http://192.168.193.147:5000/map',
    'http://192.168.193.147:5000/reports'
]

for p in pages:
    html = urllib.request.urlopen(p).read().decode('utf-8')
    links = re.findall(r'<a\s+[^>]*href=["\']([^"\']*)["\'][^>]*class=["\']([^"\']*nav-item[^"\']*)["\'][^>]*>(.*?)</a>', html, re.DOTALL)
    if not links:
        links = re.findall(r'<a\s+[^>]*class=["\']([^"\']*nav-item[^"\']*)["\'][^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>', html, re.DOTALL)
        links = [(href, cls, txt) for cls, href, txt in links]
    print(f"\nPage: {p}")
    for href, cls, content in links:
        txt = re.sub(r'<[^>]*>', '', content).strip()
        txt = ' '.join(txt.encode('ascii', 'ignore').decode().split())
        active = ' [ACTIVE]' if 'active' in cls else ''
        print(f"   {txt} -> {href}{active}")
