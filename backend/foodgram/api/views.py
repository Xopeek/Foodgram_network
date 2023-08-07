from io import BytesIO

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from fpdf import FPDF
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, SAFE_METHODS

from foodgram.settings import (PDF_SIZE_FONT,
                               CELL_WIDTH,
                               CELL_HEIGHT,
                               CELL_AUTO_WIDTH)
from .pagination import CustomPagination
from .services import RecipeFilter
from recipes.models import Recipe, Tag, Ingredient, ShoppingCart, Favorite
from recipes.serializers import (TagSerializer, IngredientSerializer,
                                 WriteRecipeSerializer, RecipeCreateSerializer,
                                 FavoriteSerializer, ShoppingCartSerializer)


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
            shopping_cart = ShoppingCart.objects.create(
                user=self.request.user,
                recipe=recipe
            )
            serializer = ShoppingCartSerializer(
                shopping_cart,
                context={'request': request}
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if self.request.method == 'DELETE':
            try:
                user = request.user
                shop_cart = user.shop_cart.first()
                if shop_cart is not None:
                    shop_cart.delete()
                return Response(
                    status=status.HTTP_204_NO_CONTENT
                )
            except Exception:
                return Response(
                    {'ERROR': 'Корзина не найдена'},
                    status=status.HTTP_404_NOT_FOUND
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
            favorite = Favorite.objects.create(
                user=self.request.user,
                recipe=recipe
            )
            serializer = FavoriteSerializer(
                favorite,
                context={'request': request}
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        elif self.request.method == 'DELETE':
            try:
                user = request.user
                favorite = user.favorite.first()
                if favorite is not None:
                    favorite.delete()
                return Response(
                    status=status.HTTP_204_NO_CONTENT
                )
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
        pdf_file.add_font('DejaVuSans', fname='api/DejaVuSans.ttf', uni=True)
        pdf_file.set_font('DejaVuSans', size=PDF_SIZE_FONT)
        pdf_file.cell(
            CELL_WIDTH,
            CELL_HEIGHT,
            'Shopping List',
            ln=True,
            align='C'
        )
        for item in item_shop_cart:
            ingredients = item.recipe.ingredient_list.all()
            for ingredient in ingredients:
                ingredient_text = (f'{ingredient.amount}'
                                   f' {ingredient.ingredient.measurement_unit}'
                                   f' - {ingredient.ingredient.name}')
                pdf_file.multi_cell(
                    CELL_AUTO_WIDTH,
                    CELL_HEIGHT,
                    txt=ingredient_text
                )
        buffer.write(pdf_file.output(dest='S'))
        pdf_file = buffer.getvalue()
        buffer.close()
        response.write(pdf_file)
        return response
