from django.db import models

# Create your models here.

class Book(models.Model):

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    description = models.TextField()
    rating = models.FloatField(null=True)
    image_url = models.URLField()
    book_url  = models.URLField(unique=True)