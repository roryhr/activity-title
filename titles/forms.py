from django import forms

from titles.models import Title


class TitleForm(forms.ModelForm):
    class Meta:
        model = Title
        fields = ["title"]
