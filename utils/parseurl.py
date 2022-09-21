import urllib.request
from utils.web import check_url, MyParser, strip_tags
import gzip


def parse_url(url):
    """Parse an url and return a dict with the title, description and image"""
    header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'}
    if check_url(url):
        try:
            req = urllib.request.Request(url, headers=header)
            with urllib.request.urlopen(req) as response:
                html = response.read()
                if response.info().get('Content-Encoding') == 'gzip':
                    udata = gzip.decompress(html)
                    data = udata.decode('utf-8')
                else:
                    data = html.decode('utf-8')
                parser = MyParser()
                parser.feed(data)
                return {
                    'title': parser.title,
                    'description': strip_tags(parser.description),
                    'image': parser.image if check_url(parser.image) else '/static/images/bookmark.png'
                }
        except Exception as e:
            print(e)
            return None
    else:
        return None
