from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from .managers import UserManager
from django.core.exceptions import ValidationError

import random
import phonenumbers
from phonenumbers import carrier
from phonenumbers.phonenumberutil import number_type

from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings


def validate_phone(value):
    try:
        number = phonenumbers.parse('+' + str(value), None)
        if not carrier._is_mobile(number_type(number)):
            raise ValidationError
    except:
        raise ValidationError('Incorrect phone number')


def validate_code(value):
    try:
        User.objects.get(self_invite_code=value)
    except:
        raise ValidationError('Incorrect check_code')


class UserLogin(models.Model):
    phone = models.BigIntegerField(verbose_name='Номер телефона',
                                   validators=[validate_phone])
    check_code = models.CharField(max_length=4, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def generate_check_code():
        return ''.join(
            [random.choice(list('123456789')) for _ in range(4)])

    def __str__(self):
        return str(self.phone)


class User(AbstractBaseUser):
    phone = models.BigIntegerField(unique=True,
                                   verbose_name='Номер телефона')
    self_invite_code = models.CharField(max_length=6,
                                        verbose_name='Ваш код',
                                        blank=True)
    other_invite_code = models.CharField(max_length=6,
                                         verbose_name='Чужой код',
                                         blank=True,
                                         validators=[validate_code])

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return str(self.phone)

    def natural_key(self):
        return self.phone

    def get_short_name(self):
        return self.phone

    class Meta:
        verbose_name = 'Пользователь'

    @staticmethod
    def generate_invite():
        invite_list = User.objects.all().values_list('self_invite_code', flat=True)
        invite_code = ''.join(
            [random.choice(list('123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM')) for _ in range(6)])
        while invite_code in invite_list:
            invite_code = ''.join(
                [random.choice(list('123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM')) for _ in
                 range(6)])
        return invite_code

    @receiver(post_save, sender=settings.AUTH_USER_MODEL)
    def create_auth_token(sender, instance=None, created=False, **kwargs):
        if created:
            Token.objects.create(user=instance)
