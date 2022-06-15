from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core import validators
from django.utils.deconstruct import deconstructible

class Post(models.Model):
    user = models.ForeignKey('accounts.MyUser', verbose_name=_("نویسنده"), on_delete=models.CASCADE, related_name="user_posts")
    title = models.CharField(_("عنوان"), max_length=50, unique=True)
    image = models.ImageField(_("عکس"), help_text="بهتر است نسبت عکس 16:9 باشد.", upload_to='posts/')
    text =  models.TextField(_("متن"), max_length=20_000)
    date = models.DateTimeField(_("تاریخ"), auto_now=True)
    slug = models.CharField(_("کد صفحه"), max_length=50, unique=True)
    is_pub = models.BooleanField(_("منتشر شده"), default=False)
    tags = models.ManyToManyField('Tag', verbose_name=_("برچسب ها"), blank=True, related_name='taged_posts')

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
