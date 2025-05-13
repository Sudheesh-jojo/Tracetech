from django import forms
from .models import Lost
from .models import Found


class Lostform(forms.ModelForm):
    class Meta:
        model = Lost 
        fields = '__all__'  
class Foundform(forms.ModelForm):
    class Meta:
        model = Found 
        fields = '__all__' 

