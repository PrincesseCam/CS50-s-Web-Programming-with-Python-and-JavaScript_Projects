from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Listing, Comment, Categories, Watchlist, Bid


def index(request):
    Activelistings = Listing.objects.filter(isActive=True)
    # For each listing, fetch the highest bid (if any)
    listings_with_bids = []
    for listing in Activelistings:
        highest_bid = listing.bids.order_by('-amount').first()  # Get the highest bid
        listings_with_bids.append({
            'listing': listing,
            'current_bid': highest_bid.amount if highest_bid else listing.starting_bid
        })
    return render(request, "auctions/index.html", {
        "listings": Activelistings,
        "listings_with_bids": listings_with_bids
    })

########################################

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

########################################
    
@login_required
def createListing(request):
    if request.method == "GET":
        allCategories = Categories.objects.all()
        return render(request, "auctions/create.html", {
            "categories": allCategories
        })
    else:
        # Get data from the form
        title = request.POST["title"]
        description = request.POST["description"]
        imageUrl = request.POST["imageUrl"]
        bid_amount = request.POST["Bid"] 
        category = request.POST["category"]

        # Convert bid amount to a Decimal (important for consistency with model)
        try:
            bid_amount = Decimal(bid_amount)
        except (ValueError, TypeError):
            return render(request, "auctions/create.html", {
                "categories": Categories.objects.all(),
                "error": "Invalid starting bid amount. Please enter a valid number."
            })

        # Get current user who is creating the listing
        currentUser = request.user

        # Fetch the category object based on the selected category
        if category == "None" or category == "":
            catData = None  # No category selected
        else:
            # Fetch the category object based on the selected category
            try:
                catData = Categories.objects.get(categoryName=category)
            except Categories.DoesNotExist:
                return render(request, "auctions/create.html", {
                    "categories": Categories.objects.all(),
                    "error": "Invalid category selected."
                })

        # Create a new Listing object
        newListing = Listing(
            title=title,
            description=description,
            imageUrl=imageUrl, 
            starting_bid=bid_amount,
            category=catData,
            owner=currentUser,
        )

        newListing.save()

        return HttpResponseRedirect(reverse('index'))
    
########################################
    
def categoriesListing(request):
    # Get all categories for the dropdown or buttons
    allCategories = Categories.objects.all()

    return render(request, "auctions/categories.html", {
        "categories": allCategories
    })

from decimal import Decimal

def category_items(request, category_id):
    if category_id == "none":
        # Display listings with no category
        listings = Listing.objects.filter(isActive=True, category__isnull=True)
        category_name = "None"
    else:
        # Display listings in the selected category
        try:
            category = Categories.objects.get(id=category_id)
            listings = Listing.objects.filter(isActive=True, category=category)
            category_name = category.categoryName
        except Categories.DoesNotExist:
            listings = Listing.objects.filter(isActive=True)
            category_name = "Invalid Category"

    # Attach the highest bid or starting bid for each listing
    listings_with_bids = []
    for listing in listings:
        highest_bid = listing.bids.order_by('-amount').first()
        listings_with_bids.append({
            "listing": listing,
            "current_bid": highest_bid.amount if highest_bid else listing.starting_bid
        })

    return render(request, "auctions/category_items.html", {
        "listings_with_bids": listings_with_bids,
        "category_name": category_name
    })



########################################
    
def listingDetail(request, id):
    listing = Listing.objects.get(pk=id)
    comments = Comment.objects.filter(listing=listing)
    highest_bid = listing.bids.order_by('-amount').first() 

    # Check if the listing is in the user's watchlist
    is_in_watchlist = False
    if request.user.is_authenticated:
        is_in_watchlist = Watchlist.objects.filter(user=request.user, listing=listing).exists()

    # Check if the user is the owner
    is_owner = (request.user == listing.owner)

    # Check if the listing is closed
    is_closed = not listing.isActive

    # If the listing is closed, get the winner (highest bidder)
    winner = None
    if is_closed and highest_bid:
        winner = highest_bid.user

    if request.method == "POST":
        # Comment submission
        if 'comment' in request.POST:
            comment_content = request.POST.get('comment', '')
            if comment_content:
                new_comment = Comment(user=request.user, listing=listing, content=comment_content)
                new_comment.save()
                messages.success(request, "Your comment was added!")
                return redirect('listingDetail', id=listing.id)
            else:
                messages.error(request, "Your comment cannot be empty.")

        # Bid submission
        if 'bid' in request.POST:
            if not is_closed:
                bid_amount = float(request.POST.get('bid', 0))

                if bid_amount <= listing.starting_bid:
                    messages.error(request, "Your bid must be higher than the starting bid.")
                elif highest_bid and bid_amount <= highest_bid.amount:
                    messages.error(request, "Your bid must be higher than the current highest bid.")
                else:
                    # Place a new bid
                    new_bid = Bid(user=request.user, listing=listing, amount=bid_amount)
                    new_bid.save()
                    messages.success(request, "Your bid was successfully placed!")
                    return redirect('listingDetail', id=listing.id)
            else:
                messages.error(request, "Bidding is closed for this auction.")

        # Handle closing the auction
        if 'close_auction' in request.POST and is_owner and listing.isActive:
            listing.isActive = False
            listing.save()
            messages.success(request, f"Auction closed. The winner is {highest_bid.user.username}!")
            return redirect('listingDetail', id=listing.id)


    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comments": comments,
        "highest_bid": highest_bid,
        "is_in_watchlist": is_in_watchlist,
        "is_owner": is_owner,
        "is_closed": is_closed,
        "winner": winner
    })

########################################
@login_required
def watchlist(request):
    watchlist_items = Watchlist.objects.filter(user=request.user)
    return render(request, "auctions/watchlist.html", {
        "watchlist_items": watchlist_items
    })

@login_required
def add_to_watchlist(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    Watchlist.objects.get_or_create(user=request.user, listing=listing)
    return redirect('listingDetail', id=listing_id)

@login_required
def remove_from_watchlist(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    Watchlist.objects.filter(user=request.user, listing=listing).delete()
    return redirect('listingDetail', id=listing_id)


########################################
@login_required
def close_listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    if listing.owner == request.user:
        listing.isActive = False
        listing.save()

    return redirect('listingDetail', id=listing_id)
