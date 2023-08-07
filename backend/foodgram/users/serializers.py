from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

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
        return obj.author.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        if request is not None and request.GET.get('recipes_limit'):
            recipes = obj.author.all()[:int(request.GET.get('recipes_limit'))]
        else:
            recipes = obj.author.all()
        serializer = RecipesSerializer(recipes, many=True, read_only=True)
        return serializer.data

    def validate(self, data):
        user = self.context['request'].user
        if user.followers.exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя'
            )
        return data
