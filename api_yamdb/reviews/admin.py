from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'bio', 'role',
    )
    list_editable = ('first_name', 'last_name', 'bio',)
    search_fields = ('username', 'email',)
    list_filter = ('role',)
    empty_value_display = '--пусто--'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    list_editable = ('slug',)
    search_fields = ('name', 'slug',)
    list_filter = ('name', 'slug',)
    empty_value_display = '--пусто--'


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    list_editable = ('slug',)
    search_fields = ('name', 'slug',)
    list_filter = ('name', 'slug',)
    empty_value_display = '--пусто--'


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'year', 'description',)
    list_editable = ('category', 'year', 'description',)
    search_fields = ('name', 'year',)
    list_filter = ('category', 'genre', 'year',)
    empty_value_display = '--пусто--'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'title', 'score', 'text', 'pub_date',)
    list_editable = ('title', 'text',)
    search_fields = ('author', 'title',)
    list_filter = ('author', 'title', 'score', 'pub_date',)
    empty_value_display = '--пусто--'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'review', 'text', 'pub_date',)
    list_editable = ('review', 'text',)
    search_fields = ('author', 'review',)
    list_filter = ('author', 'review', 'pub_date',)
    empty_value_display = '--пусто--'
