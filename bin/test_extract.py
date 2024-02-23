from urllib.parse import urlparse 
from html import unescape

urls = [
        ('https:&#x2F;&#x2F;www.dopt.com&#x2F;examples&#x2F;getting-started-checklist', 'https://www.dopt.com/examples/getting-started-checklist')
        ]

def extract(str):
    decoded = unescape(url[0])
    extracted = urlparse(decoded.strip())
    if extracted.scheme:
        return extracted


for url in urls:
    extracted = extract(url[0])
    if url[1] != extracted.geturl():
        print(f"unexpected: {url[1]} did not match {extracted}")
