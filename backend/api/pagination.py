from rest_framework.pagination import PageNumberPagination

PAGE_SIZE = 6


class CustomPagination(PageNumberPagination):

    page_size = PAGE_SIZE
    page_size_query_param = 'limit'
