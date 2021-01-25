"""topiclens URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from interface import interface_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^interface/', include('interface.urls')),

    url(r'^api_interface/update_topics/$', interface_views.update_topics),
    url(r'^api_interface/split_topics/$', interface_views.split_topics),
    url(r'^api_interface/split_topics_noupdate/$', interface_views.split_topics_noupdate),
    url(r'^api_interface/merge_topics/$', interface_views.merge_topics),
    url(r'^api_interface/gen_json/$', interface_views.gen_json),
    url(r'^api_interface/get_doc/$', interface_views.get_doc),
    url(r'^api_interface/get_init_cords/$', interface_views.get_init_cords),
    url(r'^api_interface/init_state/$', interface_views.init_state),
    url(r'^api_interface/last_state/$', interface_views.last_state),
    url(r'^api_interface/num_topics/$', interface_views.num_topics),
    url(r'^api_interface/get_tree_graph/$', interface_views.get_tree_graph),

]
