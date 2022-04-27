from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (AdminUserViewSet, CategoryViewSet, CommentViewSet,
                    GenreViewSet, ReviewViewSet, TitlesViewSet,
                    UserGetConfirmationCodeView, UserGetUpdateProfileView,
                    user_obtain_token)

router = DefaultRouter()
router.register('users', AdminUserViewSet)
router.register('categories', CategoryViewSet, basename='categories')
router.register('genres', GenreViewSet, basename='genres')
router.register('titles', TitlesViewSet, basename='titles')
router.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews')
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    'comments')

urlpatterns = [
    path('v1/auth/token/', user_obtain_token),
    path('v1/auth/signup/', UserGetConfirmationCodeView.as_view()),
    path('v1/users/me/', UserGetUpdateProfileView.as_view()),
    path('v1/', include(router.urls)),
]
