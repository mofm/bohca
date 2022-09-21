from django.contrib import admin
from .models import Bookmarks, BookmarkCategory, BookmarkTags


# Register your models here.
@admin.register(Bookmarks)
class BookmarksAdmin(admin.ModelAdmin):
    list_display = ('bm_id', 'user', 'link', 'image', 'title', 'description', 'body', 'category', 'created', 'updated')
    list_filter = ('user', 'category', 'tags')
    search_fields = ('bm_id', 'user', 'link', 'image', 'title', 'description', 'body', 'tags',
                     'category', 'created', 'updated')
    ordering = ('-created',)


@admin.register(BookmarkCategory)
class BookmarkCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'user')
    list_filter = ('user',)
    search_fields = ('name', 'slug', 'user')
    ordering = ('name',)


@admin.register(BookmarkTags)
class BookmarkTagsAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'user')
    list_filter = ('user',)
    search_fields = ('name', 'slug', 'user')
    ordering = ('name',)
