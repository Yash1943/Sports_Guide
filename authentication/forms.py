from django import forms
from .models import Sport
from .models import Session

class SportForm(forms.ModelForm):
    class Meta:
        model = Sport
        fields = ['id', 'sport_name']
