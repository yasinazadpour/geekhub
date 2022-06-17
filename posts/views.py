import numpy as np
from accounts.forms import JoinForm, UpdateUserForm
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.sessions.models import Session
from django.core.paginator import Paginator
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from PIL import Image

from .models import Post, Tag


User = get_user_model()

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

def login_view(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        passwd = request.POST.get('password')
        username = request.POST.get('username')

        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)

            if user.check_password(passwd):
                login(request, user)
                return redirect('/')
            
            return render(request, 'login.html', {'title': 'ورود', 'msg': {'password': 'گذرواژه وارد شده صحیح نمی باشد.'}})

        return render(request, 'login.html', {'title': 'ورود', 'msg': {'username': 'کاربری با نام کاربری وارد شده وجود ندارد.'}})

    return render(request, 'login.html', {'title': 'ورود'})

def join_view(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':

        passwd = request.POST.get('password')
        username = request.POST.get('username')
        email = request.POST.get('email')
        data = {
            'password1': passwd, 
            'password2': passwd,
            'email': email,
            'username': username.lower(),
            'name': username.lower()
        }

        form = JoinForm(data)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/me')
            
        return render(request, 'join.html', {'title': 'عضویت', 'form': form})

    return render(request, 'join.html', {'title': 'عضویت'})

@login_required(login_url="/login")
def me_view(request):
    if request.method == 'POST':
        user = request.user
        data = {
            'username': user.username,
            'email': user.email,
            'name': user.name,
        }
        request.POST = data|clean_data(request.POST)
        form = UpdateUserForm(request.POST, request.FILES, instance=user)

        if form.is_valid():
            image = request.FILES.get('image')
            form.save()
            if image:
                image = np.array(Image.open(image))
                user.set_image(image)

        return render(request, 'me_view.html', {'title': 'پروفایل', 'form': form})

    return render(request, 'me_view.html', {'title': 'پروفایل'})


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect('/me')

        return render(request, 'password_change.html', {'title': 'تعویض گذرواژه', 'form': form})
        
    return render(request, 'password_change.html', {'title': 'تعویض گذرواژه'})

def delete_account(request):
    user = request.user
    if user.is_authenticated:
        if request.method == 'POST':
            password = request.POST.get('password')
            is_valid = user.check_password(password)

            if is_valid:
                user.delete()
                return redirect('/')

            return render(request, 'delete_account.html', {'title': 'حذف حساب کاربری','message': 'گذرواژه وارد شده صحیح نیست.'})

        return render(request, 'delete_account.html',{'title': 'حدف حساب کاربری'})
        
    return redirect('/')

def log_out(request):
    logout(request) 
    return redirect('/')


@require_POST
def log_out_all(request):
    user = request.user
    if user.is_authenticated:
        my_session_key = request.session.session_key
        for s in Session.objects.exclude(session_key=my_session_key):
            data = s.get_decoded()
            if data.get('_auth_user_id') == str(user.pk):
                s.delete()

        return redirect('/me')
        
    return redirect('/')

def clean_data(data):
    newData = {}
    for key,value in data.items():
        newData[key] = value[0] if isinstance(value, list) else value
    
    return newData
