from django.shortcuts import render,redirect,HttpResponse, get_object_or_404
from .models import *
from django.views import View
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .libs import process_string, DevelopStat, StatDisplay, process_string_dev
from django.core.mail import send_mail
import time, requests
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ChatSerializer, MapSerializer
from braces.views import CsrfExemptMixin


def index(request):
    """Landing site"""
    message = None  # error message for claiming existing character
    # if user is logged in display their characters
    if request.user.is_authenticated:
        your_characters = CharacterModel.objects.filter(user=request.user)
    else:
        your_characters = []

    # if logged user claims character check if character exists and isn't claimed
    if request.method == 'POST':
        id = request.POST.get('id','0')
        id = id.replace(' ','')
        try:
            character = CharacterModel.objects.get(pk=id)
            if not character.user:
                character.user = request.user
                character.save()
            else:
                message = 'Ta postać już do kogoś należy.'
        except:
            message = 'Postać o takim identyfikatorze nie istnieje.'

    return render(request, 'warhammer/index.html', {'your_characters':your_characters, 'message':message})


def choose_race(request):
    """Step 1 of character creation - choose race"""
    all_races = RaceModel.objects.all()

    return render(request,'warhammer/rasa.html', {'all_races': all_races})


class RollStats(View):
    """Step 2 of character creation - roll / choose stats and profession"""
    def get(self, request, race_slug):

        race = get_object_or_404(RaceModel,slug=race_slug)  # match race slug to race type
        s_stats = StartingStatsModel.objects.filter(race=race).order_by('-bonus')  # get correct stat bonuses
        # get correct starting professions
        if race == RaceModel.objects.get(pk=1):
            starting_professions = HumanStartingProfession.objects.all().order_by('profession')
        elif race == RaceModel.objects.get(pk=2):
            starting_professions = ElfStartingProfession.objects.all().order_by('profession')
        elif race == RaceModel.objects.get(pk=3):
            starting_professions = DwarfStartingProfession.objects.all().order_by('profession')
        else:
            starting_professions = HalflingStartingProfession.objects.all().order_by('profession')


        return render(request,'warhammer/staty.html', {'s_stats': s_stats,'starting_professions':starting_professions})

    def post(self,request, race_slug):
        race = get_object_or_404(RaceModel,slug=race_slug)
        s_stats = StartingStatsModel.objects.filter(race=race).order_by('-bonus')
        if race == RaceModel.objects.get(pk=1):
            starting_professions = HumanStartingProfession.objects.all().order_by('profession')
        elif race == RaceModel.objects.get(pk=2):
            starting_professions = ElfStartingProfession.objects.all().order_by('profession')
        elif race == RaceModel.objects.get(pk=3):
            starting_professions = DwarfStartingProfession.objects.all().order_by('profession')
        else:
            starting_professions = HalflingStartingProfession.objects.all().order_by('profession')

        # manual validation because apparently I have too much time
        form_is_valid = True
        # this will throw error if user gives string in number input
        try:
            WW = int(request.POST['WW'])
            US = int(request.POST['US'])
            ZR = int(request.POST['ZR'])
            K = int(request.POST['K'])
            Odp = int(request.POST['Odp'])
            Ogd = int(request.POST['Ogd'])
            Int = int(request.POST['Int'])
            SW = int(request.POST['SW'])
            Vit = int(request.POST['Żyw'])
            PP = int(request.POST['PP'])
            PROF = int(request.POST['PROF'])
        except:
            form_is_valid = False

        if form_is_valid:
            verification_list1 = [WW,US,ZR,K,Odp,Int,SW,Ogd]

            # checks if stats are between 2 and 20
            for form_input in verification_list1:
                if form_input not in range(2,21):
                    form_is_valid = False
            # Vit and PP can be between 1 and 10, PROF 1-100 (those have separate tables)
            if Vit not in range(1,11) or PP not in range(1,11) or PROF not in range(1,101):
                form_is_valid = False
            # if there are no mistakes - create temporary entry in database (with stats), and redirect to step 3
            if form_is_valid:
                string = str(WW) + ',' + str(US) + ',' + str(K) + ',' + str(Odp) + ',' + str(ZR) + ',' + str(Int) + ',' + str(SW) + ',' + str(Ogd) + ',' + str(Vit) + ',' + str(PP) + ',' + str(PROF)
                step = Step1Model(WW=WW,US=US,ZR=ZR,K=K,Odp=Odp,Int=Int,SW=SW,Vit=Vit,PP=PP,PROF=PROF, string=string)
                step.save()
                return redirect('wh:custom', race_slug=race_slug, pk=step.pk)
        # there is browser side validation so no need for error message - user has to change HTML to get to this point
        return render(request, 'warhammer/staty.html', {'s_stats': s_stats, 'starting_professions': starting_professions})


def CustomizeCharacter(request,race_slug,pk):
    # Step 3 - choose skills, pick name etc.
    s_time = time.time()
    step1 = get_object_or_404(Step1Model,pk=pk)
    race = get_object_or_404(RaceModel,slug=race_slug)
    starting_profession = ProfessionModel.objects.get(pk=1)  # just in case

    # gets professions table - there are different ones for different races
    if race == RaceModel.objects.get(pk=1):
        starting_professions = HumanStartingProfession.objects.all()
    elif race == RaceModel.objects.get(pk=2):
        starting_professions = ElfStartingProfession.objects.all()
    elif race == RaceModel.objects.get(pk=3):
        starting_professions = DwarfStartingProfession.objects.all()
    else:
        starting_professions = HalflingStartingProfession.objects.all()

    # gets profession from table
    for prof in starting_professions:
        if prof.roll_range.find('-') != -1:  # checks if profession has a range or is single number
            roll_range = prof.roll_range.split('-')
            if step1.PROF in range(int(roll_range[0]), int(roll_range[1])+1):
                starting_profession = prof.profession
                break
        else:
            if step1.PROF == int(prof.roll_range):
                starting_profession = prof.profession
                break

    # creates radio and modals for skills
    all_skills = SkillsModel.objects.all()
    all_abilities = AbilitiesModel.objects.all()

    prof_skills = process_string(starting_profession.skills, all_skills, 'prof_skills')
    race_skills = process_string(race.skills, all_skills, 'race_skills')

    prof_abilities = process_string(starting_profession.abilities, all_abilities, 'prof_abilities')
    race_abilities = process_string(race.abilities, all_abilities, 'race_abilities')
    # process_strings returns list[options_modals, counter, mandatory_modals, mandatory_plain_text, query_set]

    # process stats for display, creating character
    s1 = step1.string.split(',')
    character_stats = []  # its list with ALL current stats (in order)

    # calculates values of basic stats - based on step 2 and selected race
    basic_stats = StatsModel.objects.filter(is_secondary=False)
    for i,stat in enumerate(basic_stats, 0):
        base = StartingStatsModel.objects.get(race=race, stat=stat)
        value = base.base + int(s1[i])
        character_stats.append(value)

    # secondary stats
    character_stats.append(1)  # A
    # Żyw
    vit = VitalityModel.objects.get(race=race)
    vit_roll = int(s1[8])

    # awful, hardcoded table in python
    if vit_roll in range(1,4):
        character_stats.append(vit.v_1_3)
    elif vit_roll in range(4,7):
        character_stats.append(vit.v_4_6)
    elif vit_roll in range(7,10):
        character_stats.append(vit.v_7_9)
    else:
        character_stats.append(vit.v_10)
    character_stats.append(int(character_stats[2]/10))  # S
    character_stats.append(int(character_stats[3]/10))  # Wt
    Sz = StartingStatsModel.objects.get(race=race, stat=13)
    character_stats.append(Sz.base)  # Sz
    character_stats.append(0)  # Mag
    character_stats.append(0)  # PO
    # PP
    fate = FateModel.objects.get(race=race)
    fate_roll = int(s1[9])

    # another hardcoded table xD
    if fate_roll in range(1, 5):
        character_stats.append(fate.f_1_4)
    elif fate_roll in range(5, 8):
        character_stats.append(fate.f_5_7)
    else:
        character_stats.append(fate.f_8_10)

    # Develop stat form - when creating character you can develop one stat for free
    all_stats = StatsModel.objects.all()
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

    # random abilities - humans get 2 random abilities, halfligs get 1
    random_table = []
    race_couter = 0  # how many random abilities character gets
    if race.pk == 1:
        race_couter = 2
    elif race.pk == 4:
        race_couter = 1

    if race_couter > 0:
        random_table = RandomAbilityModel.objects.filter(race=race).order_by('roll_range')

    # its just for displaying stats in template
    stats_table =[]
    for i,stat in enumerate(all_stats,0):
        maslo = StatDisplay()
        maslo.stat = stat
        maslo.value = character_stats[i]
        stats_table.append(maslo)

    # Query Set for MODALS (actually its list)
    qs_skills = race_skills[4] + prof_skills[4]
    qs_abilities = race_abilities[4] + prof_abilities[4]

    equipment = starting_profession.equipment + '\n ubranie podróżne, sztylet, wybrana broń jednoręczna, plecak z podstawowym wyposażeniem'

    ##########################  POST   ###########################################
    if request.method == 'POST':
        # gets name, eq and coins from form
        name = request.POST.get('name','dlaczego kombinujesz?')
        equipment = request.POST.get('eq','nic')
        coins = request.POST.get('coins','0')

        # verify coins number - if user cheats they get nothing
        try:
            coins = int(coins)
            if coins < 2 or coins > 20:
                coins = 0
            else:
                coins = coins*240
        except:
            coins = 0

        # if user is logged link this character to them
        if request.user.is_authenticated:
            new_character = CharacterModel(name=name, profession=starting_profession, race=race, equipment=equipment, coins=coins, user=request.user)
            new_character.save()
        else:
            new_character = CharacterModel(name=name, profession=starting_profession, race=race, equipment=equipment, coins=coins, user=None)
            new_character.save()

        selected_prof_skills = []
        # creates lists with skills and abilities of user's choice
        for i in range(0, prof_skills[1]):
            selected_prof_skills.append(request.POST[str(i)+'prof_skills'])
        selected_race_skills = []
        for i in range(0, race_skills[1]):
            selected_race_skills.append(request.POST[str(i)+'race_skills'])
        selected_prof_abilities = []
        for i in range(0, prof_abilities[1]):
            selected_prof_abilities.append(request.POST[str(i)+'prof_abilities'])
        selected_race_abilities = []
        for i in range(0, race_abilities[1]):
            selected_race_abilities.append(request.POST[str(i)+'race_abilities'])
        developed_stat = StatsModel.objects.get(short = request.POST['develop_stat'])

        #  random abilities
        random_abilities =[]
        if race_couter == 1:
            r_a = request.POST['0_random_ability']
            random_abilities.append(r_a)
        elif race_couter == 2:
            random_abilities.append(request.POST['0_random_ability'])
            random_abilities.append(request.POST['1_random_ability'])

        # validate random inputs
        for i,ability in enumerate(random_abilities, 0):
            try:
                if int(ability) in range(1,101):
                    for rand in random_table:
                        if rand.roll_range.find('-') != -1:
                            roll_range = rand.roll_range.split('-')
                            if int(ability) in range(int(roll_range[0]), int(roll_range[1]) + 1):
                                random_abilities[i] = rand.ability.name
                                break
                        else:
                            if int(ability) == int(rand.roll_range):
                                random_abilities[i] = rand.ability.name
                                break
            except:
                pass

        # adds skills
        selected_skills = race_skills[3] + selected_race_skills
        for i, skill in enumerate(selected_skills, 0):
            if skill == '':
                pass
            else:
                skill = skill.lower()
                skill = skill.replace(skill[0], skill[0].upper(),1)  # change 1st letter to capital
                bonus = None  # bonus is word in brackets ex: Language(Polish) - Language is skill, Polish - bonus
                if skill.find(' (') != -1:
                    skill = skill.split(' (')
                    bonus = '(' + skill[1]
                    skill = skill[0]
                    if bonus[-1] =='\r':
                        bonus = bonus[:-1]
                if skill[-1] == '\r':
                    skill = skill[:-1]
                a_skill = SkillsModel.objects.get(name=skill)
                char_skill, created = CharacterSkills.objects.get_or_create(character=new_character, skill=a_skill,bonus=bonus)
                char_skill.is_developed = False
                if not created:
                    char_skill.level += 10
                try:
                    char_skill.save()
                except:
                    pass

        # repeated code!!!!
        selected_skills = prof_skills[3] + selected_prof_skills #
        for i, skill in enumerate(selected_skills, 0):
            if skill == '':
                pass
            else:
                skill = skill.lower()
                skill = skill.replace(skill[0], skill[0].upper(),1)
                bonus = None
                if skill.find(' (') != -1:
                    skill = skill.split(' (')
                    bonus = '(' + skill[1]
                    skill = skill[0]
                    if bonus[-1] =='\r':
                        bonus = bonus[:-1]
                if skill[-1] == '\r':
                    skill = skill[:-1]
                a_skill = SkillsModel.objects.get(name=skill)
                char_skill, created = CharacterSkills.objects.get_or_create(character=new_character, skill=a_skill,bonus=bonus)
                if not created:
                    char_skill.level += 10
                    char_skill.is_developed = True
                try:
                    char_skill.save()
                except:
                    pass

        # adds abilities
        selected_abilities = prof_abilities[3] + race_abilities[3] + selected_prof_abilities + selected_race_abilities + random_abilities
        for i, skill in enumerate(selected_abilities, 0):
            if skill == '' or skill[0] == '2' or skill[0] == '1':
                pass
            else:
                bonus = None
                skill = skill.lower()
                skill = skill.replace(skill[0], skill[0].upper(),1)
                if skill.find('(') != -1:
                    skill = skill.split('(')
                    bonus = '(' + skill[1]
                    skill = skill[0][:-1]
                if skill[-1] == '\r':
                    skill = skill[:-1]

                try:
                    skill = AbilitiesModel.objects.get(name=skill)
                    char_skill = CharacterAbilities.objects.get_or_create(character=new_character, ability=skill, bonus=bonus)
                    char_skill.save()
                except:
                    pass

        # adds stats
        for i,stat in enumerate(all_stats,0):
            add_stat = CharactersStats()
            add_stat.character = new_character
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

        return redirect('wh:character_screen', pk=new_character.pk)

    context = {
        'profession': starting_profession,
        'mandatory_prof_skills': prof_skills[2],
        'optional_prof_skills': prof_skills[0],
        'mandatory_race_skills': race_skills[2],
        'optional_race_skills': race_skills[0],
        'mandatory_prof_abilities': prof_abilities[2],
        'optional_prof_abilities': prof_abilities[0],
        'mandatory_race_abilities': race_abilities[2],
        'optional_race_abilities': race_abilities[0],
        'character_stats': character_stats,
        'develop_stats': develop_stat_inputs,
        'random_table': random_table,
        'race_counter': race_couter,
        'race': race,
        'all_stats': all_stats,
        'stats_table': stats_table,
        'qs_skills': qs_skills,
        'qs_abilities': qs_abilities,
        't':time.time() - s_time,
        'equipment':equipment
    }

    return render(request, 'warhammer/dostosuj_rase_profesje.html', context)


def professions(request):
    """Displays all professions"""
    all_professions = ProfessionModel.objects.all()
    return render(request, 'warhammer/profesje.html', {'all_professions':all_professions})


def selected_profession(request, profession_slug):
    """displays profession based on slug"""
    prof = get_object_or_404(ProfessionModel, slug=profession_slug)
    all_skills = SkillsModel.objects.all()
    skills_string = prof.skills

    prof_skills = []
    for skill in all_skills:
        modal_link = "<a href=\"#\" data-toggle=\"modal\" data-target=\"#" + skill.slug + "\">" + skill.name + "</a>"
        if skills_string.find(skill.name) != -1:
            skills_string = skills_string.replace(skill.name, modal_link)
            prof_skills.append(skill)

    all_abilities = AbilitiesModel.objects.all()
    abilities_string = prof.abilities
    prof_abilities = []
    for skill in all_abilities:
        modal_link = "<a href=\"#\" data-toggle=\"modal\" data-target=\"#" + skill.slug + "\">" + skill.name + "</a>"
        if abilities_string.find(skill.name) != -1:
            abilities_string = abilities_string.replace(skill.name, modal_link)
            prof_abilities.append(skill)

    stats_list = prof.stats.split('\n')
    all_stats = StatsModel.objects.all()
    prof_stats = []
    prof_stats_bonus = []
    for i,stat in enumerate(all_stats, 0):
        if stats_list[i].replace('\r','') != '-':
            prof_stats.append(stat)
            prof_stats_bonus.append(stats_list[i])
    stats_list = zip(prof_stats,prof_stats_bonus)

    context ={
        'abilities': abilities_string,
        'prof_abilities': prof_abilities,  # abilities objects
        'skills': skills_string,
        'prof_skills': prof_skills,  # skills objects from SkillModel
        'stats_list':stats_list,
        'profession': prof,  # profession object


    }

    return render(request, 'warhammer/profesja_szczegol.html', context )


def character_screen(request, pk):
    """Character screen"""
    character = get_object_or_404(CharacterModel, pk=pk)
    char_stats = CharactersStats.objects.filter(character=character)
    char_skills = CharacterSkills.objects.filter(character=character).order_by('skill')
    char_abilities = CharacterAbilities.objects.filter(character=character).order_by('ability')
    message = None
    if not request.user.is_authenticated:
        message = 'Aktualnie każdy kto ma link do tej postaci jest w stanie dowolnie ją edytować.' \
                  'Jeśli chcesz mieć nad tym kontrolę to zaloguj się i użyj opcji: \'dodaj istniejącego bohatera\' wykorzysująć identyfikator: ' + str(character.pk)

    if character.user and character.user != request.user and not request.user.is_staff:
        return redirect('wh:index')
    develop_stats = char_stats.filter(max_bonus__gt=0)
    dev_basic = []
    dev_secondary =[]
    for stat in develop_stats:
        if stat.stat.is_secondary:
            dev_secondary.append(stat)
        else:
            dev_basic.append(stat)

    prof_abi = process_string_dev(character.profession.abilities,'abilities')
    dev_abi = []
    for prof_ability in prof_abi:
        flag = True
        for char_ability in char_abilities:
            if char_ability.ability.name == prof_ability.name and char_ability.bonus == prof_ability.bonus:
                flag = False
                break
        if flag:
            dev_abi.append(prof_ability)

    prof_skills = process_string_dev(character.profession.skills,'skills')
    dev_skills = []
    for prof_skill in prof_skills:
        flag = True
        for char_skill in char_skills:
            if char_skill.skill.name == prof_skill.name and char_skill.bonus == prof_skill.bonus:
                if char_skill.is_developed or char_skill.level > 15:
                    flag = False
                    break
        if flag:
            dev_skills.append(prof_skill)

    # coins
    zk = int(character.coins / 240)
    s = int((character.coins - zk * 240)/12)
    p = int(character.coins - zk * 240 - s * 12)
    coins = [zk,s,p]

    if request.method == 'POST':
        # Add / subtract PD
        if request.POST.get('PD') == 'PD':
            try:
                value = int(request.POST.get('value_PD'))
                if character.current_exp + value >= 0:
                    character.current_exp += value
                    character.total_exp += value
                    character.save()
                    character = CharacterModel.objects.get(pk=pk)
                else:
                    message = 'Punkty doświadczenia muszą być dodatnie.'
            except(ValueError,TypeError):
                message = 'Dodana / odjęta wartość musi być liczbą całkowitą.'

        # Edit_eq
        if request.POST.get('edit_eq') == 'edit_eq':
            try:
                eq = request.POST['form_eq']
                character.equipment = eq
                character.save()
                character = CharacterModel.objects.get(pk=pk)
            except:
                message = 'Hmmm... Coś poszło nie tak - chyba znalazłeś buga.'

        if request.POST.get('coins') == 'coins':
            zk = request.POST.get('zk', 0)
            s = request.POST.get('s', 0)
            p = request.POST.get('p', 0)
            if not zk:
                zk = 0
            if not s:
                s = 0
            if not p:
                p = 0
            try:
                new_coins = int(zk) * 240 + int(s)*12 + int(p)
                new_coins = character.coins + new_coins
                if new_coins >= 0:
                    character.coins = new_coins
                    character.save()
                    return redirect('wh:character_screen', pk=character.pk)
                else:
                    message = 'Twoje fundusze nie mogą być na minusie.'

            except(ValueError, TypeError):
                message = 'Monety są liczbami całkowitymi...'

        # Edit_stats
        if request.POST.get('edit_stats') == 'edit_stats':
            for stat in char_stats:
                try:
                    edited_value = int(request.POST.get(stat.stat.short))
                    if 0 <= edited_value <= 100:
                        stat.base = edited_value
                        stat.save()
                        char_stats = CharactersStats.objects.filter(character=character)
                    else:
                        message = 'Nie zapisano jednej (bądź więcej) cech, ponieważ podana została liczba spoza przedziału <0, 100>.'
                except (ValueError, TypeError):
                    message = 'Nie zapisano jednej (bądź więcej) cech, ponieważ coś jest nie tak z input\'ami.'

        # Remove skills
        try:
            if request.POST.get('remove_skill').find('remove_skill_') != -1:
                try:
                    skill_pk = request.POST.get('remove_skill').split('remove_skill_')
                    skill_pk = int(skill_pk[1])
                    skill_to_removal = CharacterSkills.objects.get(pk=skill_pk)
                    if skill_to_removal.character == character:
                        skill_to_removal.delete()
                        return redirect('wh:character_screen', pk=character.pk)
                    else:
                        message = 'Próbujesz usunąć umiejętność która nie należy do tego Bohatera.'
                except(ValueError, TypeError, ObjectDoesNotExist):
                    message = 'Próbujesz usunąć umiejętność która nie istnieje.'
        except(AttributeError):
            pass

        # Add skills
        if request.POST.get('add_skill') == 'add_skill':
            try:
                skill_pk = request.POST.get('add_skill_select')
                skill_pk = int(skill_pk)
                skill_to_add = SkillsModel.objects.get(pk=skill_pk)
                skill_to_add_bonus = request.POST.get('add_skill_bonus')
                new_skill = CharacterSkills()
                new_skill.character = character
                new_skill.skill = skill_to_add
                if skill_to_add_bonus:
                    new_skill.bonus = skill_to_add_bonus
                new_skill.save()
                return redirect('wh:character_screen', pk=character.pk)

            except(ValueError, ObjectDoesNotExist, TypeError):
                message = 'Chciałeś dodać nieistniejącą umiejętność. Dziwne...'

        # Remove abilities
        try:
            if request.POST.get('remove_ability').find('remove_ability_') != -1:
                try:
                    ability_pk = request.POST.get('remove_ability').split('remove_ability_')
                    ability_pk = int(ability_pk[1])
                    ability_to_removal = CharacterAbilities.objects.get(pk=ability_pk)
                    if ability_to_removal.character == character:
                        ability_to_removal.delete()
                        return redirect('wh:character_screen', pk=character.pk)
                    else:
                        message = 'Próbujesz usunąć zdolność która nie należy do tego Bohatera.'
                except(ValueError, TypeError, ObjectDoesNotExist):
                    message = 'Próbujesz usunąć zdolność która nie istnieje.'
        except(AttributeError):
            pass

        # Add ability
        if request.POST.get('add_ability') == 'add_ability':
            try:
                ability_pk = request.POST.get('add_ability_select')
                ability_pk = int(ability_pk)
                ability_to_add = AbilitiesModel.objects.get(pk=ability_pk)
                ability_to_add_bonus = request.POST.get('add_ability_bonus')
                new_ability = CharacterAbilities()
                new_ability.character = character
                new_ability.ability = ability_to_add
                if ability_to_add_bonus:
                    new_ability.bonus = ability_to_add_bonus
                new_ability.save()
                return redirect('wh:character_screen', pk=character.pk)

            except(ValueError, ObjectDoesNotExist, TypeError):
                message = 'Chciałeś dodać nieistniejącą umiejętność. Dziwne...'

        # Develop_Stats
        if request.POST.get('dev_stat'):
            try:
                short = request.POST.get('dev_stat')
                stat = StatsModel.objects.get(short=short)
                stat_to_dev = char_stats.get(stat=stat)
                if stat_to_dev.bonus < stat_to_dev.max_bonus and character.current_exp >= 100:
                    if stat.is_secondary:
                        stat_to_dev.bonus += 1
                        stat_to_dev.save()
                        character.current_exp -= 100
                        character.save()
                        character = CharacterModel.objects.get(pk=pk)
                    else:
                        if stat.short == 'K':
                            pre_val = int((stat_to_dev.base + stat_to_dev.bonus)/10)
                            post_val = int((stat_to_dev.base + stat_to_dev.bonus + 5)/10)
                            if post_val > pre_val:
                                krzepa = StatsModel.objects.get(short='S')
                                krzepa = char_stats.get(stat=krzepa)
                                krzepa.base += 1
                                krzepa.save()

                        if stat.short == 'Odp':
                            pre_val = int((stat_to_dev.base + stat_to_dev.bonus)/10)
                            post_val = int((stat_to_dev.base + stat_to_dev.bonus + 5)/10)
                            if post_val > pre_val:
                                krzepa = StatsModel.objects.get(short='Wt')
                                krzepa = char_stats.get(stat=krzepa)
                                krzepa.base += 1
                                krzepa.save()

                        stat_to_dev.bonus += 5
                        stat_to_dev.save()
                        character.current_exp -= 100
                        character.save()
                        character = CharacterModel.objects.get(pk=pk)
                else:
                    message = 'Masz za mało PD żeby rozwinąć jakąkolwiek cechę.'
                develop_stats = char_stats.filter(max_bonus__gt=0)
            except ObjectDoesNotExist:
                message = 'Zmieniałeś coś w inputach?'

        # Develop_Abilities
        if request.POST.get('dev_ability'):
            try:
                abi_index = int(request.POST.get('dev_ability'))
                ability = dev_abi[abi_index]
                new_abi = CharacterAbilities()
                new_abi.character = character
                new_abi.ability = AbilitiesModel.objects.get(name=ability.name)
                if ability.bonus:
                    new_abi.bonus = ability.bonus
                if character.current_exp >= 100:
                    new_abi.save()
                    dev_abi.pop(abi_index)
                    character.current_exp -= 100
                    character.save()
                    character = CharacterModel.objects.get(pk=pk)
                    char_abilities = CharacterAbilities.objects.filter(character=character).order_by('ability')
                else:
                    message = 'Masz za mało PD żeby wykupić tę zdolność'
            except:
                message = 'Dziwne...'

        # Develop_Skills
        if request.POST.get('dev_skill'):
            try:
                skill_index = int(request.POST.get('dev_skill'))
                skill = dev_skills[skill_index]
                exists_developed = False
                if character.current_exp >= 100:
                    for char_skill in char_skills:
                        if skill.name == char_skill.skill.name and skill.bonus == char_skill.bonus:
                            if not char_skill.is_developed:
                                dev_skills.pop(skill_index)
                                char_skill.is_developed = True
                                char_skill.level += 10
                                char_skill.save()
                                character.current_exp -= 100
                                character.save()
                                exists_developed = True
                                break
                            else:
                                exists_developed = True
                                break

                    if not exists_developed:
                        new_skill = CharacterSkills()
                        new_skill.character = character
                        new_skill.skill = SkillsModel.objects.get(name=skill.name)
                        if skill.bonus:
                            new_skill.bonus = skill.bonus
                        new_skill.save()
                        character.current_exp -= 100
                        character.save()
                        character = CharacterModel.objects.get(pk=pk)
                        dev_skills.pop(skill_index)
                    char_skills = CharacterSkills.objects.filter(character=character).order_by('skill')
                else:
                    message = 'Masz za mało PD aby wykupić tę umiejętnosć'
            except (ObjectDoesNotExist, ValueError, IndexError, TypeError):
                pass

        # Edit notes
        if request.POST.get('edit_notes', None):
            try:
                notes = request.POST.get('form_notes', character.notes)
                character.notes = notes
                character.save()
                character = CharacterModel.objects.get(pk=pk)
            except:
                message = 'Hmmm... Coś poszło nie tak - chyba znalazłeś buga.'

        # Change profession
        if request.POST.get('change_profession', None):
            new_profession = request.POST.get('profession', '0')
            try:
                new_profession = ProfessionModel.objects.get(pk=int(new_profession))
                character.profession = new_profession
                # new stats
                new_stats = new_profession.stats.split('\n')
                for i,stat in enumerate(new_stats,0):
                    if stat.find('-') == -1:
                        maslo = char_stats[i]
                        maslo.max_bonus = int(stat)
                        maslo.save()
                    else:
                        maslo = char_stats[i]
                        maslo.max_bonus = 0
                        maslo.save()

                for skill in char_skills:
                    skill.is_developed = False
                    skill.save()

                character.save()
                return redirect('wh:character_screen', pk=character.pk)

            except (ValueError, ObjectDoesNotExist, TypeError):
                pass
    all_professions = ProfessionModel.objects.all()
    all_abilities = AbilitiesModel.objects.all()
    all_skills = SkillsModel.objects.all().order_by('name')
    context = {
        'all_abilities': all_abilities,
        'all_skills': all_skills,
        'all_professions': all_professions,
        'character': character,
        'stats_table': char_stats,
        'char_skills': char_skills,
        'char_abilities': char_abilities,
        'develop_stats': develop_stats,
        'dev_basic': dev_basic,
        'dev_secondary': dev_secondary,
        'dev_abilities': dev_abi,
        'dev_skills': dev_skills,
        'coins': coins,
        'message':message,
        'rows':range(10),
        'columns':range(7)

    }
    return render(request, 'warhammer/bohater.html', context)


def register(request):
    """Register site"""
    if request.user.is_authenticated:
        return redirect('wh:index')
    message = None
    if request.method == 'POST':
        username = request.POST.get('login','nic')
        password = request.POST.get('password','nic')
        r_password = request.POST.get('r_password','nic1')
        mail = request.POST.get('email', 'abc@example.com')

        # login and password requirements:
        if len(username) >= 4 and username.find(' ') == -1:
            if len(password) >= 5:
                if password == r_password:
                    if not User.objects.filter(username__iexact=username).exists():
                        user = User.objects.create_user(username, mail, password)  # creates user
                        user = authenticate(request, username=username, password=password)
                        if user is not None:
                            login(request, user)
                            return redirect('wh:index')
                        return HttpResponse('Udało się!')
                    else:
                        message = 'Login zajęty'
                else:
                    message = 'Hasła muszą byc jednakowe'
            else:
                message = 'Hasło musi mieć minimum 5 znaków'
        else:
            message = 'Login musi mieć minimum 4 znaki i nie może zawierać spacji.'
    return render(request,'warhammer/register.html', {'message':message})


def login_view(request):
    """login site"""
    if request.user.is_authenticated:
        return redirect('wh:index')
    message = None
    if request.method == 'POST':
        username = request.POST.get('login', 'a')
        password = request.POST.get('password', 'a')
        try:
            user = User.objects.get(username__iexact=username)
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                return redirect('wh:index')
            else:
                message = 'Podano złą kombinację loginu i hasła.'
        except ObjectDoesNotExist:
            message = 'Podano złą kombinację loginu i hasła.'
    return render(request,'warhammer/login.html',{'message':message})


def logout_view(request):
    logout(request)
    return redirect('wh:index')


def contact(request):
    message = None
    if request.method == 'POST':
        subject = request.POST.get('subject','no subject')
        email = request.POST.get('email', 'no email')
        content = request.POST.get('content', 'no content') + '\nemail: '+ email
        try:
            send_mail(subject,content,'zyvik.kontakt@wp.pl',['pawel86gw2@gmail.com'])
            message = 'Wiadomość wysłana!'
        except:
            message = 'Coś nie wyszło - wyślij maila na pawel86@gmail.com'

    return render(request,'warhammer/contact.html', {'message':message})

# Dice roller and MAP API
class ChatView(CsrfExemptMixin, APIView):
    """Api view for dice roller and map"""
    authentication_classes = []
    def get(self, request, game_id):
        game = get_object_or_404(GameModel, id=game_id)
        messages = MessagesModel.objects.filter(game=game).order_by('-id')[:15]
        map = MapModel.objects.get(game=game)
        serializer = ChatSerializer(messages, many=True)
        map_serializer = MapSerializer(map, many=False)
        return Response({
            'chat': serializer.data,
            'map': map_serializer.data
        })

    def post(self, request, game_id):
        try:
            if request.data.get('message'):
                MessagesModel.objects.create(
                    game=GameModel.objects.get(id=game_id),
                    author=request.data.get('author'),
                    message=request.data.get('message')
                )
            else:
                game = GameModel.objects.get(id=game_id)
                map_obj = MapModel.objects.get(game=game)
                map_obj.map = request.data.get('map')
                map_obj.counter += 1
                map_obj.save()
        except:
            pass
        return HttpResponse("git majonez")


def game_master_room(request, game_id):
    """Unfinished concept - right now there is one game and no option to create your own"""
    game = get_object_or_404(GameModel, pk=game_id)
    if request.user == game.admin:
        npcs = NPCModel.objects.filter(game=game)
        if request.method == 'POST':
            # Adding NPC's
            if request.POST.get('add_npc'):
                try:
                    NPC = NPCModel(
                        game=game,
                        name=request.POST.get('npc_name', 'boring name'),
                        WW=int(request.POST.get('npc_WW', '0')),
                        US=int(request.POST.get('npc_US', '0')),
                        notes=request.POST.get('npc_notes')
                    )
                    NPC.save()
                except ValueError:
                    pass

            # deleting NPC's
            if request.POST.get('delete_npc'):
                npc = NPCModel.objects.get(pk=int(request.POST.get('delete_npc')))
                # checks if npc belongs to this game
                if npc.game == game:
                    npc.delete()

        return render(request, 'warhammer/DMRoom.html', {'game': game, 'npcs': npcs, 'columns': range(7), 'rows': range(10)})
    else:
        login_error = 'Nie jestesteś mistrzem tej gry - zawróć.'
        return render(request, 'warhammer/DMRoom.html', {'game': game, 'login_error':login_error})


def skills_list(request):
    skills = SkillsModel.objects.order_by("name")
    return render(request, 'warhammer/skills_list.html', {'skills': skills})


def abilities_list(request):
    abilities = AbilitiesModel.objects.all()
    return render(request, 'warhammer/abilities_list.html', {'abilities': abilities})

