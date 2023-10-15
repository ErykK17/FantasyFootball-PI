from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, MyFootballer

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2'
        ]
    def clean_username(self):
        username = self.cleaned_data.get('username')
        usr = User.objects.filter(username=username)
        if usr.exists():
            raise forms.ValidationError("Nazwa użytkownika jest już w użyciu")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        eml = User.objects.filter(email=email)
        print("siema", eml)
        if eml.exists():
            raise forms.ValidationError("EMail jest już w użyciu")
        return email
    
    def clean_password1(self):
        pass1 = self.cleaned_data.get('password1')
        return pass1

    def clean_password2(self):
        pass1 = self.cleaned_data.get('password1')
        pass2 = self.cleaned_data.get('password2')
        if pass1 != pass2:
            raise forms.ValidationError("Podane hasła się różnią")
        return pass2  

class AddFoobtallerForm(forms.ModelForm):
    
    class Meta:
        model = MyFootballer
        fields = '__all__'
