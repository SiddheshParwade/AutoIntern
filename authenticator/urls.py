from django.contrib.auth import views as authView
from django.urls import path , include
from . import views

urlpatterns = [
    path("register/",views.register,name='register'),
    path("",authView.LoginView.as_view(),name='login'),
    path('dashboard/',include('Dashboard.urls')),
]
