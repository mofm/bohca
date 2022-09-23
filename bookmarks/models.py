from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.utils.text import slugify

from utils.web import check_url


class BookmarkTags(models.Model):
    """Contains Bookmarks tags"""

    name = models.CharField(max_length=30)
    slug = models.SlugField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('slug', 'user')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(BookmarkTags, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Bookmarks(models.Model):
    """Bookmarks"""

    bm_id = models.CharField(max_length=12, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    link = models.TextField()
    image = models.CharField(max_length=200, blank=True, null=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    body = models.TextField(null=True, blank=True)
    tags = models.ManyToManyField(BookmarkTags, blank=True)
    category = models.ForeignKey('BookmarkCategory', on_delete=models.CASCADE, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """Make sure to generate a unique random bookmark id"""
        if Bookmarks.objects.filter(link=self.link, user=self.user).exists():
            raise ValueError('Bookmark already exists')
        if self.id is None:
            while True:
                random = get_random_string(12)
                if not Bookmarks.objects.filter(bm_id=random).exists():
                    self.bm_id = random
                    return super().save(*args, **kwargs)
                continue
        else:
            return super().save(*args, **kwargs)

    def is_url(self):
        """Check the bookmark is actually a link"""
        return check_url(self.link)


class BookmarkCategory(models.Model):
    """Bookmark Category"""
    name = models.CharField(max_length=50)
    slug = models.SlugField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        'self', null=True, blank=True,
        related_name='children', on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('slug', 'user')

    def save(self, *args, **kwargs):
        # prevent a category to be itself parent
        if self.id and self.parent and self.id == self.parent.id:
            self.parent = None
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        full_name = [self.name]
        k = self.parent
        while k is not None:
            full_name.append(k.name)
            k = k.parent
        return ' -> '.join(full_name[::-1])
