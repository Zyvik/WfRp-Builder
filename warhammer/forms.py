from django import forms
from .models import Step1Model

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

