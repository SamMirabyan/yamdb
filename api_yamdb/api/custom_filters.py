import django_filters

from reviews.models import Category, Genre, Title


class CustomFilter(django_filters.FilterSet):
    """
    Класс для фильтрации свзяанных полей
    модели Title по slug вместно pk (id).
    """
    genre = django_filters.ModelMultipleChoiceFilter(
        field_name='genre__slug',
        to_field_name='slug',
        queryset=Genre.objects.all()
    )
    category = django_filters.ModelMultipleChoiceFilter(
        field_name='category__slug',
        to_field_name='slug',
        queryset=Category.objects.all()
    )
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )
    year = django_filters.NumberFilter(
        field_name='year'
    )

    class Meta:
        model = Title
        fields = ('genre', 'category', 'name', 'year',)
