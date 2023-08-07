from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework import status

from .serializers import SubscribeSerializer
from api.pagination import CustomPagination
from .models import User, Subscribe


class UserCustomViewSet(UserViewSet):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPagination
    http_method_names = ('get', 'post', 'delete')

    @action(
        detail=True,
        methods=['post', 'delete'],
        serializer_class=SubscribeSerializer
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, pk=id)

        if self.request.method == 'POST':
            Subscribe.objects.create(user=user, author=author)
            return Response(status=status.HTTP_201_CREATED)
        if self.request.method == 'DELETE':
            sub = author.following_users.first()
            if sub is not None:
                sub.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('get',),
        url_path='subscriptions'
    )
    def subscriptions(self, request):
        user = self.request.user
        sub = user.followers.all()
        queryset = User.objects.filter(pk__in=sub.values('author_id'))
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages,
            many=True
        )
        return self.get_paginated_response(serializer.data)
