from django.contrib import admin
from django import forms

from .models import Title


# Step 1: Create a custom form with Textarea for 'title'
class TitleForm(forms.ModelForm):
    class Meta:
        model = Title
        fields = "__all__"  # Or specify the exact fields you want to include
        widgets = {
            "title": forms.Textarea(attrs={"rows": 3, "cols": 40}),
        }


# Step 2: Register the Title model with the custom form
class TitleAdmin(admin.ModelAdmin):
    form = TitleForm


admin.site.register(Title, TitleAdmin)
