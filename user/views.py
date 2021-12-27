from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMultiAlternatives
from django.http import request
from django.http.response import HttpResponseForbidden
from user.models import *
import os
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import auth
from .forms import SignUpForm
from django.views.generic import ListView
from django.shortcuts import render, redirect


def home(request):
    #just landing page
    return render(request, 'home.html',)


def signup(request):
    #register user using signupform in forms.py >>> (email as username)
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            print('\n\n\n\n\n form is valid  \n\n\n\n')
            form.save()
            user = auth.authenticate(
            email=request.POST['email'], password=request.POST['password'])

            auth.login(request, user) # handle successful registraion redirection
            return redirect('home')
    else: 
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def login(request):
    if request.method == 'POST':        
        user = auth.authenticate(
            username=request.POST['email'], password=request.POST['password'])
        if user is not None:
            auth.login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Username or password is incorrect!'})
    else:
        return render(request, 'login.html')

class MoviesList(ListView):
    #get the list of movies to pick and 
    pass