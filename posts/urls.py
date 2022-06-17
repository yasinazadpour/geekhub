from django.urls import path
from .views import *


app_name = 'posts'

urlpatterns = [
    path('', home, name='home'),
    path('tags/<name>', tag_view, name='tag'),
    path('search', search_view, name='search'),
    path('about', about_view, name='about'),
    path('login', login_view, name='login'),
    path('join', join_view, name='join'),
    path('me', me_view, name='me'),
    path('<slug>', post_view, name='post'),
]
