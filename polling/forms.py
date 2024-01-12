from django import forms

from .models import Choice

class VoteForm(forms.Form):
    choice = forms.ChoiceField(widget=forms.RadioSelect)

    def __init__(self, poll_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = Choice.objects.filter(poll_id=poll_id)
        self.fields['choice'].choices = [(choices.id, choices.choice_text) for choice in choices]