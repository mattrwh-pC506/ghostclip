from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create_item', views.create_item, name='create_item'),
    path('transactions_update', views.transactions_update,
         name='transactions_update'),
    path('transactions_search', views.search_transactions,
         name='transactions_search'),
]
