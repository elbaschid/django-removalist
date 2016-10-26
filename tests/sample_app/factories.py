import factory

from .models import OldUser


class GroupFactory(factory.DjangoModelFactory):
    name = 'Some Group'

    class Meta:
        model = 'auth.Group'
        django_get_or_create = ('name',)


class OldUserFactory(factory.DjangoModelFactory):

    group = factory.SubFactory(GroupFactory)

    @factory.sequence
    def text(n):
        return 'User {}'.format(n)

    @factory.sequence
    def number(n):
        return n

    class Meta:
        model = OldUser
