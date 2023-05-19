from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver



class User(AbstractUser):
    pass


class Listing(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('closed', 'Closed'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    highest_bid = models.OneToOneField('Bid', on_delete=models.SET_NULL, null=True, blank=True, related_name='listing_highest_bid')
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_listings')

    def __str__(self):
        return self.title
    
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bids')
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Bid by {self.bidder.username} on {self.listing.title}'

@receiver(post_save, sender=Listing)
def create_initial_bid(sender, instance, created, **kwargs):
    if created:
        Bid.objects.create(listing=instance, bidder=instance.creator, amount=instance.price)

@receiver(post_save, sender=User)
def create_watchlist(sender, instance, created, **kwargs):
    if created:
        Watchlist.objects.create(user=instance)

class Watchlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    listings = models.ManyToManyField(Listing, blank=True)

    def __str__(self):
        return f"Watchlist for {self.user.username}"    
    
@receiver(post_save, sender=Listing)
def create_initial_bid(sender, instance, created, **kwargs):
    if created:
        Bid.objects.create(listing=instance, bidder=instance.creator, amount=instance.price)
