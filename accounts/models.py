import os
from uuid import uuid4

import cv2
from django.conf import settings
from django.contrib import auth
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import PermissionsMixin
from django.core import files
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given  email, and password.
        """
        email = self.normalize_email(email)
        # Lookup the real model class from the global app registry so this
        # manager method can be used in migrations. This is fine because
        # managers are by definition working on the real model.
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('verified') is not True:
            raise ValueError('Superuser must have verified=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

    def with_perm(self, perm, is_active=True, include_superusers=True, backend=None, obj=None):
        if backend is None:
            backends = auth._get_backends(return_tuples=True)
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    'You have multiple authentication backends configured and '
                    'therefore must provide the `backend` argument.'
                )
        elif not isinstance(backend, str):
            raise TypeError(
                'backend must be a dotted import path string (got %r).'
                % backend
            )
        else:
            backend = auth.load_backend(backend)
        if hasattr(backend, 'with_perm'):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()


class MyUser(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    email and password are required. Other fields are optional.
    """

    name = models.CharField(_('نام کامل'), default=_('بدون نام'), max_length=50)
    image = models.ImageField(_('عکس'), default='users/default.png', upload_to='users/')
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
                'unique': _("کاربری با این آدرس ایمیل از قبل وجود دارد."),
        },
    )
    verified = models.BooleanField(_("اعتبار سنجی شده"), default=False)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'

    def __str__(self) -> str:
        return f"{self.email}"

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        swappable = 'AUTH_USER_MODEL'

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the name .
        """
        return self.name.strip()

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

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
