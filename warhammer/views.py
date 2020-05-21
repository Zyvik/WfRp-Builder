from itertools import zip_longest
from smtplib import SMTPException
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.views.generic.list import ListView
from django.views import View
from . import forms as f
from . import models as m
from .libs import character_screen_lib as csl, character_creation_lib as ccl, \
    profession_detail_lib as pdl


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
        # if user not authenticated - give no context
        return render(request, 'warhammer/index.html')

    def post(self, request):
        if request.user.is_authenticated:
            form = f.ClaimCharacterForm(request.POST, request=request)
            if form.is_valid():
                return redirect('wh:index')

            your_characters = m.CharacterModel.objects.filter(user=request.user)
            context = {
                'your_characters': your_characters,
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
    2nd and 3rd steps in character creation - roll for stats and customize char
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

        # customize character (3rd step) context
        context = {
            'character_stats': customize_form.character_stats,
            'race': race,
            'form': customize_form
        }
        return render(request, 'warhammer/customize_character.html', context)

    # Roll stats (2nd step) context
    context = {
        'stats_and_form': list(zip_longest(starting_stats, stats_form)),
        'starting_professions': starting_professions,
    }
    return render(request, 'warhammer/roll_stats.html', context)


class CharacterScreen(View):
    """
    View, develop, edit selected character
    """

    def get(self, request, **kwargs):
        user = request.user
        character = get_object_or_404(m.CharacterModel, pk=self.kwargs['pk'])
        if character.user and character.user != user and not user.is_staff:
            return redirect('wh:index')
        # get character stats, abilities, skills
        char_stats = m.CharactersStats.objects.filter(character=character)
        char_skills = m.CharacterSkills.objects.filter(character=character)
        char_skills = char_skills.order_by('skill')
        char_abilities = m.CharacterAbilities.objects.filter(character=character)
        char_abilities = char_abilities.order_by('ability')
        # error handling
        error_code = request.GET.get('error', None)
        error_msg = csl.get_error_message(error_code) if error_code else None

        context = {
            'claim_message': csl.get_claim_message(request, character),
            'error_message': error_msg,
            'character': character,
            'stats_table': char_stats,
            'char_skills': char_skills,
            'char_abilities': char_abilities,
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
            # cols and rows shouldn't be harcoded
            'rows': range(10),
            'columns': range(7)
        }
        return render(request, 'warhammer/character_screen.html', context)

    def post(self, request, **kwargs):
        character = get_object_or_404(m.CharacterModel, pk=self.kwargs['pk'])
        action = request.POST.get('action', None)
        # all actions are functions that take 2 arguments (request, character)
        action_dict = {
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

        error = action_dict.get(action, csl.action_error)(request, character)
        if error:
            base_url = reverse('wh:character_screen', args=[character.pk])
            error_url = f"?error={error}"
            return redirect(base_url + error_url)
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
    """
    Logs user in - logic is inside LoginForm
    """

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('wh:index')
        form = f.LoginForm()
        return render(request, 'warhammer/register.html', {'form': form})

    def post(self, request):
        form = f.LoginForm(request.POST, request=request)
        if form.is_valid():
            return redirect('wh:index')
        return render(request, 'warhammer/register.html', {'form': form})


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

        context = {'message': message, 'form': form}
        return render(request, 'warhammer/contact.html', context)


class SkillList(ListView):
    model = m.SkillsModel
    template_name = 'warhammer/skills_list.html'


class AbilityList(ListView):
    model = m.AbilitiesModel
    template_name = 'warhammer/abilities_list.html'


class ProfessionList(ListView):
    model = m.ProfessionModel
    template_name = 'warhammer/profession_list.html'


def profession_detail(request, profession_slug):
    profession = get_object_or_404(m.ProfessionModel, slug=profession_slug)
    all_skills = m.SkillsModel.objects.all()
    all_abilities = m.AbilitiesModel.objects.all()

    skills_string = pdl.create_modals(all_skills, profession.skills)
    abilities_string = pdl.create_modals(all_abilities, profession.abilities)
    stats_list = pdl.prepare_stats_for_display(profession)

    context = {
        'abilities': abilities_string,
        'prof_abilities': all_abilities,  # abilities objects
        'skills': skills_string,
        'prof_skills': all_skills,  # skills objects from SkillModel
        'stats_list': stats_list,
        'profession': profession,  # profession object
    }

    return render(request, 'warhammer/profession_detail.html', context)
