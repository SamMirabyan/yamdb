from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (filters, generics, mixins, permissions, status,
                            viewsets)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Genre, Review, Title

from .custom_filters import CustomFilter
from .permission import AdminOnly, AuthorOrStaffOrReadOnly, ReadOnly
from .serializers import (AdminUserSerializer, CategorySerializer,
                          CommentSerializer,
                          CreateUpdateDestroyReviewSerializer, GenreSerializer,
                          ListRetrieveReviewSerializer, ObtainTokenSerializer,
                          TitleReadSerializer, TitleWriteSerializer,
                          UserProfileSerializer, UserSignUpSerializer)
from .utils import send_confirmation_email

User = get_user_model()


class CreateListDestroyMixin(mixins.CreateModelMixin, mixins.ListModelMixin,
                             mixins.DestroyModelMixin, viewsets.GenericViewSet
                             ):
    pass


class TitlesViewSet(viewsets.ModelViewSet):
    '''Для работы с моделью произведений.'''
    queryset = Title.objects.all()
    serializer_class = TitleReadSerializer
    permission_classes = (ReadOnly | AdminOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = CustomFilter

    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'list':
            return TitleReadSerializer
        return TitleWriteSerializer


class CategoryViewSet(CreateListDestroyMixin):
    '''Для работы с моделью категорий произведений.'''
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (ReadOnly | AdminOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('name',)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(CreateListDestroyMixin):
    '''Для работы с моделью жанров произведений.'''
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (ReadOnly | AdminOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('name',)
    search_fields = ('name',)
    lookup_field = 'slug'


class ReviewViewSet(viewsets.ModelViewSet):
    '''
    Данный вьюсет используется два сериализатора.
    '''
    serializer_class = ListRetrieveReviewSerializer
    permission_classes = (AuthorOrStaffOrReadOnly,)

    def get_queryset(self):
        title = self.get_title()
        return title.reviews.all()

    def perform_create(self, serializer):
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)

    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'list':
            return ListRetrieveReviewSerializer
        return CreateUpdateDestroyReviewSerializer

    def get_title(self):
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, id=title_id)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (AuthorOrStaffOrReadOnly,)

    def get_queryset(self):
        review = self.get_review()
        return review.comments.all()

    def perform_create(self, serializer):
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)

    def perform_destroy(self, instance):
        instance.delete()
        return Response(status=status.HTTP_200_OK)

    def get_review(self):
        review_id = self.kwargs.get('review_id')
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Review, id=review_id, title__id=title_id)


class AdminUserViewSet(viewsets.ModelViewSet):
    '''
    Используется администратором для
    выполнения всех действий с пользователем.
    '''
    permission_classes = (AdminOnly,)

    filter_backends = (DjangoFilterBackend, filters.SearchFilter,
                       filters.OrderingFilter)

    filterset_fields = ('role',)
    search_fields = ('username', 'email',)
    ordering_fields = ('username',)

    serializer_class = AdminUserSerializer
    queryset = User.objects.all()

    lookup_field = 'username'  # username вместо pk (id)


class UserGetUpdateProfileView(generics.RetrieveUpdateAPIView):
    '''
    Используется пользователем для управления своим профилем.
    '''
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user


class UserGetConfirmationCodeView(mixins.RetrieveModelMixin,
                                  mixins.CreateModelMixin,
                                  generics.GenericAPIView):
    '''
    При get запросе от существующего пользователя
    направляем на эл.почту уведомительное письмо.

    При post запросе создаем нового пользователя
    и направляем на эл.почту уведомительное письмо.

    Код подтверждения формируется при каждом запросе
    и НЕ ХРАНИТСЯ в атрибутах пользователя.
    '''
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSignUpSerializer

    def retrieve(self, request, *args, **kwargs):
        '''
        Метод обработки get запросов.
        - пустой запрос: сообщение об ошибке, статус 400.
        - запрос с некорректными данными: сообщение об ошибке, статус 404.
        - запрос с корректными данными: пиьсмо на эл.почту.
        '''
        if not request.data:
            err_message = {'Ошибка!': 'Поля "username" и "email" обязательны!'}
            return Response(err_message, status=status.HTTP_400_BAD_REQUEST)
        data = self.dispatch_credentials(data=None, serializer=True)
        return Response(data)

    def create(self, request, *args, **kwargs):
        '''
        Метод обработки post запросов.
        - пустой запрос: сообщение об ошибке, статус 400.
        - запрос с некорректными данными: сообщение об ошибке, статус 404.
        - запрос с корректными данными: пиьсмо на эл.почту.
        '''
        response = super().create(request, *args, **kwargs)
        self.dispatch_credentials(data=response.data)
        return Response(data=response.data, status=status.HTTP_200_OK)

    def dispatch_credentials(self, data=None, serializer=False):
        '''
        Определяет GET и POST запросы.
        Формирует код подтверждения.
        Направляет электронное письмо.
        '''
        user = self.get_object(**data) if data else self.get_object()
        if serializer:
            serializer = self.get_serializer(user)
            data = serializer.data
        token = PasswordResetTokenGenerator().make_token(user)
        send_confirmation_email(**data, **{'confirmation_code': token})
        if serializer:
            return data

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get_object(self, **kwargs):
        '''
        Разрешаем создание объекта из внешних данных.
        '''
        if kwargs:
            return get_object_or_404(User, **kwargs)

        return get_object_or_404(User, **self.request.data)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def user_obtain_token(request):
    '''
    Если использовать сериализатор по модели User,
    то при POST запросе будет возникать ошибка существующего юзера.

    Придется POST запросы обрабатывать как GET.
    Однако придется также обращаться в модели User за кодом подтверждения,
    который я решил не хранить (в целях безопасности).

    Чтобы избежать этой возни, я использую "независимый" сериализатор.
    Шаги все те же, а безопаность выше.
    '''
    serializer = ObtainTokenSerializer(data=request.data)

    serializer.is_valid(raise_exception=True)
    confirmation_code = serializer.validated_data.pop('confirmation_code')
    user = get_object_or_404(User, **serializer.validated_data)

    if PasswordResetTokenGenerator().check_token(user, confirmation_code):
        token = RefreshToken.for_user(user)
        return Response({'access': str(token.access_token)})

    serializer._errors.update({
        'confirmation_code': 'неверный код подтверждения'
    })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
