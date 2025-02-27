from django.contrib import admin
from reviews.models import (Category,
                            Comment,
                            Genre,
                            GenreTitle,
                            Review,
                            Title,
                            User)


class TitleInline(admin.StackedInline):
    """Класс для создания встроенного редактора произведений."""

    model = Title
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Класс настройки административной панели для модели Category."""

    inlines = (
        TitleInline,
    )


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """Класс настройки административной панели для модели Genre."""

    inlines = (
        TitleInline,
    )


@admin.register(GenreTitle)
class GenreTitleAdmin(admin.ModelAdmin):
    """Класс настройки административной панели связанной модели GenreTitle."""
    list_display = ('title', 'genre')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Класс настройки административной панели для модели Comment."""

    list_display = (
        'text',
        'author',
        'pub_date',
        'review'
    )
    search_fields = ('text', 'author')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Класс настройки административной панели для модели Review."""

    list_display = (
        'text',
        'title',
        'author',
        'pub_date',
    )
    search_fields = ('text', 'title')


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    """Класс настройки административной панели для модели Title."""

    list_display = (
        'name',
        'year',
        'description',
        'category',
        'genre',
    )
    list_editable = (
        'description',
        'category',
        'location',
        'year',
        'name',
    )
    search_fields = ('name', 'genre', 'category')
    list_filter = ('year',)
    list_display_links = ('name',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Класс настройки административной панели для модели User."""

    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'bio',
        'role'
    )
    search_fields = ('username', 'email')
