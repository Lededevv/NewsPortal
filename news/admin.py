
from django.contrib import admin
from .models import Category, Post


# Inline класс для отображения тегов при создании статей
class CategoryInline(admin.TabularInline):
    model = Post.category.through  # Используем промежуточную модель для M2M
    extra = 1  # Число дополнительных пустых полей

# Регистрация модели Article с inline полем
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['heading','author', 'article', 'rating_post']
    inlines = [CategoryInline]

# Регистрация модели Tag отдельно
@admin.register(Category)
class Category(admin.ModelAdmin):
    pass




# admin.site.register(Category)
# admin.site.register(Post)