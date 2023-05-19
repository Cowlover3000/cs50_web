from decimal import Decimal, DecimalException
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from .forms import ListingForm
from django.contrib.auth.decorators import login_required
from .models import Bid, Listing, Watchlist, Comment, User, Category
from auctions.forms import ListingForm
from django.contrib import messages


def index(request):
    active_listings = Listing.objects.filter(status='active')
    return render(request, 'auctions/index.html', {'listings': active_listings})


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

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'auctions/category_list.html', {'categories': categories})

def category_detail(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    listings = Listing.objects.filter(category=category, status='active')
    return render(request, 'auctions/category_detail.html', {'category': category, 'listings': listings})

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

@login_required
def listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.creator = request.user
            listing.save()
            return redirect('listing_detail', listing_id=listing.pk)
    else:
        form = ListingForm()

    return render(request, 'auctions/listing.html', {'form': form})



@login_required
def add_to_watchlist(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    watchlist = request.user.watchlist
    watchlist.listings.add(listing)
    return redirect('listing_detail', listing_id=listing_id)

@login_required
def remove_from_watchlist(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    watchlist = request.user.watchlist
    watchlist.listings.remove(listing)
    return redirect('listing_detail', listing_id=listing_id)

def listing_detail(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    comments = Comment.objects.filter(listing=listing)

    return render(request, 'auctions/listing_detail.html', {'listing': listing, 'comments': comments})


@login_required
def watchlist_view(request):
    watchlist = Watchlist.objects.get(user=request.user)
    listings = watchlist.listings.all()

    return render(request, 'auctions/watchlist.html', {'listings': listings})



@login_required
def close_listing(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)

    if request.method == 'POST':
        if listing.creator != request.user:
            messages.error(request, 'You do not have permission to close this listing.')
        elif listing.status == 'closed':
            messages.warning(request, 'This listing is already closed.')
        else:
            highest_bid = listing.highest_bid
            if highest_bid is not None:
                listing.winner = highest_bid.bidder
            listing.status = 'closed'
            listing.save()
            messages.success(request, 'Listing has been closed successfully.')
        return redirect('listing_detail', listing_id=listing_id)

    return render(request, 'auctions/close_listing.html', {'listing': listing})


@login_required
def bid_listing(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    winner = None

    if listing.status == 'closed':
        messages.error(request, 'This listing is closed.')
        return redirect('listing_detail', listing_id=listing_id)

    if request.method == 'POST':
        bid_amount = request.POST.get('bid_amount')
        try:
            bid_amount = Decimal(bid_amount)
        except DecimalException:
            messages.error(request, 'Invalid bid amount.')
            return redirect('listing_detail', listing_id=listing_id)

        if bid_amount <= listing.price:
            messages.error(request, 'Bid amount must be greater than the current price.')
            return redirect('listing_detail', listing_id=listing_id)

        if listing.highest_bid is not None and bid_amount <= listing.highest_bid.amount:
            messages.error(request, 'Bid amount must be strictly greater than the current highest bid.')
            return redirect('listing_detail', listing_id=listing_id)

        # Maak een nieuw bod aan en sla het op als het aan de voorwaarden voldoet
        if listing.highest_bid is None or bid_amount > listing.highest_bid.amount:
            new_bid = Bid.objects.create(listing=listing, bidder=request.user, amount=bid_amount)
            listing.highest_bid = new_bid
            listing.save()

            messages.success(request, 'Your bid has been placed successfully.')
        else:
            messages.error(request, 'Your bid amount is not higher than the current highest bid.')

        return redirect('listing_detail', listing_id=listing_id)

    if listing.status == 'closed':
        highest_bid = listing.highest_bid
        if highest_bid:
            winner = highest_bid.bidder

    return render(request, 'auctions/listing_detail.html', {'listing': listing, 'winner': winner})

def add_comment(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)

    if request.method == 'POST':
        text = request.POST.get('comment_text')
        if text:
            Comment.objects.create(user=request.user, listing=listing, text=text)
            messages.success(request, 'Your comment has been posted successfully.')
        else:
            messages.error(request, 'Please enter a comment.')

    return redirect('listing_detail', listing_id=listing_id)