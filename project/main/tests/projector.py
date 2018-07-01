import pytest
import datetime
from main.models import Transaction, RuleSet, NameRule, AmountRule, DateRule
from main.projector import (
    get_rule_sets_with_name_matches,
    add_amount_matches,
    add_date_matches,
    get_best_match,
)


@pytest.fixture
def add_simple_operator_rules(name_rule_factory, amount_rule_factory):
    factories = {'name': name_rule_factory, 'amount': amount_rule_factory}

    def builder(factory_name, rule_sets, rules, num_to_add, operator, value):
        factory = factories[factory_name]
        new_rules = [
            factory(
                rule_set=rule_sets[x],
                value=value,
                operator=operator,
            ) for x in range(num_to_add)
        ]
        return [*new_rules, *rules]

    return builder


@pytest.fixture
def add_date_rules(date_rule_factory):
    def builder(rule_sets, rules, num_to_add, starting_date, day_range_buffer, repeats_every_num, repeats_every_type):
        new_rules = [
            date_rule_factory(
                rule_set=rule_sets[x],
                starting_date=starting_date,
                day_range_buffer=day_range_buffer,
                repeats_every_num=repeats_every_num,
                repeats_every_type=repeats_every_type,
            ) for x in range(num_to_add)
        ]
        return [*new_rules, *rules]
    return builder


@pytest.fixture
def starting_rule_sets(rule_set_factory):
    def builder(num_to_build):
        return [rule_set_factory(name=f'RuleSet{x}') for x in range(num_to_build)]
    return builder


def test_build_rule_set_map_for_name_only(sample_item, starting_rule_sets, add_simple_operator_rules):
    rs = starting_rule_sets(4)
    nrs = []
    nrs = add_simple_operator_rules('name', rs, nrs, 4, 'STARTSWITH', 'abc')
    nrs = add_simple_operator_rules('name', rs, nrs, 3, 'ENDSWITH', '123')
    nrs = add_simple_operator_rules('name', rs, nrs, 2, 'CONTAINS', 'c1')
    nrs = add_simple_operator_rules('name', rs, nrs, 1, 'EXACT', 'abc123')

    sut = {rule_set: [] for rule_set in nrs}
    sut = get_rule_sets_with_name_matches(sample_item, 'abc123')

    for i, rule_set in enumerate(rs):
        assert len(sut[rule_set]) == (len(rs) - i)


def test_add_amount_matches(sample_item, starting_rule_sets, add_simple_operator_rules):
    rs = starting_rule_sets(9)
    nrs = []
    nrs = add_simple_operator_rules('name', rs, nrs, 9, 'STARTSWITH', 'abc')
    nrs = add_simple_operator_rules('name', rs, nrs, 8, 'ENDSWITH', '123')
    nrs = add_simple_operator_rules('name', rs, nrs, 7, 'CONTAINS', 'c1')
    nrs = add_simple_operator_rules('name', rs, nrs, 6, 'EXACT', 'abc123')
    nrs = add_simple_operator_rules('amount', rs, nrs, 5, 'GT', 4)
    nrs = add_simple_operator_rules('amount', rs, nrs, 4, 'GTE', 5)
    nrs = add_simple_operator_rules('amount', rs, nrs, 3, 'LT', 6)
    nrs = add_simple_operator_rules('amount', rs, nrs, 2, 'LTE', 5)
    nrs = add_simple_operator_rules('amount', rs, nrs, 1, 'EQ', 5)

    sut = {rule_set: [] for rule_set in nrs}
    sut = get_rule_sets_with_name_matches(sample_item, 'abc123')
    sut = add_amount_matches(sut, -5)

    for i, rule_set in enumerate(rs):
        assert len(sut[rule_set]) == (len(rs) - i)


@pytest.fixture
def setup_date_tests(
        sample_item, starting_rule_sets, add_simple_operator_rules, add_date_rules):
    def setup(
            starting_date=None,
            day_range_buffer=None,
            repeats_every_num=None,
            repeats_every_type=None,
            transaction_date=None,
    ):
        rs = starting_rule_sets(3)
        nrs = []
        nrs = add_simple_operator_rules('name', rs, nrs, 3, 'EXACT', 'abc123')
        nrs = add_simple_operator_rules('amount', rs, nrs, 3, 'EQ', 5)
        nrs = add_date_rules(
            rs, nrs, 1, starting_date, day_range_buffer, repeats_every_num, repeats_every_type)
        sut = {rule_set: [] for rule_set in nrs}
        sut = get_rule_sets_with_name_matches(sample_item, 'abc123')
        sut = add_amount_matches(sut, -5)
        sut = add_date_matches(sut, transaction_date)
        return rs, sut

    return setup


def test_add_date_matches_for_recurring_month_with_three_day_buffer_after(setup_date_tests):
    rs, sut = setup_date_tests(
        starting_date=datetime.date(2018, 1, 1),
        day_range_buffer=3,
        repeats_every_num=1,
        repeats_every_type='MONTH',
        transaction_date=datetime.date(2018, 5, 3),
    )

    assert len(sut.keys()) == 1
    assert len(sut[rs[0]]) == 3


def test_add_date_matches_for_recurring_month_with_three_day_buffer_before(setup_date_tests):
    rs, sut = setup_date_tests(
        starting_date=datetime.date(2018, 1, 1),
        day_range_buffer=3,
        repeats_every_num=1,
        repeats_every_type='MONTH',
        transaction_date=datetime.date(2018, 4, 30),
    )

    assert len(sut.keys()) == 1
    assert len(sut[rs[0]]) == 3


def test_add_date_fails_to_match_for_recurring_month_when_after_buffer(setup_date_tests):
    rs, sut = setup_date_tests(
        starting_date=datetime.date(2018, 1, 1),
        day_range_buffer=3,
        repeats_every_num=1,
        repeats_every_type='MONTH',
        transaction_date=datetime.date(2018, 5, 5),
    )

    assert len(sut.keys()) == 0


def test_add_date_fails_to_match_for_recurring_month_when_before_buffer(setup_date_tests):
    rs, sut = setup_date_tests(
        starting_date=datetime.date(2018, 1, 1),
        day_range_buffer=3,
        repeats_every_num=1,
        repeats_every_type='MONTH',
        transaction_date=datetime.date(2018, 4, 27),
    )

    assert len(sut.keys()) == 0


def test_add_date_matches_for_month_with_no_buffer(setup_date_tests):
    rs, sut = setup_date_tests(
        starting_date=datetime.date(2018, 1, 1),
        day_range_buffer=0,
        repeats_every_num=1,
        repeats_every_type='MONTH',
        transaction_date=datetime.date(2018, 5, 1),
    )

    assert len(sut.keys()) == 1
    assert len(sut[rs[0]]) == 3


def test_add_date_fails_for_day_with_no_buffer_when_after(setup_date_tests):
    rs, sut = setup_date_tests(
        starting_date=datetime.date(2018, 1, 1),
        day_range_buffer=0,
        repeats_every_num=7,
        repeats_every_type='DAY',
        transaction_date=datetime.date(2018, 5, 2),
    )

    assert len(sut.keys()) == 0


def test_add_date_fails_for_day_with_no_buffer_when_before(setup_date_tests):
    rs, sut = setup_date_tests(
        starting_date=datetime.date(2018, 1, 1),
        day_range_buffer=0,
        repeats_every_num=7,
        repeats_every_type='DAY',
        transaction_date=datetime.date(2018, 4, 29),
    )

    assert len(sut.keys()) == 0


def test_add_date_matches_if_falls_within_buffer_after_date(setup_date_tests):
    rs, sut = setup_date_tests(
        starting_date=datetime.date(2018, 1, 1),
        day_range_buffer=2,
        repeats_every_num=7,
        repeats_every_type='DAY',
        transaction_date=datetime.date(2018, 5, 2),
    )

    assert len(sut.keys()) == 1
    assert len(sut[rs[0]]) == 3


def test_add_date_matches_if_falls_within_buffer_before_date(setup_date_tests):
    rs, sut = setup_date_tests(
        starting_date=datetime.date(2018, 1, 1),
        day_range_buffer=2,
        repeats_every_num=7,
        repeats_every_type='DAY',
        transaction_date=datetime.date(2018, 4, 30),
    )

    assert len(sut.keys()) == 1
    assert len(sut[rs[0]]) == 3


def test_add_date_matches_for_day_with_no_buffer(setup_date_tests):
    rs, sut = setup_date_tests(
        starting_date=datetime.date(2018, 1, 1),
        day_range_buffer=0,
        repeats_every_num=7,
        repeats_every_type='DAY',
        transaction_date=datetime.date(2018, 5, 28),
    )
    assert len(sut.keys()) == 1
    assert len(sut[rs[0]]) == 3


def test_get_best_match(sample_item, starting_rule_sets, add_simple_operator_rules):
    rs = starting_rule_sets(9)
    nrs = []
    nrs = add_simple_operator_rules('name', rs, nrs, 9, 'STARTSWITH', 'abc')
    nrs = add_simple_operator_rules('name', rs, nrs, 8, 'ENDSWITH', '123')
    nrs = add_simple_operator_rules('name', rs, nrs, 7, 'CONTAINS', 'c1')
    nrs = add_simple_operator_rules('name', rs, nrs, 6, 'EXACT', 'abc123')
    nrs = add_simple_operator_rules('amount', rs, nrs, 5, 'GT', 4)
    nrs = add_simple_operator_rules('amount', rs, nrs, 4, 'GTE', 5)
    nrs = add_simple_operator_rules('amount', rs, nrs, 3, 'LT', 6)
    nrs = add_simple_operator_rules('amount', rs, nrs, 2, 'LTE', 5)
    nrs = add_simple_operator_rules('amount', rs, nrs, 1, 'EQ', 5)

    sut = {rule_set: [] for rule_set in nrs}
    sut = get_rule_sets_with_name_matches(sample_item, 'abc123')
    sut = add_amount_matches(sut, -5)

    assert get_best_match(sut) == rs[0]
