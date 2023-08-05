from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework import exceptions, status

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
            if Subscribe.objects.filter(
                user=user,
                author=author
            ).exists():
                raise exceptions.ValidationError(
                    'Дважды подписаться нельзя'
                )
            Subscribe.objects.create(user=user, author=author)
            return Response(status=status.HTTP_201_CREATED)
        if self.request.method == 'DELETE':
            get_object_or_404(
                Subscribe,
                user=user,
                author=author
            ).delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=False,
        methods=('get',),
        url_path='subscriptions'
    )
    def subscriptions(self, request):
        user = self.request.user
        sub = user.followers.all()
        authors = [item.author.id for item in sub]
        queryset = User.objects.filter(pk__in=authors)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages,
            many=True
        )
        return self.get_paginated_response(serializer.data)
        # user = self.request.user
        # all_follow = Subscribe.objects.filter(user=user)
        # pages = self.paginate_queryset(all_follow)
        # serializer = SubscribeSerializer(
        #     pages,
        #     many=True,
        #     context={'request': request}
        # )
        # return self.get_paginated_response(serializer.data)
