from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

# User model
class User(AbstractUser):
    pass

# Categories model
class Categories(models.Model):
    categoryName = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.categoryName}"

# Listing model
class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    imageUrl = models.URLField(blank=True, null=True)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)  
    category = models.ForeignKey('Categories', on_delete=models.SET_NULL, related_name="listings", null=True, blank=True)
    owner = models.ForeignKey('User', on_delete=models.CASCADE, related_name="listings")
    isActive = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.starting_bid}"

# Bid model
class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user} bid {self.amount} on {self.listing}"

# Comment model
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()  
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.listing}"

# WatchList model
class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'listing') 

    def __str__(self):
        return f"{self.user.username}'s watchlist: {self.listing.title}"
