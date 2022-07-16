from api.pagination import CustomPagination
from api.serializers import UserSubscriptionSerializer
from api.utils import FilterDataset
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_401_UNAUTHORIZED
from users.models import CustomUser
from users.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet, FilterDataset):
    """CRUD user models."""
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=('GET', 'PUT', 'PATCH',),
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='me'
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
        permission_classes=(IsAuthenticated,),
        url_path='subscribe'
    )
    def subscribe(self, request, pk):
        """Создаёт/удалет связь между пользователями."""
        return self.obj_favorite_cart_subscribe(request, pk, self.SUBSCRIBE)

    @action(
        methods=('GET',),
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
        pages = self.paginate_queryset(authors)
        serializer = UserSubscriptionSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=('POST',),
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='set_password'
    )
    def set_password(self, request):
        """Обновление пароля"""
        if 'new_password' not in request.data:
            return Response(
                data={'error': [
                    'полe "new_password" обязательно к заполнению'
                ]},
                status=status.HTTP_400_BAD_REQUEST
            )
        if 'current_password' not in request.data:
            return Response(
                data={'error': [
                    'полe "current_password" обязательно к заполнению'
                ]},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.data['new_password'] != request.data['current_password']:
            return Response(
                data={'error': [
                    "'new_password' и 'current_password' не совпадают"
                ]},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.user.check_password(request.data['new_password']):
            return Response(
                data={
                    'new_password': ['Проверьте правильность ввода']
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        request.user.set_password(request.data['new_password'])
        request.user.save()
        return Response(
            data=request.data,
            status=status.HTTP_201_CREATED
        )
