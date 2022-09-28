from bookmarks.models import Bookmarks, BookmarkCategory


class ExportHTML:
    def __init__(self, user, response):
        self.user = user
        self.response = response

    def _categories(self):
        return BookmarkCategory.objects.filter(user=self.user)

    def _bookmarks(self, category=None):
        return Bookmarks.objects.filter(user=self.user, category__name=category)

    def _template(self):
        return """
<!DOCTYPE NETSCAPE-Bookmark-file-1>
<!-- This is an automatically generated file.
        It will be read and overwritten.
        DO NOT EDIT! -->
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bohca</TITLE>
<H1>Bookmarks</H1>
<DL><p>
{}
{}
</DL><p>
        """.format(self.categorized(), self.uncategorized())

    def categorized(self):
        data = []
        for category in self._categories():
            data.append('\t<DT><H3>{}</H3>'.format(category.name))
            data.append('\t<DL><p>')
            for bookmark in self._bookmarks(category.name):
                tags = ' '.join([tag.name for tag in bookmark.tags.all()])
                data.append('\t\t<DT><A HREF="{}" ADD_DATE="{}" TAGS="{}">{}</A>'.format(
                    bookmark.link, bookmark.created.timestamp(), tags, bookmark.title))
            data.append('\t</DL><p>')

        return "\n".join(data)

    def uncategorized(self):
        data = []
        for bookmark in self._bookmarks():
            tags = ' '.join([tag.name for tag in bookmark.tags.all()])
            data.append('\t<DT><A HREF="{}" ADD_DATE="{}" TAGS="{}">{}</A>'.format(
                bookmark.link, bookmark.created.timestamp(), tags, bookmark.title))

        return "\n".join(data)

    def export(self):
        self.response['Content-Disposition'] = 'attachment; filename="bookmarks.html"'
        self.response.write(self._template())

        return self.response
