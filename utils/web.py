from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from html.parser import HTMLParser
from io import StringIO


def check_url(url):
    """Check if a url is valid"""
    validate = URLValidator()
    try:
        validate(url)
        return True
    except ValidationError:
        return False


class MyParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.title = ''
        self.description = ''
        self.image = ''
        self.lasttag = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self.lasttag = 'title'
        elif tag == 'meta':
            if ('property', 'og:description') in attrs:
                self.description = dict(attrs).get('content')
            # elif ('property', 'og:title') in attrs:
            #     self.title = dict(attrs).get('content')
            elif ('property', 'og:image') in attrs:
                self.image = dict(attrs).get('content')

    def handle_data(self, data):
        if self.lasttag == 'title':
            self.title = data
            self.lasttag = ''


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()
