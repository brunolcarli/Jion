from django.db import models


class Emotion(models.Model):
    reference = models.CharField(max_length=100)
    pleasantness = models.FloatField(default=0)
    attention = models.FloatField(default=0)
    sensitivity = models.FloatField(default=0)
    aptitude = models.FloatField(default=0)
