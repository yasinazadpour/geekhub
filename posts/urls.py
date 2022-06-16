from django.urls import path
from .views import home, tag_view, search_view


app_name = 'posts'

urlpatterns = [
    path('', home, name='home'),
    path('tags/<name>', tag_view, name='tag'),
    path('search', search_view, name='search'),
]
