import os
import json
import datetime

from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
import plaid

from .models import Item, Account, Category, Location, Transaction


client = plaid.Client(client_id = settings.PLAID_CLIENT_ID, secret=settings.PLAID_SECRET,
        public_key=settings.PLAID_PUBLIC_KEY, environment=settings.PLAID_ENV)

# Views
def index(request):
    items = Item.objects.filter(user_id=1)
    context = {
            'plaid_public_key': settings.PLAID_PUBLIC_KEY,
            'plaid_environment': settings.PLAID_ENV,
            'linked_items': items,
            }
    return render(request, 'main/index.html', context)

def create_item(request):
    public_token = request.POST.get('public_token')
    exchange_response = client.Item.public_token.exchange(public_token)
    access_token = exchange_response['access_token']
    item_res = client.Item.get(access_token)
    print(item_res)
    institution_res = client.Institutions.get_by_id(item_res['item']['institution_id'])

    new_item = Item.objects.create(
            item_id=item_res.get('item', {})['item_id'],
            institution_id=institution_res.get('institution', {})['institution_id'],
            institution_name=institution_res.get('institution', {})['name'],
            access_token=access_token,
            public_token=public_token,
            family=request.user.family)

    new_item.save()
    return JsonResponse({ 'item_id': new_item.item_id})

def transactions_update(request):
    body = json.loads(request.body)
    item = Item.objects.filter(pk=body.get('item_id')).first()
    new_transaction_count  = body.get('new_transactions')
    today = datetime.date.today()
    week_ago = today - datetime.timedelta(days=7)
    response = client.Transactions.get(item.access_token, start_date=str(week_ago), end_date=str(today), count=new_transaction_count)

    for account in response.get('accounts', []):
        aid = account['account_id']
        acc = Account.objects.filter(pk=aid).first() or Account(account_id=aid)
        acc.available_balance=account.get('balances', {})['available'],
        acc.current_balance=account.get('balances', {})['current'],
        acc.limit=account.get('balances', {})['limit'],
        acc.mask=account['mask'],
        acc.name=account['name'],
        acc.official_name=account['official_name'],
        acc.subtype=account['subtype'],
        acc.type=account['type'],
        acc.save()

    for transaction in response.get('transactions', []):
        tid = transaction['transaction_id']
        tran = Transaction.objects.filter(pk=tid).first() or Transaction(transaction_id=tid)
        tran.account = Account.objects.filter(pk=tran['account_id']).first()
        tran.amount = response['amount']
        tran.name = response['name']
        tran.pending = response['pending']
        tran.date = datetime.datetime.strptime(response['date'], '%Y-%m-%d').date()

        categories = list(enumerate(transaction.get('category', [])))
        for index, category in categories:
            cat = Category.objects.filter(pk=category).first()
            if not cat:
                cat = Category(token=category)
                parent = Category.objects.filter(pk=categories[index][1]).first()
                if parent:
                    cat.parent = parent
                cat.save()

            existing_cat_rel = Transactions.objects.filter(
                    pk=tran.transaction_id,
                    categories__pk=cat.category_id)

            if not existing_cat_rel:
                tran.categories.add(cat)

        location = get('location', {})
        loc = Location.objects.filter(*location).first() or Location(*location)
        loc.save()
        tran.location = loc

        tran.save()

        ptid = response['pending_transaction']
        if ptid:
            ptran = Transactions.object.get(pk=ptid).delete()

    return JsonResponse({ message: 'success' })
