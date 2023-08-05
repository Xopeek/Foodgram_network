from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from recipes.models import Recipe
from recipes.serializers import RecipesSerializer
from .models import User


class CreateUserSerializer(UserCreateSerializer):
    """Создание нового пользователя."""

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'password'
        )


class SubscribeSerializer(serializers.ModelSerializer):
    """Список подписок."""
    recipes = serializers.SerializerMethodField(
        method_name='get_recipes'
    )
    count_recipes = serializers.SerializerMethodField(
        method_name='get_count_recipes'
    )

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'followers',
            'recipes',
            'count_recipes'
        )

    def get_count_recipes(self, obj):
        return Recipe.objects.filter(
            author=obj
        ).count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        if request is not None and request.GET.get('recipes_limit'):
            recipes = Recipe.objects.filter(
                author=obj
            )[:int(request.GET.get('recipes_limit'))]
        else:
            recipes = Recipe.objects.filter(author=obj)
        serializer = RecipesSerializer(recipes, many=True, read_only=True)
        return serializer.data
