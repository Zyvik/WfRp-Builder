from django import forms
from .models import NPCModel


class CreateNpcForm(forms.ModelForm):
    class Meta:
        model = NPCModel
        fields = ('name', 'WW', 'US', 'notes')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            self.fields[field].widget.attrs['placeholder'] = field
            self.fields[field].label = ''


class RemoveNpcForm(forms.Form):
    npc_pk = forms.IntegerField(min_value=1)
