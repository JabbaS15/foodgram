from foodgram.settings import PAGE_SIZE
from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size = PAGE_SIZE
    page_size_query_param = 'limit'
