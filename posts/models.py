from django.db import models
from django.utils.translation import gettext_lazy as _


class Post(models.Model):
    user = models.ForeignKey('accounts.MyUser', verbose_name=_("نویسنده"), on_delete=models.CASCADE, related_name="user_posts")
    title = models.CharField(_("عنوان"), max_length=50, unique=True)
    text =  models.TextField(_("متن"), max_length=20_000)
    date = models.DateTimeField(_("تاریخ"), auto_now=True)
    slug = models.CharField(_("کد صفحه"), max_length=50, unique=True)
    is_pub = models.BooleanField(_("منتشر شده"), default=False)

    class Meta:
        verbose_name = _('پست')
        verbose_name_plural = _('پست ها')

    def __str__(self):
        return f'{self.title}'

