from django.urls import path, re_path

from .views import *

urlpatterns = [
    re_path(
        r'^login/$',
        LoginView.as_view(),
        name='login'
    ),
    re_path(
        r'^logout/$',
        LogoutView.as_view(),
        name='logout'
    ),
    path("", DefaultPageView.as_view(), name="home"),
    path("search/", SearchResults.as_view(), name="search"),
    path("bookmarks", BookmarkListView.as_view(), name="bookmarks"),
    path("bookmarks/<str:bm_id>", BookmarkDetailView.as_view(), name="bookmark"),
    path("bookmarks/delete/<int:pk>", DeleteBookmark.as_view(), name="delete"),
    path("bookmarks/edit/<int:pk>", EditBookmark.as_view(), name="edit"),
    path("add_bookmark", AddBookmark.as_view(), name="add_bookmark"),
    path("categories/", CategoryListView.as_view(), name="categories"),
    path("categories/<slug:slug>", BookmarkCategoryView.as_view(), name="category"),
    path("categories/delete/<int:pk>", DeleteCategoryView.as_view(), name="delete_category"),
    path("tags/", TagListView.as_view(), name="tags"),
    path("tags/<slug:slug>", BookmarkTagView.as_view(), name="tag"),
    path("tags/delete/<int:pk>", DeleteTagView.as_view(), name="delete_tag"),
    path("profile/<username>", ProfileView.as_view(), name="profile"),
    path('password-change/', ChangePasswordView.as_view(), name='password_change'),
]
