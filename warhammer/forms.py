from uuid import UUID
from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from .models import SkillsModel, AbilitiesModel, ProfessionModel, CharacterModel


class ClaimCharacterForm(forms.Form):
    """
    Assigns existing character to user in clean_pk()
    """
    pk = forms.CharField(label='', min_length=36, max_length=36)
    pk.widget.attrs.update({
        'class': 'form-control form-control-lg',
        'placeholder': 'Identyfikator bohatera',
        'data-placeholder': 'Character\'s ID'
    })

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ClaimCharacterForm, self).__init__(*args, **kwargs)

    def clean_pk(self):
        pk = self.cleaned_data['pk']

        # checks if pk is valid UUID
        try:
            test_uuid = UUID(pk, version=4)
        except ValueError:
            raise forms.ValidationError('To nie jest identyfikator postaci')

        # checks if character with given id exists
        try:
            character = CharacterModel.objects.get(pk=pk)
        except ObjectDoesNotExist:
            raise forms.ValidationError("Postać o tym id nie istnieje.")

        # checks if character 'belongs' to someone
        if character.user is None:
            character.user = self.request.user
            character.save()
            return pk
        raise forms.ValidationError("Ta postać już do kogoś należy")


class RollStatsForm(forms.Form):
    ww = forms.IntegerField(min_value=2, max_value=20, label='')
    us = forms.IntegerField(min_value=2, max_value=20, label='')
    k = forms.IntegerField(min_value=2, max_value=20, label='')
    odp = forms.IntegerField(min_value=2, max_value=20, label='')
    int = forms.IntegerField(min_value=2, max_value=20, label='')
    sw = forms.IntegerField(min_value=2, max_value=20, label='')
    ogd = forms.IntegerField(min_value=2, max_value=20, label='')
    zr = forms.IntegerField(min_value=2, max_value=20, label='')
    zyw = forms.IntegerField(min_value=1, max_value=10, label='')
    pp = forms.IntegerField(min_value=1, max_value=10, label='')
    prof = forms.IntegerField(min_value=1, max_value=100, label='')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        widget_class = 'form-control form-control-lg'
        for i in self.fields:
            self.fields[i].widget.attrs['class'] = widget_class
            self.fields[i].widget.attrs['placeholder'] = '2k10'
        self.fields['zyw'].widget.attrs['placeholder'] = '1k10'
        self.fields['pp'].widget.attrs['placeholder'] = '1k10'
        self.fields['prof'].widget.attrs['placeholder'] = '1k100'


class RegisterForm(forms.Form):
    login = forms.CharField(
        min_length=3,
        max_length=30
    )
    password = forms.CharField(
        min_length=5,
        max_length=30,
        widget=forms.PasswordInput,
        label="Hasło"
    )
    confirm_password = forms.CharField(
        min_length=5,
        max_length=30,
        widget=forms.PasswordInput,
        label="Potwierdź hasło"
    )

    login.widget.attrs.update({'class': 'form-control form-control-lg mb-4'})
    password.widget.attrs.update({'class': 'form-control form-control-lg mb-4'})
    confirm_password.widget.attrs.update({'class': 'form-control form-control-lg'})

    def clean_login(self):
        username = self.cleaned_data['login']

        if ' ' in username:
            error_msg = 'Login nie może zawierać spacji.'
            raise forms.ValidationError(error_msg)
        if User.objects.filter(username__iexact=username).exists():
            error_msg = 'Użytkownik o takim loginie już istnieje.'
            raise forms.ValidationError(error_msg)
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data['password']
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            self.add_error('password', 'Hasła muszą być jednakowe.')


class LoginForm(forms.Form):
    """
    Login user in clean() function
    """
    login = forms.CharField(
        min_length=3,
        max_length=30
    )
    password = forms.CharField(
        min_length=5,
        max_length=30,
        widget=forms.PasswordInput,
        label='Hasło'
    )

    login.widget.attrs.update({'class': 'form-control form-control-lg mb-4'})
    password.widget.attrs.update({'class': 'form-control form-control-lg mb-4'})

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        error_msg = "Błędna kombinacja loginu i hasła."
        username = cleaned_data['login']
        password = cleaned_data['password']
        try:
            user = User.objects.get(username__iexact=username)
            user = authenticate(
                request=self.request,
                username=user.username,
                password=password
            )
            if user is not None:
                login(self.request, user)
            else:
                self.add_error('login', error_msg)
        except ObjectDoesNotExist:
            self.add_error('login', error_msg)


class ContactForm(forms.Form):
    email = forms.EmailField(required=False, label='')
    subject = forms.CharField(label='')
    message = forms.CharField(widget=forms.Textarea, label='')

    email_widget = {
        'class': 'form-control form-control-lg',
        'placeholder': 'Email (opcjonalnie)',
        'data-placeholder': 'Email (optional)'
    }
    subject_widget = {
        'class': 'form-control form-control-lg',
        'placeholder': 'Temat',
        'data-placeholder': 'Subject'
    }
    message_widget = {
        'class': 'form-control',
        'placeholder': 'Treść wiadomości',
        'rows': '8',
        'cols': '20',
        'style': 'font-size:small',
        'data-placeholder': 'Message'
    }

    email.widget.attrs.update(email_widget)
    subject.widget.attrs.update(subject_widget)
    message.widget.attrs.update(message_widget)


class CoinsForm(forms.Form):
    gold = forms.IntegerField(label='', required=False)
    silver = forms.IntegerField(label='', required=False)
    bronze = forms.IntegerField(label='', required=False)

    gold.widget.attrs.update({'placeholder': 'zk', 'data-placeholder': 'g'})
    silver.widget.attrs.update({'placeholder': 's'})
    bronze.widget.attrs.update({'placeholder': 'p', 'data-placeholder': 'c'})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        widget_class = 'form-control form-control-lg'
        for i in self.fields:
            self.fields[i].widget.attrs['class'] = widget_class


class ExperienceForm(forms.Form):
    exp = forms.IntegerField(label='')
    exp.widget.attrs.update(
        {'class': 'form-control',
         'placeholder': 'dodaj PD',
         'data-placeholder': 'Exp'
         }
    )


class EquipmentForm(forms.Form):
    eq = forms.CharField(label='', widget=forms.Textarea)

    eq_widget = {
        'id': 'form_eq',
        'class': 'form-control rounded-0',
        'rows': '10',
        'style': 'display: none; font-size: small'
    }
    eq.widget.attrs.update(eq_widget)


class AddSkillForm(forms.Form):
    add_skill = forms.ModelChoiceField(
        queryset=SkillsModel.objects.all(),
        empty_label=None,
        label=''
    )
    skill_bonus = forms.CharField(label='', required='')

    add_skill.widget.attrs.update({'class': 'form-control'})
    skill_bonus.widget.attrs.update({'class': 'form-control',
                                     'placeholder': 'bonus'})


class AddAbilityForm(forms.Form):
    add_ability = forms.ModelChoiceField(
        queryset=AbilitiesModel.objects.all(),
        empty_label=None,
        label=''
    )
    ability_bonus = forms.CharField(label='', required='')

    add_ability.widget.attrs.update({'class': 'form-control'})
    ability_bonus.widget.attrs.update({'class': 'form-control',
                                       'placeholder': 'bonus'})


class NotesForm(forms.Form):
    notes = forms.CharField(label='', widget=forms.Textarea)

    notes_widget = {
        'id': 'form_notes',
        'class': 'form-control rounded-0',
        'rows': '10',
        'style': 'font-size: small'
    }
    notes.widget.attrs.update(notes_widget)


class ChangeProfessionForm(forms.Form):
    profession = forms.ModelChoiceField(
        queryset=ProfessionModel.objects.all(),
        empty_label=None,
        label=''
    )

    profession.widget.attrs.update({'class': 'form-control form-control-lg ml-5'})
