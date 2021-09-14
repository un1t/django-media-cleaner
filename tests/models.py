from django.db import models


class Post(models.Model):
    text = models.TextField()
    photo = models.ImageField(blank=True)
    attachment = models.FileField(blank=True)


class Product(models.Model):
    name = models.CharField(max_length=100)
    photo = models.ImageField(blank=True)
