from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Employe, Presence, Absence

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

class EmployeForm(forms.ModelForm):
    class Meta:
        model = Employe
        fields = ['nom', 'prenom', 'poste', 'statut', 'numero_telephone', 'email', 'adresse']
        widgets = {
            'adresse': forms.Textarea(attrs={'rows': 3}),
        }

class PresenceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(PresenceForm, self).__init__(*args, **kwargs)
        if user and not user.is_staff:
            self.fields['employe'].initial = user.employe
            self.fields['employe'].widget = forms.HiddenInput()

    class Meta:
        model = Presence
        fields = ['employe', 'date', 'heure_entree', 'heure_sortie', 'statut', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'heure_entree': forms.TimeInput(attrs={'type': 'time'}),
            'heure_sortie': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class AbsenceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(AbsenceForm, self).__init__(*args, **kwargs)
        if user and not user.is_staff:
            self.fields['employe'].initial = user.employe
            self.fields['employe'].widget = forms.HiddenInput()

    class Meta:
        model = Absence
        fields = ['employe', 'date_debut', 'date_fin', 'raison', 'description']
        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class PresenceFilterForm(forms.Form):
    date_debut = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    date_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    employe = forms.ModelChoiceField(
        queryset=Employe.objects.all(),
        required=False
    )
    statut = forms.ChoiceField(
        choices=[('', 'Tous')] + Presence.STATUT_CHOICES,
        required=False
    )

class AbsenceFilterForm(forms.Form):
    date_debut = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    date_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    employe = forms.ModelChoiceField(
        queryset=Employe.objects.all(),
        required=False
    )
    statut = forms.ChoiceField(
        choices=[('', 'Tous')] + Absence.STATUT_CHOICES,
        required=False
    )
    raison = forms.ChoiceField(
        choices=[('', 'Toutes')] + Absence.RAISON_CHOICES,
        required=False
    ) 