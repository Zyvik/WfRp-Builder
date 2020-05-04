from warhammer import models


"""For GET"""
class DevelopStat():
    stat = ''
    bonus = ''


class StatDisplay():
    stat = ''
    value = ''


def get_starting_professions(race):
    """
    Gets starting professions for provided race
    """
    if race == models.RaceModel.objects.get(pk=1):
        starting_professions = models.HumanStartingProfession.objects.all().order_by('profession')
    elif race == models.RaceModel.objects.get(pk=2):
        starting_professions = models.ElfStartingProfession.objects.all().order_by('profession')
    elif race == models.RaceModel.objects.get(pk=3):
        starting_professions = models.DwarfStartingProfession.objects.all().order_by('profession')
    else:
        starting_professions = models.HalflingStartingProfession.objects.all().order_by('profession')
    return starting_professions


def get_exact_profession(profession_list, index):
    """
    Gets profession from provided "table"
    """
    for prof in profession_list:
        # check if index is in range if roll_range is actually range
        if prof.roll_range.find('-') != -1:
            roll_range = prof.roll_range.split('-')
            if index in range(int(roll_range[0]), int(roll_range[1])+1):
                return prof.profession
        # if roll_range is not range:
        elif index == int(prof.roll_range):
            return prof.profession


def prepare_skill_form(skill_string, object_list, name):
    """
    Skills in ProfessionModel are separated by '\n'.
    Skills can be separated by '/' - then you can choose between two or more skills .
    """
    free_skills = []
    choices = []
    raw_skills = []
    skill_list = skill_string.split('\n')
    for skill in skill_list:
        if ' / ' in skill:
            choices.append(skill)
        else:
            free_skills.append(skill)
            raw_skills.append(skill)
    radio_buttons = create_radio_for_choices(choices, name)
    radio_buttons = create_modal_links(object_list, radio_buttons)  # radio buttons now have modals in them
    free_skills = create_modal_links(object_list, free_skills)  # its now list of HTML <a> elements
    return [radio_buttons, free_skills, raw_skills]


def create_radio_for_choices(skill_choices, name):
    """
    Returns list of string representations of radio button input tags (HTML)
    """
    radio_buttons = []
    for index, skill in enumerate(skill_choices):
        inputs = []
        options = skill.split(' / ')
        for choice in options:
            choice = choice[:-1] if choice[-1] == '\r' else choice
            radio = f"<label><input required class=\"mr-2\" type=\"radio\" value=\"{choice.upper()}\" name=\"{index}_{name}\">{choice}</label>"
            inputs.append(radio)
        radio_buttons.append(' / '.join(inputs))
    return radio_buttons


def create_modal_links(all_skill_list, user_skill_list):
    """
    Returns list of <a> tags containing HTML to trigger modals
    """
    radio_string = '\n'.join(user_skill_list)
    for skill in all_skill_list:
        modal_link = "<a href=\"#\" data-toggle=\"modal\" data-target=\"#" + skill.slug + "\">" + skill.name + "</a>"
        radio_string = radio_string.replace(skill.name, modal_link)

    # check just in case
    radio_list = radio_string.split('\n')
    if radio_list[0] == '':
        radio_list.pop(0)

    return radio_list


def create_character_stats(stats_form, race):
    clean_stats = [
        stats_form.cleaned_data['ww'],
        stats_form.cleaned_data['us'],
        stats_form.cleaned_data['k'],
        stats_form.cleaned_data['odp'],
        stats_form.cleaned_data['int'],
        stats_form.cleaned_data['sw'],
        stats_form.cleaned_data['ogd'],
        stats_form.cleaned_data['zr'],
        stats_form.cleaned_data['zyw'],
        stats_form.cleaned_data['pp'],
        stats_form.cleaned_data['prof'],
    ]
    character_stats = []
    # calculate basic stats
    basic_stats = models.StatsModel.objects.filter(is_secondary=False)
    for i, stat in enumerate(basic_stats, 0):
        base = models.StartingStatsModel.objects.get(race=race, stat=stat)
        value = base.base + clean_stats[i]
        character_stats.append(value)

    # secondary stats
    character_stats.append(1)  # A - all characters start with 1 attack
    character_stats.append(get_zyw_value(clean_stats[8], race))  # final zyw (vitality) value
    character_stats.append(int(character_stats[2] / 10))  # S
    character_stats.append(int(character_stats[3] / 10))  # Wt
    sz = models.StartingStatsModel.objects.get(race=race, stat=13)
    character_stats.append(sz.base)  # Sz
    character_stats.append(0)  # Mag
    character_stats.append(0)  # PO
    character_stats.append(get_pp_value(clean_stats[9], race))  # PP

    return character_stats


def get_zyw_value(roll, race):
    vit = models.VitalityModel.objects.get(race=race)
    if roll in range(1, 4):
        return vit.v_1_3
    if roll in range(4, 7):
        return vit.v_4_6
    if roll in range(7, 10):
        return vit.v_7_9
    return vit.v_10


def get_pp_value(roll, race):
    fate = models.FateModel.objects.get(race=race)
    if roll in range(1, 5):
        return fate.f_1_4
    if roll in range(5, 8):
        return fate.f_5_7
    return fate.f_8_10


def prepare_develop_stat_form(starting_profession):
    """
    Do poprawy
    :param starting_profession:
    :return:
    """
    all_stats = models.StatsModel.objects.all()
    prof_stats = starting_profession.stats.split('\n')
    develop_stat_inputs = []
    for i,stat in enumerate(all_stats, 0):
        prof_stats[i] = prof_stats[i].replace('\r','')
        if prof_stats[i] != '-':
            dev_stat = DevelopStat()
            dev_stat.stat = stat
            if stat.is_secondary:
                dev_stat.bonus = '+1'
            else:
                dev_stat.bonus = '+5'
            develop_stat_inputs.append(dev_stat)
        else:
            prof_stats[i] = 0
    return develop_stat_inputs, prof_stats


def prepare_random_ability_table(race):
    # random abilities
    random_table = []
    race_couter = 0
    if race.pk == 1:
        race_couter = 2
    elif race.pk == 4:
        race_couter = 1

    if race_couter > 0:
        random_table = models.RandomAbilityModel.objects.filter(race=race).order_by('roll_range')
    return random_table, race_couter


def prepare_stats_table(character_stats):
    all_stats = models.StatsModel.objects.all()
    stats_table = []
    for i, stat in enumerate(all_stats, 0):
        maslo = StatDisplay()
        maslo.stat = stat
        maslo.value = character_stats[i]
        stats_table.append(maslo)
    return stats_table


"""For POST"""


def clean_coins(coins_string):
    try:
        coins = int(coins_string)
        if coins in range(2, 21):
            return coins * 240
    except ValueError:
        pass
    return 0


def clean_selected_skills(request, type, prof_list, race_list):
    selected_prof_skills = []
    for i in range(0, len(prof_list)):
        selected_prof_skills.append(request.POST[str(i) + '_prof_' + type])
    selected_race_skills = []
    for i in range(0, len(race_list)):
        selected_race_skills.append(request.POST[str(i) + '_race_' + type])
    return selected_prof_skills, selected_race_skills


def clean_random_abilities(request, race_counter, random_table):
    random_abilities = []
    try:
        if race_counter == 1:
            r_a = request.POST['0_random_ability']
            random_abilities.append(r_a)
        elif race_counter == 2:
            random_abilities.append(int(request.POST['0_random_ability']))
            random_abilities.append(int(request.POST['1_random_ability']))
    except ValueError:
        pass

    for i, ability in enumerate(random_abilities):
        if ability in range(1, 101):
            for value in random_table:
                range_list = value.roll_range.split('-')
                if len(range_list) == 1 and ability == range_list[0]:
                    random_abilities[i] = value.ability.name
                    break
                elif len(range_list) == 2 and ability in range(int(range_list[0]), int(range_list[1])+1):
                    random_abilities[i] = value.ability.name
                    break

    return random_abilities


def save_skills(selected_skills, character, source):
    for i, skill in enumerate(selected_skills, 0):
        if skill:
            skill = skill.lower()
            skill = skill.replace(skill[0], skill[0].upper(), 1)
            bonus = None
            if ' (' in skill:
                skill = skill.split(' (')
                bonus = '(' + skill[1]
                skill = skill[0]
                bonus = bonus[:-1] if bonus[-1] == '\r' else bonus

            skill = skill[:-1] if skill[-1] == '\r' else skill
            skill = models.SkillsModel.objects.get(name=skill)
            char_skill, created = models.CharacterSkills.objects.get_or_create(character=character, skill=skill,
                                                                               bonus=bonus)
            char_skill.is_developed = False
            if not created:
                char_skill.level += 10
                char_skill.is_developed = True if source == 'profession' else False
            try:
                char_skill.save()
            except:
                pass


def save_abilities(selected_abilities, character):
    for i, skill in enumerate(selected_abilities, 0):
        # wtf is '2' or '1' ? xD - have no idea, will leave it here in case its important
        if skill != '' or skill[0] != '2' or skill[0] != '1':
            bonus = None  # Can abilities even have bonuses?
            skill = skill.lower()
            skill = skill.replace(skill[0], skill[0].upper(), 1)
            if skill.find('(') != -1:
                skill = skill.split('(')
                bonus = '(' + skill[1]
                skill = skill[0][:-1]
            if skill[-1] == '\r':
                skill = skill[:-1]

            try:
                skill = models.AbilitiesModel.objects.get(name=skill)
                char_skill = models.CharacterAbilities.objects.get_or_create(character=character, ability=skill,
                                                                             bonus=bonus)
                char_skill.save()
            except:
                pass


def save_stats(character_stats, character, prof_stats, request):
    developed_stat = models.StatsModel.objects.get(short=request.POST['develop_stat'])
    all_stats = models.StatsModel.objects.all()
    for i, stat in enumerate(all_stats, 0):
        add_stat = models.CharactersStats(
            character=character,
            stat=stat,
            base=character_stats[i]
        )
        add_stat.character = character
        add_stat.stat = stat
        add_stat.base = character_stats[i]
        add_stat.max_bonus = int(prof_stats[i])
        if stat == developed_stat:
            if stat.is_secondary:
                add_stat.bonus = 1
            else:
                add_stat.bonus = 5
        else:
            add_stat.bonus = 0
        add_stat.save()
