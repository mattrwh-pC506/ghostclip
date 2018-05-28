import pytest
import factory
from faker import Factory as FakerFactory

from main.models import RuleSet

faker = FakerFactory.create()
faker.seed(1234)


@pytest.fixture
def rule_set_factory(db, item_factory):
    class RuleSetFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = RuleSet
            django_get_or_create = ('name',)

        name = faker.pystr()
        item = factory.SubFactory(item_factory)

    return RuleSetFactory


@pytest.fixture
def sample_rule_set(rule_set_factory):
    return rule_set_factory()
