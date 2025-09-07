from datetime import datetime
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import permissions

from .serializers import *

import pytz
from django.core.cache import cache
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from .filters import PostFilter
from .forms import PostForm
from .models import Post, Category, Author
from django.utils.translation import gettext as _

@login_required
def unsubscribe_from_category(request, category_id):
    category = Category.objects.get(id=category_id)
    user = request.user
    if user in category.subscribers.all():
        category.subscribers.remove(user)
        messages.success(request, 'Вы успешно отписались от категории.')
    else:
        messages.warning(request, 'Вы не были подписаны на эту категорию.')

    return redirect('post_detail', pk=request.POST.get('post_pk'))

@login_required
def subscribe_to_category(request, category_id):
    category = Category.objects.get(id=category_id)
    user = request.user
    if user not in category.subscribers.all():
        category.subscribers.add(user)
    return redirect('post_detail', pk=request.POST.get('post_pk'))

@login_required
def upgrade_me(request):
    user = request.user
    author_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        author_group.user_set.add(user)
        print(user.pk)
        Author.objects.create(user_id = user.pk)
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
        context['time_now'] = timezone.now()
        context['next_sale'] = None
        context['filterset'] = self.filterset
        context['current_time'] =  timezone.now(),
        context['timezones'] = pytz.common_timezones



        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def post(self,request):
        if request.method == 'POST':
            user_tz = request.POST.get('timezone')
            if user_tz:
                # Устанавливаем временную зону в сессии
                request.session['django_timezone'] = user_tz
                # Активируем выбранную временную зону
                timezone.activate(pytz.timezone(user_tz))
        return redirect('/news')

def Set_timezone(request):
    if request.method == 'POST':
        user_tz = request.POST.get('timezone')
        if user_tz:
            # Записываем временную зону в сессию
            request.session['django_timezone'] = user_tz
            # Перенаправляем обратно на страницу новостей
        return redirect(request.META.get('HTTP_REFERER'))

    return render(request, 'news.html')

class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_authenticated'] = self.request.user.is_authenticated
        context['categories'] = self.object.category.all()  # Важно вызвать метод all()
        return context

    def get_object(self, *args, **kwargs):  # переопределяем метод получения объекта, как ни странно

        obj = cache.get(f'post-{self.kwargs["pk"]}',
                        None)  # кэш очень похож на словарь, и метод get действует так же. Он забирает значение по ключу, если его нет, то забирает None.

        # если объекта нет в кэше, то получаем его и записываем в кэш

        if not obj:
            print("запись изменения в кеш")
            obj = super().get_object(queryset=self.queryset)
            cache.set(f'post-{self.kwargs["pk"]}', obj)

        return obj



class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'news.add_post'
    form_class = PostForm
    model = Post
    template_name = 'news_edit.html'

    def form_valid(self, form):
        categories = form.cleaned_data['categories']


        try:
            post = form.save(commit=False)
            post.author = Author.objects.get(user=self.request.user)  # устанавливаем автора
            post.save()  # пробуем сохранить пост
            post.category.add(*categories)


            return super().form_valid(form)
        except ValidationError as e:
            # Ошибка превышения дневного лимита публикаций
            messages.error(self.request, str(e))
            return self.form_invalid(form)
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_authenticated'] = self.request.user.is_authenticated
        # Получаем категории, относящиеся к посту
        context['categories'] = self.object.category.all()
        return context


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

class Index(View):
    def get(self, request):
        curent_time = timezone.now()

        # .  Translators: This message appears on the home page only
        models = Post.objects.all()

        context = {
            'models': models,
            'current_time': timezone.now(),
            'timezones': pytz.common_timezones,  # добавляем в контекст все доступные часовые пояса

        }

        return HttpResponse(render(request, 'news.html', context))

    #  по пост-запросу будем добавлять в сессию часовой пояс, который и будет обрабатываться написанным нами ранее middleware
    def post(self, request):
        request.session['django_timezone'] = request.POST['timezone']
        return redirect('/')

class PostViewset(viewsets.ModelViewSet):
   queryset =Post.objects.all()
   serializer_class = PostSerializer


class AuthorViewset(viewsets.ModelViewSet):
   queryset = Author.objects.all()
   serializer_class = AuthorSerializer


class UserViewset(viewsets.ModelViewSet):
   queryset = User.objects.all()
   serializer_class = UserSerializer
