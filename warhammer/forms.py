from django import forms
from .models import Step1Model


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

