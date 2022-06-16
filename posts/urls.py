from django.urls import path
from .views import home


app_name = 'posts'

urlpatterns = [
    path('', home, name='home')
]
