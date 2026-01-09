from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils import timezone
from datetime import timedelta


class CustomUser(AbstractUser):
    
    phone = models.CharField(max_length=15, blank=True, null=True)
    otp_code = models.CharField(max_length=6, blank=True, null=True)  # new field
    otp_expires_at = models.DateTimeField(blank=True, null=True)   

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(max_length=150,unique=True,validators=[username_validator],
                                error_messages={'unique': 'A user with that username already exists.'},
                                help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
                                verbose_name='username')
    def is_otp_expired(self):
        if not self.otp_expires_at:
            return True
        return timezone.now() > self.otp_expires_at
    def __str__(self):
        return self.username
class Room(models.Model):
    # Each chat room has a unique name (like "Project Alpha","Sria")
    name = models.CharField(max_length=100, unique=True)#Room name
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)# User who created the room
    created_at = models.DateTimeField(auto_now_add=True)# Timestamp when room was created

    def __str__(self):
        return self.name
class Message(models.Model):
    # Each message belongs to a user and a specific room
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')# room where message is sent
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)# user who sent the message
    content = models.TextField()# message content
    # timestamp = models.DateTimeField(auto_now_add=True)# when message was sent
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        # Show username and partial message
        return f"{self.user.username}: {self.content[:20]}"