import os
import json

from django.shortcuts import render
from django.http import JsonResponse
import plaid

from .models import Item


PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET = os.getenv('PLAID_SECRET')
PLAID_PUBLIC_KEY = os.getenv('PLAID_PUBLIC_KEY')
PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')

client = plaid.Client(client_id = PLAID_CLIENT_ID, secret=PLAID_SECRET,
        public_key=PLAID_PUBLIC_KEY, environment=PLAID_ENV)

# Helpers
def memoize(obj):
    cache = obj.cache = {}
    def memoizer(*args, **kwargs):
        sargs = json.dumps(args)
        if sargs not in cache:
            cache[sargs] = obj(*args, **kwargs)
        return cache[sargs]
    return memoizer

@memoize
def item_factory(access_token):
    return client.Item.get(access_token)

@memoize
def institution_factory(item_response):
    return client.Institutions.get_by_id(item_response['item']['institution_id'])

# Views
def index(request):
    items = Item.objects.filter(user_id=1)
    context = {
            'plaid_public_key': PLAID_PUBLIC_KEY,
            'plaid_environment': PLAID_ENV,
            'linked_items': items,
            }
    return render(request, 'main/index.html', context)

def create_item(request):
    public_token = request.POST.get('public_token')
    exchange_response = client.Item.public_token.exchange(public_token)
    access_token = exchange_response['access_token']

    new_item = Item.objects.create(
            item_id=item_factory(access_token)['item']['item_id'],
            institution_id=institution_factory(item_factory(access_token))['institution']['institution_id'],
            institution_name=institution_factory(item_factory(access_token))['institution']['name'],
            access_token=access_token,
            user_id=1)

    new_item.save()
    return JsonResponse({ 'error': 'none' })
