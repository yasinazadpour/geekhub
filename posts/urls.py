from django.urls import path
from .views import *


app_name = 'posts'

urlpatterns = [
    path('', index, name='index'),
    path('tags/<name>', tag_view, name='tag'),
    path('search', search_view, name='search'),
    path('about', about_view, name='about'),
    path('login', login_view, name='login'),
    path('verify', verify, name='verify'),
    path('me', me_view, name='me'),
    path('change-password', change_password, name='change_password'),
    path('add-comment', add_comment, name='add_comment'),
    path('delete-account', delete_account, name='delete_account'),
    path('reset-password', reset_password, name='reset_password'),
    path('logout-all', log_out_all, name='log_out_all'),
    path('logout', log_out, name='login'),
    path('<slug>', post_view, name='post'),
]
