from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Post, Category
from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group

from django.contrib.auth.models import Group


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        # Сначала сохраняем пользователя
        user = super().save_user(request, sociallogin, form)

        # Теперь пользователь сохранён и имеет id, можем добавить его в группу
        try:
            group = Group.objects.get(name='common')
            user.groups.add(group)
        except Group.DoesNotExist:
            pass



    def populate_user(self, request, sociallogin, data):
        """ Устанавливаем начальные атрибуты пользователя при регистрации через социальную сеть. Только добавляем пользователя в группу "common". """
        user = super().populate_user(request, sociallogin, data)


        return user
class BasicSignupForm(SignupForm):

    def save(self, request):
        user = super(BasicSignupForm, self).save(request)
        basic_group = Group.objects.get(name='common')
        basic_group.user_set.add(user)
        return user

class PostForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(queryset=Category.objects.all(), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Post
        fields = [
            'heading',
            'text',
            'categories',  # Новое поле категорий
        ]
        labels = {
            'heading': 'Заголовок',
            'text': 'Текст',
        }

    def clean(self):
        cleaned_data = super().clean()
        text = cleaned_data.get("text")
        heading = cleaned_data.get("heading")

        if heading == text:
            raise ValidationError(
                "Описание не должно быть идентично заголовку."
            )

        return cleaned_data


    def clean(self):
        cleaned_data = super().clean()
        text = cleaned_data.get("text")
        heading = cleaned_data.get("heading")

        if heading == text:
            raise ValidationError(
                "Описание не должно быть идентично тексту."
            )

        return cleaned_data




# class BaseRegisterForm(UserCreationForm):
#     email = forms.EmailField(label = "Email")
#     first_name = forms.CharField(label = "Имя")
#     last_name = forms.CharField(label = "Фамилия")
#
#     class Meta:
#         model = User
#         fields = ("username",
#                   "first_name",
#                   "last_name",
#                   "email",
#                   "password1",
#                   "password2", )