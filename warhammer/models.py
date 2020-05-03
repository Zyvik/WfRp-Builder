from django.db import models
import uuid
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class StatsModel(models.Model):
    name = models.CharField(max_length=30)
    short = models.CharField(max_length=10)
    description = models.TextField(max_length=500)
    is_secondary = models.BooleanField(default=False)

    def __str__(self):
        name = self.short
        if self.is_secondary:
            name += ' (s)'

        return name


class RaceModel(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField(max_length=2000)
    slug = models.CharField(max_length=30)
    skills = models.TextField(max_length=2000)
    abilities = models.TextField(max_length=2000)

    def __str__(self):
        return self.name


class VitalityModel(models.Model):
    race = models.ForeignKey(RaceModel, on_delete=models.CASCADE)
    stat = models.ForeignKey(StatsModel, on_delete=models.CASCADE)
    v_1_3 = models.IntegerField()
    v_4_6 = models.IntegerField()
    v_7_9 = models.IntegerField()
    v_10 = models.IntegerField()

    def __str__(self):
        return str(self.race)


class FateModel(models.Model):
    race = models.ForeignKey(RaceModel, on_delete=models.CASCADE)
    stat = models.ForeignKey(StatsModel, on_delete=models.CASCADE)
    f_1_4 = models.IntegerField()
    f_5_7 = models.IntegerField()
    f_8_10 = models.IntegerField()

    def __str__(self):
        return str(self.race)


class StartingStatsModel(models.Model):
    race = models.ForeignKey(RaceModel, on_delete=models.CASCADE)
    stat = models.ForeignKey(StatsModel, on_delete=models.CASCADE)
    base = models.IntegerField(default=20)
    bonus = models.IntegerField(default=2)  # how many d10 you will roll for bonus

    def __str__(self):
        return str(self.race) + ' ' + str(self.stat)


class ProfessionModel(models.Model):
    name = models.CharField(max_length=50)
    stats = models.TextField(max_length=2000)
    skills = models.TextField(max_length=2000)
    abilities = models.TextField(max_length=2000)
    equipment = models.TextField(max_length=2000)
    next_profession = models.TextField(max_length=2000)
    is_starting = models.BooleanField(default=True)
    slug = models.CharField(max_length=50, default='slimak')

    def __str__(self):
        return self.name


class SkillsModel(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=2000)
    stat = models.ForeignKey(StatsModel, on_delete=models.CASCADE)
    is_basic = models.BooleanField(default=True)
    slug = models.CharField(max_length=50, default='slimak')

    def __str__(self):
        return self.name


class AbilitiesModel(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=2000)
    slug = models.CharField(max_length=50, default='slimak')

    def __str__(self):
        return self.name


class SkillsProfessionMiddle(models.Model):
    profession = models.ForeignKey(ProfessionModel, on_delete=models.CASCADE)
    skill = models.ForeignKey(SkillsModel, on_delete=models.CASCADE)


class HumanStartingProfession(models.Model):
    profession = models.ForeignKey(ProfessionModel, on_delete=models.CASCADE)
    roll_range = models.CharField(max_length=10)

    def __str__(self):
        return self.roll_range


class DwarfStartingProfession(models.Model):
    profession = models.ForeignKey(ProfessionModel, on_delete=models.CASCADE)
    roll_range = models.CharField(max_length=10)


class ElfStartingProfession(models.Model):
    profession = models.ForeignKey(ProfessionModel, on_delete=models.CASCADE)
    roll_range = models.CharField(max_length=10)


class HalflingStartingProfession(models.Model):
    profession = models.ForeignKey(ProfessionModel, on_delete=models.CASCADE)
    roll_range = models.CharField(max_length=10)


class Step1Model(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    WW = models.IntegerField()
    US = models.IntegerField()
    ZR = models.IntegerField()
    K = models.IntegerField()
    Odp = models.IntegerField()
    Int = models.IntegerField()
    SW = models.IntegerField()
    Vit = models.IntegerField()
    PP = models.IntegerField()
    PROF = models.IntegerField()
    string = models. CharField(max_length=150)


class CharacterModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=50)
    race = models.ForeignKey(RaceModel, on_delete=models.CASCADE)
    profession = models.ForeignKey(ProfessionModel, on_delete=models.CASCADE)
    equipment = models.TextField(max_length=5000)
    current_exp = models.IntegerField(default=0)
    total_exp = models.IntegerField(default=0)
    coins = models.IntegerField(default=0)
    notes = models.TextField(max_length=5000, default='NOTATKI')


class CharacterSkills(models.Model):
    character = models.ForeignKey(CharacterModel,on_delete=models.CASCADE)
    skill = models.ForeignKey(SkillsModel, on_delete=models.CASCADE)
    bonus = models.CharField(max_length=50, blank=True, null=True)
    level = models.IntegerField(default=0)
    is_developed = models.BooleanField(default=True)

    def __str__(self):
        return self.skill.name + ' ' + self.character.name


class CharactersStats(models.Model):
    character = models.ForeignKey(CharacterModel, on_delete=models.CASCADE)
    stat = models.ForeignKey(StatsModel, on_delete=models.CASCADE)
    base = models.IntegerField()
    bonus = models.IntegerField()
    max_bonus = models.IntegerField()

    def __str__(self):
        return self.stat.name + ' ' + self.character.name


class CharacterAbilities(models.Model):
    character = models.ForeignKey(CharacterModel,on_delete=models.CASCADE)
    ability = models.ForeignKey(AbilitiesModel, on_delete=models.CASCADE)
    bonus = models.CharField(max_length=50, blank=True, null=True)
    stat = models.ForeignKey(StatsModel, on_delete=models.CASCADE, blank=True, null=True)
    stat_bonus = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.ability) + ' ' + self.character.name


class RandomAbilityModel(models.Model):
    race = models.ForeignKey(RaceModel, on_delete=models.CASCADE)
    ability = models.ForeignKey(AbilitiesModel, on_delete=models.CASCADE)
    roll_range = models.CharField(max_length=10)

    def __str__(self):
        return str(self.race) + str(self.roll_range)

class GameModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=30)
    admin = models.ForeignKey(User, on_delete=models.CASCADE)


class MessagesModel(models.Model):
    game = models.ForeignKey(GameModel, on_delete=models.CASCADE)
    author = models.TextField(max_length=100)
    message = models.TextField(max_length=1000)


class MapModel(models.Model):
    game = models.ForeignKey(GameModel, on_delete=models.CASCADE)
    map = models.TextField(max_length=1000)
    counter = models.IntegerField(default=1)


class NPCModel(models.Model):
    game = models.ForeignKey(GameModel, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    WW = models.IntegerField()
    US = models.IntegerField()
    notes = models.TextField(max_length=1000)

