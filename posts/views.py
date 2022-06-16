from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Post


def home(request):
    num_page = request.GET.get('page', 1)
    q = request.GET.get('q')
    if q == 'top':
        # TODO: order by comments count and ...
        query = Post.objects.all().order_by('?')
    elif q == 'oldest':
        query = Post.objects.all().order_by('date')
    else:
        query = Post.objects.all().order_by('-date')

    p = Paginator(query, 25)
    page = p.get_page(num_page)
    return render(request, 'index.html', {'page': page})
