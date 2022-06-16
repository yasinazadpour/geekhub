from django.http import Http404
from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Post, Tag


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


def tag_view(request, name):
    query = Tag.objects.filter(name=name)
    if query.exists():
        num_page = request.GET.get('page', 1)
        q = request.GET.get('q')
        tag = query.first()
        if q == 'top':
            # TODO: order by comments count and ...
            posts = tag.posts.order_by('?')
        elif q == 'oldest':
            posts = tag.posts.all().order_by('date')
        else:
            posts = tag.posts.all().order_by('-date')

        p = Paginator(posts, 25)
        page = p.get_page(num_page)
        return render(request, 'tag_view.html', {'page': page,'tag': tag,'title': f'# {tag.name}'})

    else:
        raise Http404


def search_view(request):
    num_page = request.GET.get('page', 1)
    text = request.GET.get('text')
    # TODO: use another features to order posts
    if text:
        query = Post.objects.filter(title__icontains=text).order_by('-date')
        p = Paginator(query, 25)
        page = p.get_page(num_page)
        return render(request, 'search.html', {'page': page, 'title': 'جستجو'})
    return render(request, 'search.html', {'title': 'جستجو'})
