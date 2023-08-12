from django.urls import path, include
from django.conf.urls.static import static
from rest_framework import routers

from django.conf import settings
from users.views import UserCustomViewSet
from api.views import TagsViewSet, IngredientsViewSet, RecipeViewSet

router = routers.DefaultRouter()
router.register('users', UserCustomViewSet)
router.register('tags', TagsViewSet)
router.register('ingredients', IngredientsViewSet)
router.register('recipes', RecipeViewSet)


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls))
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
