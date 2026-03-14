from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Post, Like, Comment


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken')
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, 'Account created! Please login.')
        return redirect('login')

    return render(request, 'home/register.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('feed')
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('login')

    return render(request, 'home/login.html')


def user_logout(request):
    logout(request)
    return redirect('login')


@login_required
def feed(request):
    posts = Post.objects.all().order_by('-created_at')
    liked_posts = Like.objects.filter(user=request.user).values_list('post_id', flat=True)
    return render(request, 'home/feed.html', {'posts': posts, 'liked_posts': liked_posts})


@login_required
def create_post(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        caption = request.POST.get('caption', '')

        if image:
            Post.objects.create(
                author=request.user,
                image=image,
                caption=caption
            )
            return redirect('feed')
        else:
            messages.error(request, 'Please select an image')
            return redirect('create_post')

    return render(request, 'home/create_post.html')


@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    already_liked = Like.objects.filter(user=request.user, post=post).exists()

    if already_liked:
        Like.objects.filter(user=request.user, post=post).delete()
    else:
        Like.objects.create(user=request.user, post=post)

    return redirect('feed')


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    text = request.POST.get('text', '')

    if text:
        Comment.objects.create(
            author=request.user,
            post=post,
            text=text
        )

    return redirect('feed')