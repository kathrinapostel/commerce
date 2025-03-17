from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class User(AbstractUser):
    """User model - inherited from Django implementation"""
    pass

class Auction(models.Model):
    """Auction model contains all info about one auction:
    * auction's title
    * auction's description
    * who is selling
    * auction's current price
    * when auction was published
    * what is auction's category
    * auction's image URL
    * is auction closed?
    """

    # Categories - choices
    FASHION = "FAS"
    ELECTRONICS = "ELE"
    HOME_GARDES = "HGA"
    SPORTING_GOODS = "SPO"
    TOYS = "TOY"
    MUSIC = "MUS"

    CATEGORY = [
        (FASHION, "Fashion"),
        (ELECTRONICS, "Electronics"),
        (HOME_GARDES, "Homes"),
        (SPORTING_GOODS, "Sports"),
        (TOYS, "Toys"),
        (MUSIC, "Music"),
    ]

    # Model fields
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=64, blank=False)
    description = models.TextField(blank=True)
    current_price = models.DecimalField(max_digits=11, decimal_places=2, default=0.0)
    category = models.CharField(max_length=3, choices=CATEGORY, default=FASHION)
    image_url = models.URLField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Preis-Feld hinzugefügt
    publication_date = models.DateTimeField(auto_now_add=True)
    closed = models.BooleanField(default=False)
    end_date = models.DateTimeField(null=True, blank=True)

    def clean(self):
        if self.price is None:
            raise ValidationError("Price cannot be empty.")
        if self.price <= 0:
            raise ValidationError("Price must be greater than 0.")

    def save(self, *args, **kwargs):
        """Auktion automatisch schließen, wenn das Enddatum erreicht ist"""
        if self.end_date and self.end_date < timezone.now():
            self.closed = True
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "auction"
        verbose_name_plural = "auctions"

    def __str__(self):
        return f"Auction id: {self.id}, title: {self.title}, seller: {self.seller}"

class Bid(models.Model):
    """Bid model contains all info about single bid:
    * price
    * who bid
    * when
    * on what auction
    """

    # Model fields
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_date = models.DateTimeField(auto_now_add=True)
    bid_price = models.DecimalField(max_digits=11, decimal_places=2)

    def save(self, *args, **kwargs):
        """Aktualisiert den aktuellen Preis der Auktion, wenn das Gebot höher ist"""
        if not self.auction.closed:
            if self.bid_price > self.auction.current_price:
                self.auction.current_price = self.bid_price
                self.auction.save()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "bid"
        verbose_name_plural = "bids"

    def __str__(self):
        return f"{self.user} bid {self.bid_price} $ on {self.auction}"

class Comment(models.Model):
    """Comment model contains all info about single comment:
    * content
    * who posted
    * when
    * on what auction
    """

    # Model fields
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(blank=False)
    comment_date = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name = "comment"
        verbose_name_plural = "comments"

    def __str__(self):
        return f"Comment {self.id} on auction {self.auction} made by {self.user}"

class Watchlist(models.Model):
    """Watchlist model contains all info about object on watchlist:
    * which auction is on watchlist
    * on whose watchlist this auction is
    """

    # Model field
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")

    class Meta:
        verbose_name = "watchlist"
        verbose_name_plural = "watchlists"
        # Forces to not have auction duplicates for one user
        unique_together = ["auction", "user"]

    def __str__(self):
        return f"{self.auction} on user {self.user} watchlist"
