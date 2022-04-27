from django.contrib.auth import get_user_model
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title
from .custom_fields import CurrentTitleDefault

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'


class TitleReadSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для отображения одного или нескольких title.
    Поле rating получается из модели Title.
    '''
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'category', 'genre', 'year', 'description', 'rating',
        )
        read_only_fields = ('id',)


class TitleWriteSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для создания, обновления и удаления title.
    '''
    category = serializers.SlugRelatedField(queryset=Category.objects.all(),
                                            slug_field='slug')
    genre = serializers.SlugRelatedField(queryset=Genre.objects.all(),
                                         slug_field='slug', many=True)

    class Meta:
        model = Title
        fields = '__all__'


class CreateUpdateDestroyReviewSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для создания, обновления и удаления review.
    Поля "author" и "title" скрыты и получаются через default поля.
    '''
    score = serializers.IntegerField(min_value=1, max_value=10)
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    title = serializers.HiddenField(
        default=CurrentTitleDefault()
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'score', 'author', 'title')
        read_only_fields = ('id',)

        validators = (
            serializers.UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=('author', 'title',)
            ),
        )


class ListRetrieveReviewSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для отоборажения одного или нескольких review.
    '''
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date',)
        read_only_fields = ('id', 'author', 'pub_date',)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )

    review = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    title = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    class Meta:
        model = Comment
        fields = '__all__'


class BaseUserSerializer(serializers.ModelSerializer):
    '''
    Базовый сериализатор для управления пользователями.
    '''
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )


class UserProfileSerializer(BaseUserSerializer):
    '''
    Сериализатор для работы юзера со своим профилем.
    '''
    class Meta(BaseUserSerializer.Meta):
        read_only_fields = ('username', 'email', 'role',)


class AdminUserSerializer(BaseUserSerializer):
    '''
    Сериализатор для управления админом (суперпользователем)
    данными пользователя.
    '''
    class Meta(BaseUserSerializer.Meta):
        lookup_field = 'username'

    def validate(self, data):
        '''
        Запрещаем использовать 'me' в качестве имени юзера.
        '''
        if data.get('username') == 'me':
            raise serializers.ValidationError({
                'username': 'Ошибка! Данное имя нельзя использовать.'
            })

        return data

    def update(self, instance, validated_data):
        '''
        Запрещаем кому-либо обновлять username.
        Так нельзя, ребята.
        '''
        if 'username' in validated_data:
            raise serializers.ValidationError({
                'username': 'Ошибка! Это поле нельзя менять.'
            })

        return super().update(instance, validated_data)


class UserSignUpSerializer(AdminUserSerializer):
    '''
    Cериализатор для обработки запроса на подписку.
    '''
    class Meta(BaseUserSerializer.Meta):
        fields = ('username', 'email',)


class ObtainTokenSerializer(serializers.Serializer):
    '''
    "Независимый" от модели сериализатор для обработки
    запросов на токены.
    '''
    username = serializers.CharField()
    confirmation_code = serializers.CharField()
