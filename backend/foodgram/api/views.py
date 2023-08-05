from io import BytesIO

import rest_framework.exceptions
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from fpdf import FPDF

from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, SAFE_METHODS

from .pagination import CustomPagination
from .services import RecipeFilter
from recipes.models import Recipe, Tag, Ingredient, ShoppingCart, Favorite
from recipes.serializers import (TagSerializer, IngredientSerializer,
                                 WriteRecipeSerializer, RecipeCreateSerializer,
                                 RecipesSerializer)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return WriteRecipeSerializer
        return RecipeCreateSerializer

    @action(
        detail=True,
        methods=('post', 'delete')
    )
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(
            Recipe,
            pk=kwargs.get('pk')
        )
        if self.request.method == 'POST':
            if ShoppingCart.objects.filter(
                user=self.request.user,
                recipe=recipe
            ).exists():
                return Response(
                    {'ERROR': 'Уже в корзине'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(
                user=self.request.user,
                recipe=recipe
            )
            serializer = RecipesSerializer(
                recipe,
                context={'request': request}
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if self.request.method == 'DELETE':
            if not ShoppingCart.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists():
                raise rest_framework.exceptions.ValidationError(
                    'E:T'
                )
            get_object_or_404(
                ShoppingCart,
                user=request.user,
                recipe=recipe
            ).delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=True,
        methods=('post', 'delete')
    )
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(
            Recipe,
            pk=kwargs.get('pk')
        )
        if self.request.method == 'POST':
            if Favorite.objects.filter(
                user=self.request.user,
                recipe=recipe
            ).exists():
                return Response(
                    {'ERROR': 'Уже в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.create(
                user=self.request.user,
                recipe=recipe
            )
            serializer = RecipesSerializer(
                recipe,
                context={'request': request}
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        elif self.request.method == 'DELETE':
            try:
                favorite = get_object_or_404(
                    Favorite,
                    user=request.user,
                    recipe=recipe
                )
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Exception:
                return Response(
                    {'ERROR': 'Запись не найдена'},
                    status=status.HTTP_404_NOT_FOUND
                )

    @action(detail=False)
    def download_shopping_cart(self, request):
        item_shop_cart = ShoppingCart.objects.filter(user=self.request.user)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = ('attachment;'
                                           ' filename="shopping_list.pdf"')
        buffer = BytesIO()
        pdf_file = FPDF()
        pdf_file.add_page()
        pdf_file.add_font("DejaVuSans", fname="api/DejaVuSans.ttf", uni=True)
        pdf_file.set_font("DejaVuSans", size=12)
        pdf_file.cell(200, 10, 'Shopping List', ln=True, align="C")
        for item in item_shop_cart:
            ingredients = item.recipe.ingredient_list.all()
            for ingredient in ingredients:
                ingredient_text = (f'{ingredient.amount}'
                                   f' {ingredient.ingredient.measurement_unit}'
                                   f' - {ingredient.ingredient.name}')
                pdf_file.multi_cell(0, 10, txt=ingredient_text)
        buffer.write(pdf_file.output(dest='S'))
        pdf_file = buffer.getvalue()
        buffer.close()
        response.write(pdf_file)
        return response
