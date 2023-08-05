from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from rest_framework import serializers, exceptions
from drf_base64.fields import Base64ImageField

from .models import (Recipe,
                     Ingredient,
                     Tag,
                     IngredientRecipe,
                     Favorite,
                     ShoppingCart)

from users.models import Subscribe, User


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
        return Subscribe.objects.filter(user=user, author=obj).exists()


class RecipesSerializer(serializers.ModelSerializer):

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
    amount = serializers.IntegerField()

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
    cooking_time = serializers.IntegerField()

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

    def get_ingredient(self, recipe, ingredients):
        for ingredient_data in ingredients:
            amount = ingredient_data['amount']
            try:
                ingredient = get_object_or_404(
                    Ingredient,
                    pk=ingredient_data['id']
                )
            except Exception:
                raise exceptions.ValidationError(
                    {'error': 'ERROR'}
                )

            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
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
        self.get_ingredient(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', [])
        for ingredient in ingredients:
            amount = ingredient['amount']
            ingredient = get_object_or_404(
                Ingredient,
                pk=ingredient['id']
            )
            IngredientRecipe.objects.update_or_create(
                recipe=instance,
                ingredient=ingredient,
                defaults={'amount': amount}
            )
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
        if self.Meta.model.objects.filter(
                user=data.get('user'),
                recipe=data.get('recipe')
        ).exists():
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
        if self.Meta.model.objects.filter(
                user=data.get('user'),
                recipe=data.get('recipe')
        ).exists():
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
