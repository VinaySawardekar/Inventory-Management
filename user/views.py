from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm, UserUpdateForm, ProfileUpdateForm
from django.contrib import messages
from dashboard.models import Notification


# Create your views here.

def register(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account has been created for {username}. Continue to Log in')
            return redirect('user-login')
    else:
        form = CreateUserForm()
    context = {
        'form': form,

    }
    return render(request, 'user/register.html', context)
def profile(request):
    notif_data = Notification.objects.filter(is_seen=False,visible_to=request.user).order_by('-date')[:1]
    notif_data_all = Notification.objects.filter(visible_to=request.user)
    notif_count = Notification.objects.filter(is_seen=False,visible_to=request.user).count()
    context= {
        'notif_data': notif_data,
        'notif_count': notif_count,
        'notif_data_all': notif_data_all,
    }
    return render(request, 'user/profile.html',context)

def profile_update(request):
    if request.method=='POST':
        user_form = UserUpdateForm(request.POST, instance = request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance = request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('user-profile')
    else:
        user_form = UserUpdateForm(instance = request.user)
        profile_form = ProfileUpdateForm(instance = request.user.profile)

    notif_data = Notification.objects.filter(is_seen=False,visible_to=request.user).order_by('-date')[:1]
    notif_data_all = Notification.objects.filter(visible_to=request.user)
    notif_count = Notification.objects.filter(is_seen=False,visible_to=request.user).count()
    context={
        'user_form':user_form,
        'profile_form':profile_form,
        'notif_data': notif_data,
        'notif_count': notif_count,
        'notif_data_all': notif_data_all,
    }
    return render(request, 'user/profile_update.html', context)