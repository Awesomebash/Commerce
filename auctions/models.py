from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    categoryTitle = models.CharField(max_length=64)
    
    def __str__(self) -> str:
        return f"{self.id}: {self.categoryTitle}"

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=1000)
    image = models.ImageField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="categoriesListings")
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="userListings")
    active = models.BooleanField()
    watcher = models.ManyToManyField(User, blank=True, related_name="watching")

    def __str__(self) -> str:
        return f"{self.id}: {self.title}"

class Bid(models.Model):
    price = models.IntegerField()
    bidsListing = models.ForeignKey(Listing, on_delete=models.PROTECT, related_name="listingsBids")
    bidUser = models.ForeignKey(User, on_delete=models.PROTECT, related_name="userBid")

    def __str__(self) -> str:
        return f"{self.id}: {self.price}"

class Comment(models.Model):
    commentText = models.CharField(max_length=1000) 
    commentListing = models.ForeignKey(Listing, on_delete=models.PROTECT, related_name="listingComment")
    commentUser = models.ForeignKey(User, on_delete=models.PROTECT, related_name="userComments")
    
    def __str__(self) -> str:
        return f"{self.id}: {self.commentUser.username}"
