from distutils.util import strtobool
from django_filters import rest_framework

from recipes.models import Favorite, Recipe, ShoppingCart, Tag

CHOICES_LIST = (
    ('0', 'False'),
    ('1', 'True')
)


class RecipeFilter(rest_framework.FilterSet):
    is_favorited = rest_framework.ChoiceFilter(
        choices=CHOICES_LIST,
        method='filter_is_favorited'
    )
    is_in_shopping_cart = rest_framework.ChoiceFilter(
        choices=CHOICES_LIST,
        method='filter_is_in_shopping_cart'
    )
    author = rest_framework.NumberFilter(
        field_name='author',
        lookup_expr='exact'
    )
    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    def filter_is_favorited(self, queryset, name, value):

        if self.request.user.is_anonymous:
            return queryset.none()

        favorites = Favorite.objects.filter(
            user=self.request.user
        ).values_list('recipe__id', flat=True)
        if strtobool(value):
            return queryset.filter(id__in=favorites)
        else:
            return queryset.exclude(id__in=favorites)

    def filter_is_in_shopping_cart(self, queryset, name, value):

        if self.request.user.is_anonymous:
            return queryset.none()

        shopping_cart = ShoppingCart.objects.filter(
            user=self.request.user
        ).values_list('recipe__id', flat=True)
        if strtobool(value):
            return queryset.filter(id__in=shopping_cart)
        else:
            return queryset.exclude(id__in=shopping_cart)

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags',
        )
