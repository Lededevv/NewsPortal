from datetime import datetime
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from .filters import PostFilter
from .forms import PostForm
from .models import Post


@login_required
def upgrade_me(request):
    user = request.user
    author_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        author_group.user_set.add(user)
    return redirect('/news')


class PostSearch(LoginRequiredMixin, ListView):
    model = Post
    ordering = '-time_in'
    template_name = 'news_search.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['next_sale'] = None
        context['filterset'] = self.filterset
        context['is_authenticated'] = self.request.user.is_authenticated

        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs


class PostsList(ListView):
    model = Post
    ordering = '-time_in'
    template_name = 'news.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_author'] = not self.request.user.groups.filter(name='authors').exists()
        context['is_authenticated'] = self.request.user.is_authenticated
        context['time_now'] = datetime.utcnow()
        context['next_sale'] = None
        context['filterset'] = self.filterset

        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs


class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_authenticated'] = self.request.user.is_authenticated
        return context


class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'news.add_post'
    form_class = PostForm
    model = Post
    template_name = 'news_edit.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_authenticated'] = self.request.user.is_authenticated
        return context


class PostUpdate(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    permission_required = 'news.change_post'
    form_class = PostForm
    model = Post
    template_name = 'news_edit.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_authenticated'] = self.request.user.is_authenticated
        return context


class PostDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'news.delete_post'
    model = Post
    form_class = PostForm
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')


class ArticleCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'news.add_post'
    form_class = PostForm
    model = Post
    template_name = 'news_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.article = True

        return super().form_valid(form)


class ArticleUpdate(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    permission_required = 'news.change_post'
    form_class = PostForm
    model = Post
    template_name = 'news_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.article = True

        return super().form_valid(form)


class ArticleDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'news.delete_post'
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')

# from django.contrib.auth.models import User
# from django.views.generic.edit import CreateView
# from .forms import BaseRegisterForm

# class BaseRegisterView(CreateView):
#     model = User
#     form_class = BaseRegisterForm
#     success_url = '/'
