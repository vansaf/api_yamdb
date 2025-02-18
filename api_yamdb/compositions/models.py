from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Review(models.Model):
    author = models.ForeignKey(
        User,
        related_name='reviews',
        on_delete=models.CASCADE
    )
    text = models.TextField()
    created = models.DateField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True
    )
    composition = models.ForeignKey(
        #Composition,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.CharField(max_length=10)

    def __str__(self):
        return self.text


class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)

    def __str__(self):
        """Функция для описания класса."""
        return self.text
