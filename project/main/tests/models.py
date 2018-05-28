import pytest
from django.contrib.auth import get_user_model
import main.signals
from main.models import (
    Family, User, Item, Transaction,
    Location, Category, Account, RuleSet,
    NameRule, AmountRule, DateRule
)


def assert_created(model, instance):

    def test_handler():
        assert instance in model.objects.all()

    test_handler()


def test_create_family(sample_family):
    assert_created(Family, sample_family)


def test_create_user(sample_user):
    assert_created(User, sample_user)


def test_create_item(sample_item):
    assert_created(Item, sample_item)


def test_create_transaction(sample_transaction):
    assert_created(Transaction, sample_transaction)


def test_create_location(sample_location):
    assert_created(Location, sample_location)


def test_create_category(sample_category):
    assert_created(Category, sample_category)


def test_create_account(sample_account):
    assert_created(Account, sample_account)


def test_create_rule_set(sample_rule_set):
    assert_created(RuleSet, sample_rule_set)


def test_create_name_rule(sample_name_rule):
    assert_created(NameRule, sample_name_rule)


def test_create_amount_rule(sample_amount_rule):
    assert_created(AmountRule, sample_amount_rule)


def test_create_date_rule(sample_date_rule):
    assert_created(DateRule, sample_date_rule)
