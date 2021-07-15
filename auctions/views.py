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
    bid_amount = forms.DecimalField(widget=forms.TextInput(attrs={'size':20}), label = "Enter your bid   ", max_digits=10, decimal_places=2)

# Form for adding a comment
class NewCommentForm(forms.Form):
    comment = forms.CharField(widget=forms.TextInput(attrs={'size':100}), label = "Add a comment", max_length=500)



# Main active listing page
def index(request):
    active_listings = Listing.objects.filter(active=True)
    bids = Bid.objects.all()

    return render(request, "auctions/index.html", {
        "listings": active_listings, "bids": bids
    })

# Closed listings page
def closed(request):
    closed_listings = Listing.objects.filter(active=False)

    return render(request, "auctions/closed.html", {
        "listings": closed_listings
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
                highest_bid = new_input.cleaned_data["starting_bid"],
                high_bidder = request.user,
                category_id = new_input.cleaned_data["category_id"],
                image_url = new_input.cleaned_data["image_url"],
                active = True
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

    # Try to get the listing
    try:
        listing = Listing.objects.get(list_title=title)
        
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

        # Get the highest bid
        highest_bid = listing.highest_bid
    
        # Create a new bid form
        bid_form = NewBidForm()  

        # Create a new comment form     
        comment_form = NewCommentForm()
        
        comments = Comment.objects.filter(listing_id=listing.id)         # Get the comments

        # Send listing, title status, bid form and highest bid
        return render(request, "auctions/listing.html", {
            "listing": listing, 
            "in_list": in_list,  
            "highest_bid": highest_bid,
            "bid_form": bid_form,
            "comments": comments,
            "comment_form": comment_form,            
        })        

    # Do nothing if listing doesn't exist
    except Listing.DoesNotExist:
        return HttpResponseRedirect(reverse("index"))


# if user logged in, try to add the listing to their watchlist
@login_required
def watchlist_add(request, title):     
    listing = Listing.objects.get(list_title=title)             # Get the listing
    logged_user = request.user                                  # Get the user's id
    users_list = Watchlist.objects.filter(user_id=logged_user)  # Get the users watchlist
    comments = Comment.objects.filter(listing_id=listing.id)         # Get the comments   
    comment_form = NewCommentForm()     # Create a new comment form     
    
    # Check if the user has this title in the watchlist
    if users_list.filter(listing_id=listing.id):
        message = str(title) + " is already in your watchlist"    # Let user know its already there
        in_list = "True"


        # Send back to listing page with message
        return render(request, "auctions/listing.html", {
            "listing": listing, 
            "in_list": in_list, 
            "message": message, 
            "title": title,
            "comments": comments,
            "comment_form": comment_form
        })

    # Add listing to the watchlist
    else:
        watch = Watchlist(
            user_id = logged_user,
            listing_id = listing
        )
        watch.save()     
        message = str(title) + " has been added to your watchlist"    # Let user know its been added
    
    # Send the users watchlist to the template
    return render(request, "auctions/watchlist.html", {
        "users_list": users_list, "message": message, "title": title    
    })


# If user logged in, try to remove the listing from their watchlist
@login_required
def watchlist_remove(request, title):     
    listing = Listing.objects.get(list_title=title)             # Get the listing
    logged_user = request.user                                  # Get the user's id
    to_remove = Watchlist.objects.filter(user_id=logged_user, listing_id=listing)  # Get the listing from users watchlist
    
    # Remove listing from the watchlist
    to_remove.delete()  

    # Advise listing removed
    message = str(title) + " has been removed from your watchlist"     
    in_list = "False"   
    
    users_list = Watchlist.objects.filter(user_id=logged_user)  # Get the users updated watchlist

    # Send the users watchlist to the template
    return render(request, "auctions/watchlist.html", {
        "users_list": users_list, "message": message, "title": title
    })


# View users watchlist
@login_required
def watchlist_view(request):     
    logged_user = request.user      # Get the user's id 

    try:
        users_titles = Watchlist.objects.filter(user_id=logged_user)  # Get the users watchlist
    except Watchlist.DoesNotExist:
        users_titles = None

    if users_titles is None:
        message = "List is empty"
        return render(request, "auctions/watchlist.html", {
            "message": message
        })
    else:
        # Send the users watchlist to the template
        return render(request, "auctions/watchlist.html", {
            "users_list": users_titles
        })



# Bid on an item
@login_required
def bid(request, title):
    logged_user = request.user      # Get the user's id 
    listing = Listing.objects.get(list_title=title)         # Get the listing
    users_list = Watchlist.objects.filter(user_id=logged_user)  # Get the users watchlist
    in_list = "False"
    message = None

    # Validate submitted bid
    if request.method == "POST":        
        new_input = NewBidForm(request.POST)

    if new_input.is_valid():    
        # Check the bid is higher than current highest bid
        new_bid = new_input.cleaned_data["bid_amount"]

        if new_bid > listing.highest_bid:
            # Add the bid to the bid db
            bid = Bid(
                listing_id = listing,
                bidder_id = logged_user,
                bid_amount = new_bid
                )
            bid.save() 

            # Update the listing's highest_bid and bidder
            listing.highest_bid = new_input.cleaned_data["bid_amount"]
            listing.high_bidder = logged_user
            listing.save()

            message = "Your bid has been accepted"
        else:
            message = "New bid must be higher than the current price"
  
    # Create a new bid form
    bid_form = NewBidForm()   

    # Create a new comment form     
    comment_form = NewCommentForm()

    # Check if the user has this title in the watchlist
    if users_list.filter(listing_id=listing.id):
        in_list = "True"

    comments = Comment.objects.filter(listing_id=listing.id)

    # Go back to listing 
    return render(request, "auctions/listing.html", {
        "listing": listing, 
        "in_list": in_list,  
        "message": message,
        "bid_form": bid_form,
        "comments": comments,
        "comment_form": comment_form
    })


# Close an auction listing
@login_required
def close(request, title):
    logged_user = request.user      # Get the user's id 
    listing = Listing.objects.get(list_title=title)         # Get the listing            
    comment_form = NewCommentForm()          # Create a new comment form


    if logged_user == listing.poster_id:
        # Close the auction
        listing.active = False
        listing.save()

        message = "This auction has been closed. " + str(listing.high_bidder) + " won the auction."

    comments = Comment.objects.filter(listing_id=listing.id)

    # Go back to listing 
    return render(request, "auctions/listing.html", {
        "listing": listing, 
        "message": message,
        "comments": comments,
        "comment_form": comment_form
    })

# Add a comment
@login_required
def comment(request, title):
    logged_user = request.user      # Get the user's id 
    listing = Listing.objects.get(list_title=title)         # Get the listing
    comment_form = NewCommentForm()          # Create a new comment form

    if request.method == "POST":        
        new_input = NewCommentForm(request.POST)

        if new_input.is_valid():   
            comment = new_input.cleaned_data["comment"]
            
            # Add the comment to the comment db
            new_comment = Comment(
                user_id = logged_user,
                listing_id = listing,
                comment = comment
                )
            new_comment.save() 

    comments = Comment.objects.filter(listing_id=listing.id)

    # Go back to listing 
    return render(request, "auctions/listing.html", {
        "listing": listing, 
        "comments": comments,
        "comment_form": comment_form
    })
