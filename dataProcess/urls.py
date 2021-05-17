from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^upload/data_recieve/$', views.process_data),
    url('', views.upload, name='upload'),
    
]