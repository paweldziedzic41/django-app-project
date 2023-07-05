from django import forms
from .models import Account
from django.http import HttpResponse

class RegsitrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter Password',
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm Password',
    }))
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'password']
        
    # Function __init__ changes the CSS classes of all input fields    
    def __init__(self,*args,**kwargs):
        super(RegsitrationForm, self).__init__(*args,**kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Last name'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone number'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super(RegsitrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError(
                "Password does not match"
            )
        
