import os
import json

from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
import plaid

from .models import Item


client = plaid.Client(client_id = settings.PLAID_CLIENT_ID, secret=settings.PLAID_SECRET,
        public_key=settings.PLAID_PUBLIC_KEY, environment=settings.PLAID_ENV)

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
            'plaid_public_key': settings.PLAID_PUBLIC_KEY,
            'plaid_environment': settings.PLAID_ENV,
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
            family=request.user.family)

    new_item.save()
    return JsonResponse({ 'item_id': new_item.item_id})


