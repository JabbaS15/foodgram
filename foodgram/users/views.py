from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models import CustomUser
from users.serializers import UserRegistationSerializer


class UserViewSet(viewsets.ModelViewSet):
    """CRUD user models."""
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistationSerializer

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        methods=['get', 'put', 'patch'],
        permission_classes=[IsAuthenticated]
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
