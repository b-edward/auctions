from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import *


# form for creating a new listing
class NewListingForm(forms.Form):
    list_title = forms.CharField(widget=forms.TextInput(attrs={'size':100}), label = "Listing Title", max_length=100)
    description = forms.CharField(widget=forms.TextInput(attrs={'size':100}), label = "Description", max_length=500)
    starting_bid = forms.DecimalField(widget=forms.TextInput(attrs={'size':100}), label = "Starting Bid", max_digits=10, decimal_places=2)
    category_id = forms.CharField(widget=forms.TextInput(attrs={'size':100}), label="Category (optional)", max_length=100, required=False)
    image_url = forms.CharField(widget=forms.TextInput(attrs={'size':100}), label="Image URL (optional)", max_length=300, required=False)


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all()
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


def create_new(request):
    if request.method == "POST":
        # Validate submitted listing
        new_input = NewListingForm(request.POST)
        if new_input.is_valid():    
            # Save new listing
            new_listing = Listing(
                poster_id = request.user,
                list_title = new_input.cleaned_data["list_title"],
                description = new_input.cleaned_data["description"],
                starting_bid = new_input.cleaned_data["starting_bid"],
                category_id = new_input.cleaned_data["category_id"],
                image_url = new_input.cleaned_data["image_url"],
                )
            new_listing.save()

        # Display the index    
        return HttpResponseRedirect(reverse("index"))

    else:
        return render(request, "auctions/create.html", {
            "form": NewListingForm()
        })

def listing(request, title):

    listing = Listing.objects.get(list_title=title)
    return render(request, "auctions/listing.html", {
        "listing": listing
    })