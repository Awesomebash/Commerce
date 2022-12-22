from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django import forms 
from django.contrib.auth.models import User
from .models import *

#TODO: Bid system


class ListingForm(forms.ModelForm):
    image = forms.ImageField(required = False)
    class Meta:
        model = Listing
        fields = ['title', 'description', 'image', 'category']

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['price']

class WatchlistForm(forms.Form):
    wishlist = forms.BooleanField(required=False)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['commentText']

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
    if request.method == "POST":
        if not request.user.is_authenticated:
            return render(request, "auctions/error.html") 
        print(request.POST)
        form = CommentForm(request.POST)
        if not form.is_valid():
            form = BidForm(request.POST)
            if not form.is_valid():
                return render(request, "auctions/error.html")
            obj = form.save(commit=False)
            obj.bidsListing = localListingObject
            obj.save()
            return redirect('index')
        obj = form.save(commit=False)
        obj.commentListing = localListingObject
        obj.commentUser = request.user
        obj.save()
        return redirect('index')
    else:
        userWishlist = request.user.id in Listing.objects.values_list('watcher', flat=True)
        userWishlist = request.user.id != None
        return render(request, "auctions/listing.html", {
            'listing': localListingObject,
            'bidForm': BidForm(),
            'watchlistForm': WatchlistForm(initial={'wishlist': userWishlist}),
            'comments': Comment.objects.filter(commentListing=localListingObject),
            'commentForm': CommentForm()
        })

@login_required(login_url="/login")
def watchlist(request):
    if request.method == "POST":
        form = WatchlistForm(request.POST)
        if not form.is_valid():
            return render(request, "auctions/error.html")
        listing = Listing.objects.get(id=request.POST["listing"])
        if form.cleaned_data["wishlist"]:
            listing.watcher.add(request.user)
        else:
            listing.watcher.remove(request.user)
        return redirect('index')
    else:
        return render(request, "auctions/index.html", {
            'listings': Listing.objects.filter(active=True, watcher=request.user)
        })

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
