
from django import forms
from .models import Machine,Alert


class MachineUpdateForm(forms.ModelForm):

    class Meta:
        model = Machine

        fields = [
            "last_maintenance",
            "next_maintenance",
            "remarks"
        ]

        widgets = {
            "last_maintenance": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d"
            ),

            "next_maintenance": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d"
            ),

            "remarks": forms.Textarea(
                attrs={"rows": 4}
            )
        }

    def clean(self):

        cleaned_data = super().clean()

        last_date = cleaned_data.get("last_maintenance")
        next_date = cleaned_data.get("next_maintenance")

        if last_date and next_date and next_date < last_date:
            self.add_error(
                "next_maintenance",
                "Next maintenance cannot be before last maintenance."
            )

        return cleaned_data


class AlertUpdateForm(forms.ModelForm):

    class Meta:

        model = Alert

        fields = [
            "status",
            "message",
            "resolution_note"
        ]

        widgets = {
            "status": forms.Select(
                attrs={"class": "form-select"}
            ),

            "message": forms.Textarea(
                attrs={"rows": 4}
            ),

            "resolution_note": forms.Textarea(
                attrs={"rows": 4}
            )
        }
