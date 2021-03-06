import os
import json
import datetime
from statistics import mean, mode
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
import plaid
from main.models.item import Item
from main.models.transaction import Account, Transaction

from django_rq import job

client = plaid.Client(client_id=settings.PLAID_CLIENT_ID, secret=settings.PLAID_SECRET,
                      public_key=settings.PLAID_PUBLIC_KEY, environment=settings.PLAID_ENV)

# Helpers


def calculate_date_offset(end_date, days_back_to_check):
    return end_date - datetime.timedelta(days=days_back_to_check)


def get_transactions(start_date, end_date, item):
    transactions = client.Transactions.get(
        item.access_token,
        start_date=str(start_date),
        end_date=str(end_date),
    )
    return transactions


@job('high')
def create_and_update_accounts(start_date, end_date, item):
    response = get_transactions(start_date, end_date, item)
    for account in response.get('accounts', []):
        aid = account['account_id']
        acc = Account.objects.filter(pk=aid).first() or Account(account_id=aid)
        acc.item = item
        acc.available_balance = account.get('balances', {})['available']
        acc.current_balance = account.get('balances', {})['current']
        acc.limit = account.get('balances', {})['limit']
        acc.mask = account['mask']
        acc.name = account['name']
        acc.official_name = account['official_name']
        acc.subtype = account['subtype']
        acc.type = account['type']
        acc.save()


@job('high')
def create_and_update_transactions(start_date, end_date, item):
    response = get_transactions(start_date, end_date, item)
    for transaction in response.get('transactions', []):
        tid = transaction['transaction_id']
        account_obj = Account.objects.filter(
            pk=transaction['account_id']).first()
        if account_obj.track:
            tran = Transaction.objects.filter(
                pk=tid).first() or Transaction(transaction_id=tid)
            tran.account = account_obj
            tran.amount = transaction['amount']
            tran.amount = tran.amount * -1
            tran.name = transaction['name']
            tran.pending = transaction['pending']
            tran.date = datetime.datetime.strptime(
                transaction['date'], '%Y-%m-%d').date()

            tran.save()

            ptid = transaction['pending_transaction_id']
            if ptid:
                try:
                    ptran = Transaction.objects.get(pk=ptid).delete()
                except:
                    pass


@job('high')
def delete_missing_pending_transactions(start_date, end_date, item):
    response = get_transactions(start_date, end_date, item)
    incoming_transaction_ids = [t['transaction_id']
                                for t in response.get('transactions', [])]
    if incoming_transaction_ids:
        pending_transactions_to_delete = Transaction.objects.filter(
            date__gte=start_date, date__lte=end_date, pending=True).exclude(transaction_id__in=incoming_transaction_ids)

        for ttd in pending_transactions_to_delete:
            ttd.delete()

# Views


def index(request):
    items = Item.objects.filter(user_id=1)
    context = {
        'plaid_public_key': settings.PLAID_PUBLIC_KEY,
        'plaid_environment': settings.PLAID_ENV,
        'linked_items': items,
    }

    return render(request, 'main/index.html', context)


def search_transactions(request):
    matches = Transaction.objects.filter(
        name__icontains=request.GET.get('q')).order_by('-date')
    matches = [{'name': t.name, 'date': t.date, 'amount': t.amount}
               for t in matches]
    amounts = [tr['amount'] for tr in matches]
    avg_amount = mean(amounts)
    low_amount = min(amounts)
    high_amount = max(amounts)

    dates = [tr['date'] for tr in matches]
    days = [date.day for date in dates]
    first_date = min(dates)
    low_day = min(days)
    most_frequent_day = None
    try:
        most_frequent_days = mode(days)
    except:
        pass
    high_day = max(days)

    body = {
        'amountStats': {'avg': avg_amount, 'low': low_amount, 'high': high_amount},
        'dateStats': {'mode': most_frequent_day, 'low': low_day, 'high': high_day, 'first': first_date},
        'matches': matches,
    }
    return JsonResponse(body, json_dumps_params={'indent': 2})


def create_item(request):
    public_token = request.POST.get('public_token')
    exchange_response = client.Item.public_token.exchange(public_token)
    access_token = exchange_response['access_token']
    item_res = client.Item.get(access_token)
    institution_res = client.Institutions.get_by_id(
        item_res['item']['institution_id'])

    new_item = Item.objects.create(
        item_id=item_res.get('item', {})['item_id'],
        institution_id=institution_res.get('institution', {})[
            'institution_id'],
        institution_name=institution_res.get('institution', {})['name'],
        access_token=access_token,
        public_token=public_token,
        user=request.user,
    )

    new_item.save()
    return JsonResponse({'item_id': new_item.pk})


def transactions_update(request):
    body = json.loads(request.body)
    item = Item.objects.filter(pk=body.get('item_id')).first()
    webhook_code = body.get('webhook_code', '')
    end_date = datetime.date.today()

    if webhook_code == 'INITIAL_UPDATE':
        start_date = calculate_date_offset(end_date, 30)
        create_and_update_accounts(start_date, end_date, item).delay()
        create_and_update_transactions(start_date, end_date, item)

    elif webhook_code == 'HISTORICAL_UPDATE':
        for x in range(0, 52*3):
            end_date = calculate_date_offset(end_date, 7)
            start_date = calculate_date_offset(end_date, 7)
            create_and_update_accounts.delay(start_date, end_date, item)
            create_and_update_transactions.delay(start_date, end_date, item)
            delete_missing_pending_transactions.delay(
                start_date, end_date, item)

    elif webhook_code == 'MANUAL_UPDATE':
        start_date = datetime.datetime.strptime(
            body.get('start_date', ''), '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(
            body.get('end_date', ''), '%Y-%m-%d').date()
        weeks = int((end_date - start_date).days / 7) + 1
        for x in range(0, weeks):
            end_date = calculate_date_offset(end_date, 7)
            start_date = calculate_date_offset(end_date, 7)
            create_and_update_accounts.delay(start_date, end_date, item)
            create_and_update_transactions.delay(start_date, end_date, item)
            delete_missing_pending_transactions.delay(
                start_date, end_date, item)

    elif webhook_code == 'TRANSACTIONS_REMOVED':
        removed_transactions = body.get('removed_transactions', [])
        for rt in removed_transactions:
            to_delete = Transaction.objects.get(pk=to_delete)
            to_delete.delete()

    else:
        start_date = calculate_date_offset(end_date, 7)
        create_and_update_accounts.delay(start_date, end_date, item)
        create_and_update_transactions.delay(start_date, end_date, item)
        delete_missing_pending_transactions.delay(start_date, end_date, item)

    return JsonResponse({'message': 'success'})
