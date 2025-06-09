from django import forms
from .models import Task, Project


class TaskForm (forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'important', 'project']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título'}),
            'description': forms.Textarea(attrs={'class': 'form-control','placeholder': 'descripción' }),
            'important': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CreateNewProject(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del proyecto'}),
        }
