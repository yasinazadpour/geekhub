import os
from uuid import uuid4

import cv2
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core import files, validators
from django.db import models
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class UsernameValidator(validators.RegexValidator):
    regex = r'^(?!.*\.\.)(?!.*\.$)[^\W][a-z0-9_.]{2,29}$'
    message = _('یک نام کاربری معتبر وارد کنید.')


class MyUser(AbstractUser):

    username_validator = UsernameValidator()

    username = models.CharField(
        _('نام کاربری'), 
        unique=True, 
        max_length=30, 
        validators=[username_validator],
        error_messages={
                'unique': _("کاربری با این نام کاربری از قبل وجود دارد."),
        },
    )
    name = models.CharField(_('نام کامل'), default=_('بدون نام'), max_length=50)
    email = models.EmailField(
        _('آدرس ایمیل'), 
        unique=True,
        error_messages={
                'unique': _("کاربری با این آدرس ایمیل از قبل وجود دارد."),
        },
    )
    image = models.ImageField(_('عکس'), default='users/default.png', upload_to='users/')
    first_name = last_name = None  # use name instead of first_name and last_name

    def get_full_name(self):
        return self.name.strip()

    def get_short_name(self):
        return self.get_full_name()

    def __str__(self) -> str:
        return f"{self.username}"

    def set_image(self, img, ColorConversionCode=cv2.COLOR_BGR2RGB):
        try:
            imageY, imageX = img.shape[0], img.shape[1]

            maxSize = imageX if imageX < imageY else imageY
            x = 0 if imageY < imageX else int(imageY/2-(maxSize/2))
            y = 0 if imageX < imageY else int(imageX/2-(maxSize/2))

            img = img[x:x+maxSize, y:y+maxSize]
            img = cv2.cvtColor(img, ColorConversionCode)

            img = cv2.resize(img, settings.USER_IMAGE_SIZE)

            path = f'{settings.USER_PATH}/'
            if not os.path.exists(path):
                os.mkdir(path)
            path += f'{uuid4()}.png'

            self.image.delete()
            cv2.imwrite(path, img)

            self.image = files.File(open(path, 'rb')).name.replace('web/media', '')
            self.save()
            return True

        except:
            return False

