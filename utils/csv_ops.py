from bookmarks.models import Bookmarks, BookmarkCategory, BookmarkTags
import csv
import codecs


class ImportCsv:
    def __init__(self, user):
        self.user = user
        self.csv_file = None

    def set_csv_file(self, csv_file):
        self.csv_file = csv_file

    def import_csv(self):
        if self.csv_file is None:
            return False

        reader = csv.DictReader(codecs.iterdecode(self.csv_file, 'utf-8'))
        for row in reader:
            category = self.create_category(row['Category'])
            self.create_bookmark(category, row['Title'], row['Link'], row['Description'], row['Image'], row['Tags'])

        return True

    def create_category(self, category):
        category = category.strip()
        if category == '':
            category = 'Uncategorized'
        category, created = BookmarkCategory.objects.get_or_create(name=category, user=self.user)
        return category

    def create_bookmark(self, category, title, link, desc, image, tags):
        bookmark, created = Bookmarks.objects.get_or_create(user=self.user, link=link)
        bookmark.title = title
        bookmark.category = category
        bookmark.description = desc
        bookmark.image = image
        bookmark.save()
        self.create_tags(bookmark, tags)

    def create_tags(self, bookmark, tags):
        tags = tags.split(' ')
        for tag in tags:
            tag = tag.strip()
            if tag == '':
                continue
            tag, created = BookmarkTags.objects.get_or_create(name=tag, user=self.user)
            bookmark.tags.add(tag)
            bookmark.save()


class BackupCsv:
    def __init__(self, user, response):
        self.user = user
        self.response = response

    def get_backup(self):
        bookmarks = Bookmarks.objects.filter(user=self.user)
        self.response['Content-Disposition'] = 'attachment; filename="bookmarks.csv"'
        writer = csv.writer(self.response, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Link', 'Title', 'Description', 'Image', 'Category', 'Tags'])
        for bookmark in bookmarks:
            tags = ' '.join([tag.name for tag in bookmark.tags.all()])
            writer.writerow([bookmark.link, bookmark.title, bookmark.description,
                             bookmark.image, bookmark.category, tags])

        return self.response
