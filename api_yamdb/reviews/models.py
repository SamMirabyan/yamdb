from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg

from .validators import year_validator


class UserRoles:
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'


class User(AbstractUser):
    '''
    Убрал поле confirmation_code из модели,
    чтобы не хранить данные в незашифрованном виде.
    Вместо этого код подтверждения выслается каждый
    раз на почту при обращении юзера на эндпоинт:
    .../auth/signup/.
    '''
    ROLES = (
        (UserRoles.ADMIN, 'admin'),
        (UserRoles.MODERATOR, 'moderator'),
        (UserRoles.USER, 'user'),
    )
    email = models.EmailField(
        verbose_name='адрес электронной почты',
        unique=True
    )
    bio = models.TextField(
        verbose_name='информация о пользователе',
        max_length=4000, blank=True,
    )
    role = models.CharField(
        verbose_name='роль пользователя', max_length=32,
        choices=ROLES,
        default=UserRoles.USER,
    )

    @property
    def _is_staff(self):
        return self.is_admin or self.is_moderator

    @property
    def is_admin(self):
        return self.role == UserRoles.ADMIN

    @property
    def is_moderator(self):
        return self.role == UserRoles.MODERATOR


class Category(models.Model):
    """Категории произведений."""
    name = models.CharField(
        max_length=200, verbose_name='Категория произведения'
    )
    slug = models.SlugField(
        unique=True, default='-пусто-', verbose_name='URL категории'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Жанры произведения."""
    name = models.CharField(max_length=200, verbose_name='Жанр произведения')
    slug = models.SlugField(unique=True, verbose_name='URL жанра')

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    """Произведения, к которым пишут отзывы."""
    name = models.CharField(
        max_length=200,
        verbose_name='Название произведения'
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        blank=True, null=True,
        verbose_name='Категория произведения'
    )

    genre = models.ManyToManyField(
        Genre,
        blank=True,
        verbose_name='Жанр произведения'
    )
    year = models.PositiveSmallIntegerField(validators=[year_validator],
                                            blank=True,
                                            verbose_name='Год издания')
    description = models.TextField(verbose_name='Описание произведения')

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name

    @property
    def rating(self):
        rating = self.reviews.aggregate(Avg('score')).get('score__avg')
        if rating:
            return round(rating)


class Review(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Название'
    )
    score = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='Оценка'
    )
    text = models.TextField(verbose_name='Отзыв')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ('pub_date',)
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review'
            )
        ]

    def __str__(self):
        return self.title.name


class Comment(models.Model):
    text = models.TextField(verbose_name='Комментарий')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации'
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:15]
