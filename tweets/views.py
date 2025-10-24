from django.shortcuts import render
from .models import Tweet
from .forms import TweetForm
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
# Create your views here.

def index(request):
    return render(request,'index.html')

def tweet_list(request):
    tweets = Tweet.objects.all().order_by('-created_at')
    return render(request, 'tweet_list.html',{'tweets':tweets})

@login_required
def tweet_create(request):
    if request.method== "POST":
        form = TweetForm(request.POST, request.FILES)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.user = request.user
            tweet.save()
            return redirect('tweet_list')
    else:
        form = TweetForm()
    return render(request, 'tweet_from.html',{'form':form})


@login_required
def tweet_edit(request,tweet_id):
    tweet = get_object_or_404(Tweet, pk = tweet_id, user = request.user)
    if request.method =='POST':
        form = TweetForm(request.POST, request.FILES, instance=tweet)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.user = request.user
            tweet.save()
            return redirect('tweet_list')
    else: 
        form = TweetForm(instance=tweet)
    return render(request, 'tweet_from.html',{'form':form})


@login_required
def tweet_delete(request, tweet_id):
    tweet = get_object_or_404(Tweet , pk = tweet_id, user = request.user)
    if request.method == 'POST':
        tweet.delete()
        return redirect('tweet_list')
    return render(request, 'tweet_confirm_delete.html',{'tweet':tweet})
    


def register_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, "Account created successfully. Please log in.")
            return redirect("login_page")

    return render(request, "register.html")

def login_page(request):
    if request.method == "GET" and request.GET.get('next'):
        messages.error(request, "You need to Register/Login to access that page.")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)

            if user is not None:
                login(request, user)
                next_url = request.GET.get('next') or 'tweet_list'
                messages.success(request, "Login successful.")
                return redirect(next_url)
            else:
                messages.error(request, "Invalid credentials.")
        except User.DoesNotExist:
            messages.error(request, "No account found with that email.")

    return render(request, "login.html")

def logout_page(request):
    logout(request)
    return redirect('login_page')