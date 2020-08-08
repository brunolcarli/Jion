from django.db import models


class Emotion(models.Model):
    reference = models.CharField(max_length=100, null=False, blank=False)
    pleasantness = models.FloatField(default=0)
    attention = models.FloatField(default=0)
    sensitivity = models.FloatField(default=0)
    aptitude = models.FloatField(default=0)


class Quote(models.Model):
    reference = models.CharField(max_length=100, null=False, blank=False)
    quote = models.TextField(null=False, blank=False)
    author = models.CharField(max_length=100, null=False, blank=False)
    date = models.DateField(auto_now_add=True)
