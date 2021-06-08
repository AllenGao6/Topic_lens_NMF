from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^upload/data_recieve/$', views.process_data),
    url(r'^upload/analyze/$', views.analyze),
    url('', views.upload, name='upload'),
    
]