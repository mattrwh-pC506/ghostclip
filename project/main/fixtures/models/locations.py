import pytest
import factory
from faker import Factory as FakerFactory

from main.models import Location

faker = FakerFactory.create()
faker.seed(1234)


@pytest.fixture
def location_factory(db):
    class LocationFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = Location

        address = faker.pystr()
        city = faker.pystr()
        state = faker.pystr()
        zip = faker.pystr()
        lat = faker.pystr()
        lon = faker.pystr()

    return LocationFactory


@pytest.fixture
def sample_location(location_factory):
    return location_factory()
