from django import forms

class LocationForm(forms.Form):
    location = forms.CharField(max_length=100, required=True, label="Location", widget=forms.TextInput(attrs={'placeholder': 'Enter city or location'}))
