import pytest

from .sample_app.factories import OldUserFactory
from .sample_app.models import NewUser


@pytest.mark.django_db()
def test_insert_trigger():
    old_users = [OldUserFactory(), OldUserFactory()]
    new_users = NewUser.objects.all()

    assert sorted([u.id for u in old_users]) == sorted([u.id for u in new_users])


@pytest.mark.django_db()
def test_update_trigger():
    old_user_1, old_user_2 = [OldUserFactory(), OldUserFactory()]

    assert NewUser.objects.all().count() == 2

    old_user_1.text = 'updated text'
    old_user_1.save()

    changed_user = NewUser.objects.get(id=old_user_1.id)
    unchanged_user = NewUser.objects.get(id=old_user_2.id)
    assert changed_user.text == old_user_1.text
    assert unchanged_user.text == old_user_2.text


@pytest.mark.django_db()
def test_delete_trigger():
    old_user_1, old_user_2 = [OldUserFactory(), OldUserFactory()]

    assert NewUser.objects.all().count() == 2

    old_user_1.delete()

    assert NewUser.objects.all().count() == 1

    new_user = NewUser.objects.all().first()
    assert new_user.id == old_user_2.id
