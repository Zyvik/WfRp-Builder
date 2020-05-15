from django import forms
from .models import NPCModel


class NpcForm(forms.ModelForm):
    class Meta:
        model = NPCModel
        fields = ('name', 'WW', 'US', 'notes')