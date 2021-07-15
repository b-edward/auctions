from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    poster_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="poster")
    list_title = models.CharField(max_length=100, help_text="Enter a title using 100 characters or less.")     
    description	= models.CharField(max_length=1000, help_text="Enter a description using 1000 characters or less.")    
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)	
    highest_bid = models.DecimalField(max_digits=10, decimal_places=2)	
    bidder_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")
    category_id	= models.CharField(max_length=100)
    image_url = models.CharField(max_length=300, help_text="Enter the URL of an image, using 300 characters or less.")
    active = models.BooleanField() 
    
    def __str__(self):
        return f"{self.list_title}"

'''
class Bid(models.Model):
    listing_id = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_bid")
    bidder_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"${self.bid_amount}"
'''

class Comment(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commenter")
    listing_id = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_comment")
    comment = models.CharField(max_length=500, help_text="Enter a comment using 500 characters or less.")

    def __str__(self):
        return f"{self.user_id} commented: \"{self.comment}\" on {self.listing_id}."    

class Watchlist(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watcher")     
    listing_id = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_watch")

    def __str__(self):
        return f"{self.user_id} is watching: {self.listing_id}."