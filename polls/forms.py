from django import forms
from .models import Question, Choice
from django.forms import modelformset_factory


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'pub_date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['question_text'].widget.attrs.update({'class': 'form-control'})
        self.fields['pub_date'].widget.attrs.update({'class': 'form-control', 'type': 'datetime-local'})

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['choice_text']

    
ChoiceFormSet = modelformset_factory(
    Choice,
    form=ChoiceForm,
    extra=3,
    min_num=2,
    validate_min=True,
)