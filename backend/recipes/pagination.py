from rest_framework.pagination import PageNumberPagination


class RecipePagination(PageNumberPagination):
    """Кастомный пагинатор для списка рецептов."""

    page_size_query_param = 'limit'
