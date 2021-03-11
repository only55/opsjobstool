"""datacenter URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.views.generic import RedirectView
from ansible_main.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', auth),
    path('', RedirectView.as_view(url='login/')),
    path('logout/', logout),
    path('login/', login),
    path('select/command/', select_command),
    path('group/remove/', group_remove),
    path('group/insert/', group_insert),
    path('group/update/', group_update),
    path('host/name/', host_name),
    path('host/insert/', host_insert),
    path('host/remove/', host_remove),
    path('host/update/', host_update),
    path('task/range/', task_range),
    path('task/list/', task_list),
    re_path(r'(table)/', table),
    path('group/name/', group_name),
    path('machine/group/', machine_group),
    path('machine/host/', RedirectView.as_view(url='/machine/host/home/')),
    re_path(r'machine/host/(.+)/', machine_host),
    path('accept/task/', accept_task),
    path('index/', index),
    path('event/log/', event_log),
    path('event/info/', event_info),
    path('task/info/', task_info),
    path('task/order/', task_order),
    path('task/create/', user_exec),
    re_path('deloy/(.+)', page_404),
    re_path('deloy/(.+)', page_404),
    re_path('deloy/(.+)', page_404),
    re_path('process/', page_404),
    re_path('exit/', page_404),

]
