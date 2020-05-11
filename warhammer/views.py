from django.shortcuts import render,redirect,HttpResponse, get_object_or_404, reverse
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
from .forms import RollStatsForm, RegisterForm, LoginForm, ContactForm, ClaimCharacterForm, ExperienceForm, EquipmentForm, CoinsForm, AddSkillForm, AddAbilityForm, NotesForm, ChangeProfessionForm
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

    dev_abi = csl.get_abilities_to_develop(character, 'ability')
    dev_skills = csl.get_abilities_to_develop(character, 'skill')

    # coins
    zk = int(character.coins / 240)
    s = int((character.coins - zk * 240)/12)
    p = int(character.coins - zk * 240 - s * 12)
    coins = [zk,s,p]

    exp_form = ExperienceForm()
    eq_form = EquipmentForm(initial={'eq': character.equipment})
    coins_form = CoinsForm()
    add_skill_form = AddSkillForm()
    add_ability_form = AddAbilityForm()
    notes_form = NotesForm(initial={'notes': character.notes})
    change_profession_form = ChangeProfessionForm()
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
        if coins_form.is_valid() and request.POST.get('coins'):
            error = csl.update_coins(coins_form.cleaned_data, character)
            if error:
                return redirect(reverse('wh:character_screen', args=[character.pk]) + '?error=' + error)
            return redirect('wh:character_screen', pk=character.pk)

        # Edit_stats
        if request.POST.get('edit_stats') == 'edit_stats':
            error = csl.edit_stats(request, character)
            if error:
                return redirect(reverse('wh:character_screen', args=[character.pk]) + '?error=' + error)
            return redirect('wh:character_screen', pk=character.pk)

        # Remove skills
        if request.POST.get('remove_skill'):
            error = csl.remove_skill(request.POST.get('remove_skill'), character)
            if error:
                return redirect(reverse('wh:character_screen', args=[character.pk]) + '?error=' + error)
            return redirect('wh:character_screen', pk=character.pk)

        # Add skills
        add_skill_form = AddSkillForm(request.POST)
        if add_skill_form.is_valid() and request.POST.get('add_skill'):
            error = csl.add_skill(add_skill_form.cleaned_data, character)
            if error:
                return redirect(reverse('wh:character_screen', args=[character.pk]) + '?error=' + error)
            return redirect('wh:character_screen', pk=character.pk)

        # Remove abilities
        if request.POST.get('remove_ability'):
            error = csl.remove_ability(request.POST['remove_ability'], character)
            if error:
                return redirect(reverse('wh:character_screen', args=[character.pk]) + '?error=' + error)
            return redirect('wh:character_screen', pk=character.pk)

        # Add ability
        add_ability_form = AddAbilityForm(request.POST)
        if add_ability_form.is_valid() and request.POST.get('add_ability'):
            error = csl.add_ability(add_ability_form.cleaned_data, character)
            if error:
                return redirect(reverse('wh:character_screen', args=[character.pk]) + '?error=' + error)
            return redirect('wh:character_screen', pk=character.pk)

        # Edit notes
        notes_form = NotesForm(request.POST)
        if notes_form.is_valid():
            character.notes = notes_form.cleaned_data.get('notes')
            character.save()
            return redirect('wh:character_screen', pk=character.pk)

        # Develop_Stats
        if request.POST.get('dev_stat'):
            error = csl.develop_stats(request, character)
            if error:
                return redirect(reverse('wh:character_screen', args=[character.pk]) + '?error=' + error)
            return redirect('wh:character_screen', pk=character.pk)

        # Develop_Abilities
        if request.POST.get('dev_ability'):
            error = csl.develop_abilities(request, character)
            if error:
                return redirect(reverse('wh:character_screen', args=[character.pk]) + '?error=' + error)
            return redirect('wh:character_screen', pk=character.pk)

        # Develop_Skills
        if request.POST.get('dev_skill'):
            error = csl.develop_skills(request, character)
            if error:
                return redirect(reverse('wh:character_screen', args=[character.pk]) + '?error=' + error)
            return redirect('wh:character_screen', pk=character.pk)

        # Change profession
        change_profession_form = ChangeProfessionForm(request.POST)
        if request.POST.get('profession') and change_profession_form.is_valid():
            error = csl.change_profession(change_profession_form.cleaned_data, character)
            if error:
                return redirect(reverse('wh:character_screen', args=[character.pk]) + '?error=' + error)
            return redirect('wh:character_screen', pk=character.pk)

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
        'add_skill_form': add_skill_form,
        'add_ability_form': add_ability_form,
        'notes_form': notes_form,
        'change_profession_form': change_profession_form,
        'rows': range(10),
        'columns': range(7)

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

