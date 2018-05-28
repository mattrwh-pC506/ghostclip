import pytest
import factory
from faker import Factory as FakerFactory

from main.models import Category

faker = FakerFactory.create()
faker.seed(1234)


@pytest.fixture
def parent_category_factory(db):
    class ParentCategoryFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = Category
            django_get_or_create = ('token',)

        token = faker.pystr()

    return ParentCategoryFactory


@pytest.fixture
def category_factory(db, parent_category_factory):
    class CategoryFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = Category
            django_get_or_create = ('token',)

        token = faker.pystr()
        parent = factory.SubFactory(parent_category_factory)

    return CategoryFactory


@pytest.fixture
def sample_category(category_factory):
    return category_factory()
