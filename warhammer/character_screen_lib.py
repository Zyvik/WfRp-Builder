def update_exp(exp_value, character):
    character.current_exp += exp_value
    character.total_exp += exp_value
    character.save()