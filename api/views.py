from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Genre, Review, Title, User

from .filters import TitleFilter
from .permissions import (IsAdmin, IsAdminModeratorOwnerOrReadOnly,
                          IsAdminOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, GetTokenSerializer,
                          ReadTitleSerializer, ReviewSerializer,
                          SignUpSerializer, UserSerializer,
                          WriteTitleSerializer)


class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    pagination_class = PageNumberPagination
    permission_classes = (IsAdmin,)

    @action(
        detail=False,
        methods=('GET', 'PATCH'),
        url_path='me',
        permission_classes=(IsAuthenticated,)
    )
    def own_profile(self, request):
        if request.method == 'GET':
            serializer = UserSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = SignUpSerializer(data=request.data)
    if (
        'username' in request.data and User.objects.filter(
            username=request.data['username']).exists()
    ):
        send_email(request.data['username'], request.data['email'])
        return Response(
            serializer.initial_data,
            status=status.HTTP_400_BAD_REQUEST
        )
    if serializer.is_valid():
        serializer.save()
        send_email(request.data['username'], request.data['email'])
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_token(request):
    serializer = GetTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(User, username=request.data['username'])
    if not default_token_generator.check_token(
        user,
        request.data['confirmation_code']
    ):
        return Response(
            'Неверный код подтверждения или код не действителен!'
            f'{serializer.errors}',
            status=status.HTTP_400_BAD_REQUEST
        )
    return Response(
        {'token': str(RefreshToken.for_user(user).access_token)},
        status=status.HTTP_200_OK
    )


def send_email(username, email):
    confirmation_code = default_token_generator.make_token(
        User.objects.get(username=username)
    )
    send_mail(
        'Confirmation code from yamdb',
        f'Your confirmation code is: {confirmation_code}',
        settings.EMAIL_SENT,
        [email],
        fail_silently=True,
    )


class CommentViewSet(viewsets.ModelViewSet):

    serializer_class = CommentSerializer
    permission_classes = (IsAdminModeratorOwnerOrReadOnly, )
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('review', 'author')
    search_fields = ('text',)

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminModeratorOwnerOrReadOnly, )
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('title', 'author')

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class TitleViewSet(viewsets.ModelViewSet):

    queryset = Title.objects.all()
    serializer_class = WriteTitleSerializer
    permission_classes = (IsAdminOrReadOnly, )
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    filterset_fields = ('genre', 'category', 'name', 'year')

    def perform_create(self, serializer):
        serializer.save()

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ReadTitleSerializer
        return WriteTitleSerializer


class SignSeparationViewSet(mixins.CreateModelMixin,
                            mixins.ListModelMixin,
                            mixins.DestroyModelMixin,
                            viewsets.GenericViewSet):

    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save()


class GenresViewSet(SignSeparationViewSet):

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

    # потому что удаляем мы по slug, а базово он удаляет по pk
    def destroy(self, request, *args, **kwargs):
        get_object_or_404(Genre, slug=kwargs['pk']).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoriesViewSet(SignSeparationViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def destroy(self, request, *args, **kwargs):
        get_object_or_404(Category, slug=kwargs['pk']).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
