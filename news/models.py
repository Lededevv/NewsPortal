from django.contrib.auth.models import User
from django.db import models
# from datetime import datetime, timezone

from django.db.models import Sum, Count
from django.template.defaulttags import comment


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.FloatField(default=0.0)

    def update_rating(self):
        # все посты автора
        posts_a = self.post_set.all()
        # если у автора есть статья или новость
        if posts_a:
            r_p = 3 * posts_a.aggregate(total_rating=Sum('rating_post'))['total_rating']
            sum_rating = 0
            # сумма рейтингов комментариев ко всем постам
            for post in posts_a:
                post_com = post.comment_set.all()
                # если есть комментарии к посту
                if post_com:
                    sum_rating += post_com.aggregate(total_rating=Sum('rating_com'))['total_rating']
                # если есть новость,  но нет комментария к ней
                else:
                    sum_rating += 0
        # если нет новости и статьи
        else:
            r_p = 0
            sum_rating = 0

        user_a = User.objects.get(pk=self.user_id)
        # комментарии автора
        comment_a = user_a.comment_set.all()
       # если автор оставлял комментарии
        if comment_a:
            r_c = comment_a.aggregate(total_rating=Sum('rating_com'))['total_rating']
        # если автор не оставлял комментарии
        else:
            r_c = 0

        self.rating = sum_rating + r_p + r_c
        self.save()


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)


class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    article = models.BooleanField(default=False)
    time_in = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField(Category, through='PostCategory')
    heading = models.CharField(max_length=255, unique=True)
    text = models.TextField()
    rating_post = models.FloatField(default=0.0)

    def like(self):

        self.rating_post += 1
        self.save()

    def dislike(self):
        if self.rating_post > 0:
            self.rating_post -= 1
            self.save()
        else:
            self.rating_post = 0
            self.save()

    def preview(self):
        return self.text[0:124] + "..."


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    time_create = models.DateTimeField(auto_now_add=True)
    rating_com = models.FloatField(default=0.0)

    def like(self):
        self.rating_com += 1
        self.save()

    def dislike(self):

        if self.rating_com > 0:
            self.rating_com -= 1
            self.save()
        else:
            self.rating_com = 0
            self.save()
