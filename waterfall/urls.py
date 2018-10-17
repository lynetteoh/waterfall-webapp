"""waterfall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from webapp import views
from django.urls import include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('profile', views.profile, name='profile'),
    path('balance', views.balance, name='balance'),
    path('pay', views.pay, name='pay'),
    path('request', views.request, name='request'),
    path('team', views.team, name='team'),
    path('login', auth_views.LoginView, name='login'),
    path('product', views.product, name='product'),
    path('register-new', views.register_new, name='register_new'),
    path('logout', auth_views.LogoutView, name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('dashboard/view-more-c/', views.view_more_current, name='view_more_current'),
    path('dashboard/view-more-h/', views.view_more_history, name='view_more_history'),
    path('create-group', views.create_group, name='create_group'),
    path('all-groups', views.all_groups, name='all_groups'),
    path('edit-group', views.edit_group, name='edit_group'),
    re_path(r'^group/(?P<name>[\w|\W]+)/$', views.group_dash, name="group_dash"),
    re_path(r'^group/(?P<name>[\w|\W]+)/view-more-current$', views.view_more_current, name="view_group_current"),
    re_path(r'^group/(?P<name>[\w|\W]+)/view-more-history$', views.view_more_history, name="view_group_history"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
