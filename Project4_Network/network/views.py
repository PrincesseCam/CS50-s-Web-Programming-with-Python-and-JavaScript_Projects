from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from .models import User, Post
import json
from django.views.decorators.http import require_POST


def index(request):
    posts = Post.objects.all().order_by('-created_at')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/index.html", {
        "page_obj": page_obj
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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        profile_picture = request.FILES.get("profile_picture")

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            
            # Add profile picture
            if profile_picture:
                user.profile.image = profile_picture
                user.profile.save()
                
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required
def new_post(request):
    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            post = Post.objects.create(user=request.user, content=content)
            return redirect('index')
    return render(request, "network/new_post.html")


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    
    # Add debug prints
    print(f"Profile user: {profile_user.username}")
    print(f"Has profile: {hasattr(profile_user, 'profile')}")
    if hasattr(profile_user, 'profile'):
        print(f"Profile image: {profile_user.profile.image}")
        print(f"Profile image URL: {profile_user.profile.get_image_url}")
    
    posts = Post.objects.filter(user=profile_user).order_by('-created_at')
    is_following = request.user.is_authenticated and request.user.following.filter(id=profile_user.id).exists()
    
    # Handle profile picture update
    if request.method == "POST" and request.user == profile_user:
        if 'profile_picture' in request.FILES:
            profile_user.profile.image = request.FILES['profile_picture']
            profile_user.profile.save()
            return HttpResponseRedirect(reverse('profile', args=[username]))
    
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, "network/profile.html", {
        "profile_user": profile_user,
        'posts': posts,
        "page_obj": page_obj,
        "is_following": is_following,
        "followers_count": profile_user.followers.count(),
        "following_count": profile_user.following.count()
    })


@login_required
def following(request):
    following_users = request.user.following.all()
    posts = Post.objects.filter(user__in=following_users).order_by('-created_at')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/following.html", {
        "page_obj": page_obj
    })


@login_required
def edit_post(request, post_id):
    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)
    
    post = get_object_or_404(Post, id=post_id)
    if post.user != request.user:
        return JsonResponse({"error": "Cannot edit another user's post."}, status=403)
    
    data = json.loads(request.body)
    post.content = data.get("content", "")
    post.save()
    return JsonResponse({"message": "Post updated successfully."})


@require_POST
@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return JsonResponse({
        "liked": liked,
        "likes_count": post.likes.count()
    })


@require_POST
@login_required
def toggle_follow(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    if request.user == user_to_follow:
        return JsonResponse({"error": "Cannot follow yourself"}, status=400)
    
    if request.user in user_to_follow.followers.all():
        user_to_follow.followers.remove(request.user)
        following = False
    else:
        user_to_follow.followers.add(request.user)
        following = True
    
    return JsonResponse({
        "following": following,
        "followers_count": user_to_follow.followers.count()
    })

