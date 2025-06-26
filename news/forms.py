from django import forms
from django.core.exceptions import ValidationError

from .models import Post


class PostForm(forms.ModelForm):
    text = forms.CharField(min_length=20)

    class Meta:
        model = Post
        fields = [
            'heading',
            'author',
            'text',

        ]
        labels = {
            'heading': 'Заголовок',
            'author': 'Автор',
            'text' : 'Текст'
        }


    def clean(self):
        cleaned_data = super().clean()
        text = cleaned_data.get("text")
        heading = cleaned_data.get("heading")

        if heading == text:
            raise ValidationError(
                "Описание не должно быть идентично тексту."
            )

        return cleaned_data