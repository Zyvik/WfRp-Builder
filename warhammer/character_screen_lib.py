from django.core.exceptions import ObjectDoesNotExist
from warhammer import models, forms


def get_coins(character):
    """
    Prepare coins to display
    :param character: models.CharacterModel object
    :return: [gold, silver, bronze]
    """
    zk = int(character.coins / 240)
    s = int((character.coins - zk * 240) / 12)
    p = int(character.coins - zk * 240 - s * 12)
    return [zk, s, p]


def update_exp(request, character):
    """
    Updates character's exp
    :param request:
    :param character: models.CharacterModel object
    :return: None
    """
    form = forms.ExperienceForm(request.POST)
    if form.is_valid():
        exp_value = form.cleaned_data['exp']
        character.current_exp += exp_value
        character.total_exp += exp_value
        character.save()
        return None
    return 'HTML'


def update_coins(request, character):
    """
    Updates coins and returns error code
    :param request:
    :param character: models.CharacterModel object
    :return: str - error code
    """
    coins_form = forms.CoinsForm(request.POST)
    if coins_form.is_valid():
        cleaned_data = coins_form.cleaned_data
        zk = cleaned_data.get('gold', 0)
        s = cleaned_data.get('silver', 0)
        p = cleaned_data.get('bronze', 0)

        # getting rid of NoneType
        zk = zk if zk else 0
        s = s if s else 0
        p = p if p else 0

        new_coins = zk*240 + s*12 + p
        new_coins = character.coins + new_coins
        if new_coins >= 0:
            character.coins = new_coins
            character.save()
            return None
        return '1'  # negative coins
    return 'HTML'


def edit_eq(request, character):
    eq_form = forms.EquipmentForm(request.POST)
    if eq_form.is_valid():
        character.equipment = eq_form.cleaned_data.get('eq')
        character.save()
        return None
    return 'HTML'  #


def edit_notes(request, character):
    notes_form = forms.NotesForm(request.POST)
    if notes_form.is_valid():
        character.notes = notes_form.cleaned_data.get('notes')
        character.save()
        return None
    return 'HTML'


def remove_skill(request, character):
    """

    :param request:
    :param character: models.CharacterModel object
    :return: str - error code
    """
    skill_pk = request.POST.get('remove_skill')
    try:
        skill_pk = int(skill_pk)
    except ValueError:
        return '420'  # error code

    try:
        skill_to_removal = models.CharacterSkills.objects.get(pk=skill_pk)
    except(ValueError, TypeError, ObjectDoesNotExist):
        return '2'  # 'Nie istniejąca umiejetność

    if skill_to_removal.character == character:
        skill_to_removal.delete()
        return None
    return '3'  # 'Próbujesz usunąć umiejętność która nie należy do tego Bohatera.'


def add_skill(request, character):
    """

    :param request:
    :param character: CharacterModel object
    :return: str - error code
    """
    add_skill_form = forms.AddSkillForm(request.POST)
    if add_skill_form.is_valid() and request.POST.get('add_skill'):
        skill_pk = add_skill_form.cleaned_data.get('add_skill')
        bonus = add_skill_form.cleaned_data.get('skill_bonus')
        try:
            skill_to_add = models.SkillsModel.objects.get(pk=skill_pk)
        except ObjectDoesNotExist:
            return '4'  # Skill doesnt exist

        new_skill = models.CharacterSkills(
            skill=skill_to_add,
            bonus=bonus,
            character=character
        )
        new_skill.save()
        return None
    return '5'  # choose valid skill


def remove_ability(request, character):
    """

    :param request: string representation of int
    :param character: models.CharacterModel object
    :return: str - error code
    """
    ability_pk = request.POST.get('remove_ability')
    try:
        ability_pk = int(ability_pk)
    except ValueError:
        return '420'  # error code

    try:
        ability = models.CharacterAbilities.objects.get(pk=ability_pk)
    except ObjectDoesNotExist:
        return '2'  # Ability doesnt exists

    if ability.character == character:
        ability.delete()
        return None
    return '3'  # 'Ability doesnt belong to character


def add_ability(request, character):
    """

    :param request: from AddAbilityForm
    :param character: CharacterModel object
    :return: str - error code
    """
    add_ability_form = forms.AddAbilityForm(request.POST)
    if add_ability_form.is_valid() and request.POST.get('add_ability'):
        cleaned_data = add_ability_form.cleaned_data
        ability_pk = cleaned_data.get('add_ability')
        bonus = cleaned_data.get('ability_bonus')
        try:
            ability_to_add = models.AbilitiesModel.objects.get(pk=ability_pk)
        except ObjectDoesNotExist:
            return '4'  # Ability doesnt exist

        new_ability = models.CharacterAbilities(
            ability=ability_to_add,
            bonus=bonus,
            character=character
        )
        new_ability.save()
        return None
    return 'xd'  # Choose valid ability


def edit_stats(request, character):
    error_flag = False
    char_stats = models.CharactersStats.objects.filter(character=character)
    for stat in char_stats:
        try:
            edited_value = int(request.POST.get(stat.stat.short))
        except (ValueError, TypeError):
            return '5'  # Int

        if 0 <= edited_value <= 100:
            stat.base = edited_value
            stat.save()
        else:
            error_flag = True

    return '6' if error_flag else None  # stat outside of <0; 100> range


def change_profession(request, character):
    change_profession_form = forms.ChangeProfessionForm(request.POST)
    if request.POST.get('profession') and change_profession_form.is_valid():
        cleaned_data = change_profession_form.cleaned_data
        new_profession_pk = cleaned_data.get('profession')
        char_stats = models.CharactersStats.objects.filter(character=character)
        char_skills = models.CharacterSkills.objects.filter(character=character)
        try:
            new_profession = models.ProfessionModel.objects.get(pk=new_profession_pk)
        except ObjectDoesNotExist:
            return '7'

        character.profession = new_profession
        # new stats
        new_stats = new_profession.stats.split('\n')
        for new_stat, old_stat in zip(new_stats, char_stats):
            if '-' in new_stat:
                old_stat.max_bonus = 0
                old_stat.save()
            else:
                old_stat.max_bonus = int(new_stat)  # this can result in error...
                old_stat.save()

        for skill in char_skills:
            skill.is_developed = False
            skill.save()

        character.save()
        return None
    return 'x'  # Choose valid option


def develop_stats(request, character):
    char_stats = models.CharactersStats.objects.filter(character=character)
    short = request.POST.get('dev_stat')
    try:
        stat = models.StatsModel.objects.get(short=short)
    except ObjectDoesNotExist:
        return '8'  # this stat doesnt exists

    stat_to_dev = char_stats.get(stat=stat)
    if stat_to_dev.bonus < stat_to_dev.max_bonus and character.current_exp >= 100:
        if stat.is_secondary:
            stat_to_dev.bonus += 1
            stat_to_dev.save()
            character.current_exp -= 100
            character.save()
        else:  # aka. if stat is basic
            if stat.short == 'K' or stat.short == 'Odp':
                pre_val = int((stat_to_dev.base + stat_to_dev.bonus)/10)
                post_val = int((stat_to_dev.base + stat_to_dev.bonus + 5)/10)
                if post_val > pre_val and stat.short == 'K':
                    strength = models.StatsModel.objects.get(short='S')
                    strength = char_stats.get(stat=strength)
                    strength.base += 1
                    strength.save()
                elif post_val > pre_val and stat.short == 'Odp':
                    endurance = models.StatsModel.objects.get(short='Wt')
                    endurance = char_stats.get(stat=endurance)
                    endurance.base += 1
                    endurance.save()
            stat_to_dev.bonus += 5
            stat_to_dev.save()
            character.current_exp -= 100
            character.save()
            return None
    else:
        return '9'  # Not enough exp, or stat already developed to maximum


def get_abilities_to_develop(character, kind):
    """

    :param character:
    :param kind: 'ability' or 'skill'
    :return: [Talent, Talent, ...]
    """
    class Talent:
        """Talent is either skill or ability"""
        name = None
        bonus = None
        object = None
        char_skill_obj = None  # just for skills (if it exists and you develop it skill gets +10)

    talent_dict = {'ability': character.profession.abilities, 'skill': character.profession.skills}

    prof_talents = talent_dict.get(kind)
    prof_talents_str = prof_talents.replace(' / ', '\n')
    prof_talents_list = prof_talents_str.split('\n')

    talent_list = []
    for prof_talent in prof_talents_list:
        prof_talent = prof_talent.replace('\r', '')
        talent = Talent()
        if ' (' in prof_talent:
            prof_talent = prof_talent.split(' (')
            talent.name = prof_talent[0]
            talent.bonus = '(' + prof_talent[1]
        else:
            talent.name = prof_talent

        talent_list.append(talent)
        if kind == 'ability':
            talent.object = models.AbilitiesModel.objects.get(name=talent.name)
            character_abilities = models.CharacterAbilities.objects.filter(character=character)
            for ability in character_abilities:
                if talent.name == ability.ability.name and talent.bonus == ability.bonus:
                    talent_list.pop()
                    break

        else:
            talent.object = models.SkillsModel.objects.get(name=talent.name)
            character_skills = models.CharacterSkills.objects.filter(character=character)
            for skill in character_skills:
                if talent.name == skill.skill.name and talent.bonus == skill.bonus:
                    talent.char_skill_obj = skill
                    if skill.is_developed or skill.level > 15:
                        talent_list.pop()
                        break

    return talent_list


def develop_abilities(request, character):
    if character.current_exp < 100:
        return '10'  # Not enough exp

    abilities_list = get_abilities_to_develop(character, 'ability')
    ability_to_dev = request.POST.get('dev_ability')  # 'AbilityName bonus'

    for ability in abilities_list:
        if f'{ability.name} {ability.bonus}' == ability_to_dev:
            new_ability = models.CharacterAbilities(
                character=character,
                ability=ability.object,
                bonus=ability.bonus
            )
            new_ability.save()
            character.current_exp -= 100
            character.save()
            return None
    return '11'  # 'Sorry, you cant develop this ability'


def develop_skills(request, character):
    if character.current_exp < 100:
        return '10'  # Not enough exp

    skill_list = get_abilities_to_develop(character, 'skill')
    skill_to_dev = request.POST.get('dev_skill')  # 'AbilityName bonus'
    for skill in skill_list:
        if f'{skill.name} {skill.bonus}' == skill_to_dev:
            if skill.char_skill_obj:  # add +10 to level if skill exists
                skill.char_skill_obj.is_developed = True
                skill.char_skill_obj.level += 10
                skill.char_skill_obj.save()
            else:  # create new skill
                print('dziwne')
                new_skill = models.CharacterSkills(
                    character=character,
                    skill=skill.object,
                    bonus=skill.bonus
                )
                new_skill.save()
            character.current_exp -= 100
            character.save()
            return None
    return '12'  # 'Cant develop this skill'


def action_error(request, character):
    return 'HTML'
