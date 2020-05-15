from django.db import models
from django.contrib.auth.models import User


class GameModel(models.Model):
    name = models.CharField(max_length=30)
    admin = models.ForeignKey(User, on_delete=models.CASCADE)


class MessagesModel(models.Model):
    game = models.ForeignKey(GameModel, on_delete=models.CASCADE)
    author = models.TextField(max_length=100)
    message = models.TextField(max_length=1000)


class MapModel(models.Model):
    game = models.OneToOneField(GameModel, on_delete=models.CASCADE)
    map = models.TextField(max_length=1000)
    counter = models.IntegerField(default=1)


class NPCModel(models.Model):
    game = models.ForeignKey(GameModel, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    WW = models.IntegerField()
    US = models.IntegerField()
    notes = models.TextField(max_length=1000)
