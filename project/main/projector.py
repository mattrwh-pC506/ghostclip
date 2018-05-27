from .models import Transaction, NameRule, AmountRule, DateRule


def build_rule_set_map(field_value, rules, rule_sets):
    for r in [rule for rule in rules if rule.matches(field_value)]
        rule_sets[r.rule_set] = [*rule_sets.get(r.rule_set, []), r]
    return rule_sets


def get_rule_sets_with_name_matches(item, name):
    rules = NameRule.objects.filter(item=item)
    return build_rule_set_map(name, rules, {})


def add_amount_matches(rule_sets, amount):
    rules = AmountRule.objects.filter(rule_set__in=list(rule_sets.keys()))
    return build_rule_set_map(amount, rules, rule_sets)


def add_date_matches(rule_sets, date):
    rules = DateRule.objects.filter(rule_set__in=list(rule_sets.keys()))
    return build_rule_set_map(date, rules, rule_sets)


def add_to_matching_rule_set_if_any(transaction):
    item = transaction.account.item
    sets = get_rule_sets_with_name_matches(item, transaction.name)
    sets = add_amount_matches(sets, transaction.amount)
    sets = add_date_matches(sets, transaction.date)

    if sets:
        match = max(sets.keys(), key=(lambda k: len(sets[k])))
        Transaction.objects.filter(pk=transaction.pk).update(rule_set=match)

        # TODO: create projections in gcal / models
