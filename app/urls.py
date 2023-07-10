"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from django.contrib import admin

from project.api.action import Login, LogOut, Register, Reset
from project.api.contact import ContactDetail
from project.api.user import UserList, UserDetail, UserSearch
from project.views import LoginView, ContactsView, RegisterView, UpdateView, ResetView

urlpatterns = [
    # api
    path('api/register', Register.as_view()),
    path('api/login', Login.as_view()),
    path('api/logout', LogOut.as_view()),
    path('api/reset', Reset.as_view()),

    # api/user
    path('api/user', UserList.as_view()),
    path('api/user/<uuid>', UserDetail.as_view()),
    path('api/user/search/<key>', UserSearch.as_view()),

    # api/contact
    path('api/contact', UserList.as_view()),
    path('api/contact/<uuid>', ContactDetail.as_view()),

    # html
    path('login/', LoginView.as_view()),
    path('contact/', ContactsView.as_view()),
    path('register/', RegisterView.as_view()),
    path('update/', UpdateView.as_view()),
    path('reset/', ResetView.as_view()),
    path('admin/', admin.site.urls),
]
