def update_exp(exp_value, character):
    character.current_exp += exp_value
    character.total_exp += exp_value
    character.save()


def update_coins(cleaned_data, character):
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
        return True
    return False
