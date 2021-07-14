from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import AnonymousUser
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import *
from . import util
from django.contrib.auth.decorators import login_required


# Form for creating a new listing
class NewListingForm(forms.Form):
    list_title = forms.CharField(widget=forms.TextInput(attrs={'size':100}), label = "Listing Title", max_length=100)
    description = forms.CharField(widget=forms.TextInput(attrs={'size':100}), label = "Description", max_length=1000)
    starting_bid = forms.DecimalField(widget=forms.TextInput(attrs={'size':100}), label = "Starting Bid", max_digits=10, decimal_places=2)
    category_id = forms.CharField(widget=forms.TextInput(attrs={'size':100}), label="Category (optional)", max_length=100, required=False)
    image_url = forms.CharField(widget=forms.TextInput(attrs={'size':100}), label="Image URL (optional)", max_length=300, required=False)

# Form for bidding on an auction
class NewBidForm(forms.Form):
    listing_id = forms.CharField(widget=forms.TextInput(attrs={'size':10}), label = "Listing Title", max_length=1000)
    bidder_id = forms.CharField(widget=forms.TextInput(attrs={'size':10}), label = "Bidder Name", max_length=1000) 
    bid_amount = forms.DecimalField(widget=forms.TextInput(attrs={'size':100}), label = "Starting Bid", max_digits=10, decimal_places=2)


# Main listing page
def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all()
    })


# Login to existing account
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


# Log out of account session
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


# Create a new user account
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


# Create a new auction listing
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


# Call up the listing for this title
def listing(request, title):
    in_list = False     # Default to indicate title not in users watchlist

    # Get the listing
    listing = Listing.objects.get(list_title=title)

    # Check that listing exists
    if listing:  
        # Check if user is logged in or not   
        if request.user.is_anonymous:
            pass
        else:
            logged_user = request.user      # Get user id
            watchlist = Watchlist.objects.filter(user_id=logged_user)   # Get users watchlist
            
            # Check user has a watchlist
            if watchlist:
                # Check if title is in the watchlist
                if watchlist.filter(listing_id=listing.id):
                    in_list = "True"    # Indicate title is in users watchlist
                else:
                    pass    

    # Do nothing if listing doesn't exist
    else:    
        pass    


    # Get the bids for this title
    # bids = 
    #
    # Determine the highest bid
    # highest_bid = util.high_bid(   )
    #
    # Create a new bid form
    # new_bid = 
    #

    # Send listing, title status, bid form and highest bid
    return render(request, "auctions/listing.html", {
        "listing": listing, 
        "in_list": in_list,  
        #"highest_bid": highest_bid
        #"form": new_bid
    })


# if user logged in, try to add the listing to their watchlist
@login_required
def watchlist(request, title):     
    listing = Listing.objects.get(list_title=title)             # Get the listing
    logged_user = request.user                                  # Get the user's id
    users_list = Watchlist.objects.filter(user_id=logged_user)  # Get the users watchlist
    
    # Check if the user has this title in the watchlist
    if users_list.filter(listing_id=listing.id):
        message = " is already in your watchlist"    # Let user know its already there
        in_list = "True"

        # Send back to listing page with message
        return render(request, "auctions/listing.html", {
        "listing": listing, "in_list": in_list, "message": message, "title": title
        })

    # Add listing to the watchlist
    else:
        watch = Watchlist(
            user_id = logged_user,
            listing_id = listing
        )
        watch.save()     
        message = " has been added to your watchlist"    # Let user know its been added
    
    # Send the users watchlist to the template
    return render(request, "auctions/watchlist.html", {
        "users_list": users_list, "message": message, "title": title    
    })


# If user logged in, try to remove the listing from their watchlist
@login_required
def remove_watch(request, title):     
    listing = Listing.objects.get(list_title=title)             # Get the listing
    logged_user = request.user                                  # Get the user's id
    to_remove = Watchlist.objects.filter(user_id=logged_user, listing_id=listing)  # Get the listing from users watchlist
    
    # Remove listing from the watchlist
    to_remove.delete()  

    # Advise listing removed
    message = " has been removed from your watchlist"     
    in_list = "False"   
    
    users_list = Watchlist.objects.filter(user_id=logged_user)  # Get the users updated watchlist

    # Send the users watchlist to the template
    return render(request, "auctions/watchlist.html", {
        "users_list": users_list, "message": message, "title": title
    })


# Bid on an item
'''
@login_required
def remove_watch(request, title):     
    listing = Listing.objects.get(list_title=title)             # Get the listing
    logged_user = request.user                                  # Get the user's id
    to_remove = Watchlist.objects.filter(user_id=logged_user, listing_id=listing)  # Get the listing from users watchlist
    
    # Remove listing from the watchlist
    to_remove.delete()  

    # Advise listing removed
    message = "The listing has been removed from your watchlist"     
    in_list = "False"   
    
    users_list = Watchlist.objects.filter(user_id=logged_user)  # Get the users updated watchlist

    # Send the users watchlist to the template
    return render(request, "auctions/watchlist.html", {
        "users_list": users_list, "message": message
    })
'''