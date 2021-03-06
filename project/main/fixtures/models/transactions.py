import pytest
import factory
from django.db.models.signals import post_save, post_delete
from faker import Factory as FakerFactory
import random
from main.models.transaction import Transaction

faker = FakerFactory.create()
faker.seed(1234)


@pytest.fixture
def transaction_factory(db, account_factory):
    class TransactionFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = Transaction
            django_get_or_create = ('transaction_id', 'name',)

        transaction_id = 'transaction1'
        name = 'transaction1name'
        calendar_event_id = faker.pystr()
        account = factory.SubFactory(account_factory)
        amount = faker.pyfloat(
            left_digits=random.randint(1, 3), right_digits=2, positive=faker.pybool())
        date = faker.past_date()
        pending = faker.pybool()

    return TransactionFactory


@pytest.fixture
@factory.django.mute_signals(post_save, post_delete)
def sample_transaction(transaction_factory):
    return transaction_factory()
