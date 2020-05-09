from django.shortcuts import render,redirect,HttpResponse, get_object_or_404
from .models import *
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .libs import process_string_dev
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ChatSerializer, MapSerializer

from django.views import View
from .forms import RollStatsForm, RegisterForm, LoginForm, ContactForm, ClaimCharacterForm, ExperienceForm, EquipmentForm, CoinsForm
from .character_creation import get_starting_professions
from . import character_creation
from warhammer import profession_detail_lib as prof_detail
from warhammer import character_screen_lib as csl


class IndexView(View):
    """
    Landing page - displays user's characters and gives option to claim existing character
    """
    def get(self, request):
        if request.user.is_authenticated:
            your_characters = CharacterModel.objects.filter(user=request.user)
            form = ClaimCharacterForm()
            return render(request, 'warhammer/index.html', {'your_characters': your_characters, 'form': form})
        return render(request, 'warhammer/index.html', {'your_characters': None, 'form': None})

    def post(self, request):
        if request.user.is_authenticated:
            message = None
            form = ClaimCharacterForm(request.POST)
            if form.is_valid():
                pk = form.cleaned_data.get('pk')
                try:
                    character = CharacterModel.objects.get(pk=pk)
                    if character.user is None:
                        character.user = request.user
                        character.save()
                        return redirect('wh:index')
                    else:
                        message = 'Ta postać już do kogoś należy.'
                except ObjectDoesNotExist:
                    message = 'Postać o takim identyfikatorze nie istnieje.'
            your_characters = CharacterModel.objects.filter(user=request.user)
            return render(request, 'warhammer/index.html', {'your_characters': your_characters,
                                                            'form': form, 'message': message})
        return render(request, 'warhammer/index.html', {'your_characters': None, 'form': None})


def choose_race(request):
    """
    1st step in character creation - choosing race
    """
    all_races = RaceModel.objects.all()
    return render(request, 'warhammer/race.html', {'all_races': all_races})


def roll_stats(request, race_slug):
    """
    2nd step in character creation - rolling for stats
    """
    stats_form = RollStatsForm(request.GET)
    race = get_object_or_404(RaceModel, slug=race_slug)
    starting_stats = StartingStatsModel.objects.filter(race=race).order_by('-bonus')
    starting_professions = get_starting_professions(race)

    if stats_form.is_valid():
        # preparing form for 3rd step - customizing character
        customize_form = character_creation.CharacterCustomizeForm(race, stats_form)

        if request.method == 'POST':
            new_character = character_creation.create_new_character(request, customize_form)
            return redirect('wh:character_screen', pk=new_character.pk)

        context = {
            'profession': customize_form.profession,
            'mandatory_prof_skills': customize_form.prof_s_free,
            'optional_prof_skills': customize_form.prof_s_radio,
            'mandatory_race_skills': customize_form.race_s_free,
            'optional_race_skills': customize_form.race_s_radio,
            'mandatory_prof_abilities': customize_form.prof_a_free,
            'optional_prof_abilities': customize_form.prof_a_radio,
            'mandatory_race_abilities': customize_form.race_a_free,
            'optional_race_abilities': customize_form.race_a_radio,
            'character_stats': customize_form.character_stats,
            'develop_stats': customize_form.develop_stats_form,
            'random_table': customize_form.random_table,
            'race_counter': customize_form.race_counter,
            'race': race,
            'all_stats': StatsModel.objects.all(),
            'stats_table': customize_form.stats_table,
            'qs_skills': customize_form.all_skills,
            'qs_abilities': customize_form.all_abilities,
            't': 12,
            'equipment': customize_form.profession.equipment
        }

        return render(request, 'warhammer/dostosuj_rase_profesje.html', context)

    return render(request, 'warhammer/roll_stats.html', {'s_stats': starting_stats, 'starting_professions': starting_professions, 'stats_form': stats_form})


def professions(request):
    all_professions = ProfessionModel.objects.all()
    return render(request, 'warhammer/profesje.html', {'all_professions': all_professions})


def selected_profession(request, profession_slug):
    profession = get_object_or_404(ProfessionModel, slug=profession_slug)
    all_skills = SkillsModel.objects.all()
    all_abilities = AbilitiesModel.objects.all()

    skills_string = prof_detail.create_modals(all_skills, profession.skills)
    abilities_string = prof_detail.create_modals(all_abilities, profession.abilities)
    stats_list = prof_detail.prepare_stats_for_display(profession)

    context = {
        'abilities': abilities_string,
        'prof_abilities': all_abilities,  # abilities objects
        'skills': skills_string,
        'prof_skills': all_skills,  # skills objects from SkillModel
        'stats_list': stats_list,
        'profession': profession,  # profession object
    }

    return render(request, 'warhammer/profesja_szczegol.html', context)


def character_screen(request, pk):
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

    exp_form = ExperienceForm()
    eq_form = EquipmentForm(initial={'eq': character.equipment})
    coins_form = CoinsForm()
    if request.method == 'POST':

        # Add / subtract PD
        exp_form = ExperienceForm(request.POST)
        if exp_form.is_valid():
            exp_value = exp_form.cleaned_data.get('exp', 0)
            csl.update_exp(exp_value, character)
            return redirect('wh:character_screen', pk=character.pk)

        # Edit_eq
        eq_form = EquipmentForm(request.POST)
        if eq_form.is_valid():
            character.equipment = eq_form.cleaned_data.get('eq')
            character.save()
            return redirect('wh:character_screen', pk=character.pk)

        # Edit coins
        coins_form = CoinsForm(request.POST)
        if coins_form.is_valid():
            validate_coins = csl.update_coins(coins_form.cleaned_data, character)
            if validate_coins:
                return redirect('wh:character_screen', pk=character.pk)
            message = 'Nie możesz mieć ujemnych pieniążków :('

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
        'exp_form': exp_form,
        'eq_form': eq_form,
        'coins_form': coins_form,
        'rows':range(10),
        'columns':range(7)

    }
    return render(request, 'warhammer/bohater.html', context)


class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('wh:index')
        form = RegisterForm()
        return render(request, 'warhammer/register.html', {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('login')
            password = form.cleaned_data.get('password')
            user = User.objects.create_user(username=username, password=password)  # creates user
            user = authenticate(request, username=username, password=password)
            login(request, user)
            return redirect('wh:index')
        return render(request, 'warhammer/register.html', {'form': form})


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('wh:index')
        form = LoginForm()
        return render(request, 'warhammer/login.html', {'form': form})

    def post(self, request):
        message = None
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('login')
            password = form.cleaned_data.get('password')
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
        return render(request, 'warhammer/login.html', {'message': message, 'form': form})


def logout_view(request):
    logout(request)
    return redirect('wh:index')


class ContactView(View):
    def get(self, request):
        form = ContactForm()
        return render(request, 'warhammer/contact.html', {'form': form})

    def post(self, request):
        message = None
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data.get('subject', 'no subject')
            email = form.cleaned_data.get('email', 'no email')
            content = form.cleaned_data.get('content', 'no content') + '\nemail: ' + email
            try:
                send_mail(subject, content, 'zyvik.kontakt@wp.pl', ['pawel86gw2@gmail.com'])
                message = 'Wiadomość wysłana!'
            except:
                message = 'Coś nie wyszło - wyślij maila na pawel86@gmail.com'

        return render(request, 'warhammer/contact.html', {'form': form, 'message': message})


# Dice roller and MAP API
class ChatView(APIView):
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

