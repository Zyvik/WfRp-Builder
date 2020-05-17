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
    tokens = models.PositiveIntegerField(default=13)
    columns = models.PositiveIntegerField(default=7)
    rows = models.PositiveIntegerField(default=10)
    map = models.TextField(max_length=1000)

    def __str__(self):
        return f"Map: {self.game}"

    def create_blank_map(self):
        token_range = range(self.tokens+1)
        token_list = list(map(str, token_range))  # turn range into list of str
        fields = [str(self.tokens)] * (self.columns * self.rows)  # empty_space
        map_string = ','.join(token_list + fields)
        return map_string


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
    map_object = MapModel(game=instance)
    map_object.map = map_object.create_blank_map()
    map_object.save()
