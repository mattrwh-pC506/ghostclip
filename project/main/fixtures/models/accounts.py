import pytest
import factory
from faker import Factory as FakerFactory
import random
from main.models import Account

faker = FakerFactory.create()
faker.seed(1234)


@pytest.fixture
def account_factory(db, item_factory):
    class AccountFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = Account
            django_get_or_create = ('account_id',)

        account_id = 'account1'
        item = factory.SubFactory(item_factory)
        available_balance = faker.pyfloat(
            left_digits=random.randint(1, 3), right_digits=2, positive=True)
        current_balance = faker.pyfloat(
            left_digits=random.randint(1, 3), right_digits=2, positive=True)
        limit = faker.pyfloat(left_digits=random.randint(
            1, 3), right_digits=2, positive=True)
        mask = faker.pystr(min_chars=4, max_chars=4)
        name = faker.pystr()
        official_name = faker.pystr()
        subtype = faker.pystr()
        type = faker.pystr()
        track = faker.pybool()

    return AccountFactory


@pytest.fixture
def sample_account(account_factory):
    return account_factory()
