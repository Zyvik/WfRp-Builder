from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


class GameModel(models.Model):
    name = models.CharField(max_length=30)
    admin = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.admin})"


class MessagesModel(models.Model):
    game = models.ForeignKey(GameModel, on_delete=models.CASCADE)
    author = models.TextField(max_length=100)
    message = models.TextField(max_length=1000)

    def __str__(self):
        return f"message {self.pk} in {self.game}"


class MapModel(models.Model):
    game = models.OneToOneField(GameModel, on_delete=models.CASCADE)
    map = models.TextField(max_length=1000)

    def __str__(self):
        return f"Map: {self.game}"


class NPCModel(models.Model):
    game = models.ForeignKey(GameModel, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    WW = models.IntegerField()
    US = models.IntegerField()
    notes = models.TextField(max_length=1000)

    def __str__(self):
        return f"NPC {self.name} in {self.game}"


# Create MapModel for created game
@receiver(post_save, sender=GameModel)
def create_map(sender, instance, **kwargs):
    token_range = range(14)  # 0-12 are tokens, 13 is empty space
    tokens = list(map(str, token_range))  # turn range into list of str
    fields = ['13'] * (7*10)  # empty_space * (columns*rows)
    map_string = ','.join(tokens + fields)
    MapModel.objects.create(game=instance, map=map_string)
