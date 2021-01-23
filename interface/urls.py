from django.conf.urls import url

from . import interface_views

urlpatterns = [
    url('', interface_views.index, name='index'),
]