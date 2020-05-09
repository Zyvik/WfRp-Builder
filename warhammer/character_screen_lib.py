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
