from django.urls import include, path
from rest_framework import routers

from api.views import (CategoriesViewSet, CommentViewSet, GenresViewSet,
                       ReviewViewSet, TitleViewSet, UserViewSet, get_token,
                       signup)


app_name = 'api'

router = routers.DefaultRouter()

router.register('users', UserViewSet, basename='users')
router.register(r'titles/(?P<title_id>\d+)/reviews',
                ReviewViewSet, basename='reviews')
router.register(r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)'
                r'/comments', CommentViewSet, basename='comments')
router.register(r'titles', TitleViewSet, basename='title')
router.register(r'genres', GenresViewSet, basename='genres')
router.register(r'categories', CategoriesViewSet, basename='categories')


api_users_pattern = [
    path('auth/signup/', signup, name='signup'),
    path('auth/token/', get_token, name='get_token'),
]
urlpatterns = [
    path('v1/', include(api_users_pattern)),
    path('v1/', include(router.urls)),
]
