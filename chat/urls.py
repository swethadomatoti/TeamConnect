from django.urls import path
from .import views
urlpatterns = [
    path('', views.room_list, name='home'),
    path('register/',views.register_user,name='register'),
    path('login/',views.login_user,name='login'),
    path('forgot-password/',views.forgot_password,name='forgot_password'),
    path('verify-otp/',views.verify_otp,name='verify_otp'),
    path('reset-password/',views.reset_password,name='reset_password'),
    path('logout/',views.logout_user,name='logout'),
    path('usersdata/', views.Users_list, name='users_list'),
    path('delete/', views.delete_user, name='delete_user'), 
    path('room/', views.room_list, name='room_list'), 
    path('createroom/', views.create_room, name='create_room'),
    path('<str:room_name>/', views.room_detail, name='room_detail'),  
    path('delete/<str:room_name>/', views.delete_room, name='delete_room'),     
]
 