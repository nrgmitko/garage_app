from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Car, MaintenanceRequest, Review
from django.utils.timezone import now


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['make', 'model', 'year', 'vin', 'horsepower', 'upgrades', 'image']
        widgets = {
            'year': forms.NumberInput(attrs={'min': 1900, 'max': 2100}),
        }


class MaintenanceRequestForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = ['car', 'requested_date', 'notes']
        widgets = {
            'requested_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['car'].queryset = Car.objects.filter(owner=user)

        initial_car_id = self.data.get('car') or self.initial.get('car')
        if initial_car_id:
            self.fields['car'].initial = initial_car_id

        self.fields['requested_date'].widget.attrs['min'] = now().date().isoformat()

    def clean_requested_date(self):
        selected_date = self.cleaned_data['requested_date']
        if selected_date < now().date():
            raise forms.ValidationError("You cannot choose a past date.")
        return selected_date


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = None
