from django.urls import path

from . import views

urlpatterns = [
        path('', views.index, name='index'),
        path('create_item', views.create_item, name='create_index')
        ]


# @app.route("/get_access_token", methods=['POST'])
# @app.route("/item", methods=['GET', 'POST'])
