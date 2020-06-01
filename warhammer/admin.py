from django.contrib import admin
from . import models as m

# Register your models here.
admin.site.register(m.StatsModel)
admin.site.register(m.RaceModel)
admin.site.register(m.VitalityModel)
admin.site.register(m.FateModel)
admin.site.register(m.StartingStatsModel)
admin.site.register(m.ProfessionModel)
admin.site.register(m.SkillsModel)
admin.site.register(m.HumanStartingProfession)
admin.site.register(m.ElfStartingProfession)
admin.site.register(m.DwarfStartingProfession)
admin.site.register(m.HalflingStartingProfession)
admin.site.register(m.CharacterModel)
admin.site.register(m.CharacterSkills)
admin.site.register(m.AbilitiesModel)
admin.site.register(m.CharacterAbilities)
admin.site.register(m.CharactersStats)
admin.site.register(m.RandomAbilityModel)
