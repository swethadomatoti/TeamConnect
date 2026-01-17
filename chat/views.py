from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .form import RegistrationForm
from .models import CustomUser,Room,Message
# Create your views here.
from .task import send_welcome_celeryemail, send_otp_email
def register_user(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)#creating an form
        if form.is_valid():#Validate the form data
            user = form.save()# Save the new user to the database
            # send mail using celery
            send_welcome_celeryemail(user.username,user.email)
            messages.success(request, "Registration successful! Check your email for a welcome message.")
            return render(request,'login.html')
        else:
            print("Form invalid:", form.errors)
    else:
        form = RegistrationForm()
        print("Form invalid:", form.errors)
    return render(request, 'register.html', {'form': form})

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('room_list')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'login.html')

import random  
from django.utils import timezone
from datetime import timedelta

# Step 1: Show form to enter email
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')# Get email 
        try:
            user = CustomUser.objects.get(email=email)# Find user by email
            otp = str(random.randint(100000, 999999))# generate a 6-digit OTP
            user.otp_code = otp# Save OTP and expiry time to user record
            user.otp_expires_at = timezone.now() + timedelta(minutes=1)# setting 1 minute expiry
            user.save()           #current date and time + time duration          
            send_otp_email.delay(user, otp)
            messages.success(request, 'OTP has been sent to your email.')
            request.session['reset_email'] = user.email  # store temporarily for further verification
            return redirect('verify_otp')  # move to OTP verification page  
        except CustomUser.DoesNotExist:
            messages.error(request, 'Email not found!')
    return render(request, 'forgot_password.html')

def verify_otp(request):
    email = request.session.get('reset_email')#This email identifies which user is trying to reset their password.
    if not email:
        messages.error(request, "Session expired. Please try again.")
        return redirect('forgot_password')
    user = CustomUser.objects.get(email=email) #verifying who the user is before checking the OTP.
    if request.method == 'POST':#if the form is submitted
        entered_otp = request.POST.get('otp')#Getting the entered otp
        if entered_otp == user.otp_code and not user.is_otp_expired():# it checks if the entered Otp is matched or not 
            request.session['otp_verified'] = True  
            return redirect('reset_password') 
        else:
            messages.error(request, "Invalid or expired OTP.")
    return render(request, 'verify_otp.html', {'email': email})

# Step 2: Reset password form
def reset_password(request):
    email = request.session.get('reset_email')
    otp_verified = request.session.get('otp_verified', False)
    if not email or not otp_verified:
        messages.error(request, "Unauthorized access.")
        return redirect('forgot_password')
    user = CustomUser.objects.get(email=email)
    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 == password2:
            user.set_password(password1)
            user.otp_code = ''
            user.otp_expires_at = None
            user.save()
            # clear session
            request.session.pop('reset_email', None)
            request.session.pop('otp_verified', None)
            messages.success(request, 'Password reset successfully! You can now login.')
            return redirect('login')
        else:
            messages.error(request, 'Passwords do not match.')
    return render(request, 'reset_password.html', {'user': user})

def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return render(request, 'logout.html')

def Users_list(request):
    customuser = CustomUser.objects.all()  # fetch all users
    return render(request, 'usersdata.html', {'customuser': customuser})
from django.http import HttpResponse
def delete_user(request):
  m=CustomUser.objects.filter(username="SwethaD")
  m.delete()
  return HttpResponse("User deleted successfully")

 


@login_required
def room_list(request):
    # Display all available chat rooms
    rooms = Room.objects.all()
    return render(request, 'room_list.html', {'rooms': rooms})


@login_required
def create_room(request):
    # Allow user to create a new chat room
    if request.method == 'POST':
        room_name = request.POST.get('room_name')
        if room_name:
            # Create room only if it doesn’t already exist
            room, created = Room.objects.get_or_create(
                name=room_name,
                defaults={'created_by': request.user}
            )
            return redirect('room_detail', room_name=room.name)
    return render(request, 'create_room.html')


@login_required
def room_detail(request, room_name):
    # Retrieve room and display messages
    room = get_object_or_404(Room, name=room_name)
    messages = room.messages.all().order_by('timestamp')

    # Handle message sending
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(
                room=room,
                user=request.user,
                content=content
            )
            return redirect('room_detail', room_name=room.name)

    return render(request, 'room_detail.html', {
        'room': room,
        'messages': messages
    })

@login_required
def delete_room(request, room_name):
    room = get_object_or_404(Room, name=room_name)
    # Optional: restrict so only the creator can delete
    if room.created_by != request.user:
        messages.error(request, "You are not allowed to delete this room.")
        return redirect('room_list')
    room.delete()
    messages.success(request, f"Room '{room_name}' deleted successfully!")
    return redirect('room_list')
