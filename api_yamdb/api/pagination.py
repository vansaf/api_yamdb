from rest_framework.pagination import PageNumberPagination


class ReviewPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100
