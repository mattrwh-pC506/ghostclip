import pytest
import factory
from faker import Factory as FakerFactory
from main.models import NameRule, AmountRule, DateRule
import random

faker = FakerFactory.create()
faker.seed(1234)


@pytest.fixture
def name_rule_factory(db, rule_set_factory):
    class NameRuleFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = NameRule
            django_get_or_create = ('rule_set', 'value', 'operator')

        rule_set = factory.SubFactory(rule_set_factory)
        value = faker.pystr()
        operator = factory.LazyFunction(
            lambda: random.choice([x[0] for x in NameRule.OPERATOR_CHOICES]))

    return NameRuleFactory


@pytest.fixture
def amount_rule_factory(db, rule_set_factory):
    class AmountRuleFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = AmountRule
            django_get_or_create = ('rule_set', 'value', 'operator')

        rule_set = factory.SubFactory(rule_set_factory)
        value = faker.pyfloat(
            left_digits=random.randint(1, 3), right_digits=2, positive=faker.pybool())
        operator = factory.LazyFunction(
            lambda: random.choice([x[0] for x in AmountRule.OPERATOR_CHOICES]))

    return AmountRuleFactory


@pytest.fixture
def date_rule_factory(db, rule_set_factory):
    class DateRuleFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = DateRule
            django_get_or_create = (
                'rule_set',
                'starting_date',
                'day_range_buffer',
                'repeats_every_num',
                'repeats_every_type',
            )

        rule_set = factory.SubFactory(rule_set_factory)
        starting_date = faker.past_date()
        day_range_buffer = random.randint(0, 3)
        repeats_every_num = random.randint(1, 6)
        repeats_every_type = factory.LazyFunction(
            lambda: random.choice([x[0] for x in DateRule.TYPE_CHOICES]))

    return DateRuleFactory


@pytest.fixture
def sample_name_rule(name_rule_factory):
    return name_rule_factory()


@pytest.fixture
def sample_amount_rule(amount_rule_factory):
    return amount_rule_factory()


@pytest.fixture
def sample_date_rule(date_rule_factory):
    return date_rule_factory()
