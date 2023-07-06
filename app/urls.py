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

from project.views import LoginView, UserInfo, UserList, Login, ContactsView, RegisterView, UpdateView, ResetView

urlpatterns = [
    # api
    path('api/register', Login.as_view()),
    path('api/login', Login.as_view()),
    path('api/update', Login.as_view()),
    path('api/reset', Login.as_view()),
    path('api/user', UserList.as_view()),
    path('api/user/<uuid>', UserInfo.as_view()),

    # html
    path('login/', LoginView.as_view()),
    path('contact/', ContactsView.as_view()),
    path('register/', RegisterView.as_view()),
    path('update/', UpdateView.as_view()),
    path('reset/', ResetView.as_view()),
]
