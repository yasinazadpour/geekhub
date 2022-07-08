import numpy as np
from accounts.forms import JoinForm, UpdateUserForm
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.contrib.sessions.models import Session
from django.core.paginator import Paginator
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from PIL import Image
from django.http.response import JsonResponse
from .forms import CommentForm
from .models import Post, Tag, Token

User = get_user_model()

def index(request):
    num_page = request.GET.get('page', 1)
    q = request.GET.get('q')
    if q == 'top':
        query = Post.objects.filter(is_pub=True).order_by('-views','-date')
    else:
        query = Post.objects.filter(is_pub=True).order_by('-date')

    p = Paginator(query, 25)
    page = p.get_page(num_page)
    return render(request, 'index.html', {'page': page, 'showtags': True})


def tag_view(request, name):
    query = Tag.objects.filter(name=name)
    if query.exists():
        num_page = request.GET.get('page', 1)
        q = request.GET.get('q')
        tag = query.first()
        if q == 'top':
            # TODO: order by comments count and ...
            posts = tag.posts.order_by('-views','-date')
        else:
            posts = tag.posts.all().order_by('-date')

        p = Paginator(posts, 25)
        page = p.get_page(num_page)
        return render(request, 'tag_view.html', {'page': page,'tag': tag,'title': f'# {tag.name}', 'showtags': True})

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
        post.views += 1
        post.save()
        related = []

        if tags:=post.tags.all():
            for tag in tags:
                if related:
                    related = related | tag.posts
                else:
                    related = tag.posts
        
        if count:=len(set(related)) < 6:
            tops = Post.objects.filter(is_pub=True).order_by('-date')
            if related:
                related = related|tops[:6-count]
            else:
                related = tops[:6-count]

        related = related[:6]

        return render(request, 'post_view.html', {'post': post, 'title': post.title,'related': set(related),  'showtags': True})

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
        email = request.POST.get('email')
        query = User.objects.filter(email=email)

        # Delete unverified users
        query.filter(verified=False).delete()

        if query.exists():
            user = User.objects.get(email=email)

            if user.check_password(passwd):
                login(request, user)
                return redirect('/')
            
            return render(request, 'login.html', {'title': 'ورود', 'msg': {'password': 'گذرواژه وارد شده صحیح نمی باشد.'}})

        # if email does not exists create it
        data = {
            'password1': passwd, 
            'password2': passwd,
            'email': email,
        }

        form = JoinForm(data)

        if form.is_valid():
            user = form.save()
            user.is_active = False
            user.save()
            
            # TODO: send email
            print(f"token: {Token.generate(user).pk}")
            
            return render(request, 'login.html', {'title': 'ورود', 'created': True})

        print(form.errors.as_json())
        return render(request, 'login.html', {'title': 'ورود','form':form})

    return render(request, 'login.html', {'title': 'ورود'})

@login_required(login_url="/login")
def me_view(request):
    if request.method == 'POST':
        user = request.user
        data = {
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
    if request.method == 'GET':
        token = request.GET.get('token')
        is_valid = Token.check_token(token)
        
        if is_valid:
            return render(request, 'password_change.html', {'title': 'تعویض گذرواژه', 'can_reset': True})

        elif token is None and request.user.is_authenticated:
            return render(request, 'password_change.html', {'title': 'تعویض گذرواژه'})
            
        return render(request, 'password_change.html', {'title': 'تعویض گذرواژه', 'msg': 'متاسفانه کد بازیابی منقضی شده است.'})
    
    if request.method == 'POST':
        token = request.POST.get('token')
        token = Token.check_token(token)
        if token:
            form = SetPasswordForm(token.user, request.POST)

        else :
            if not request.user.is_authenticated:
                return redirect('/login')
                
            form = PasswordChangeForm(request.user, request.POST)
        
        if form.is_valid():
            
            if request.user.is_authenticated:
                user = form.save()
                login(request, user)
                return redirect('/me')
                
            user = form.save()
            return redirect('/login')
            
        return render(request, 'password_change.html', {'title': 'تعویض گذرواژه', 'form': form,'can_reset': bool(token)})
        
    return render(request, 'password_change.html', {'title': 'تعویض گذرواژه'})

def verify(request):
    if request.user.is_authenticated:
        return redirect('/')
    
    token = request.GET.get('token')
    
    if token:=Token.check_token(token):
        token.user.is_active = True
        token.user.save()
        Token.objects.filter(user=token.user).delete()
        login(request, token.user)
        
    return render(request, 'verify.html', {'title': 'تایید ایمیل'})


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

def reset_password(request):
    user = request.user
    if user.is_authenticated :
        print(f"token: {Token.generate(user).pk}")
        return render(request, 'reset_password.html',{'title': 'بازیابی گذرواژه','success': True})

    if request.method == 'POST':
        email = request.POST.get('email')
        query = User.objects.filter(email=email)
        if query.exists():
            print(f"token: {Token.generate(query.first()).pk}")
            return render(request, 'reset_password.html',{'title': 'بازیابی گذرواژه','success': True})
        
        return render(request, 'reset_password.html',{'title': 'بازیابی گذرواژه','msg': 'کاربری با نشانی ایمیل وارد شده وجود ندارد.','email': email})

    return render(request, 'reset_password.html',{'title': 'بازیابی گذرواژه'})
        
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


@require_POST
def add_comment(request):
    user = request.user
    if user.is_authenticated:
        request.POST = clean_data(request.POST)|{'user': user}
        form  = CommentForm(request.POST)
        if form.is_valid():
            c = form.save()
            return JsonResponse({
                'pk': c.pk,
                'user': {'pk': c.user.pk, 'name':c.user.name, 'image': c.user.image.url},
                'text': c.text,
                'date': 'همین حالا',
                'repTo':c.rep_to.pk if c.rep_to else 0
            })
        return JsonResponse({},status=300)
    
    return JsonResponse({},status=300)


def clean_data(data):
    newData = {}
    for key,value in data.items():
        newData[key] = value[0] if isinstance(value, list) else value
    
    return newData
