import pytest
import factory
from faker import Factory as FakerFactory

from main.models import Item

faker = FakerFactory.create()
faker.seed(1234)


@pytest.fixture
def item_factory(db, user_factory):
    class ItemFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = Item
            django_get_or_create = ('item_id',)

        item_id = 'item1'
        institution_id = faker.pystr()
        user = factory.SubFactory(user_factory)
        institution_name = faker.company()
        access_token = faker.pystr()
        public_token = faker.pystr()

    return ItemFactory


@pytest.fixture
def sample_item(item_factory):
    return item_factory()
