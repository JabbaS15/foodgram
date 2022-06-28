from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_401_UNAUTHORIZED

from api.serializers import UserSubscriptionSerializer
from users.models import CustomUser
from users.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """CRUD user models."""
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    add_serializer = UserSerializer

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=('GET', 'PUT', 'PATCH', ),
        detail=False,
        permission_classes=(IsAuthenticated, ),
        url_path='subscribe'
    )
    def me(self, request):
        """API для редактирования текущим пользователем своих данных."""
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=user.role, partial=True)
        return Response(serializer.data)

    @action(
        methods=('GET', 'POST', 'DELETE',),
        detail=True,
        permission_classes=(IsAuthenticated, ),
        url_path='subscribe'
    )
    def subscribe(self, request, pk):
        """Создаёт/удалет связь между пользователями."""
        user = self.request.user

        if user.is_anonymous:
            return Response(status=HTTP_401_UNAUTHORIZED)

        subscribed = user.is_subscribed
        obj = get_object_or_404(self.queryset, id=pk)
        serializer = self.add_serializer(
            obj, context={'request': self.request})
        obj_exist = subscribed.filter(id=pk).exists()

        if (self.request.method in ('GET', 'POST',)) and not obj_exist:
            subscribed.add(obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if (self.request.method in ('DELETE',)) and obj_exist:
            subscribed.remove(obj)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=('GET', ),
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='subscriptions'
    )
    def subscriptions(self, request):
        """Подписки пользоваетеля."""
        user = self.request.user
        if user.is_anonymous:
            return Response(status=HTTP_401_UNAUTHORIZED)
        authors = user.is_subscribed.all()
        serializer = UserSubscriptionSerializer(
            authors, many=True, context={'request': request}
        )
        return Response(serializer.data)
