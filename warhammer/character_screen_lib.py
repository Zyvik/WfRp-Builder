from warhammer import models
from django.core.exceptions import ObjectDoesNotExist


def update_exp(exp_value, character):
    """
    Updates character's exp
    :param exp_value: integer
    :param character: models.CharacterModel object
    :return: None
    """
    character.current_exp += exp_value
    character.total_exp += exp_value
    character.save()


def update_coins(cleaned_data, character):
    """
    Updates coins and returns error code
    :param cleaned_data: CoinsForm cleaned data
    :param character: models.CharacterModel object
    :return: str - error code
    """
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
    return '1'


def remove_skill(skill_pk, character):
    """

    :param skill_pk: string representation of int
    :param character: models.CharacterModel object
    :return: str - error code
    """
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


def add_skill(cleaned_data, character):
    """

    :param cleaned_data: from AddSkillForm
    :param character: CharacterModel object
    :return: str - error code
    """
    skill_pk = cleaned_data.get('add_skill')
    bonus = cleaned_data.get('skill_bonus')
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


def remove_ability(ability_pk, character):
    """

    :param ability_pk: string representation of int
    :param character: models.CharacterModel object
    :return: str - error code
    """
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


def add_ability(cleaned_data, character):
    """

    :param cleaned_data: from AddAbilityForm
    :param character: CharacterModel object
    :return: str - error code
    """
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
