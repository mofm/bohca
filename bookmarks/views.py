from django.shortcuts import redirect
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View, DeleteView, UpdateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.db import IntegrityError

from .models import Bookmarks, BookmarkCategory, BookmarkTags
from .forms import CategoryForm, TagForm, UserUpdateForm
from utils.web import check_url
from utils.parseurl import parse_url


# Create your views here.
class LoginView(TemplateView, View):
    template_name = 'login.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response({})

    def post(self, request, *args, **kwargs):
        user = authenticate(username=request.POST.get('username'),
                            password=request.POST.get('password'))
        next_url = request.POST.get('next')
        if not next_url:
            next_url = 'home'

        if user is not None:
            # the password verified for the user
            if user.is_active:
                login(request, user)
                messages.success(request, "You are now logged in!")
            else:
                messages.warning(request, "The password is valid, but the account has been disabled!")
        else:
            # the authentication system was unable to verify the username and password
            messages.warning(request, "The username and password were incorrect.")

        return redirect(next_url)


class LogoutView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('home')

        logout(request)
        messages.success(request, "You are now logged out!")
        return redirect('home')


def paginate(posts, request):
    p = Paginator(posts, 10)  # creating a paginator object
    # getting the desired page number from url
    page_number = request.GET.get('page')
    try:
        page_obj = p.get_page(page_number)  # returns the desired page object
    except PageNotAnInteger:
        # if page_number is not an integer then assign the first page
        page_obj = p.page(1)
    except EmptyPage:
        # if page is empty then return last page
        page_obj = p.page(p.num_pages)
    context = {'page_obj': page_obj}
    return context


class DefaultPageView(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # featured last 10 bookmarks
        posts = Bookmarks.objects.filter(user=self.request.user).order_by('-created')[:10]
        context.update(page_obj=posts)
        return context


class SearchResults(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    template_name = 'search.html'
    model = Bookmarks

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query:
            object_list = self.model.objects.filter(
                Q(title__icontains=query) | Q(description__icontains=query) | Q(link__icontains=query)
            ).distinct()
            return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_authenticated:
            return context

        object_list = self.get_queryset()
        results = object_list.count()
        context.update(paginate(object_list, self.request), results=results)
        return context


class DeleteBookmark(LoginRequiredMixin, DeleteView):
    login_url = '/login'
    model = Bookmarks
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(DeleteBookmark, self).get_object()
        if not obj.user == self.request.user:
            raise Http404
        return obj


class AddBookmark(LoginRequiredMixin, View):
    login_url = '/login'

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        try:
            data = request.POST.get("add_bookmark_input")
            if data and check_url(data):
                parsed_html = parse_url(data)
                Bookmarks.objects.create(
                    user=request.user,
                    link=data,
                    description=parsed_html["description"],
                    title=parsed_html["title"],
                    image=parsed_html["image"],
                )
                messages.success(request, "Bookmark added!")
            else:
                messages.warning(request, "Invalid URL!")
        except Exception:
            messages.error(request, "Error adding bookmark!")

        return redirect(request.META.get('HTTP_REFERER'))


class EditBookmark(LoginRequiredMixin, UpdateView):
    login_url = '/login'
    model = Bookmarks
    fields = ['title', 'description', 'category', 'tags']
    template_name = 'bookmark_edit.html'

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(EditBookmark, self).get_object()
        if not obj.user == self.request.user:
            raise Http404
        return obj

    def get_success_url(self, **kwargs):
        return "/bookmarks/%s" % self.object.pk

    def get_queryset(self):
        qs = super(EditBookmark, self).get_queryset()
        return qs.filter(user=self.request.user)

    def get_form(self, *args, **kwargs):
        form = super(EditBookmark, self).get_form(*args, **kwargs)
        form.fields['category'].queryset = BookmarkCategory.objects.filter(user=self.request.user)
        form.fields['tags'].queryset = BookmarkTags.objects.filter(user=self.request.user)
        for myField in form.fields:
            form.fields[myField].widget.attrs['class'] = 'form-control'
        return form

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class BookmarkCategoryView(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    template_name = 'category.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = BookmarkCategory.objects.filter(user=self.request.user, slug=kwargs['slug'])
        posts = Bookmarks.objects.filter(user=self.request.user, category__id__in=category).order_by('-created')
        context.update(paginate(posts, self.request), category=category)
        return context


class BookmarkTagView(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    template_name = 'tag.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = BookmarkTags.objects.filter(user=self.request.user, slug=kwargs['slug'])
        posts = Bookmarks.objects.filter(user=self.request.user, tags__id__in=tag).order_by('-created')
        context.update(paginate(posts, self.request), tag_name=tag[0].name)
        return context


class ProfileView(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_form = UserUpdateForm(self.request.POST or None, instance=self.request.user)
        context.update({'profile_form': profile_form})
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        try:
            if 'profile_form' in request.POST and context['profile_form'].is_valid():
                context['profile_form'].save()
                messages.success(request, "Profile updated successfully!")
        except IntegrityError:
            messages.warning(request, "Email already exists!")

        return self.render_to_response(context)


class BookmarkListView(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    template_name = 'bookmarks.html'
    model = Bookmarks

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user).order_by('-created')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = self.get_queryset()
        context.update(paginate(posts, self.request))
        return context


class BookmarkDetailView(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    template_name = 'bookmark_detail.html'
    context_object_name = "bookmark"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        next_url = self.request.GET.get('next')
        context.update({'bookmark': Bookmarks.objects.get(id=kwargs['pk']), 'next': next_url})
        return context


class CategoryListView(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    template_name = 'category_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_form = CategoryForm(self.request.POST or None)
        cat_color = ('bg-primary', 'bg-secondary', 'bg-success', 'bg-danger', 'bg-warning',
                     'bg-info', 'bg-dark')
        context.update({'categories': BookmarkCategory.objects.filter(user=self.request.user),
                        'category_form': category_form, 'cat_color': cat_color})
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        try:
            if 'category_form' in request.POST and context['category_form'].is_valid():
                init_form = context['category_form'].save(commit=False)
                init_form.user = request.user
                init_form.save()
                messages.success(request, "Category added successfully!")
        except IntegrityError:
            messages.warning(request, "Category already exists!")

        return HttpResponseRedirect(self.request.path)


class TagListView(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    template_name = 'tag_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag_form = TagForm(self.request.POST or None)
        tag_color = ('badge-primary', 'badge-secondary', 'badge-success', 'badge-danger', 'badge-warning',
                     'badge-info', 'badge-dark', 'badge-light')
        context.update({'tags': BookmarkTags.objects.filter(user=self.request.user), 'tag_color': tag_color,
                        'tag_form': tag_form})
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        try:
            if 'tag_form' in request.POST and context['tag_form'].is_valid():
                init_form = context['tag_form'].save(commit=False)
                init_form.user = request.user
                init_form.save()
                messages.success(request, "Tag added successfully!")
        except IntegrityError:
            messages.warning(request, "Tag already exists!")

        return HttpResponseRedirect(self.request.path)


class ChangePasswordView(LoginRequiredMixin, PasswordChangeView):
    login_url = '/login'
    template_name = 'change_password.html'
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


class DeleteCategoryView(LoginRequiredMixin, DeleteView):
    login_url = '/login'
    model = BookmarkCategory
    success_url = reverse_lazy('categories')

    def get_object(self, queryset=None):
        obj = super(DeleteCategoryView, self).get_object()
        if not obj.user == self.request.user:
            raise Http404
        return obj

    def form_valid(self, form):
        messages.success(self.request, "Category deleted successfully!")
        return super().form_valid(form)


class DeleteTagView(LoginRequiredMixin, DeleteView):
    login_url = '/login'
    model = BookmarkTags
    success_url = reverse_lazy('tags')

    def get_object(self, queryset=None):
        obj = super(DeleteTagView, self).get_object()
        if not obj.user == self.request.user:
            raise Http404
        return obj

    def form_valid(self, form):
        messages.success(self.request, "Tag deleted successfully!")
        return super().form_valid(form)
