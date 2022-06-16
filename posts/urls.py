from django.urls import path
from .views import home, tag_view, search_view, post_view


app_name = 'posts'

urlpatterns = [
    path('', home, name='home'),
    path('tags/<name>', tag_view, name='tag'),
    path('search', search_view, name='search'),
    path('<slug>', post_view, name='post'),
]
