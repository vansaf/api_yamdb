from requests import Response
from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Вывод произвидений по страницам."""
    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'results': data
        })
