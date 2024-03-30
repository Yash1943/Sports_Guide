from django import forms
from .models import Sport

class SportForm(forms.ModelForm):
    class Meta:
        model = Sport
        fields = ['id', 'sport_name']
