from django.core.validators import (RegexValidator,
                                    MinValueValidator,
                                    MaxValueValidator)
from django.db import models

from foodgram.settings import (MIN_VALUE_COOKING_TIME,
                               MAX_VALUE_COOKING_TIME,
                               MIN_VALUE_AMOUNT,
                               MAX_VALUE_AMOUNT)
from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        'Название',
        max_length=256,
        db_index=True,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=256,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        'Название',
        max_length=256,
        db_index=True,
        unique=True
    )
    color = models.CharField(
        'HEX-код',
        max_length=7,
        unique=True,
        validators=[
            RegexValidator(
                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Введите HEX-код!'
            )
        ]
    )
    slug = models.SlugField(
        'Slug',
        unique=True,
        max_length=256
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='author',
    )
    name = models.CharField(
        'Название',
        max_length=256
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/',
    )
    text = models.TextField(
        'Описание'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[MinValueValidator(
            MIN_VALUE_COOKING_TIME,
            message='Время приготовления не может быть меньше минуты!'
        ),
            MaxValueValidator(
                MAX_VALUE_COOKING_TIME,
                message='Слишком большое время приготовления!'
        )]
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        null=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_list',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        'Колличество ингредиента',
        validators=[MinValueValidator(
            MIN_VALUE_AMOUNT,
            message='Как минимум 1!'
        ),
            MaxValueValidator(
                MAX_VALUE_AMOUNT,
                message='Слишком много!'
        )]
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'

    def __str__(self):
        return (
            f'{self.ingredient.name} ({self.ingredient.measurement_unit})'
            f' - {self.amount}'
        )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Кто добавил'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Рецепт'
    )

    class Meta:
        ordering = ('user', )
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.user} > {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shop_cart',
        verbose_name='Кто добавил'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shop_cart',
        verbose_name='Рецепт'
    )

    class Meta:
        ordering = ('user',)
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'

    def __str__(self):
        return f'{self.user} > {self.recipe}'
