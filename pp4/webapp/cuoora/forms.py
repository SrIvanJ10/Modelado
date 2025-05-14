from django import forms
from .models import Answer, Question, Topic

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['description']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Escribe aquí tu respuesta'
            })
        }

class QuestionForm(forms.ModelForm):
    # Campo para seleccionar topics existentes con desplegable múltiple
    existing_topics = forms.ModelMultipleChoiceField(
        queryset=Topic.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control',
            'style': 'height: 100px;', # Para mostrar varias opciones a la vez
        }),
        label="Seleccionar topics"
    )
    
    # Campo para crear un nuevo topic
    new_topic = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'O escribe aquí para crear un nuevo topic'
        }),
        label="Nuevo topic"
    )
    
    class Meta:
        model = Question
        fields = ['title', 'description']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Escribe aquí los detalles de tu pregunta'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título de tu pregunta'
            })
        }
        
    def clean(self):
        cleaned_data = super().clean()
        existing_topics = cleaned_data.get('existing_topics')
        new_topic = cleaned_data.get('new_topic')
        
        # Verificar que se seleccione al menos un topic o se cree uno nuevo
        if not existing_topics and not new_topic:
            raise forms.ValidationError("Debes seleccionar al menos un topic existente o crear uno nuevo.")
        
        return cleaned_data