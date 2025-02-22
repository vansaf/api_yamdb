from django.urls import include, path

from rest_framework import routers


app_name = 'api'

router_v1 = routers.DefaultRouter()

# router_v1.register('v1/posts', PostViewSet, basename='posts')
# router_v1.register('v1/groups', GroupViewSet, basename='groups')
# router_v1.register('v1/follow', FollowView, basename='follow')
# router_v1.register(r'v1/posts/(?P<post_id>\d+)/comments',
#                    CommentViewSet, basename='comments')

urlpatterns = [
    path('v1/auth/signup/', SignUpView.as_view(), name='signup'),
    path('v1/auth/token/', GetTokenView.as_view(), name='token'),
]

urlpatterns += router_v1.urls
