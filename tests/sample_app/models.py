from django.db import models


class NewUser(models.Model):
    text = models.TextField()
    number = models.IntegerField()
    group = models.ForeignKey('auth.Group')


class OldUser(models.Model):
    text = models.TextField()
    number = models.IntegerField()
    group = models.ForeignKey('auth.Group')
