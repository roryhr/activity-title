from django import forms

from titles.models import Title


class TitleForm(forms.ModelForm):
    class Meta:
        model = Title
        fields = ["title"]
        widgets = {
            "title": forms.Textarea(attrs={"cols": 30, "rows": 3}),
        }
