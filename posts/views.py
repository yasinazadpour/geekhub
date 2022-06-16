from http.client import HTTPResponse
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Post, Tag


def home(request):
    num_page = request.GET.get('page', 1)
    q = request.GET.get('q')
    if q == 'top':
        # TODO: order by comments count and ...
        query = Post.objects.filter(is_pub=True).order_by('?')
    elif q == 'oldest':
        query = Post.objects.filter(is_pub=True).order_by('date')
    else:
        query = Post.objects.filter(is_pub=True).order_by('-date')

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
        query = Post.objects.filter(title__icontains=text, is_pub=True).order_by('-date')
        p = Paginator(query, 25)
        page = p.get_page(num_page)
        return render(request, 'search.html', {'page': page, 'title': 'جستجو'})
    return render(request, 'search.html', {'title': 'جستجو'})


def post_view(request, slug):
    query = Post.objects.filter(slug=slug)

    if (query.exists() and request.user.is_staff) or (query.filter(is_pub=True).exists()):
        post = query.first()
        related = []

        if tags:=post.tags.all():
            for tag in tags:
                if related:
                    related = related | tag.posts
                else:
                    related = tag.posts
        
        if count:=len(set(related)) < 6:
            tops = Post.objects.filter(is_pub=True).order_by('-date')
            related = related|tops[:6-count]

        related = related[:6]

        return render(request, 'post_view.html', {'post': post, 'title': post.title,'related': set(related)})

    raise Http404


def about_view(request):
    query = Post.objects.filter(slug='about')

    if query.exists():
        post = query.first()
        return render(request, 'about.html', {'post': post, 'title': 'درباره'})

    return HttpResponse("ببخشید هنوز این صفحه رو نساختیم :(")
