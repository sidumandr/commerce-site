from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Category(models.Model):
    categoryName = models.CharField(max_length=64)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.categoryName
    

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    imageUrl = models.CharField(max_length=1000, blank=True)
    price = models.FloatField()
    isActive = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True,blank=True)
    
    #foreign keys
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userListings")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, related_name="listings")
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="auction_won")

def __str__(self):
    return self.title


class Bid(models.Model):
    bid = models.FloatField()
    user =models.ForeignKey(User, on_delete=models.CASCADE, related_name="userBids")
    listing=models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")

    class Meta:
        pass

    def __str__(self):
        return f"{self.user.username} = {self.bid} on {self.listing.title}"


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userComments") 
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments") 
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username} commented on {self.listing.title}"
    

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'listing') 
        verbose_name_plural = "Watchlists"

    def __str__(self):
        return f"{self.user.username} watches {self.listing.title}"
    
