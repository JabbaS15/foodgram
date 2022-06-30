from datetime import datetime

from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from food.models import RecipeIngredients


class FilterDataset:

    SUBSCRIBE = 'is_subscribed'
    CART = 'is_in_shopping_cart'
    FAVORITE = 'is_favorited'

    def obj_favorite_cart_subscribe(self, request, pk, method_date):
        """Работает со списком избранных."""
        user = self.request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        dataset = {
            'is_subscribed': user.is_subscribed,
            'is_in_shopping_cart': user.is_in_shopping_cart,
            'is_favorited': user.is_favorited,
        }
        data = dataset[method_date]
        obj = get_object_or_404(self.queryset, id=pk)
        serializer = self.add_serializer(
            obj, context={'request': self.request})
        obj_exist = data.filter(id=pk).exists()

        if (self.request.method in ('GET', 'POST',)) and not obj_exist:
            data.add(obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if (self.request.method in ('DELETE',)) and obj_exist:
            data.remove(obj)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def download_shopping_cart_txt(self, request):
        """Загружает файл *.txt со списком покупок."""
        user = self.request.user

        if not user.is_in_shopping_cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        ingredients = RecipeIngredients.objects.filter(
            recipe__in=(user.is_in_shopping_cart.values('id'))
        ).values(
            ingredient=F('ingredient__name'),
            measurement_unit=F('ingredient__measurement_unit')).annotate(
            amount=Sum('amount')
        )
        filename = f'{user.username}_shopping_list.txt'
        shopping_list = (
            f'Список покупок для: {user.first_name}'
            f'{datetime.now().strftime("shopping_cart")}'
        )
        for ingredient in ingredients:
            shopping_list += (
                f'{ingredient["ingredient"]}: '
                f'{ingredient["amount"]} {ingredient["measure"]}')
        response = HttpResponse(
            shopping_list, content_type='text.txt; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
