import pytest
import factory
from faker import Factory as FakerFactory
from main.models import Family

faker = FakerFactory.create()
faker.seed(1234)


@pytest.fixture
def family_factory(db):
    class FamilyFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = Family
            django_get_or_create = ('name',)

        name = f'The {faker.last_name()}s'

    return FamilyFactory


@pytest.fixture
def sample_family(family_factory):
    return family_factory()
