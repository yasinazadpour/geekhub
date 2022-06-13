from django.db import models
from django.utils.translation import gettext_lazy as _


class Post(models.Model):
    user = models.ForeignKey('accounts.MyUser', verbose_name=_("نویسنده"), on_delete=models.CASCADE, related_name="user_posts")
    title = models.CharField(_("عنوان"), max_length=50, unique=True)
    text =  models.TextField(_("متن"), max_length=20_000)
    date = models.DateTimeField(_("تاریخ"), auto_now=True)
    slug = models.CharField(_("کد صفحه"), max_length=50, unique=True)
    is_pub = models.BooleanField(_("منتشر شده"), default=False)

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
