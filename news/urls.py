from django.urls import path
# Импортируем созданное нами представление
from .views import PostsList, PostDetail, PostSearch, PostUpdate, ArticleCreate, PostCreate, ArticleUpdate, PostDelete, \
   ArticleDelete, upgrade_me

urlpatterns = [
   # path — означает путь.
   # В данном случае путь ко всем товарам у нас останется пустым,
   # чуть позже станет ясно почему.
   # Т.к. наше объявленное представление является классом,
   # а Django ожидает функцию, нам надо представить этот класс в виде view.
   # Для этого вызываем метод as_view.
   path('news/', PostsList.as_view(), name = 'post_list'),
   # pk — это первичный ключ товара, который будет выводиться у нас в шаблон
   # int — указывает на то, что принимаются только целочисленные значения
   path('news/<int:pk>', PostDetail.as_view(), name = 'post_detail'),
   path('news/search/', PostSearch.as_view(), name = 'post_search'),
   path('news/create/', PostCreate.as_view(), name = 'post_create'),
   path('news/<int:pk>/edit/', PostUpdate.as_view(), name='post_update'),
   path('news/<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),

   path('articles/create/', ArticleCreate.as_view(), name = 'article_create'),
   path('articles/<int:pk>/edit/', ArticleUpdate.as_view(), name='article_update'),
   path('articles/<int:pk>/delete/', ArticleDelete.as_view(), name='post_delete'),
   path('upgrade/', upgrade_me, name = 'upgrade')

]
