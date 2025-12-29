from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import User, Listing, Bid, Comment, Category, Watchlist
from .forms import ListingForm, BidForm, CommentForm
from django.db.models import Max
from django.contrib import messages

def index(request):
    active_listing = Listing.objects.filter(isActive=True).order_by("-id")
    return render(request, "auctions/index.html", {
        "listings": active_listing 
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


@login_required
def create_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.price = form.cleaned_data['price']
            listing.save()
            form.save_m2m()

            return redirect(reverse("listing", args=[listing.id]))
    else:
        form = ListingForm()

    return render(request, "auctions/create_listing.html", {
        "form": form
    })


def listing(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)

    highest_bid = listing.bids.order_by('-bid').first()
    current_price = highest_bid.bid if highest_bid else listing.price

    bid_form = BidForm()

    is_on_watchlist = False
    if request.user.is_authenticated:
        is_on_watchlist = Watchlist.objects.filter(user=request.user, listing=listing).exists()
    
    is_winner = request.user.is_authenticated and listing.winner == request.user and not listing.isActive

        
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "current_price": current_price,
        "is_owner": request.user.is_authenticated and request.user == listing.owner,
        "bid_form": bid_form, 
        "comment_form": CommentForm(),
        "comments": listing.comments.all().order_by("-timestamp"),
        "is_on_watchlist": is_on_watchlist, 
        "is_winner": is_winner,
        "highest_bid_user": highest_bid.user.username if highest_bid else None
    })

@login_required
def bid(request, listing_id):
    if request.method == "POST":
        listing = get_object_or_404(Listing, pk=listing_id)
        form = BidForm(request.POST)

        if form.is_valid():
            new_bid_amount = form.cleaned_data["bid"]

            highest_bid_data = listing.bids.aggregate(Max('bid'))
            current_max_bid = highest_bid_data.get('bid__max')
            current_max_price = current_max_bid if current_max_bid is not None else listing.price

            if new_bid_amount <= current_max_price:
                messages.error(request, f"Your bid must be higher than the current highest bid of ${current_max_price:.2f}")
                return redirect(reverse("listing", args=[listing_id]))
            
            Bid.objects.create(
                user=request.user,
                listing=listing,
                bid=new_bid_amount
            )

            messages.success(request, f"Your bid of (${new_bid_amount:.2f}) has been successfully recorded.")
            return redirect(reverse("listing", args=[listing_id]))
        messages.error(request, "The bid form is invalid. Please enter a valid amount!")
    
    return redirect(reverse("listing", args=[listing_id]))

@login_required
def close_auction(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    

    if request.user != listing.owner:
        messages.error(request, "You do not have permission to close this auction.")
        return redirect(reverse("listing", args=[listing_id]))

    
    if not listing.isActive:
        messages.warning(request, "This auction is already closed.")
        return redirect(reverse("listing", args=[listing_id]))

    
    highest_bid = listing.bids.order_by('-bid').first()

    if highest_bid:
        
        listing.winner = highest_bid.user
        listing.price = highest_bid.bid  
        messages.success(request, f"Auction closed! Winner: {listing.winner.username} (${listing.price:.2f}).")
    else:
        
        listing.winner = None
        messages.info(request, "Auction closed. However, there is no winner as no bids were placed.")
        
    
    listing.isActive = False
    listing.save()

    return redirect(reverse("listing", args=[listing_id]))

@login_required
def add_to_watchlist(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    
    watchlist_item, created = Watchlist.objects.get_or_create(
        user=request.user, 
        listing=listing
    )
    
    if created:
        messages.success(request, f"{listing.title} has been added to your watchlist.")
    else:
        watchlist_item.delete()
        messages.success(request, f"{listing.title} has been removed from your watchlist.")
        
    return redirect(reverse("listing", args=[listing_id]))

@login_required
def watchlist(request):
    watchlisted_listings = []

    for item in request.user.watchlist.all():
        listing = item.listing
        highest_bid = listing.bids.order_by('-bid').first()
        current_price = highest_bid.bid if highest_bid else listing.price

        watchlisted_listings.append({
            "listing": listing,
            "current_price": current_price
        })
    
    return render(request, "auctions/watchlist.html", {
        "listings": watchlisted_listings,
        "title": "Your Watchlist"
    })

@login_required
def comment(request, listing_id):
    if request.method == "POST":
        listing = get_object_or_404(Listing, pk=listing_id)
        form = CommentForm(request.POST)

        if form.is_valid():
            new_comment = form.save(commit=False)

            new_comment.author = request.user
            new_comment.listing = listing

            new_comment.save()

            messages.success(request, "Your comment has been successfully saved.")
            return redirect(reverse("listing", args=[listing_id]))
        
        messages.error(request, "The comment form is invalid. Please enter a message.")
    
    return redirect(reverse("listing", args=[listing_id]))


def categories(request):
    all_categories = Category.objects.all().order_by('categoryName')

    return render(request, "auctions/categories.html", {
        "categories": all_categories
    })

def category_listing(request, category_name):
    category = get_object_or_404(Category, categoryName=category_name)

    listings = Listing.objects.filter(category=category, isActive=True).order_by("-id")

    return render(request, "auctions/index.html", {
        "listings": listings,
        "title": f"Category: {category_name}"
    })

