from django import forms
from django.contrib.auth.forms import UserCreationForm
from user.models import User
from django.forms import ModelForm
from django.db.models import AutoField 

# from django.contrib.auth.models import User


class SignUpForm(ModelForm):
    # first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    pass_rep = forms.CharField(max_length=30, required=False, help_text='Optional.')
    # email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.') 

    class Meta:
        model = User
        fields = '__all__'


    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

    def update(self, instance, validated_data):
        #TODO hangle the password updating for user
        instance.set_password(
            validated_data.get('password'), instance.password)
        instance.save()

        return instance

