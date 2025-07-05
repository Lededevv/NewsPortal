import django_filters
from django.forms import DateInput
from django_filters import FilterSet, filters
from .models import Post, User, Category


# Создаем свой набор фильтров для модели Product.
# FilterSet, который мы наследуем,
# должен чем-то напомнить знакомые вам Django дженерики.



class PostFilter(FilterSet):
    heading = django_filters.CharFilter(field_name="heading",
                                        lookup_expr="icontains",
                                        label="Заголовок")

    author_username = django_filters.CharFilter(method="filter_by_author",
                                                label="Автор")

    time_in = django_filters.DateFilter(
        field_name="time_in",
        lookup_expr="gte",
        widget=DateInput(attrs={"type": "date"}),
        label="Опубликованы после указанной даты")


    # time_in = django_filters.DateFromToRangeFilter(
    #     widget=django_filters.widgets.RangeWidget(attrs={"type": "date"}),
    #     label="Выберите диапазон дат"
    # )
    category = django_filters.ModelMultipleChoiceFilter(
        field_name="category__name",
        to_field_name="name",  # Используйте нужное поле для вывода названий категорий
        queryset=Category.objects.all(),
        label="Категория",
        conjoined=True  # Если true, фильтры объединяются оператором AND
    )

    class Meta:
        model = Post
        fields = []

    def filter_by_author(self, queryset, name, value):

        return queryset.filter(author__user__username__icontains=value)

