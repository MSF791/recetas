from django import forms
from .models import *

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'description', 'ingredients', 'instructions', 'preparation_time', 'cuisine', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'ingredients': forms.Textarea(attrs={'class': 'form-control'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control'}),
            'preparation_time': forms.NumberInput(attrs={'class': 'form-control'}),
            'cuisine': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'title':'Titulo De La Receta',
            'description':'Descripcion De La Receta',
            'ingredients':'Ingredientes De La Receta',
            'instructions':'Instrucciones De La Receta',
            'preparation_time':'Tiempo De Preparación De La Receta',
            'cuisine':'Cocina De La receta',
            'image':'Imagen De La Receta',
        }

class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['name']  # Solo incluimos el campo 'name'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la colección'}),
        }
        labels = {
            'name': 'Nombre de la Colección',
        }