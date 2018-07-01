from main.models.transaction import Transaction
from main.models.rules import NameRule, AmountRule, DateRule


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


def get_best_match_by_date(sets, date):
    rules = DateRule.objects.filter(rule_set__in=list(sets.keys()))
    date_set_matches = build_rule_set_map(date, rules, {})
    if date_set_matches:
        return max(date_set_matches.keys(), key=(lambda k: len(date_set_matches[k])))
    else:
        return None


def recalculate_ruleset_latest_transaction(rs):
    transactions = Transaction.object.filter(rule_set=rs)
    last_transaction = transactions.order_by('-date').first()
    rs.last_transaction_name = last_transaction.name
    rs.last_transaction_amount = last_transaction.amount
    rs.save()


def add_to_matching_rule_set_if_any(transaction):
    item = transaction.account.item
    sets = get_rule_sets_with_name_matches(item, transaction.name)
    sets = add_amount_matches(sets, transaction.amount)

    if sets:
        matching_rs = get_best_match_by_date(sets, transaction.date)
        if matching_rs:
            Transaction.objects.filter(
                pk=transaction.pk).update(rule_set=matching_rs)
            recalculate_ruleset_latest_transaction(rs)
