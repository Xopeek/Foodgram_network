from djoser.serializers import UserSerializer
from rest_framework import serializers, exceptions
from drf_base64.fields import Base64ImageField

from django.conf import settings
from .models import (Recipe,
                     Ingredient,
                     Tag,
                     IngredientRecipe,
                     Favorite,
                     ShoppingCart)

from users.models import User


class UsersSerializer(UserSerializer):
    """Сериализация Пользователя."""
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.following_users.exists()


class RecipesSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализация ингредиетов."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализация тегов."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализация связанной таблицы ингредиента и рецепта."""
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient.id', read_only=True
    )
    name = serializers.CharField(
        source='ingredient.name', read_only=True
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True
    )

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class CreateIngredientSerializer(serializers.ModelSerializer):
    """Создание ингредиента для рецепта."""
    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        min_value=settings.MIN_VALUE_AMOUNT,
        max_value=settings.MAX_VALUE_AMOUNT
    )

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'amount'
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализация создания рецепта."""
    author = UsersSerializer(read_only=True)
    ingredients = CreateIngredientSerializer(many=True)
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    cooking_time = serializers.IntegerField(
        min_value=settings.MIN_VALUE_COOKING_TIME,
        max_value=settings.MAX_VALUE_COOKING_TIME
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'name',
            'image',
            'text',
            'ingredients',
            'tags',
            'cooking_time'
        )

    def create_ingredient(self, recipe, ingredients):
        try:
            IngredientRecipe.objects.bulk_create(
                [IngredientRecipe(
                    recipe=recipe,
                    ingredient=Ingredient.objects.get(pk=ingredient['id']),
                    amount=ingredient['amount']
                ) for ingredient in ingredients]
            )
        except Exception:
            raise exceptions.ValidationError(
                {'error': 'ERROR'}
            )

    def validate(self, attrs):
        if not attrs.get('ingredients'):
            raise serializers.ValidationError(
                'Добавьте ингредиенты!'
            )
        if not attrs.get('tags'):
            raise serializers.ValidationError(
                'Добавьте тэг!'
            )
        ingredients = self.context.get('ingredients', [])
        list_ingredient = [ing['id'] for ing in ingredients]
        unique_ingredient = set(list_ingredient)
        if len(list_ingredient) != len(unique_ingredient):
            raise serializers.ValidationError(
                'Ингредиенты не уникальны!'
            )
        return attrs

    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            author=author,
            **validated_data
        )
        recipe.tags.set(tags)
        self.create_ingredient(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', [])
        old_recipe = instance.ingredient_list.all()
        old_recipe.delete()
        self.create_ingredient(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return WriteRecipeSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class WriteRecipeSerializer(serializers.ModelSerializer):
    """Чтение рецепта."""
    author = UsersSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientRecipeSerializer(
        many=True,
        read_only=True,
        source='ingredient_list'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'name',
            'image',
            'text',
            'ingredients',
            'tags',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and obj.recipe.filter(user=user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and obj.shop_cart.filter(user=user).exists()
        )


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализация избранного."""

    class Meta:
        model = Favorite
        fields = (
            'id',
            'user',
            'recipe'
        )

    def validate(self, data):
        user = self.context['request'].user
        recipe = data['recipe']
        if user.favorite.filter(recipe=recipe).exists():
            raise serializers.ValidationError(
                'Уже добавлено!'
            )
        return data

    def to_representation(self, instance):
        return RecipesSerializer(
            instance.recipe,
            context={
                'request': self.context.get('request')
            }
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализация корзины."""

    class Meta:
        model = ShoppingCart
        fields = (
            'id',
            'user',
            'recipe'
        )

    def validate(self, data):
        user = data.get('user')
        if user.shop_cart.exists():
            raise serializers.ValidationError(
                'Уже добавлено!'
            )
        return data

    def to_representation(self, instance):
        return WriteRecipeSerializer(
            instance.recipe,
            context={
                'request': self.context.get('request')
            }
        ).data
