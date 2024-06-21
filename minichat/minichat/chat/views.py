from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, GroupCreateForm, MessageForm
from .models import Group, Message

def home(request):
    return render(request, 'chat/home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Hisob {username} uchun yaratildi!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'chat/register.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Hisobingiz yangilandi!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'chat/profile.html', context)

@login_required
def group_create(request):
    if request.method == 'POST':
        form = GroupCreateForm(request.POST)
        if form.is_valid():
            group = form.save()
            group.members.add(request.user)
            messages.success(request, 'Guruh muvaffaqiyatli yaratildi!')
            return redirect('group_detail', pk=group.pk)
    else:
        form = GroupCreateForm()
    return render(request, 'chat/group_create.html', {'form': form})

@login_required
def group_detail(request, pk):
    group = Group.objects.get(pk=pk)
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data.get('content')
            Message.objects.create(user=request.user, content=content, group=group)
            return redirect('group_detail', pk=pk)
    else:
        form = MessageForm()
    return render(request, 'chat/group_detail.html', {'group': group, 'form': form})

@login_required
def private_message(request, recipient_id):
    recipient = User.objects.get(pk=recipient_id)
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data.get('content')
            Message.objects.create(user=request.user, content=content, recipient=recipient)
            messages.success(request, 'Xabar muvaffaqiyatli yuborildi!')
            return redirect('private_message', recipient_id=recipient_id)
    else:
        form = MessageForm()
    return render(request, 'chat/private_message.html', {'recipient': recipient, 'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('chat')
        else:
            messages.error(request, 'Noto\'g\'ri foydalanuvchi nomi yoki parol')
    return render(request, 'chat/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def chat(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(user=request.user, content=content)
    messages = Message.objects.all().order_by('-timestamp')
    return render(request, 'chat/chat.html', {'messages': messages})