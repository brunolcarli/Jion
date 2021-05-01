from django.db import models


class Emotion(models.Model):
    reference = models.CharField(max_length=100, null=False, blank=False)
    pleasantness = models.FloatField(default=0)
    attention = models.FloatField(default=0)
    sensitivity = models.FloatField(default=0)
    aptitude = models.FloatField(default=0)


class Quote(models.Model):
    reference = models.CharField(max_length=100, null=False, blank=False)
    quote = models.BinaryField(null=False)
    author = models.CharField(max_length=100, null=False, blank=False)
    date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ['reference', 'quote']


class User(models.Model):
    reference = models.CharField(max_length=100, null=False, blank=False)
    name = models.CharField(max_length=100)
    friendshipness = models.FloatField(default=0.0)
    emotion_resume = models.ForeignKey(Emotion, on_delete=models.CASCADE, null=True)


class Message(models.Model):
    reference = models.CharField(max_length=100, null=False, blank=False)
    global_intention = models.CharField(max_length=25)
    specific_intention = models.CharField(max_length=50)
    text = models.BinaryField(null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    message_datetime = models.DateTimeField(auto_now_add=True)
    possible_responses = models.ManyToManyField("self")

    class Meta:
        unique_together = ['reference', 'text']
