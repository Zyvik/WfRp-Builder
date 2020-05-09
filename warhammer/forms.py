from django import forms
from django.contrib.auth.models import User
from .models import Step1Model, SkillsModel
from uuid import UUID


class ClaimCharacterForm(forms.Form):
    pk = forms.CharField(label='', min_length=36, max_length=36)
    pk.widget.attrs.update({'class': 'form-control form-control-lg', 'placeholder': 'Identyfikator bohatera'})

    def clean_pk(self):
        pk = self.cleaned_data['pk']
        try:
            test_uuid = UUID(pk, version=4)
        except ValueError:
            raise forms.ValidationError('To nie jest identyfikator postaci')
        return pk


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
        for i in self.fields:
            self.fields[i].widget.attrs['class'] = 'form-control form-control-lg'
            self.fields[i].widget.attrs['placeholder'] = '2k10'
        self.fields['zyw'].widget.attrs['placeholder'] = '1k10'
        self.fields['pp'].widget.attrs['placeholder'] = '1k10'
        self.fields['prof'].widget.attrs['placeholder'] = '1k100'


class RegisterForm(forms.Form):
    login = forms.CharField(min_length=3, max_length=30)
    password = forms.CharField(min_length=5, max_length=30, widget=forms.PasswordInput)
    confirm_password = forms.CharField(min_length=5, max_length=30, widget=forms.PasswordInput)

    login.widget.attrs.update({'class': 'form-control form-control-lg mb-4'})
    password.widget.attrs.update({'class': 'form-control form-control-lg mb-4'})
    confirm_password.widget.attrs.update({'class': 'form-control form-control-lg'})

    def clean_login(self):
        login = self.cleaned_data['login']

        if ' ' in login:
            raise forms.ValidationError('Login nie może zawierać spacji.')
        if User.objects.filter(username__iexact=login).exists():
            raise forms.ValidationError('Użytkownik o takim loginie już istnieje.')
        return login

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data['password']
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            self.add_error('password', 'Hasła muszą być jednakowe.')


class LoginForm(forms.Form):
    login = forms.CharField(min_length=3, max_length=30)
    password = forms.CharField(min_length=5, max_length=30, widget=forms.PasswordInput, label='Hasło')

    login.widget.attrs.update({'class': 'form-control form-control-lg mb-4'})
    password.widget.attrs.update({'class': 'form-control form-control-lg mb-4'})


class ContactForm(forms.Form):
    email = forms.EmailField(required=False, label='')
    subject = forms.CharField(label='')
    message = forms.CharField(widget=forms.Textarea, label='')

    message_widget = {
        'class': 'form-control',
        'placeholder': 'Treść wiadomości',
        'rows': '8',
        'cols': '20',
        'style': 'font-size:small'
    }
    email.widget.attrs.update({'class': 'form-control form-control-lg', 'placeholder': 'Email (opcjonalnie)'})
    subject.widget.attrs.update({'class': 'form-control form-control-lg', 'placeholder': 'Temat'})
    message.widget.attrs.update(message_widget)


class CoinsForm(forms.Form):
    gold = forms.IntegerField(label='', required=False)
    silver = forms.IntegerField(label='', required=False)
    bronze = forms.IntegerField(label='', required=False)

    gold.widget.attrs.update({'class': 'form-control form-control-lg', 'placeholder': 'zk'})
    silver.widget.attrs.update({'class': 'form-control form-control-lg', 'placeholder': 's'})
    bronze.widget.attrs.update({'class': 'form-control form-control-lg', 'placeholder': 'p'})


class ExperienceForm(forms.Form):
    exp = forms.IntegerField(label='')
    exp.widget.attrs.update({'class': 'form-control', 'placeholder': 'dodaj PD'})


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
    choices = [('', '')] + [(skill.pk, skill.name) for skill in SkillsModel.objects.all()]

    add_skill = forms.ChoiceField(choices=choices, label='')
    skill_bonus = forms.CharField(label='', required='')

    add_skill.widget.attrs.update({'class': 'form-control'})
    skill_bonus.widget.attrs.update({'class': 'form-control', 'placeholder': 'bonus'})

class Step1Form(forms.ModelForm):
    class Meta:
        model = Step1Model
        fields = '__all__'

    def clean_WW(self, *args,**kwargs):
        WW = self.cleaned_data['WW']
        if WW <2 or WW>20:
            raise forms.ValidationError('Wartość otrzymana z zsumowania 2 rzutów k10 musi być w przedziale od 2 do 20.')
        else:
            return WW

