from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django import forms 
from django.contrib.auth.models import User
from .models import *

class ListingForm(forms.ModelForm):
    image = forms.ImageField(required = False)
    class Meta:
        model = Listing
        fields = ['title', 'description', 'image', 'category']

def index(request):
    if request.method == "POST":
        if not request.POST["category"] in Category.objects.values_list('categoryTitle', flat=True):
            return render(request, "auctions/error.html")
        else:
            return render(request, "auctions/index.html", {
                'listings': Listing.objects.filter(active=True, category_id=Category.objects.get(categoryTitle=request.POST["category"]))
            })
    else:
        return render(request, "auctions/index.html", {
            'listings': Listing.objects.filter(active=True)
        })

def listing(request, title):
    try:
        localListingObject = Listing.objects.get(active=True, title__icontains=title)
    except:
        return render(request, "auctions/error.html") 
    return render(request, "auctions/listing.html", {
        'listing': localListingObject
    })

@login_required(login_url="/login")
def watchlist(request):
    return render(request, "auctions/error.html")

@login_required(login_url="/login")
def create(request):
    if request.method == "POST":
        form = ListingForm(request.POST,  request.FILES)
        if not form.is_valid():
            return render(request, "auctions/error.html")
        if request.POST["title"] in Listing.objects.values_list('title', flat=True):
            return render(request, "auctions/error.html")
        obj = form.save(commit=False)
        obj.user = request.user
        obj.active = True
        obj.save()
        return redirect('index')
    else:
        return render(request, "auctions/create.html", {
            'form': ListingForm()
        })
    

def categories(request):
    return render(request, "auctions/categories.html", {
        'categories': Category.objects.values()
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
