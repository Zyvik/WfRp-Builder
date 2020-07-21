import uuid
from django.db import models
from django.contrib.auth.models import User


class StatsModel(models.Model):
    name = models.CharField(max_length=30)
    short = models.CharField(max_length=10)
    description = models.TextField(max_length=500)
    is_secondary = models.BooleanField(default=False)

    name_en = models.CharField(max_length=30, blank=True, null=True)
    short_en = models.CharField(max_length=10, blank=True, null=True)
    description_en = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        name = self.short
        name += ' (secondary)' if self.is_secondary else ''
        return name


class RaceModel(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField(max_length=2000)
    slug = models.CharField(max_length=30)
    skills = models.TextField(max_length=2000)
    abilities = models.TextField(max_length=2000)

    name_en = models.CharField(max_length=30, blank=True, null=True)
    description_en = models.CharField(max_length=2000, blank=True, null=True)

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
        return f"{self.race} {self.stat}"


class ProfessionModel(models.Model):
    name = models.CharField(max_length=50)
    stats = models.TextField(max_length=2000)
    skills = models.TextField(max_length=2000)
    abilities = models.TextField(max_length=2000)
    equipment = models.TextField(max_length=2000)
    next_profession = models.TextField(max_length=2000)
    is_starting = models.BooleanField(default=True)
    slug = models.CharField(max_length=50, default='slimak')

    name_en = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return self.name


class SkillsModel(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=2000)
    stat = models.ForeignKey(StatsModel, on_delete=models.CASCADE)
    is_basic = models.BooleanField(default=True)
    slug = models.CharField(max_length=50, default='slimak')

    name_en = models.CharField(max_length=30, blank=True, null=True)
    description_en = models.CharField(max_length=2000, blank=True, null=True)

    def __str__(self):
        return self.name


class AbilitiesModel(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=2000)
    slug = models.CharField(max_length=50, default='slimak')

    name_en = models.CharField(max_length=30, blank=True, null=True)
    description_en = models.CharField(max_length=2000, blank=True, null=True)

    def __str__(self):
        return self.name


class HumanStartingProfession(models.Model):
    profession = models.ForeignKey(ProfessionModel, on_delete=models.CASCADE)
    roll_range = models.CharField(max_length=10)

    def __str__(self):
        return f"Human {self.profession} {self.roll_range}"


class DwarfStartingProfession(models.Model):
    profession = models.ForeignKey(ProfessionModel, on_delete=models.CASCADE)
    roll_range = models.CharField(max_length=10)

    def __str__(self):
        return f"Dwarf {self.profession} {self.roll_range}"


class ElfStartingProfession(models.Model):
    profession = models.ForeignKey(ProfessionModel, on_delete=models.CASCADE)
    roll_range = models.CharField(max_length=10)

    def __str__(self):
        return f"Elf {self.profession} {self.roll_range}"


class HalflingStartingProfession(models.Model):
    profession = models.ForeignKey(ProfessionModel, on_delete=models.CASCADE)
    roll_range = models.CharField(max_length=10)

    def __str__(self):
        return f"Halfling {self.profession} {self.roll_range}"


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

    def __str__(self):
        return f"{self.name}, {self.race}, {self.profession}, ({self.user})"


class CharacterSkills(models.Model):
    character = models.ForeignKey(CharacterModel, on_delete=models.CASCADE)
    skill = models.ForeignKey(SkillsModel, on_delete=models.CASCADE)
    bonus = models.CharField(max_length=50, blank=True, null=True)
    level = models.IntegerField(default=0)
    is_developed = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.pk} {self.skill.name} {self.character.name}"


class CharactersStats(models.Model):
    character = models.ForeignKey(CharacterModel, on_delete=models.CASCADE)
    stat = models.ForeignKey(StatsModel, on_delete=models.CASCADE)
    base = models.IntegerField()
    bonus = models.IntegerField()
    max_bonus = models.IntegerField()

    def __str__(self):
        return f"{self.pk} {self.stat.name} {self.character.name}"


class CharacterAbilities(models.Model):
    character = models.ForeignKey(CharacterModel, on_delete=models.CASCADE)
    ability = models.ForeignKey(AbilitiesModel, on_delete=models.CASCADE)
    bonus = models.CharField(max_length=50, blank=True, null=True)
    stat = models.ForeignKey(StatsModel, on_delete=models.CASCADE, blank=True, null=True)
    stat_bonus = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.pk} {self.ability} {self.character.name}"


class RandomAbilityModel(models.Model):
    race = models.ForeignKey(RaceModel, on_delete=models.CASCADE)
    ability = models.ForeignKey(AbilitiesModel, on_delete=models.CASCADE)
    roll_range = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.race} {self.roll_range}"
