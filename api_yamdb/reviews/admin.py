from django.contrib import admin
from reviews.models import GenreTitle


@admin.register(GenreTitle)
class GenreTitleAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre')
