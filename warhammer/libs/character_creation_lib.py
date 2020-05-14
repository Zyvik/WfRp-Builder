from django.core.exceptions import ObjectDoesNotExist
from warhammer import models as m


def get_starting_professions(race):
    """
    Gets starting professions for provided race
    """
    race_dict = {
        1: m.HumanStartingProfession.objects.all,
        2: m.ElfStartingProfession.objects.all,
        3: m.DwarfStartingProfession.objects.all,
        4: m.HalflingStartingProfession.objects.all
    }
    professions = race_dict.get(race.pk, m.HumanStartingProfession.objects.all)
    professions = professions().order_by('profession')
    return professions


class CharacterCustomizeForm:
    all_skills = m.SkillsModel.objects.all()
    all_abilities = m.AbilitiesModel.objects.all()

    def __init__(self, race, stats_form):
        self.race = race
        self.profession_index = stats_form.cleaned_data['prof']
        self.starting_professions = get_starting_professions(race)
        self.profession = self.get_exact_profession()
        self.character_stats = create_character_stats(stats_form, race)
        self.develop_stats_form, self.prof_stats = self.prepare_develop_stat_form()
        self.random_table, self.race_counter = self.prepare_random_ability_table()
        self.stats_table = self.prepare_stats_table()

        self.prof_s_radio, self.prof_s_free, self.prof_s_raw = prepare_skill_form(
            skill_string=self.profession.skills,
            object_list=self.all_skills,
            name='prof_skills'
        )
        self.race_s_radio, self.race_s_free, self.race_s_raw = prepare_skill_form(
            skill_string=self.race.skills,
            object_list=self.all_skills,
            name='race_skills'
        )
        self.prof_a_radio, self.prof_a_free, self.prof_a_raw = prepare_skill_form(
            skill_string=self.profession.abilities,
            object_list=self.all_abilities,
            name='prof_abilities'
        )
        self.race_a_radio, self.race_a_free, self.race_a_raw = prepare_skill_form(
            skill_string=self.race.abilities,
            object_list=self.all_abilities,
            name='race_abilities'
        )

    def get_exact_profession(self):
        """
        Gets profession from provided "table"
        """
        for prof in self.starting_professions:
            # check if index is in range if roll_range is actually range
            if '-' in prof.roll_range:
                roll_range = prof.roll_range.split('-')
                start = int(roll_range[0])
                end = int(roll_range[1]) + 1
                if self.profession_index in range(start, end):
                    return prof.profession
            # if roll_range is not range:
            elif self.profession_index == int(prof.roll_range):
                return prof.profession

    def prepare_develop_stat_form(self):
        class DevelopStat:
            stat = None
            bonus = None

        all_stats = m.StatsModel.objects.all()
        prof_stats = self.profession.stats.split('\n')
        develop_stat_inputs = []
        for i, stat in enumerate(all_stats):
            prof_stats[i] = prof_stats[i].replace('\r', '')
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

    def prepare_random_ability_table(self):
        # random abilities
        race_dict = {1: 2, 4: 1}
        race_counter = race_dict.get(self.race.pk, 0)

        random_table = []
        if race_counter > 0:
            random_table = m.RandomAbilityModel.objects.filter(race=self.race)
            random_table = random_table.order_by('roll_range')
        return random_table, race_counter

    def prepare_stats_table(self):
        class StatDisplay:
            stat = ''
            value = ''

        all_stats = m.StatsModel.objects.all()
        stats_table = []
        for i, stat in enumerate(all_stats, 0):
            maslo = StatDisplay()
            maslo.stat = stat
            maslo.value = self.character_stats[i]
            stats_table.append(maslo)
        return stats_table


def prepare_skill_form(skill_string, object_list, name):
    """
    Skills in ProfessionModel are separated by '\n'.
    Skills can be separated by '/' - then you can choose between skills
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
    # radio buttons now have modals in them
    radio_buttons = create_modal_links(object_list, radio_buttons)
    # its now list of HTML <a> elements
    free_skills = create_modal_links(object_list, free_skills)
    return radio_buttons, free_skills, raw_skills


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
            radio = f"<label><input required class=\"mr-2\" type=\"radio\" " \
                    f"value=\"{choice.upper()}\" name=\"{index}_{name}\">" \
                    f"{choice}</label>"
            inputs.append(radio)
        radio_buttons.append(' / '.join(inputs))
    return radio_buttons


def create_modal_links(all_skill_list, user_skill_list):
    """
    Returns list of <a> tags containing HTML to trigger modals
    """
    radio_string = '\n'.join(user_skill_list)
    for skill in all_skill_list:
        modal_link = f"<a href=\"#\" data-toggle=\"modal\" " \
                     f"data-target=\"#{skill.slug}\">{skill.name}</a>"
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
    basic_stats = m.StatsModel.objects.filter(is_secondary=False)
    for i, stat in enumerate(basic_stats, 0):
        base = m.StartingStatsModel.objects.get(race=race, stat=stat)
        value = base.base + clean_stats[i]
        character_stats.append(value)

    # secondary stats
    character_stats.append(1)  # A - all characters start with 1 attack
    character_stats.append(get_zyw_value(clean_stats[8], race))  # final zyw
    character_stats.append(int(character_stats[2] / 10))  # S
    character_stats.append(int(character_stats[3] / 10))  # Wt
    sz = m.StartingStatsModel.objects.get(race=race, stat=13)
    character_stats.append(sz.base)  # Sz
    character_stats.append(0)  # Mag
    character_stats.append(0)  # PO
    character_stats.append(get_pp_value(clean_stats[9], race))  # PP

    return character_stats


def get_zyw_value(roll, race):
    vit = m.VitalityModel.objects.get(race=race)
    if roll in range(1, 4):
        return vit.v_1_3
    if roll in range(4, 7):
        return vit.v_4_6
    if roll in range(7, 10):
        return vit.v_7_9
    return vit.v_10


def get_pp_value(roll, race):
    fate = m.FateModel.objects.get(race=race)
    if roll in range(1, 5):
        return fate.f_1_4
    if roll in range(5, 8):
        return fate.f_5_7
    return fate.f_8_10


"""For POST"""


def create_new_character(request, customize_form):
    name = request.POST.get('name', 'your_name')
    equipment = request.POST.get('eq', 'nic')
    coins = clean_coins(request.POST.get('coins', '0'))

    new_character = m.CharacterModel(
        name=name,
        profession=customize_form.profession,
        race=customize_form.race,
        equipment=equipment,
        coins=coins,
        user=request.user if request.user.is_authenticated else None
    )
    new_character.save()

    sel_prof_s, sel_race_s = clean_selected_skills(request, 'skills',
                                                   customize_form.prof_s_radio,
                                                   customize_form.race_s_radio)

    sel_prof_a, sel_race_a = clean_selected_skills(request, 'abilities',
                                                   customize_form.prof_a_radio,
                                                   customize_form.race_a_radio)

    random_abilities = clean_random_abilities(request,
                                              customize_form.race_counter,
                                              customize_form.random_table)

    selected_abilities = customize_form.prof_a_raw \
                         + customize_form.race_a_raw + sel_prof_a \
                         + sel_race_a + random_abilities

    save_abilities(selected_abilities, new_character)
    save_skills(customize_form.race_s_raw + sel_race_s, new_character, 'race')
    save_skills(customize_form.prof_s_raw + sel_prof_s, new_character, 'profession')
    save_stats(customize_form.character_stats, new_character, customize_form.prof_stats, request)
    return new_character


def clean_coins(coins_string):
    try:
        coins = int(coins_string)
        if coins in range(2, 21):
            return coins * 240
    except ValueError:
        pass
    return 0


def clean_selected_skills(request, kind, prof_list, race_list):
    # or abilities
    selected_prof_skills = []
    for i in range(0, len(prof_list)):
        prof_skill = request.POST.get(f'{i}_prof_{kind}', None)
        if prof_skill:
            selected_prof_skills.append(prof_skill)

    selected_race_skills = []
    for i in range(0, len(race_list)):
        race_skill = request.POST.get(f'{i}_race_{kind}', None)
        if race_skill:
            selected_race_skills.append(race_skill)
    return selected_prof_skills, selected_race_skills


def clean_random_abilities(request, race_counter, random_table):
    random_abilities = []
    try:
        if race_counter >= 1:
            random_ability = request.POST.get('0_random_ability')
            random_abilities.append(int(random_ability))
        if race_counter == 2:
            random_ability = request.POST.get('1_random_ability')
            random_abilities.append(int(random_ability))
    except ValueError:
        pass

    for i, ability in enumerate(random_abilities):
        if ability in range(1, 101):
            for value in random_table:
                range_list = value.roll_range.split('-')
                if ability in range(int(range_list[0]), int(range_list[1])+1):
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
            try:
                skill = m.SkillsModel.objects.get(name=skill)
                char_skill, created = m.CharacterSkills.objects.get_or_create(
                    character=character,
                    skill=skill,
                    bonus=bonus
                )
                if source == 'race':
                    char_skill.is_developed = False
                if not created:
                    char_skill.level += 10
                    char_skill.is_developed = True
                char_skill.save()
            except ObjectDoesNotExist:
                pass


def save_abilities(selected_abilities, character):
    for i, skill in enumerate(selected_abilities, 0):
        # wtf is '2' or '1' ? - have no idea, will leave it here just in case
        if skill != '' or skill[0] != '2' or skill[0] != '1':
            bonus = None
            skill = skill.lower()
            skill = skill.replace(skill[0], skill[0].upper(), 1)
            if skill.find('(') != -1:
                skill = skill.split('(')
                bonus = '(' + skill[1]
                skill = skill[0][:-1]
            if skill[-1] == '\r':
                skill = skill[:-1]

            try:
                skill = m.AbilitiesModel.objects.get(name=skill)
                char_skill = m.CharacterAbilities.objects.get_or_create(
                    character=character,
                    ability=skill,
                    bonus=bonus
                )
                char_skill.save()
            except (ObjectDoesNotExist, AttributeError):
                pass


def save_stats(character_stats, character, prof_stats, request):
    short = request.POST.get('develop_stat', 'WW')
    # you lose free stat development if you f*ck with HTML
    try:
        developed_stat = m.StatsModel.objects.get(short=short)
    except ObjectDoesNotExist:
        developed_stat = None

    all_stats = m.StatsModel.objects.all()
    for i, stat in enumerate(all_stats, 0):
        add_stat = m.CharactersStats(
            character=character,
            stat=stat,
            base=character_stats[i],
            max_bonus=int(prof_stats[i]),
            bonus=0
        )
        if stat == developed_stat and add_stat.max_bonus > 0:
            if stat.is_secondary:
                add_stat.bonus = 1
            else:
                add_stat.bonus = 5
        add_stat.save()
