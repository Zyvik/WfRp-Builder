from itertools import zip_longest
from django.shortcuts import render, redirect, HttpResponse,\
    get_object_or_404, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.views import View
from smtplib import SMTPException
from rest_framework.views import APIView
from rest_framework.response import Response
from warhammer import forms as f
from warhammer import models as m
from warhammer import character_creation_lib as ccl
from warhammer import profession_detail_lib as prof_detail
from warhammer import character_screen_lib as csl
from .serializers import ChatSerializer, MapSerializer


class IndexView(View):
    """
    Landing page:
    displays user's characters and gives option to claim existing character
    """
    def get(self, request):
        if request.user.is_authenticated:
            your_characters = m.CharacterModel.objects.filter(user=request.user)
            form = f.ClaimCharacterForm()

            context = {
                'your_characters': your_characters,
                'form': form
            }
            return render(request, 'warhammer/index.html', context)
        return render(request, 'warhammer/index.html')

    def post(self, request):
        if request.user.is_authenticated:
            message = None
            form = f.ClaimCharacterForm(request.POST)
            if form.is_valid():
                pk = form.cleaned_data.get('pk')
                try:
                    character = m.CharacterModel.objects.get(pk=pk)
                    if character.user is None:
                        character.user = request.user
                        character.save()
                        return redirect('wh:index')
                    else:
                        message = 'Ta postać już do kogoś należy.'
                except ObjectDoesNotExist:
                    message = 'Postać o takim identyfikatorze nie istnieje.'
            your_characters = m.CharacterModel.objects.filter(user=request.user)
            context = {
                'your_characters': your_characters,
                'message': message,
                'form': form
            }
            return render(request, 'warhammer/index.html', context)
        return redirect('wh:index')


def choose_race(request):
    """
    1st step in character creation - choosing race
    """
    all_races = m.RaceModel.objects.all()
    return render(request, 'warhammer/race.html', {'all_races': all_races})


def roll_stats(request, race_slug):
    """
    2nd step in character creation - rolling for stats
    """
    race = get_object_or_404(m.RaceModel, slug=race_slug)
    starting_stats = m.StartingStatsModel.objects.filter(race=race)
    starting_stats = starting_stats.order_by('-bonus')
    starting_professions = ccl.get_starting_professions(race)

    stats_form = f.RollStatsForm()
    if request.GET:
        stats_form = f.RollStatsForm(request.GET)
    if stats_form.is_valid():
        customize_form = ccl.CharacterCustomizeForm(race, stats_form)
        if request.method == 'POST':
            # 3rd step in character creation - customize character
            new_character = ccl.create_new_character(request, customize_form)
            return redirect('wh:character_screen', pk=new_character.pk)
        # customize character context
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
            'all_stats': m.StatsModel.objects.all(),
            'stats_table': customize_form.stats_table,
            'qs_skills': customize_form.all_skills,
            'qs_abilities': customize_form.all_abilities,
            'equipment': customize_form.profession.equipment
        }
        return render(request, 'warhammer/customize_character.html', context)
    # roll stats_context
    context = {
        'stats_and_form': list(zip_longest(starting_stats, stats_form)),
        'starting_professions': starting_professions,
    }
    return render(request, 'warhammer/roll_stats.html', context)


def profession_list(request):
    all_professions = m.ProfessionModel.objects.all()
    context = {'all_professions': all_professions}
    return render(request, 'warhammer/profession_list.html', context)


def profession_detail(request, profession_slug):
    profession = get_object_or_404(m.ProfessionModel, slug=profession_slug)
    all_skills = m.SkillsModel.objects.all()
    all_abilities = m.AbilitiesModel.objects.all()

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

    return render(request, 'warhammer/profession_detail.html', context)


class CharacterScreen(View):
    def get(self, request, **kwargs):
        user = request.user
        character = get_object_or_404(m.CharacterModel, pk=self.kwargs['pk'])
        if character.user and character.user != user and not user.is_staff:
            return redirect('wh:index')

        char_stats = m.CharactersStats.objects.filter(character=character)
        error_code = request.GET.get('error', None)
        error_msg = csl.get_error_message(error_code) if error_code else None

        context = {
            'claim_message': csl.get_claim_message(request, character),
            'error_message': error_msg,
            'character': character,
            'stats_table': char_stats,
            'char_skills': m.CharacterSkills.objects.filter(character=character).order_by('skill'),
            'char_abilities': m.CharacterAbilities.objects.filter(character=character).order_by('ability'),
            'develop_stats': char_stats.filter(max_bonus__gt=0),
            'dev_abilities': csl.get_abilities_to_develop(character, 'ability'),
            'dev_skills': csl.get_abilities_to_develop(character, 'skill'),
            'coins': csl.get_coins(character),
            'exp_form': f.ExperienceForm(),
            'eq_form': f.EquipmentForm(initial={'eq': character.equipment}),
            'coins_form': f.CoinsForm(),
            'add_skill_form': f.AddSkillForm(),
            'add_ability_form': f.AddAbilityForm(),
            'notes_form': f.NotesForm(initial={'notes': character.notes}),
            'change_profession_form': f.ChangeProfessionForm(),
            'rows': range(10),
            'columns': range(7)

        }
        return render(request, 'warhammer/character_screen.html', context)

    def post(self, request, **kwargs):
        character = get_object_or_404(m.CharacterModel, pk=self.kwargs['pk'])
        action = request.POST.get('action', None)

        action_dictionary = {
            'add_exp': csl.update_exp,
            'add_coins': csl.update_coins,
            'edit_stats': csl.edit_stats,
            'remove_skill': csl.remove_skill,
            'add_skill': csl.add_skill,
            'remove_ability': csl.remove_ability,
            'add_ability': csl.add_ability,
            'edit_eq': csl.edit_eq,
            'edit_notes': csl.edit_notes,
            'develop_stats': csl.develop_stats,
            'develop_abilities': csl.develop_abilities,
            'develop_skills': csl.develop_skills,
            'change_profession': csl.change_profession
        }

        error = action_dictionary.get(action, csl.action_error)(request, character)
        if error:
            return redirect(reverse('wh:character_screen', args=[character.pk]) + '?error=' + error)
        return redirect('wh:character_screen', pk=character.pk)


class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('wh:index')
        form = f.RegisterForm()
        return render(request, 'warhammer/register.html', {'form': form})

    def post(self, request):
        form = f.RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('login')
            password = form.cleaned_data.get('password')
            User.objects.create_user(username=username, password=password)
            user = authenticate(request, username=username, password=password)
            login(request, user)
            return redirect('wh:index')
        return render(request, 'warhammer/register.html', {'form': form})


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('wh:index')
        form = f.LoginForm()
        return render(request, 'warhammer/login.html', {'form': form})

    def post(self, request):
        message = None
        form = f.LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('login')
            password = form.cleaned_data.get('password')
            try:
                user = User.objects.get(username__iexact=username)
                user = authenticate(
                    request=request,
                    username=user.username,
                    password=password
                )
                if user is not None:
                    login(request, user)
                    return redirect('wh:index')
                else:
                    message = 'Podano złą kombinację loginu i hasła.'
            except ObjectDoesNotExist:
                message = 'Podano złą kombinację loginu i hasła.'

        return render(
            request=request,
            template_name='warhammer/login.html',
            context={'message': message, 'form': form}
        )


def logout_view(request):
    logout(request)
    return redirect('wh:index')


class ContactView(View):
    def get(self, request):
        form = f.ContactForm()
        return render(request, 'warhammer/contact.html', {'form': form})

    def post(self, request):
        message = None
        form = f.ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data.get('subject', 'no subject')
            email = form.cleaned_data.get('email', 'no email')
            content = f"{form.cleaned_data.get('content', 'no content')}\n" \
                      f"email: {email}"
            try:
                send_mail(
                    subject=subject,
                    message=content,
                    from_email='zyvik.kontakt@wp.pl',
                    recipient_list=['pawel86gw2@gmail.com']
                )
                message = 'Wiadomość wysłana!'
            except SMTPException:
                message = 'Coś nie wyszło - wyślij maila na pawel86@gmail.com'

        context = {
            'message': message,
            'form': form
        }
        return render(request, 'warhammer/contact.html', context)


# Dice roller and MAP API
class ChatView(APIView):
    authentication_classes = []

    def get(self, request, game_id):
        msg_to_display = 15
        game = get_object_or_404(m.GameModel, id=game_id)
        messages = m.MessagesModel.objects.filter(game=game).order_by('-id')
        messages = messages[:msg_to_display]
        map = m.MapModel.objects.get(game=game)
        serializer = ChatSerializer(messages, many=True)
        map_serializer = MapSerializer(map, many=False)
        return Response({
            'chat': serializer.data,
            'map': map_serializer.data
        })

    def post(self, request, game_id):
        try:
            if request.data.get('message'):
                m.MessagesModel.objects.create(
                    game=m.GameModel.objects.get(id=game_id),
                    author=request.data.get('author'),
                    message=request.data.get('message')
                )
            else:
                game = m.GameModel.objects.get(id=game_id)
                map_obj = m.MapModel.objects.get(game=game)
                map_obj.map = request.data.get('map')
                map_obj.counter += 1
                map_obj.save()
        except:
            pass
        return HttpResponse("git majonez")


def game_master_room(request, game_id):
    game = get_object_or_404(m.GameModel, pk=game_id)
    if request.user == game.admin:
        npc_list = m.NPCModel.objects.filter(game=game)
        if request.method == 'POST':
            # Adding NPC
            if request.POST.get('add_npc'):
                try:
                    npc = m.NPCModel(
                        game=game,
                        name=request.POST.get('npc_name', 'boring name'),
                        WW=int(request.POST.get('npc_WW', '0')),
                        US=int(request.POST.get('npc_US', '0')),
                        notes=request.POST.get('npc_notes')
                    )
                    npc.save()
                except ValueError:
                    pass

            # deleting NPC
            if request.POST.get('delete_npc'):
                npc_pk = int(request.POST.get('delete_npc'))
                npc = m.NPCModel.objects.get(pk=npc_pk)
                # checks if npc belongs to this game
                if npc.game == game:
                    npc.delete()

        context = {
            'game': game,
            'npcs': npc_list,
            'columns': range(7),
            'rows': range(10)
        }
        return render(request, 'warhammer/DMRoom.html', context)
    else:
        login_error = 'Nie jestesteś mistrzem tej gry - zawróć.'
        context = {
            'game': game,
            'login_error': login_error
        }
        return render(request, 'warhammer/DMRoom.html', context)


def skills_list(request):
    skills = m.SkillsModel.objects.order_by("name")
    context = {'skills': skills}
    return render(request, 'warhammer/skills_list.html', context)


def abilities_list(request):
    abilities = m.AbilitiesModel.objects.all()
    context = {'abilities': abilities}
    return render(request, 'warhammer/abilities_list.html', context)
