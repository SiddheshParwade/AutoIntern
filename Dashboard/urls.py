from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as authView

urlpatterns = [
    path("", views.dashboard, name='dashboard'),
    path('logout/', authView.LogoutView.as_view(), name='logout'),
]
