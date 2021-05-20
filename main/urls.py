from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import home, register, Login, profile, oxygen, remdesivir, plasma, thank_you

urlpatterns = [
    path('', home, name='home'),
    path('oxygen', oxygen, name='oxygen'),
    path('freefood', remdesivir, name='freefood'),
    path('plasma', plasma, name='plasma'),
    path('register', register, name='register'),
    path('login', Login.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('profile', profile, name='profile'),
    path('thank-you', thank_you, name='thank_you')
]
