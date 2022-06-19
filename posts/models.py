from uuid import uuid4
from datetime import datetime, timedelta, timezone
from django.utils import timezone as djtimezone
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core import validators
from django.utils.deconstruct import deconstructible

class Post(models.Model):
    user = models.ForeignKey('accounts.MyUser', verbose_name=_("نویسنده"), on_delete=models.CASCADE, related_name="user_posts")
    title = models.CharField(_("عنوان"), max_length=50, unique=True)
    image = models.ImageField(_("عکس"), help_text=_("بهتر است نسبت عکس 16:9 باشد."), upload_to='posts/')
    text =  models.TextField(_("متن"), max_length=20_000)
    date = models.DateTimeField(_("تاریخ"), default=djtimezone.now)
    slug = models.CharField(_("کد صفحه"), max_length=50, unique=True)
    is_pub = models.BooleanField(_("منتشر شده"), default=False)
    tags = models.ManyToManyField('Tag', verbose_name=_("برچسب ها"), blank=True, related_name='taged_posts')
    views = models.IntegerField(_("بازدید ها"), default=0)
    
    @property
    def comments(self):
        return self.post_comments.all()

    class Meta:
        verbose_name = _('پست')
        verbose_name_plural = _('پست ها')

    def __str__(self):
        return f'{self.title}'


class Comment(models.Model):
    post = models.ForeignKey('posts.Post', verbose_name=_("پست"), on_delete=models.CASCADE, related_name="post_comments")
    user = models.ForeignKey('accounts.MyUser', verbose_name=_("نویسنده"), on_delete=models.CASCADE)
    text =  models.TextField(_("متن"), max_length=200)
    date = models.DateTimeField(_("تاریخ"), auto_now=True)
    rep_to = models.ForeignKey('self', verbose_name=_("در پاسخ به"), on_delete=models.CASCADE, related_name="responses", null=True, blank=True)

    class Meta:
        verbose_name = _('نظر')
        verbose_name_plural = _('نظرات')

    def __str__(self):
        return f'{self.user.name} > {self.post.title}'


@deconstructible
class TagVilidator(validators.RegexValidator):
    regex = r'^[\.آ-یa-z_-]{3,50}$'
    message = _('یک برچسب معتبر وارد کنید.')


class Tag(models.Model):
    tag_validator = TagVilidator()

    name = models.CharField(_('نام'), max_length=50, unique=True, validators=[tag_validator])

    @property
    def posts(self):
        return self.taged_posts.filter(is_pub=True).order_by('-date')

    class Meta:
        verbose_name = _('برچسب')
        verbose_name_plural = _('برچسب ها')

    def __str__(self):
        return f'{self.name}'

class Link(models.Model):
    name = models.CharField(_("نام"), help_text=_("برای نشان دادن ایکون مناسب استفاده می شود"), max_length=50)
    about = models.CharField(_("درباره"), help_text=_("توضیحاتی درباره پیوند"), max_length=50)
    url = models.URLField(_("url"), max_length=200)


    class Meta:
        verbose_name = _('پیوند')
        verbose_name_plural = _('پیوند ها')

    def __str__(self):
        return self.name


class HotLink(models.Model):
    name = models.CharField(_("نام"), max_length=200)
    url = models.URLField(_("url"))

    class Meta:
        verbose_name = _('لینک داغ')
        verbose_name_plural = _('لینک های داغ')

    def __str__(self):
        return self.name


class Token(models.Model):
    id = models.CharField(_('توکن'), max_length=200, unique=True, primary_key=True)
    user = models.ForeignKey('accounts.MyUser', verbose_name=_("کاربر"), on_delete=models.CASCADE, related_name="user_tokens")
    date = models.DateTimeField(_("تاریخ"), auto_now=True)
    
    @classmethod
    def generate(cls, user):
        id = str(uuid4()).replace('-','')
        cls.objects.filter(user=user).delete()
        return cls.objects.create(id=id, user=user)

    @classmethod
    def check_token(cls, token):
        try:

            token = cls.objects.get(pk=token)
            now = datetime.now(tz=timezone.utc)
            return token if now - token.date < timedelta(minutes=5) else False
            
        except:
            return False

    class Meta:
        verbose_name = _('توکن')
        verbose_name_plural = _('توکن ها')

    def __str__(self):
        return self.user.username

