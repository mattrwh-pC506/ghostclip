from main.models.transaction import Transaction
from main.models.rules import NameRule, AmountRule, DateRule
from main.predictor import update_predictions_from_rule_set

import django_rq


def build_rule_set_map(field_value, rules, rule_sets):
    for r in [rule for rule in rules if rule.matches(field_value)]:
        rule_sets[r.rule_set] = [*rule_sets.get(r.rule_set, []), r]
    return rule_sets


def get_rule_sets_with_name_matches(item, name):
    rules = NameRule.objects.filter(rule_set__item=item)
    return build_rule_set_map(name, rules, {})


def add_amount_matches(rule_sets, amount):
    rules = AmountRule.objects.filter(rule_set__in=list(rule_sets.keys()))
    return build_rule_set_map(amount, rules, rule_sets)


def add_date_matches(rule_sets, date):
    rules = DateRule.objects.filter(rule_set__in=list(rule_sets.keys()))
    date_set_matches = build_rule_set_map(date, rules, {})
    return {rs: [*date_set_matches[rs], *rule_sets[rs]]
            for rs in date_set_matches.keys()}


def get_best_match(rule_sets):
    if rule_sets:
        return max(rule_sets.keys(), key=(lambda k: len(rule_sets[k])))


def recalculate_ruleset_latest_transaction(rs):
    transactions = Transaction.objects.filter(rule_set=rs)
    last_transaction = transactions.order_by('-date').first()
    rs.last_transaction_name = last_transaction.name
    rs.last_transaction_amount = last_transaction.amount
    rs.save()


def add_to_matching_rule_set_if_any(transaction):
    item = transaction.account.item
    sets = get_rule_sets_with_name_matches(item, transaction.name)
    sets = add_amount_matches(sets, abs(transaction.amount))

    if sets:
        sets = add_date_matches(sets, transaction.date)
        matching_rs = get_best_match(sets)
        if matching_rs and (transaction.rule_set != matching_rs):
            Transaction.objects.filter(
                pk=transaction.pk).update(rule_set=matching_rs)
            recalculate_ruleset_latest_transaction(matching_rs)
            django_rq.enqueue(update_predictions_from_rule_set, rule_set)
