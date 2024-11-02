from django.contrib import admin
from django import forms

from .models import Activity, Title, StravaUser


# Step 1: Create a custom form with Textarea for 'title'
class TitleForm(forms.ModelForm):
    class Meta:
        model = Title
        fields = "__all__"  # Or specify the exact fields you want to include
        widgets = {
            "title": forms.Textarea(attrs={"rows": 3, "cols": 40}),
        }


class TitleAdmin(admin.ModelAdmin):
    form = TitleForm


@admin.register(StravaUser)
class StravaUserAdmin(admin.ModelAdmin):
    list_display = ("user", "athlete_id")  # Fields to display in the admin list view
    search_fields = ("user__username", "athlete_id")


admin.site.register(Title, TitleAdmin)
admin.site.register(Activity)
