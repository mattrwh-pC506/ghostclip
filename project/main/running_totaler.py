from main.models import Transaction, RunningTotal
from datetime import datetime, timedelta


def get_date_bounds(dt, days):
    start = dt - timedelta(days=dt.weekday())
    end = start + timedelta(days=days)
    return start, end


def weekly_rt(dt):
    start, end = get_week_bounds(dt, 6)
    transactions_this_week = Transaction.objects.filter(
        date__range=(start, end), rule_set__isnull=True)
    return sum(t.amount for t in transactions_this_week)


def create_or_update_running_total_from_transaction(transaction):
    start, end = get_week_bounds(transaction.date, 6)
    rt = RunningTotal.objects.filter(start_date=start, end_date=end)
    rt_amount = weekly_rt(transaction.date)
    if rt:
        rt.amount = rt_amount
    else:
        last_start, last_end = get_date_bounds(
            transaction.date - timedelta(days=7), 6)
        last_rt = RunningTotal.objects.filter(
            start_date=last_start, end_date=last_end)
        if last_rt:
            last_target = last_rt.target
        else:
            last_target = 0

        rt = RunningTotal(
            target=last_target,
            account=transaction.account,
            amount=rt_amount,
            start_date=start,
            end_date=end
        )
    rt.save()
