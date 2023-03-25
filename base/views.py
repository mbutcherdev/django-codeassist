from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, createUserForm


# Create your views here.
def loginSystem(request):
    login_page = "login"

    if request.user.is_authenticated:  # Send user back to home if they are already logged in
        return redirect("home")

    if request.method == "POST":
        email = request.POST.get("email").lower()
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, "User does not exist")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Incorrect details.")

    context = {'page': login_page}
    return render(request, "base/login_sys.html", context)


def home(request):
    q = request.GET.get("q") if request.GET.get("q") is not None else ""

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )

    topic = Topic.objects.all()[0:5]
    room_count = rooms.count()
    # Message activity
    # Could make this a follow-only option
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {"rooms": rooms, 'topics': topic, 'room_count': room_count, 'room_messages': room_messages}

    return render(request, "base/home.html", context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by("-created_time")
    participants = room.participants.all()

    if request.method == "POST":
        message = Message.objects.create(
            user=request.user,
            room=room,
            content=request.POST.get("content")
        )
        room.participants.add(request.user)
        return redirect("room", pk=room.id)

    context = {"room": room, 'room_messages': room_messages, 'participants': participants}
    return render(request, "base/room.html", context)


# View user profiles
def userProfile(request, pk):
    user = User.objects.get(id=pk)
    user_rooms = user.room_set.all()
    user_messages = user.message_set.all()
    topics = Topic.objects.all()

    context = {"user": user, "rooms": user_rooms, "room_messages": user_messages, "topics": topics}
    return render(request, "base/profile.html", context)


@login_required(login_url="login")
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room = Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get("name"),
            description=request.POST.get("description")
        )
        return redirect("home")

    context = {"form": form, "topics": topics}
    return render(request, "base/room_form.html", context)


@login_required(login_url="login")
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse("You are not allowed to do this.")

    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get("name")
        room.topic = topic
        room.description = request.POST.get("description")
        room.save()
        return redirect("home")

    context = {"form": form, "room": room, "topics": topics}
    return render(request, "base/room_form.html", context)


@login_required(login_url="login")
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse("You are not allowed to do this.")
    if request.method == "POST":
        room.delete()
        return redirect("home")
    return render(request, "base/delete.html", {"obj": room})


def logoutSystem(request):
    logout(request)
    return redirect("home")


def registerUser(request):
    form = createUserForm()

    if request.method == "POST":
        form = createUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Don't save the user yet
            # Clean the form into lowercase
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "An error occurred during registration.")

    return render(request, "base/login_sys.html", {"form": form})


@login_required(login_url="login")
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse("You are not allowed to do this.")

    if request.method == "POST":
        message.delete()
        return redirect("home")
    return render(request, "base/delete.html", {"obj": message})


@login_required(login_url="login")
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("user-profile", pk=user.id)

    return render(request, "base/update_user.html", {"form": form})


# Mobile views
def topicsPage(request):
    q = request.GET.get("q") if request.GET.get("q") is not None else ""
    topics = Topic.objects.filter(name__icontains=q)
    context = {"topics": topics}
    return render(request, "base/topics.html", context)


def activitiesPage(request):
    room_messages = Message.objects.all().order_by("-created_time")
    context = {"room_messages": room_messages}
    return render(request, "base/activity.html", context)
