from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    location = models.JSONField(null=True)
    oxygen = models.BooleanField(default=False)
    remdesivir = models.BooleanField(default=False)
    plasma = models.BooleanField(default=False)
    phone_no = models.CharField(max_length=20, default='')
    user_type = models.CharField(max_length=255, default='')
    email = models.EmailField('email address', unique=True,
                              error_messages={
                                  'unique': "A user with that email already exists."})

    class Meta:
        db_table = 'user'
        verbose_name = 'user'
        verbose_name_plural = 'users'


class UserAddress(models.Model):

    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255)
    state = models.CharField(max_length=255, default='')
    city = models.CharField(max_length=255, default='mumbai')
    country = models.CharField(max_length=255, default='IN')
    pincode = models.CharField(max_length=6, default='')
    user = models.ForeignKey(User, related_name="address", on_delete=models.CASCADE)

    class Meta:
        db_table = 'address'
        verbose_name = 'address'
        verbose_name_plural = 'addresses'


class Continent(models.Model):

    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'continent'
        verbose_name = 'continent'
        verbose_name_plural = 'continents'

class Country(models.Model):

    name = models.CharField(max_length=255)
    continent = models.ForeignKey('Continent', on_delete=models.CASCADE)

    class Meta:
        db_table = 'country'
        verbose_name = 'country'
        verbose_name_plural = 'countries'


class State(models.Model):

    name = models.CharField(max_length=255)
    country = models.ForeignKey('Country', on_delete=models.CASCADE)

    class Meta:
        db_table = 'state'
        verbose_name = 'state'
        verbose_name_plural = 'states'


class City(models.Model):

    name = models.CharField(max_length=255)
    state = models.ForeignKey('State', on_delete=models.CASCADE)

    class Meta:
        db_table = 'city'
        verbose_name = 'city'
        verbose_name_plural = 'cities'
