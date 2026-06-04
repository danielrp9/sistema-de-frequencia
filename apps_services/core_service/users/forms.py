from django import forms
from allauth.account.forms import SignupForm
from django.core.exceptions import ValidationError
import re

class BaseSignupForm(SignupForm):
    nome_completo = forms.CharField(max_length=255, label="Nome Completo", widget=forms.TextInput(attrs={'placeholder': 'Seu nome completo'}))
    
    def save(self, request):
        user = super(BaseSignupForm, self).save(request)
        # Sincroniza e-mail com username para garantir unicidade e compatibilidade
        user.username = user.email
        user.first_name = self.cleaned_data['nome_completo']
        user.save()
        return user

class AlunoSignupForm(BaseSignupForm):
    matricula = forms.CharField(max_length=11, min_length=11, label="Matrícula", widget=forms.TextInput(attrs={'placeholder': '11 dígitos'}))

    def clean_matricula(self):
        matricula = self.cleaned_data.get('matricula')
        if not re.match(r'^\d{11}$', matricula):
            raise ValidationError("A matrícula deve conter exatamente 11 dígitos numéricos.")
        return matricula

class ProfessorSignupForm(BaseSignupForm):
    siape = forms.CharField(max_length=7, min_length=7, label="SIAPE", widget=forms.TextInput(attrs={'placeholder': '7 dígitos'}))

    def clean_siape(self):
        siape = self.cleaned_data.get('siape')
        if not re.match(r'^\d{7}$', siape):
            raise ValidationError("O SIAPE deve conter exatamente 7 dígitos numéricos.")
        return siape
